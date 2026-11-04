//! TIDBI data core.
//!
//! The original tool is a Delphi 7 / ADO front end over `base.mdb` (Jet 4).
//! `scripts/export_mdb.py` converts that database to JSON; this crate embeds
//! the export, reimplements the original SQL filters (tree nodes, rarity,
//! stat ranges, requirements and `texteffect LIKE` conditions) and exports the
//! result to the TSX UI as a native module.

use nsh_core::prelude::*;
use serde_json::{json, Value};
use std::sync::{LazyLock, Mutex};
use std::collections::{HashMap, HashSet};

const ITEMS_JSON: &str = include_str!("../data/items.json");
const EFFECTS_JSON: &str = include_str!("../data/effects.json");
const SETS_JSON: &str = include_str!("../data/sets.json");
const SET_LIST_JSON: &str = include_str!("../data/setsspisok.json");
const EFFECT_PATTERNS_JSON: &str = include_str!("../data/effect_patterns.json");
const NAMES_JSON: &str = include_str!("../data/names.json");
const AFFIX_JSON: &str = include_str!("../data/affix_i18n.json");
const DESCRIPTIONS_JSON: &str = include_str!("../data/descriptions.json");
const SET_NAMES_JSON: &str = include_str!("../data/set_names.json");
const I18N_JSON: &str = include_str!("../data/i18n.json");
/// Icons ship as this crate's assets (`assets/icons/`, `assets!()`), so every
/// target — the web build included, which has no file system — loads them
/// through NSH's asset URLs instead of `data:` URIs built by reading files.
const ICON_PREFIX: &str = "asset:/@nsh-app-tidbi/icons/";
const ICON_PLACEHOLDER: &str = "asset:/@nsh-app-tidbi/icons/IG_skill_empty_result.png";

/// Favorites are kept in a JSON file next to the app's data. NSH Storage
/// needs the reactive runtime, which is unavailable at bundle startup and in
/// `cargo test`; a plain file works on every target.
fn favorites_path() -> std::path::PathBuf {
    let base = if let Ok(home) = std::env::var("HOME") {
        std::path::PathBuf::from(home)
            .join("Library/Application Support/com.mytorchlight.tidbi")
    } else if let Ok(appdata) = std::env::var("APPDATA") {
        std::path::PathBuf::from(appdata).join("com.mytorchlight.tidbi")
    } else {
        std::path::PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/data"))
    };
    base.join("favorites.json")
}

fn load_favorites() -> HashSet<String> {
    std::fs::read_to_string(favorites_path())
        .ok()
        .and_then(|s| serde_json::from_str::<Vec<String>>(&s).ok())
        .unwrap_or_default()
        .into_iter()
        .collect()
}

fn save_favorites(favs: &HashSet<String>) {
    let path = favorites_path();
    if let Some(dir) = path.parent() {
        let _ = std::fs::create_dir_all(dir);
    }
    let list: Vec<&String> = favs.iter().collect();
    let _ = std::fs::write(path, serde_json::to_string(&list).unwrap_or_default());
}

/// The app's UI set: what `App.tsx` imports from `tidbi/native`.
#[native_module("tidbi/native")]
fn native(registry: &mut Registry) {
    registry.assets(assets!()).module::<Db>();
}

struct Item(Value);

impl Item {
    fn s(&self, key: &str) -> &str {
        self.0.get(key).and_then(Value::as_str).unwrap_or("")
    }
    fn f(&self, key: &str) -> f64 {
        self.0.get(key).and_then(Value::as_f64).unwrap_or(0.0)
    }
    fn i(&self, key: &str) -> i64 {
        self.0.get(key).and_then(Value::as_i64).unwrap_or(0)
    }

    /// `QItems` view: per-element DPS summed into `DPS_ALL`.
    fn dps(&self) -> f64 {
        let speed = self.f("SPEED");
        if speed <= 0.0 {
            return 0.0;
        }
        let mut sum = 0.0;
        for (lo, hi) in [
            ("MIN_DMG_PHYSICAL", "MAX_DMG_PHYSICAL"),
            ("MIN_DMG_ICE", "MAX_DMG_ICE"),
            ("MIN_DMG_FIRE", "MAX_DMG_FIRE"),
            ("MIN_DMG_ELECTRIC", "MAX_DMG_ELECTRIC"),
            ("MIN_DMG_POISON", "MAX_DMG_POISON"),
        ] {
            sum += ((self.f(lo) + self.f(hi)) / (2.0 * speed)).round();
        }
        sum
    }
}

#[derive(Clone)]
struct Node {
    id: String,
    parent: String,
    label: String,
    kind: String,
    inc: Vec<String>,
    exc: Vec<String>,
    arg: String,
    depth: usize,
}

fn node(
    id: &str,
    parent: &str,
    label: &str,
    kind: &str,
    inc: &[&str],
    exc: &[&str],
    arg: &str,
    depth: usize,
) -> Node {
    Node {
        id: id.into(),
        parent: parent.into(),
        label: label.into(),
        kind: kind.into(),
        inc: inc.iter().map(|s| s.to_string()).collect(),
        exc: exc.iter().map(|s| s.to_string()).collect(),
        arg: arg.into(),
        depth,
    }
}

/// The original TreeView1 categories, expressed as `UNITTYPE LIKE` groups.
fn tree_nodes(set_names: &[String]) -> Vec<Node> {
    let mut n = vec![
        node("all", "", "All Items", "all", &[], &[], "", 0),
        node("armor", "all", "Armor", "unit", &["Boots", "Leggings", "Gloves", "Belt", "Armor", "Helmet", "Shield"], &[], "", 1),
        node("helmets", "armor", "Helmets", "unit", &["Helmet"], &[], "", 2),
        node("chest", "armor", "Chest Armor", "unit", &["Chest Armor"], &[], "", 2),
        node("shoulders", "armor", "Shoulder Armor", "unit", &["Shoulder Armor"], &[], "", 2),
        node("belts", "armor", "Belts", "unit", &["Belt"], &[], "", 2),
        node("gloves", "armor", "Gloves", "unit", &["Gloves"], &[], "", 2),
        node("pants", "armor", "Pants", "unit", &["Leggings"], &[], "", 2),
        node("boots", "armor", "Boots", "unit", &["Boots"], &[], "", 2),
        node("shields", "armor", "Shields", "unit", &["Shield"], &[], "", 2),
        node("weapons", "all", "Weapons", "unit", &["Axe", "Bow", "Cannon", "Claw", "Crossbow", "Great", "Mace", "Pistol", "Polearm", "Shotgonne", "Staff", "Sword", "Wand"], &[], "", 1),
        node("one_handed", "weapons", "One handed", "unit", &["Axe", "Pistol", "Claw", "Mace", "Sword", "Wand"], &["Great"], "", 2),
        node("two_handed", "weapons", "Two handed", "unit", &["Crossbow", "Great", "Bow", "Polearm", "Staff", "Cannon", "Shotgonne"], &[], "", 2),
        node("axes", "weapons", "Axes", "unit", &["Axe"], &["Great"], "", 2),
        node("swords", "weapons", "Swords", "unit", &["Sword"], &["Great"], "", 2),
        node("maces", "weapons", "Maces", "unit", &["Mace"], &["Great"], "", 2),
        node("wands", "weapons", "Wands", "unit", &["Wand"], &[], "", 2),
        node("pistols", "weapons", "Pistols", "unit", &["Pistol"], &[], "", 2),
        node("claws", "weapons", "Claws", "unit", &["Claw"], &[], "", 2),
        node("bows", "weapons", "Bows", "unit", &["Bow"], &["Cross"], "", 2),
        node("crossbows", "weapons", "Crossbows", "unit", &["Crossbow"], &[], "", 2),
        node("greataxes", "weapons", "Greataxes", "unit", &["Greataxe"], &[], "", 2),
        node("greathammers", "weapons", "Greathammers", "unit", &["Greathammer"], &[], "", 2),
        node("greatswords", "weapons", "Greatswords", "unit", &["Greatsword"], &[], "", 2),
        node("polearms", "weapons", "Polearms", "unit", &["Polearm"], &[], "", 2),
        node("staffs", "weapons", "Staffs", "unit", &["Staff"], &[], "", 2),
        node("cannons", "weapons", "Cannons", "unit", &["Cannon"], &[], "", 2),
        node("shotgonnes", "weapons", "Shotgonnes", "unit", &["Shotgonne"], &[], "", 2),
        node("accessories", "all", "Accessories", "unit", &["Tag", "Collar", "Necklace", "Ring"], &[], "", 1),
        node("rings", "accessories", "Rings", "unit", &["Ring"], &[], "", 2),
        node("necklaces", "accessories", "Necklaces", "unit", &["Necklace"], &[], "", 2),
        node("collars", "accessories", "Collars", "unit", &["Collar"], &[], "", 2),
        node("tags", "accessories", "Tags", "unit", &["Tag"], &[], "", 2),
        node("consumables", "all", "Consumables", "unit", &["Map", "Scroll", "Dynamite", "Fish"], &[], "", 1),
        node("potions", "consumables", "Potions", "unit", &["Potion"], &[], "", 2),
        node("fish", "consumables", "Fish", "unit", &["Fish"], &[], "", 2),
        node("maps", "consumables", "Maps", "unit", &["Map"], &[], "", 2),
        node("scrolls", "consumables", "Scrolls", "unit", &["Scroll"], &[], "", 2),
        node("spells", "consumables", "Spells", "unit", &["Spell"], &[], "", 2),
        node("socketables", "consumables", "Socketables", "unit", &["Socketable"], &[], "", 2),
        node("classes", "all", "Classes", "anyclass", &[], &[], "", 1),
        node("cls_berserker", "classes", "Berserker", "class", &[], &[], "Berserker", 2),
        node("cls_engineer", "classes", "Engineer", "class", &[], &[], "Engineer", 2),
        node("cls_outlander", "classes", "Outlander", "class", &[], &[], "Outlander", 2),
        node("cls_embermage", "classes", "Embermage", "class", &[], &[], "Embermage", 2),
        node("for_pets", "all", "For Pets", "unit", &["Collar", "Tag"], &[], "", 1),
        node("quest_items", "all", "Quest Items", "unit", &["Item"], &[], "", 1),
        node("sets", "all", "Sets", "setitems", &[], &[], "", 1),
    ];
    for name in set_names {
        n.push(node(
            &format!("set:{}", name),
            "sets",
            name,
            "set",
            &[],
            &[],
            name,
            2,
        ));
    }
    n.push(node("favorites", "all", "Favorites", "favorites", &[], &[], "", 1));
    n
}

struct Core {
    items: Vec<Item>,
    effects: HashMap<String, Vec<Value>>,
    sets: HashMap<String, Vec<Value>>,
    set_list: Vec<Value>,
    patterns: Vec<Value>,
    nodes: Vec<Node>,
    node_map: HashMap<String, Node>,
    names: HashMap<String, Value>,
    affix_i18n: HashMap<String, Value>,
    descriptions: HashMap<String, Value>,
    set_names: HashMap<String, Value>,
    i18n: Value,
    favorites: Mutex<HashSet<String>>,
}

static DB: LazyLock<Core> = LazyLock::new(|| {
        let items: Vec<Item> = serde_json::from_str::<Vec<Value>>(ITEMS_JSON)
            .expect("data/items.json")
            .into_iter()
            .map(Item)
            .collect();
        let effects: Vec<Value> = serde_json::from_str(EFFECTS_JSON).expect("data/effects.json");
        let sets: Vec<Value> = serde_json::from_str(SETS_JSON).expect("data/sets.json");
        let set_list: Vec<Value> =
            serde_json::from_str(SET_LIST_JSON).expect("data/setsspisok.json");
        let patterns: Vec<Value> =
            serde_json::from_str(EFFECT_PATTERNS_JSON).expect("data/effect_patterns.json");
        let names: HashMap<String, Value> =
            serde_json::from_str(NAMES_JSON).expect("data/names.json");
        let affix_i18n: HashMap<String, Value> =
            serde_json::from_str(AFFIX_JSON).expect("data/affix_i18n.json");
        let descriptions: HashMap<String, Value> =
            serde_json::from_str(DESCRIPTIONS_JSON).expect("data/descriptions.json");
        let set_name_map: HashMap<String, Value> =
            serde_json::from_str(SET_NAMES_JSON).expect("data/set_names.json");
        let i18n: Value = serde_json::from_str(I18N_JSON).expect("data/i18n.json");

        let mut emap: HashMap<String, Vec<Value>> = HashMap::new();
        for e in effects {
            let key = e.get("item").and_then(Value::as_str).unwrap_or("").to_string();
            emap.entry(key).or_default().push(e);
        }
        let mut smap: HashMap<String, Vec<Value>> = HashMap::new();
        for s in sets {
            let key = normalize(s.get("iTRANSLATION").and_then(Value::as_str).unwrap_or(""));
            smap.entry(key).or_default().push(s);
        }
        let mut set_names: Vec<String> = set_list
            .iter()
            .map(|s| {
                s.get("DISPLAYNAME")
                    .and_then(Value::as_str)
                    .unwrap_or("")
                    .to_string()
            })
            .filter(|s| !s.is_empty())
            .collect();
        set_names.sort();
        set_names.dedup();

        let nodes = tree_nodes(&set_names);
        let node_map = nodes.iter().map(|n| (n.id.clone(), n.clone())).collect();
        // Favorites live in a plain JSON file (no reactive runtime needed).

        Core {
            items,
            effects: emap,
            sets: smap,
            set_list,
            patterns,
            nodes,
            node_map,
            names,
            affix_i18n,
            descriptions,
            set_names: set_name_map,
            i18n,
            favorites: Mutex::new(load_favorites()),
        }
});

fn db() -> &'static Core {
    &DB
}

/// Set names in `items.SETS` and `sets.iTRANSLATION` differ by case and by a
/// control character in `Mondon\x19 s Vestment`; compare them loosely.
fn normalize(s: &str) -> String {
    s.chars()
        .map(|c| match c {
            '\u{2019}' | '\u{0019}' => '\'',
            c if c.is_control() => ' ',
            c => c.to_ascii_lowercase(),
        })
        .collect::<String>()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

/// SQL `LIKE` with `%` (and `_`), case-insensitive, as Access/Jet used it.
fn like(pattern: &str, text: &str) -> bool {
    let p = pattern.to_lowercase();
    let t = text.to_lowercase();
    let parts: Vec<&str> = p.split('%').collect();
    let mut pos = 0usize;
    for (idx, part) in parts.iter().enumerate() {
        if part.is_empty() {
            continue;
        }
        // `_` is rare in this dataset; treat it as a wildcard by splitting.
        if part.contains('_') {
            let subs: Vec<&str> = part.split('_').collect();
            let mut sub_pos = pos;
            for sub in subs.iter().filter(|s| !s.is_empty()) {
                if let Some(at) = t[sub_pos..].find(sub) {
                    sub_pos += at + sub.len();
                } else {
                    return false;
                }
            }
            pos = sub_pos;
            continue;
        }
        if let Some(at) = t[pos..].find(part) {
            let found = pos + at;
            // A leading literal (no leading '%') must match at the start.
            if idx == 0 && !p.starts_with('%') && found != 0 {
                return false;
            }
            pos = found + part.len();
        } else {
            return false;
        }
    }
    // A trailing literal (no trailing '%') must reach the end.
    if !p.ends_with('%') {
        let last = parts.last().copied().unwrap_or("");
        if !last.is_empty() && !t.ends_with(last) {
            return false;
        }
    }
    true
}

fn unit_matches(u: &str, words: &[String]) -> bool {
    let lower = u.to_lowercase();
    words.iter().any(|w| lower.contains(&w.to_lowercase()))
}

fn rarity_group(u: &str) -> &'static str {
    let l = u.to_lowercase();
    if l.contains("legendary") {
        "Legendary"
    } else if l.contains("unique") {
        "Unique"
    } else if l.contains("rare") {
        "Rare"
    } else if l.contains("item") {
        "Quest"
    } else {
        "Common"
    }
}

fn between(v: f64, lo: Option<f64>, hi: Option<f64>) -> bool {
    lo.map_or(true, |x| v >= x) && hi.map_or(true, |x| v <= x)
}

fn stat_columns(field: &str) -> (&'static str, &'static str) {
    match field {
        "Physical Damage" => ("MIN_DMG_PHYSICAL", "MAX_DMG_PHYSICAL"),
        "Ice Damage" => ("MIN_DMG_ICE", "MAX_DMG_ICE"),
        "Fire Damage" => ("MIN_DMG_FIRE", "MAX_DMG_FIRE"),
        "Electric Damage" => ("MIN_DMG_ELECTRIC", "MAX_DMG_ELECTRIC"),
        "Poison Damage" => ("MIN_DMG_POISON", "MAX_DMG_POISON"),
        "Physical Armor" => ("MIN_ARM_PHYSICAL", "MAX_ARM_PHYSICAL"),
        "Ice Armor" => ("MIN_ARM_ICE", "MAX_ARM_ICE"),
        "Fire Armor" => ("MIN_ARM_FIRE", "MAX_ARM_FIRE"),
        "Electric Armor" => ("MIN_ARM_ELECTRIC", "MAX_ARM_ELECTRIC"),
        "Poison Armor" => ("MIN_ARM_POISON", "MAX_ARM_POISON"),
        _ => ("", ""),
    }
}

fn req_column(field: &str) -> &'static str {
    match field {
        "Level" => "LEVEL_REQUIRED",
        "Strength" => "STRENGTH_REQUIRED",
        "Dexterity" => "DEXTERITY_REQUIRED",
        "Focus" => "MAGIC_REQUIRED",
        "Vitality" => "DEFENSE_REQUIRED",
        _ => "",
    }
}

impl Core {
    fn favorite(&self, consol: &str) -> bool {
        self.favorites.lock().unwrap().contains(consol)
    }

    /// Item name in `lang`, falling back to English and then to the original
    /// TIDBI columns (`DISPLAYNAME` / Russian `iTRANSLATION`).
    fn localized(&self, it: &Item, lang: &str) -> String {
        let consol = it.s("ConsolNAME");
        if let Some(map) = self.names.get(consol) {
            if let Some(value) = map.get(lang).and_then(Value::as_str) {
                if !value.is_empty() {
                    return value.to_string();
                }
            }
            if lang != "en" {
                if let Some(value) = map.get("en").and_then(Value::as_str) {
                    if !value.is_empty() {
                        return value.to_string();
                    }
                }
            }
        }
        if lang == "ru" && !it.s("iTRANSLATION").is_empty() {
            return it.s("iTRANSLATION").to_string();
        }
        it.s("DISPLAYNAME").to_string()
    }

    /// One translation from an English-keyed table (`descriptions.json`,
    /// `affix_i18n.json`), in `lang`.
    fn translated(&self, map: &HashMap<String, Value>, key: &str, lang: &str) -> Option<String> {
        map.get(key)
            .and_then(|entry| entry.get(lang))
            .and_then(Value::as_str)
            .filter(|value| !value.is_empty())
            .map(str::to_string)
    }

    /// Free-text search over every exported language, plus the two columns
    /// the original tool searched.
    fn item_matches(&self, it: &Item, q: &str) -> bool {
        if it.s("DISPLAYNAME").to_lowercase().contains(q)
            || it.s("iTRANSLATION").to_lowercase().contains(q)
        {
            return true;
        }
        self.names
            .get(it.s("ConsolNAME"))
            .and_then(Value::as_object)
            .is_some_and(|map| {
                map.values()
                    .filter_map(Value::as_str)
                    .any(|value| value.to_lowercase().contains(q))
            })
    }

    fn node_matches(&self, id: &str, it: &Item) -> bool {
        if id == "all" {
            return true;
        }
        if id == "favorites" {
            return self.favorite(it.s("ConsolNAME"));
        }
        let Some(n) = self.node_map.get(id) else {
            return true;
        };
        match n.kind.as_str() {
            "unit" => {
                unit_matches(it.s("UNITTYPE"), &n.inc)
                    && (n.exc.is_empty() || !unit_matches(it.s("UNITTYPE"), &n.exc))
            }
            "class" => it.s("REQ_CLASS").eq_ignore_ascii_case(&n.arg),
            "set" => normalize(it.s("SETS")) == normalize(&n.arg),
            "anyclass" => !it.s("REQ_CLASS").is_empty(),
            "setitems" => !it.s("SETS").is_empty(),
            "favorites" => self.favorite(it.s("ConsolNAME")),
            _ => true,
        }
    }

    fn condition(&self, c: &Value, it: &Item) -> bool {
        let kind = c.get("t").and_then(Value::as_str).unwrap_or("");
        let lo = c.get("min").and_then(Value::as_f64);
        let hi = c.get("max").and_then(Value::as_f64);
        let v = c.get("v").and_then(Value::as_str).unwrap_or("");
        match kind {
            "rarity" => match v {
                "Common" => {
                    let u = it.s("UNITTYPE").to_lowercase();
                    !u.contains("rare")
                        && !u.contains("unique")
                        && !u.contains("legendary")
                        && !u.contains("item")
                }
                "Quest item" => it.s("UNITTYPE").to_lowercase().contains("item"),
                other => it
                    .s("UNITTYPE")
                    .to_lowercase()
                    .contains(&other.to_lowercase()),
            },
            "class" => it.s("REQ_CLASS").eq_ignore_ascii_case(v),
            "stat" => {
                let field = c.get("f").and_then(Value::as_str).unwrap_or("");
                if field == "DPS" {
                    between(it.dps(), lo, hi)
                } else if field == "Level" {
                    between(it.i("iLEVEL") as f64, lo, hi)
                } else if field == "Block Chance" {
                    between(it.i("BLOCK_CHANCE") as f64, lo, hi)
                } else {
                    let (min_col, max_col) = stat_columns(field);
                    if min_col.is_empty() {
                        true
                    } else {
                        // The original SQL compares MIN>=lower and MAX<=upper.
                        between(it.f(min_col), lo, None)
                            && between(it.f(max_col), None, hi)
                    }
                }
            }
            "req" => {
                let field = c.get("f").and_then(Value::as_str).unwrap_or("");
                let col = req_column(field);
                if col.is_empty() {
                    true
                } else {
                    between(it.i(col) as f64, lo, hi)
                }
            }
            "effect" => {
                let pattern = c.get("p").and_then(Value::as_str).unwrap_or("");
                let consol = it.s("ConsolNAME");
                self.effects.get(consol).is_some_and(|rows| {
                    rows.iter().any(|e| {
                        let text = e.get("texteffect").and_then(Value::as_str).unwrap_or("");
                        let number = e.get("chislo").and_then(Value::as_f64).unwrap_or(0.0);
                        like(pattern, text) && between(number, lo, hi)
                    })
                })
            }
            _ => true,
        }
    }
}

/// The Rust core the TSX UI calls. Every function is synchronous and returns
/// JSON, so it runs in the TSX call with no promise.
#[module]
pub struct Db;

#[module]
impl Db {
    /// Tree nodes, filter options and database counts, as one JSON object.
    pub fn options() -> String {
        let d = db();
        let icons = assets!().len();
        let tree: Vec<Value> = d
            .nodes
            .iter()
            .map(|n| json!({"id": n.id, "parent": n.parent, "label": n.label, "depth": n.depth}))
            .collect();
        json!({
            "counts": {
                "items": d.items.len(),
                "effects": d.effects.values().map(Vec::len).sum::<usize>(),
                "sets": d.set_list.len(),
                "icons": icons,
            },
            "tree": tree,
            "rarities": ["Common", "Rare", "Unique", "Legendary", "Quest item"],
            "stats": ["Level", "DPS", "Physical Damage", "Ice Damage", "Fire Damage",
                      "Electric Damage", "Poison Damage", "Physical Armor", "Ice Armor",
                      "Fire Armor", "Electric Armor", "Poison Armor", "Block Chance"],
            "requires": ["Level", "Strength", "Dexterity", "Focus", "Vitality", "Class"],
            "classes": ["Berserker", "Engineer", "Outlander", "Embermage"],
            "languages": [
                {"id": "en", "label": "English"},
                {"id": "zh-Hans", "label": "简体中文"},
                {"id": "zh-Hant", "label": "繁體中文"},
                {"id": "ru", "label": "Русский"},
                {"id": "de", "label": "Deutsch"},
                {"id": "ja", "label": "日本語"},
                {"id": "pl", "label": "Polski"},
            ],
            "i18n": d.i18n,
            "setNames": d.set_names,
            "effects": d.patterns,
            "sorts": [
                {"id": "type", "label": "by Type"},
                {"id": "level", "label": "by Level"},
                {"id": "dps", "label": "by DPS"},
            ],
        })
        .to_string()
    }

    /// Run a search. `spec` is JSON: node, q, filters[], or, onlySets, inNode, sort.
    pub fn query(spec: String) -> String {
        let d = db();
        let s: Value = serde_json::from_str(&spec).unwrap_or(Value::Null);
        let node = s.get("node").and_then(Value::as_str).unwrap_or("all");
        let q = s
            .get("q")
            .and_then(Value::as_str)
            .unwrap_or("")
            .trim()
            .to_lowercase();
        let empty = Vec::new();
        let filters = s.get("filters").and_then(Value::as_array).unwrap_or(&empty);
        let or_mode = s.get("or").and_then(Value::as_bool).unwrap_or(false);
        let only_sets = s.get("onlySets").and_then(Value::as_bool).unwrap_or(false);
        let in_node = s.get("inNode").and_then(Value::as_bool).unwrap_or(false);
        let sort = s.get("sort").and_then(Value::as_str).unwrap_or("type");
        let lang = s.get("lang").and_then(Value::as_str).unwrap_or("en");

        let mut rows: Vec<&Item> = d
            .items
            .iter()
            .filter(|it| {
                let base = if !q.is_empty() && !in_node {
                    true // free-text search is global unless "in selected node"
                } else {
                    d.node_matches(node, it)
                };
                if !base || (only_sets && it.s("SETS").is_empty()) {
                    return false;
                }
                if !q.is_empty() && !d.item_matches(it, &q) {
                    return false;
                }
                if filters.is_empty() {
                    return true;
                }
                if or_mode {
                    filters.iter().any(|c| d.condition(c, it))
                } else {
                    filters.iter().all(|c| d.condition(c, it))
                }
            })
            .collect();

        rows.sort_by(|a, b| match sort {
            "level" => (a.i("iLEVEL"), a.s("DISPLAYNAME")).cmp(&(b.i("iLEVEL"), b.s("DISPLAYNAME"))),
            "dps" => b
                .dps()
                .partial_cmp(&a.dps())
                .unwrap_or(std::cmp::Ordering::Equal)
                .then_with(|| a.s("DISPLAYNAME").cmp(b.s("DISPLAYNAME"))),
            _ => (a.s("UNITTYPE"), a.i("iLEVEL"), a.s("DISPLAYNAME"))
                .cmp(&(b.s("UNITTYPE"), b.i("iLEVEL"), b.s("DISPLAYNAME"))),
        });

        let total = rows.len();
        let compact: Vec<Value> = rows
            .into_iter()
            .take(4000)
            .map(|it| {
                json!([
                    it.s("ConsolNAME"),
                    d.localized(it, lang),
                    it.s("iTRANSLATION"),
                    it.s("ICON"),
                    it.i("iLEVEL"),
                    it.dps(),
                    it.s("UNITTYPE"),
                    it.s("REQ_CLASS"),
                    rarity_group(it.s("UNITTYPE")),
                    d.favorite(it.s("ConsolNAME")),
                    it.s("SETS"),
                    it.s("DISPLAYNAME"),
                ])
            })
            .collect();
        json!({ "total": total, "rows": compact }).to_string()
    }

    /// Full detail of one item, with its random enchantments, set bonuses and
    /// every exported language.
    pub fn detail(consol: String, lang: String) -> String {
        let d = db();
        let Some(it) = d.items.iter().find(|x| x.s("ConsolNAME") == consol) else {
            return "null".to_string();
        };
        let effects: Vec<String> = d
            .effects
            .get(&consol)
            .map(|rows| {
                rows.iter()
                    .filter_map(|e| e.get("texteffect").and_then(Value::as_str))
                    .filter(|s| *s != "BLANK_NO_EFFECTS")
                    .map(|text| {
                        d.translated(&d.affix_i18n, text, &lang)
                            .unwrap_or_else(|| text.to_string())
                    })
                    .collect()
            })
            .unwrap_or_default();
        let set_name = it.s("SETS");
        let mut bonuses: Vec<Value> = d
            .sets
            .get(&normalize(set_name))
            .map(|rows| {
                rows.iter()
                    .map(|r| {
                        let text = r.get("texteffect").and_then(Value::as_str).unwrap_or("");
                        json!({
                            "count": r.get("countset").and_then(Value::as_i64).unwrap_or(0),
                            "text": d.translated(&d.affix_i18n, text, &lang)
                                .unwrap_or_else(|| text.to_string()),
                        })
                    })
                    .collect()
            })
            .unwrap_or_default();
        bonuses.sort_by_key(|b| b.get("count").and_then(Value::as_i64).unwrap_or(0));

        let description = d
            .translated(&d.descriptions, it.s("DESCRIPTION"), &lang)
            .unwrap_or_else(|| it.s("DESCRIPTION").to_string());

        let damage = |lo: &str, hi: &str| json!([it.i(lo), it.i(hi)]);
        json!({
            "c": it.s("ConsolNAME"),
            "n": d.localized(it, &lang),
            "en": it.s("DISPLAYNAME"),
            "t": it.s("iTRANSLATION"),
            "names": d.names.get(&consol).cloned().unwrap_or_else(|| json!({})),
            "i": it.s("ICON"),
            "u": it.s("UNITTYPE"),
            "l": it.i("iLEVEL"),
            "lv": it.i("MINLEVEL"),
            "dps": it.dps(),
            "speed": it.f("SPEED"),
            "rarity": rarity_group(it.s("UNITTYPE")),
            "sets": set_name,
            "cl": it.s("REQ_CLASS"),
            "description": description,
            "model": format!("{}/{}", it.s("RESOURCEDIRECTORY"), it.s("MESHFILE")),
            "damage": {
                "Physical": damage("MIN_DMG_PHYSICAL", "MAX_DMG_PHYSICAL"),
                "Ice": damage("MIN_DMG_ICE", "MAX_DMG_ICE"),
                "Fire": damage("MIN_DMG_FIRE", "MAX_DMG_FIRE"),
                "Electric": damage("MIN_DMG_ELECTRIC", "MAX_DMG_ELECTRIC"),
                "Poison": damage("MIN_DMG_POISON", "MAX_DMG_POISON"),
            },
            "armor": {
                "Physical": damage("MIN_ARM_PHYSICAL", "MAX_ARM_PHYSICAL"),
                "Ice": damage("MIN_ARM_ICE", "MAX_ARM_ICE"),
                "Fire": damage("MIN_ARM_FIRE", "MAX_ARM_FIRE"),
                "Electric": damage("MIN_ARM_ELECTRIC", "MAX_ARM_ELECTRIC"),
                "Poison": damage("MIN_ARM_POISON", "MAX_ARM_POISON"),
            },
            "requires": {
                "Level": it.i("LEVEL_REQUIRED"),
                "Strength": it.i("STRENGTH_REQUIRED"),
                "Dexterity": it.i("DEXTERITY_REQUIRED"),
                "Focus": it.i("MAGIC_REQUIRED"),
                "Vitality": it.i("DEFENSE_REQUIRED"),
            },
            "sockets": [it.i("SOCKETS"), it.i("MAX_SOCKETS")],
            "block": it.i("BLOCK_CHANCE"),
            "effects": effects,
            "setBonuses": bonuses,
            "favorite": d.favorite(&consol),
        })
        .to_string()
    }

    /// The `asset:/` URI of `icons/<name>.png`, or the original tool's
    /// placeholder when the database names an icon the assets do not ship
    /// (66 names have no file in the 2014 tool either).
    pub fn icon(name: String) -> String {
        let wanted = format!("{ICON_PREFIX}{name}.png");
        assets!()
            .iter()
            .map(|file| file.uri)
            .find(|uri| *uri == wanted)
            .unwrap_or(ICON_PLACEHOLDER)
            .to_owned()
    }

    /// Toggle a favorite. Returns the new state; persisted to a JSON file.
    pub fn toggle_favorite(consol: String) -> bool {
        let d = db();
        let mut favs = d.favorites.lock().unwrap();
        let new_state = if favs.contains(&consol) {
            favs.remove(&consol);
            false
        } else {
            favs.insert(consol);
            true
        };
        save_favorites(&favs);
        new_state
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn database_loads_with_expected_counts() {
        let d = db();
        assert_eq!(d.items.len(), 6050);
        assert_eq!(d.set_list.len(), 81);
        assert!(!d.patterns.is_empty());
    }

    #[test]
    fn localized_names_come_from_the_game_export() {
        let d = db();
        let it = d
            .items
            .iter()
            .find(|x| x.s("ConsolNAME") == "crossbow_m01")
            .unwrap();
        assert_eq!(d.localized(it, "zh-Hans"), "农夫弩");
        assert_eq!(d.localized(it, "zh-Hant"), "農夫弩");
        assert_eq!(d.localized(it, "ru"), "Арбалет крестьянина");
        assert_eq!(d.localized(it, "de"), "Bauernarmbrust");
        let detail: Value =
            serde_json::from_str(&Db::detail("crossbow_m01".into(), "zh-Hans".into())).unwrap();
        assert_eq!(detail["n"].as_str(), Some("农夫弩"));
        assert_eq!(detail["en"].as_str(), Some("Peasant Crossbow"));
    }

    #[test]
    fn localized_set_names_come_from_translation_tables() {
        let d = db();
        assert_eq!(
            d.set_names["Aristocrat"]["zh-Hans"].as_str(),
            Some("贵族")
        );
        assert_eq!(
            d.set_names["The Asphyx"]["zh-Hans"].as_str(),
            Some("窒息")
        );
        assert_eq!(
            d.set_names["Mondon’s Vestment"]["zh-Hans"].as_str(),
            Some("蒙顿的法衣")
        );
    }

    #[test]
    fn localized_affixes_and_descriptions_come_from_translation_tables() {
        let d = db();
        let it = d
            .items
            .iter()
            .find(|x| x.s("ConsolNAME") == "crossbow_u01")
            .unwrap();
        assert_eq!(
            d.translated(&d.descriptions, it.s("DESCRIPTION"), "zh-Hans")
                .as_deref(),
            Some("给它上好发条让它飞吧。")
        );
        assert_eq!(
            d.translated(&d.affix_i18n, "+22 Physical Damage", "zh-Hans")
                .as_deref(),
            Some("+22点物理伤害")
        );
        let detail: Value =
            serde_json::from_str(&Db::detail("crossbow_u01".into(), "zh-Hans".into())).unwrap();
        assert_eq!(detail["description"].as_str(), Some("给它上好发条让它飞吧。"));
        assert!(detail["effects"]
            .as_array()
            .unwrap()
            .iter()
            .any(|e| e.as_str().unwrap_or("").contains("物理伤害")));
    }

    #[test]
    fn dps_matches_the_original_qitems_formula() {
        // crossbow_m01: (13+25)/(2*0.56) = 33.9 -> Access Round = 34
        let it = db()
            .items
            .iter()
            .find(|x| x.s("ConsolNAME") == "crossbow_m01")
            .unwrap();
        assert_eq!(it.dps(), 34.0);
    }

    #[test]
    fn rarity_and_like_filters() {
        assert_eq!(rarity_group("Rare Ring"), "Rare");
        assert_eq!(rarity_group("  Legendary Axe"), "Legendary");
        assert_eq!(rarity_group("Quest items"), "Quest");
        assert!(like("%+% Fire Damage%", "+10% Fire Damage"));
        assert!(like("+% Physical Damage", "+22 Physical Damage"));
        assert!(!like("%+% Fire Damage%", "+10% Ice Damage"));
    }

    #[test]
    fn queries_return_matching_rows() {
        let result: Value = serde_json::from_str(&Db::query(
            json!({
                "node": "bows",
                "q": "",
                "filters": [{"t": "rarity", "v": "Rare"}],
                "or": false,
                "onlySets": false,
                "inNode": false,
                "sort": "type"
            })
            .to_string(),
        ))
        .unwrap();
        let total = result["total"].as_u64().unwrap();
        assert!(total > 0 && total < 6050, "total={total}");
    }
}
