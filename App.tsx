import type { JSX } from "nsh/types";
import { Clipboard, Image, List, Scroll, Text, View, computed, effect, mount, signal } from "nsh";

import { Input, Link } from "nsh/base";
import { Db } from "tidbi/native";

const GITHUB_URL = "https://github.com/evrins/tl2-dex";

// ---------------------------------------------------------------------------
// Data types (the Rust module returns JSON strings)
// ---------------------------------------------------------------------------

type Row = [
  string, // ConsolNAME
  string, // localized name
  string, // iTRANSLATION (RU, base DB)
  string, // ICON
  number, // iLEVEL
  number, // DPS
  string, // UNITTYPE
  string, // REQ_CLASS
  string, // rarity group
  boolean, // favorite
  string, // SETS
  string, // English name
];

type Filter = {
  id: number;
  label: string;
  t: string;
  v?: string;
  f?: string;
  p?: string;
  min?: number;
  max?: number;
};

type TreeNode = { id: string; parent: string; label: string; depth: number };
type EffectPattern = { label: string; pattern: string };

type Detail = {
  c: string;
  n: string;
  en: string;
  t: string;
  names: Record<string, string>;
  i: string;
  u: string;
  l: number;
  lv: number;
  dps: number;
  speed: number;
  rarity: string;
  sets: string;
  cl: string;
  description: string;
  model: string;
  damage: Record<string, [number, number]>;
  armor: Record<string, [number, number]>;
  requires: Record<string, number>;
  sockets: [number, number];
  block: number;
  effects: string[];
  setBonuses: { count: number; text: string }[];
  favorite: boolean;
};


const EMPTY_DETAIL: Detail = {
  c: "", n: "", en: "", t: "", names: {}, i: "", u: "", l: 0, lv: 0, dps: 0, speed: 0,
  rarity: "Common", sets: "", cl: "", description: "", model: "",
  damage: {}, armor: {}, requires: {}, sockets: [0, 0], block: 0,
  effects: [], setBonuses: [], favorite: false,
};
const OPT: {
  counts: { items: number; effects: number; sets: number; icons: number };
  tree: TreeNode[];
  rarities: string[];
  stats: string[];
  requires: string[];
  classes: string[];
  languages: { id: string; label: string }[];
  i18n: Record<string, Record<string, string>>;
  setNames: Record<string, Record<string, string>>;
  effects: EffectPattern[];
  sorts: { id: string; label: string }[];
} = JSON.parse(Db.options());

const C = {
  bg: "#12141a",
  panel: "#1b1f2a",
  panel2: "#222735",
  line: "#2c3240",
  text: "#e6e8ee",
  muted: "#98a0b3",
  faint: "#6b7387",
  gold: "#e8c37a",
  common: "#b9c0cc",
  rare: "#5aa9e6",
  unique: "#f2a65a",
  legendary: "#ff3100",
  quest: "#8fd6a0",
  accent: "#3d6fb4",
  dps: "#e8a05a",
};

const rarityColor = (r: string): string =>
  r === "Legendary" ? C.legendary : r === "Unique" ? C.unique : r === "Rare" ? C.rare : r === "Quest" ? C.quest : C.common;

/// `UNITTYPE` is "<Rarity> <Category>"; the category maps onto a tree label.
const UNIT_TREE: Record<string, string> = {
  axe: "axes", belt: "belts", boots: "boots", bow: "bows", cannon: "cannons",
  "chest armor": "chest", claw: "claws", collar: "collars", crossbows: "crossbows",
  fish: "fish", gloves: "gloves", greataxe: "greataxes", greathammer: "greathammers",
  greatsword: "greatswords", helmet: "helmets", leggings: "pants", mace: "maces",
  map: "maps", necklace: "necklaces", pistol: "pistols", polearm: "polearms",
  potion: "potions", ring: "rings", scroll: "scrolls", shield: "shields",
  shotgonne: "shotgonnes", "shoulder armor": "shoulders", socketable: "socketables",
  spell: "spells", staff: "staffs", sword: "swords", tag: "tags", wand: "wands",
  "quest items": "quest_items",
};

const rarityBg = (r: string): string =>
  r === "Legendary" ? "#3a2a12" : r === "Unique" ? "#2c1e3a" : r === "Rare" ? "#14283a" : r === "Quest" ? "#17301f" : "#1e222c";

const iconCache = new Map<string, string>();
function icon(name: string): string {
  let uri = iconCache.get(name);
  if (uri === undefined) {
    uri = Db.icon(name);
    iconCache.set(name, uri);
  }
  return uri;
}

const num = (s: string): number | undefined => {
  const t = s.trim();
  if (!t) return undefined;
  const n = Number(t);
  return Number.isFinite(n) ? n : undefined;
};

// ---------------------------------------------------------------------------
// Reusable controls
// ---------------------------------------------------------------------------

function Btn(props: { label: string; onPress: () => void; active?: boolean; tone?: string; width?: number }) {
  return (
    <View
      role="button"
      onPress={props.onPress}
      style={{
        height: 26,
        minWidth: props.width ?? 0,
        paddingHorizontal: 9,
        borderRadius: 5,
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: props.active ? (props.tone ?? C.accent) : C.panel2,
        borderWidth: 1,
        borderColor: props.active ? (props.tone ?? C.accent) : C.line,
      }}
    >
      <Text style={{ color: props.active ? "#ffffff" : C.text, fontSize: 12, fontWeight: "600" }}>
        {props.label}
      </Text>
    </View>
  );
}

function Chip(props: { label: string; active: boolean; onPress: () => void }) {
  return (
    <View
      role="button"
      onPress={props.onPress}
      style={{
        paddingHorizontal: 7,
        paddingVertical: 4,
        borderRadius: 4,
        backgroundColor: props.active ? C.accent : C.panel2,
        borderWidth: 1,
        borderColor: props.active ? C.accent : C.line,
      }}
    >
      <Text style={{ fontSize: 11, color: props.active ? "#fff" : C.muted }}>{props.label}</Text>
    </View>
  );
}

function Picker(props: { options: string[]; value: string; onPick: (v: string) => void; render?: (v: string) => string }) {
  return (
    <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 4 }}>
      <Each of={props.options}>
        {(o) => (
          <Chip
            label={props.render ? props.render(o()) : o()}
            active={props.value === o()}
            onPress={() => props.onPick(o())}
          />
        )}
      </Each>
    </View>
  );
}

function Check(props: { label: string; on: boolean; onPress: () => void }) {
  return (
    <View role="button" onPress={props.onPress} style={{ flexDirection: "row", alignItems: "center", gap: 7, paddingVertical: 3 }}>
      <View
        style={{
          width: 14,
          height: 14,
          borderRadius: 3,
          borderWidth: 1,
          borderColor: props.on ? C.accent : C.faint,
          backgroundColor: props.on ? C.accent : "transparent",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <If when={props.on}>
          <Text style={{ color: "#fff", fontSize: 10 }}>✓</Text>
        </If>
      </View>
      <Text style={{ color: C.text, fontSize: 12 }}>{props.label}</Text>
    </View>
  );
}

function Section(props: { title: string; children?: JSX.Element }) {
  return (
    <View style={{ gap: 5, paddingBottom: 9, borderBottomWidth: 1, borderBottomColor: C.line }}>
      <Text style={{ color: C.gold, fontSize: 12, fontWeight: "700" }}>{props.title}</Text>
      {props.children}
    </View>
  );
}

function NumInput(props: { value: string; onChange: (v: string) => void; placeholder: string }) {
  return (
    <Input
      value={props.value}
      onChange={({ value }) => props.onChange(value)}
      placeholder={props.placeholder}
      keyboardType="decimal-pad"
      style={{
        flex: 1,
        height: 26,
        paddingHorizontal: 7,
        borderRadius: 4,
        borderWidth: 1,
        borderColor: C.line,
        backgroundColor: C.panel2,
        color: C.text,
        fontSize: 12,
      }}
    />
  );
}

function Labeled(props: { label: string; value: string; color?: string }) {
  return (
    <View style={{ flexDirection: "row", gap: 8, paddingVertical: 2 }}>
      <Text style={{ width: 86, color: C.faint, fontSize: 12 }}>{props.label}</Text>
      <Text style={{ flex: 1, color: props.color ?? C.text, fontSize: 12 }}>{props.value}</Text>
    </View>
  );
}

function CopyField(props: { label: string; value: string; copyLabel: string; onCopy: () => void }) {
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: 8, paddingVertical: 2 }}>
      <Text style={{ width: 86, color: C.faint, fontSize: 12 }}>{props.label}</Text>
      <Text style={{ flex: 1, color: C.text, fontSize: 12 }}>{props.value}</Text>
      <View
        role="button"
        onPress={props.onCopy}
        style={{
          paddingHorizontal: 7,
          paddingVertical: 3,
          borderRadius: 4,
          backgroundColor: C.panel2,
          borderWidth: 1,
          borderColor: C.line,
        }}
      >
        <Text style={{ color: C.muted, fontSize: 11 }}>⧉ {props.copyLabel}</Text>
      </View>
    </View>
  );
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

function App() {
  const tab = signal<"tree" | "filter">("tree");
  const node = signal("all");
  /// Tree nodes whose children are hidden; everything starts expanded.
  const collapsed = signal<ReadonlySet<string>>(new Set());
  const q = signal("");
  const lang = signal("en");
  const rows = signal<Row[]>([]);
  const total = signal(0);
  const selected = signal("");
  const locked = signal("");
  const detail = signal<Detail>(EMPTY_DETAIL);
  const iconSrc = signal("");
  const showText = signal(false);
  const about = signal(false);
  const toast = signal("");

  const live = signal(true);
  const onlySets = signal(false);
  const inNode = signal(false);
  const orMode = signal(false);
  const sort = signal("type");
  const filters = signal<Filter[]>([]);
  let nextFilterId = 1;

  const t = (key: string): string => {
    const row = OPT.i18n[key];
    return row?.[lang()] || row?.en || key;
  };
  const setLabel = (name: string): string => OPT.setNames[name]?.[lang()] || name;
  const tNode = (n: TreeNode): string => {
    if (n.id.startsWith("set:")) return setLabel(n.label);
    return OPT.i18n[`tree.${n.id}`] ? t(`tree.${n.id}`) : n.label;
  };
  /// Ids of nodes with children, which get a fold arrow.
  const parents = new Set(OPT.tree.map((n) => n.parent));
  parents.delete("");
  /// `OPT.tree` minus every node under a collapsed ancestor; parents precede children.
  const visibleTree = computed(() => {
    const closed = collapsed();
    const hidden = new Set<string>();
    return OPT.tree.filter((n) => {
      if (n.parent && (hidden.has(n.parent) || closed.has(n.parent))) {
        hidden.add(n.id);
        return false;
      }
      return true;
    });
  });
  const toggleCollapsed = (id: string): void => {
    const next = new Set(collapsed());
    if (!next.delete(id)) next.add(id);
    collapsed.set(next);
  };
  const unitLabel = (ut: string): string => {
    const lower = ut.toLowerCase().trim();
    if (lower === "quest items") return t("tree.quest_items");
    if (lower === "location item") return t("unit.location item");
    if (lower === "dynamite") return t("unit.dynamite");
    const rarity = lower.includes("legendary")
      ? "Legendary"
      : lower.includes("unique")
        ? "Unique"
        : lower.includes("rare")
          ? "Rare"
          : "";
    const base = lower.replace(/\b(legendary|unique|rare)\b/g, "").replace(/\s+/g, " ").trim();
    const key = UNIT_TREE[base];
    const label = key ? t(`tree.${key}`) : base;
    return rarity ? `${t(`rarity.${rarity}`)} · ${label}` : label;
  };
  const filterLabel = (f: Filter): string => {
    const range = `${f.min ?? "…"}–${f.max ?? "…"}`;
    if (f.t === "class") return `${t("req.Class")}: ${t(`tree.cls_${(f.v ?? "").toLowerCase()}`)}`;
    if (f.t === "stat") return `${t(`stat.${f.f ?? ""}`)} ${range}`;
    if (f.t === "req") return `${t(`req.${f.f ?? ""}`)} ${range}`;
    if (f.t === "effect") {
      const e = OPT.effects.find((x) => x.pattern === f.p);
      return `${e ? t(`effect.${e.label}`) : f.label} ${range}`;
    }
    return `${f.label} ${range}`;
  };

  // Filter form state
  const raritySel = signal<string[]>([]);
  const statSel = signal("DPS");
  const statMin = signal("");
  const statMax = signal("");
  const reqSel = signal("Level");
  const reqMin = signal("");
  const reqMax = signal("");
  const classSel = signal("Berserker");
  const effectSel = signal(OPT.effects.length ? OPT.effects[0].pattern : "%");
  const effMin = signal("");
  const effMax = signal("");

  const addFilter = (f: Omit<Filter, "id" | "label">, label: string) => {
    filters.set([...filters(), { ...f, id: nextFilterId++, label }]);
  };

  const toggleRarity = (v: string) => {
    const cur = raritySel();
    raritySel.set(cur.includes(v) ? cur.filter((x) => x !== v) : [...cur, v]);
  };

  const spec = () => ({
    node: node(),
    q: q(),
    filters: filters().map(({ t, v, f, p, min, max }) => ({ t, v, f, p, min, max })),
    rarities: raritySel(),
    or: orMode(),
    onlySets: onlySets(),
    inNode: inNode(),
    sort: sort(),
    lang: lang(),
  });

  const apply = () => {
    const result = JSON.parse(Db.query(JSON.stringify(spec())));
    rows.set(result.rows as Row[]);
    total.set(result.total as number);
  };

  effect(() => {
    spec(); // subscribe to every query input
    if (live()) apply();
  });

  const shown = computed(() => locked() || selected());

  effect(() => {
    const c = shown();
    lang();
    if (!c) return;
    const d = JSON.parse(Db.detail(c, lang())) as Detail | null;
    detail.set(d ?? EMPTY_DETAIL);
    iconSrc.set(d ? icon(d.i) : "");
  });

  const select = (c: string) => {
    if (locked()) return; // comparison lock freezes the card
    selected.set(c);
  };

  const toggleFav = (c: string) => {
    const on = Db.toggleFavorite(c);
    toast.set(on ? t("ui.fav_added") : t("ui.fav_removed"));
    apply();
    const d = JSON.parse(Db.detail(shown() || c, lang())) as Detail | null;
    detail.set(d ?? EMPTY_DETAIL);
  };

  const cardText = computed(() => {
    const d = detail();
    if (!d.c) return "";
    const lines: string[] = [];
    lines.push(d.n);
    if (d.en !== d.n) lines.push(d.en);
    lines.push(unitLabel(d.u));
    lines.push(`${t("stat.Level")} ${d.l}  ·  ${t("stat.DPS")} ${d.dps}`);
    if (d.sets) lines.push(`${t("label.set")}: ${setLabel(d.sets)}`);
    if (d.cl) lines.push(`${t("req.Class")}: ${t(`tree.cls_${d.cl.toLowerCase()}`)}`);
    lines.push("", `${t("label.damage")}:`);
    for (const k of Object.keys(d.damage)) {
      const v = d.damage[k];
      if (v[0] || v[1]) lines.push(`  ${t(`element.${k}`)}: ${v[0]}–${v[1]}`);
    }
    lines.push("", `${t("label.armor")}:`);
    for (const k of Object.keys(d.armor)) {
      const v = d.armor[k];
      if (v[0] || v[1]) lines.push(`  ${t(`element.${k}`)}: ${v[0]}–${v[1]}`);
    }
    lines.push("", `${t("label.requirements")}:`);
    for (const k of Object.keys(d.requires)) {
      if (d.requires[k]) lines.push(`  ${t(`req.${k}`)}: ${d.requires[k]}`);
    }
    if (d.sockets[0] || d.sockets[1]) lines.push("", `${t("label.sockets")}: ${d.sockets[0]} / ${d.sockets[1]}`);
    if (d.effects.length) {
      lines.push("", `${t("label.random")}:`);
      for (const e of d.effects) lines.push(`  ${e}`);
    }
    if (d.setBonuses.length) {
      lines.push("", d.sets ? `${t("label.setbonuses")} · ${setLabel(d.sets)}:` : `${t("label.setbonuses")}:`);
      for (const b of d.setBonuses) lines.push(`  (${b.count}) ${b.text}`);
    }
    if (Object.keys(d.names).length > 1) {
      lines.push("", `${t("label.allnames")}:`);
      for (const k of Object.keys(d.names)) lines.push(`  ${k}: ${d.names[k]}`);
    }
    lines.push("", `${t("label.console")}: ${d.c}`, `${t("label.model")}: ${d.model}`);
    return lines.join("\n");
  });

  // --- tree / filter panels -------------------------------------------------

  const treePanel = () => (
    <View style={{ flex: 1 }}>
      <Scroll style={{ flex: 1 }}>
        <View style={{ padding: 8, gap: 1 }}>
          <Each of={visibleTree()} key={(n) => n.id}>
            {(n) => (
              <View
                role="button"
                onPress={() => {
                  node.set(n().id);
                  if (!live()) apply();
                }}
                style={{
                  flexDirection: "row",
                  alignItems: "center",
                  paddingLeft: 3 + n().depth * 13,
                  paddingVertical: 4,
                  paddingRight: 6,
                  borderRadius: 4,
                  backgroundColor: node() === n().id ? C.accent : "transparent",
                }}
              >
                <If when={parents.has(n().id)} else={<View style={{ width: 15 }} />}>
                  <View
                    role="button"
                    testID={`tree-fold-${n().id}`}
                    onPress={() => toggleCollapsed(n().id)}
                    style={{ width: 15, alignItems: "center", justifyContent: "center" }}
                  >
                    <Text style={{ color: node() === n().id ? "#fff" : C.muted, fontSize: 9 }}>
                      {collapsed().has(n().id) ? "▶" : "▼"}
                    </Text>
                  </View>
                </If>
                <Text style={{ flex: 1, color: node() === n().id ? "#fff" : n().depth === 0 ? C.gold : C.text, fontSize: 12, fontWeight: n().depth === 0 ? "700" : "400" }}>
                  {tNode(n())}
                </Text>
              </View>
            )}
          </Each>
        </View>
      </Scroll>
      <View style={{ padding: 8, borderTopWidth: 1, borderTopColor: C.line }}>
        <Text style={{ color: C.faint, fontSize: 11 }}>
          {OPT.counts.items} {t("ui.items")} · {OPT.counts.sets} {t("tree.sets")} · {OPT.counts.icons} {t("ui.icons")}
        </Text>
      </View>
    </View>
  );

  const effectPicker = () => (
    <Scroll style={{ height: 92, borderWidth: 1, borderColor: C.line, borderRadius: 4 }}>
      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 4, padding: 5 }}>
        <Each of={OPT.effects}>
          {(e) => (
            <Chip label={t(`effect.${e().label}`)} active={effectSel() === e().pattern} onPress={() => effectSel.set(e().pattern)} />
          )}
        </Each>
      </View>
    </Scroll>
  );

  const filterPanel = () => (
    <Scroll style={{ flex: 1 }}>
      <View style={{ padding: 9, gap: 10 }}>
        <Section title={t("ui.type_rarity")}>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 4 }}>
            <Each of={OPT.rarities}>
              {(r) => (
                <Chip
                  label={t(`rarity.${r()}`)}
                  active={raritySel().includes(r())}
                  onPress={() => toggleRarity(r())}
                />
              )}
            </Each>
          </View>
        </Section>

        <Section title={t("ui.data")}>
          <Picker options={OPT.stats} value={statSel()} onPick={(v) => statSel.set(v)} render={(v) => t(`stat.${v}`)} />
          <View style={{ flexDirection: "row", gap: 5 }}>
            <NumInput value={statMin()} onChange={(v) => statMin.set(v)} placeholder={t("ui.min")} />
            <NumInput value={statMax()} onChange={(v) => statMax.set(v)} placeholder={t("ui.max")} />
            <Btn
              label="+"
              onPress={() =>
                addFilter(
                  { t: "stat", f: statSel(), min: num(statMin()), max: num(statMax()) },
                  `${statSel()} ${statMin() || "…"}–${statMax() || "…"}`,
                )
              }
            />
          </View>
        </Section>

        <Section title={t("ui.requires")}>
          <Picker options={OPT.requires} value={reqSel()} onPick={(v) => reqSel.set(v)} render={(v) => t(`req.${v}`)} />
          <If when={reqSel() === "Class"}>
            <Picker options={OPT.classes} value={classSel()} onPick={(v) => classSel.set(v)} render={(v) => t(`tree.cls_${v.toLowerCase()}`)} />
          </If>
          <If when={reqSel() !== "Class"}>
            <View style={{ flexDirection: "row", gap: 5 }}>
              <NumInput value={reqMin()} onChange={(v) => reqMin.set(v)} placeholder={t("ui.min")} />
              <NumInput value={reqMax()} onChange={(v) => reqMax.set(v)} placeholder={t("ui.max")} />
            </View>
          </If>
          <Btn
            label={t("ui.add")}
            onPress={() => {
              if (reqSel() === "Class") addFilter({ t: "class", v: classSel() }, `Class: ${classSel()}`);
              else
                addFilter(
                  { t: "req", f: reqSel(), min: num(reqMin()), max: num(reqMax()) },
                  `${reqSel()} ${reqMin() || "…"}–${reqMax() || "…"}`,
                );
            }}
          />
        </Section>

        <Section title={t("ui.effects")}>
          {effectPicker()}
          <View style={{ flexDirection: "row", gap: 5 }}>
            <NumInput value={effMin()} onChange={(v) => effMin.set(v)} placeholder={t("ui.min")} />
            <NumInput value={effMax()} onChange={(v) => effMax.set(v)} placeholder={t("ui.max")} />
            <Btn
              label="+"
              onPress={() =>
                addFilter(
                  { t: "effect", p: effectSel(), min: num(effMin()), max: num(effMax()) },
                  `${OPT.effects.find((e) => e.pattern === effectSel())?.label ?? "Effect"} ${effMin() || "…"}–${effMax() || "…"}`,
                )
              }
            />
          </View>
        </Section>

        <Section title={t("ui.options")}>
          <Check label={t("ui.only_sets")} on={onlySets()} onPress={() => onlySets.set(!onlySets())} />
          <Check label={t("ui.search_node")} on={inNode()} onPress={() => inNode.set(!inNode())} />
          <Check label={t("ui.match_any")} on={orMode()} onPress={() => orMode.set(!orMode())} />
          <Check label={t("ui.live_search")} on={live()} onPress={() => live.set(!live())} />
        </Section>

        <Section title={t("ui.sorting")}>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 4 }}>
            <Each of={OPT.sorts}>
              {(s) => (
                <Chip label={t(`sort.${s().id}`)} active={sort() === s().id} onPress={() => sort.set(s().id)} />
              )}
            </Each>
          </View>
        </Section>

        <Section title={t("ui.list")}>
          <Each of={filters()}>
            {(f) => (
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 2 }}>
                <Text style={{ flex: 1, color: C.text, fontSize: 11 }}>{filterLabel(f())}</Text>
                <View
                  role="button"
                  onPress={() => filters.set(filters().filter((x) => x.id !== f().id))}
                  style={{ paddingHorizontal: 6, paddingVertical: 2, borderRadius: 3, backgroundColor: C.panel2 }}
                >
                  <Text style={{ color: "#e88", fontSize: 11 }}>✕</Text>
                </View>
              </View>
            )}
          </Each>
          <If when={filters().length > 0}>
            <Btn label={t("ui.clear_list")} onPress={() => filters.set([])} />
          </If>
        </Section>
      </View>
    </Scroll>
  );

  // --- main -----------------------------------------------------------------

  return (
    <View style={{ flex: 1, backgroundColor: C.bg }}>
      <View style={{ height: 46, flexDirection: "row", alignItems: "center", gap: 8, paddingHorizontal: 10, backgroundColor: C.panel, borderBottomWidth: 1, borderBottomColor: C.line }}>
        <Text style={{ color: C.gold, fontSize: 15, fontWeight: "700" }}>Torchlight II · Item Database</Text>
        <View style={{ width: 12 }} />
        <View
          style={{
            width: 280,
            height: 29,
            flexDirection: "row",
            alignItems: "center",
            borderRadius: 5,
            borderWidth: 1,
            borderColor: C.line,
            backgroundColor: C.panel2,
          }}
        >
          <Input
            testID="search"
            value={q()}
            onChange={({ value }) => q.set(value)}
            onSubmit={() => apply()}
            placeholder={t("ui.search_placeholder")}
            returnKeyType="search"
            style={{
              flex: 1,
              height: 27,
              paddingHorizontal: 9,
              backgroundColor: "transparent",
              color: C.text,
              fontSize: 13,
            }}
          />
          <If when={q() !== ""}>
            <View
              role="button"
              accessibilityLabel={t("ui.clear_search")}
              onPress={() => q.set("")}
              style={{ width: 24, height: 27, alignItems: "center", justifyContent: "center" }}
            >
              <Text style={{ color: C.muted, fontSize: 15, fontWeight: "700" }}>×</Text>
            </View>
          </If>
        </View>
        <Btn label={t("ui.search")} onPress={() => apply()} />
        <View style={{ flex: 1 }} />
        <Btn label={t(showText() ? "ui.show_picture" : "ui.show_text")} onPress={() => showText.set(!showText())} />
        <Btn label={t("ui.about")} onPress={() => about.set(!about())} />
      </View>

      <View style={{ height: 32, flexDirection: "row", alignItems: "center", gap: 6, paddingHorizontal: 10, backgroundColor: "#171b24", borderBottomWidth: 1, borderBottomColor: C.line }}>
        <Text style={{ color: C.faint, fontSize: 11, fontWeight: "600" }}>{t("ui.language")}</Text>
        <Each of={OPT.languages}>
          {(l) => <Chip label={l().label} active={lang() === l().id} onPress={() => lang.set(l().id)} />}
        </Each>
        <View style={{ flex: 1 }} />
        <Text style={{ color: C.faint, fontSize: 10 }}>{t("ui.names_source")}</Text>
      </View>

      <View style={{ flex: 1, flexDirection: "row", minHeight: 0 }}>
        {/* left: tree / filter */}
        <View style={{ width: 252, backgroundColor: C.panel, borderRightWidth: 1, borderRightColor: C.line }}>
          <View style={{ flexDirection: "row", gap: 5, padding: 7 }}>
            <Btn label={t("ui.item_tree")} active={tab() === "tree"} onPress={() => tab.set("tree")} />
            <Btn label={t("ui.filter")} active={tab() === "filter"} onPress={() => tab.set("filter")} />
          </View>
          <If when={tab() === "tree"}>{treePanel()}</If>
          <If when={tab() === "filter"}>{filterPanel()}</If>
        </View>

        {/* center: results */}
        <View style={{ flex: 1, minWidth: 0 }}>
          <View style={{ height: 28, flexDirection: "row", alignItems: "center", gap: 8, paddingHorizontal: 10, backgroundColor: C.panel2, borderBottomWidth: 1, borderBottomColor: C.line }}>
            <Text style={{ width: 34, color: C.faint, fontSize: 11 }} />
            <Text style={{ flex: 1, color: C.faint, fontSize: 11, fontWeight: "700" }}>{t("label.name")}</Text>
            <Text style={{ width: 52, color: C.faint, fontSize: 11, textAlign: "right" }}>{t("stat.Level")}</Text>
            <Text style={{ width: 62, color: C.faint, fontSize: 11, textAlign: "right" }}>{t("stat.DPS")}</Text>
          </View>
          <List
            each={rows()}
            keyExtractor={(r) => r[0]}
            estimatedItemSize={38}
            style={{ flex: 1 }}
            contentStyle={{ gap: 1 }}
          >
            {(r, index) => (
              <View
                role="button"
                onPress={() => select(r()[0])}
                style={{
                  height: 38,
                  flexDirection: "row",
                  alignItems: "center",
                  gap: 8,
                  paddingHorizontal: 10,
                  backgroundColor: shown() === r()[0] ? "#2b3a52" : index() % 2 ? "#181c25" : "#151821",
                  borderLeftWidth: 3,
                  borderLeftColor: rarityColor(r()[8]),
                }}
              >
                <Image src={icon(r()[3])} style={{ width: 30, height: 30, objectFit: "contain" }} />
                <View style={{ flex: 1, minWidth: 0 }}>
                  <Text style={{ color: rarityColor(r()[8]), fontSize: 13, fontWeight: "600", numberOfLines: 1 }}>
                    {r()[1]}
                  </Text>
                  <Text style={{ color: C.faint, fontSize: 10, numberOfLines: 1 }}>
                    {unitLabel(r()[6])}{r()[1] !== r()[11] ? ` · ${r()[11]}` : ""}{r()[10] ? ` · ${r()[10]}` : ""}
                  </Text>
                </View>
                <Text style={{ color: r()[9] ? C.gold : C.muted, width: 18, fontSize: 11 }}>
                  {r()[9] ? "★" : ""}
                </Text>
                <Text style={{ color: C.muted, width: 52, fontSize: 12, textAlign: "right" }}>{r()[4]}</Text>
                <Text style={{ color: C.dps, width: 62, fontSize: 12, textAlign: "right" }}>
                  {r()[5] ? Math.round(r()[5]) : "—"}
                </Text>
              </View>
            )}
          </List>
        </View>

        {/* right: detail card */}
        <View style={{ width: 344, backgroundColor: C.panel, borderLeftWidth: 1, borderLeftColor: C.line }}>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 5, padding: 7, borderBottomWidth: 1, borderBottomColor: C.line }}>
            <Btn
              label={t(locked() ? "ui.unlock" : "ui.lock")}
              active={!!locked()}
              onPress={() => locked.set(locked() ? "" : shown())}
            />
            <Btn label={t("ui.copy_name")} onPress={() => { Clipboard.writeText(detail()?.c ?? ""); toast.set(t("ui.console_copied")); }} />
            <Btn
              label={t(detail()?.favorite ? "ui.unfav" : "ui.fav")}
              onPress={() => toggleFav(detail()?.c ?? "")}
            />
          </View>
          <If when={!!detail().c}>
            <Scroll style={{ flex: 1 }}>
              <View style={{ padding: 12, gap: 8 }}>
                <View style={{ flexDirection: "row", gap: 12, alignItems: "center" }}>
                  <View style={{ width: 64, height: 64, borderRadius: 8, backgroundColor: rarityBg(detail().rarity), borderWidth: 1, borderColor: rarityColor(detail().rarity), alignItems: "center", justifyContent: "center" }}>
                    <Image src={iconSrc()} style={{ width: 56, height: 56, objectFit: "contain" }} />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={{ color: rarityColor(detail().rarity), fontSize: 15, fontWeight: "700" }}>{detail().n}</Text>
                    <If when={detail().en !== detail().n}>
                      <Text style={{ color: C.muted, fontSize: 11 }}>{detail().en}</Text>
                    </If>
                    <Text style={{ color: C.faint, fontSize: 11 }}>{unitLabel(detail().u)}</Text>
                  </View>
                </View>

                <If when={!showText()}>
                  <View style={{ gap: 2 }}>
                    <Labeled label={t("stat.Level")} value={`${detail().l} (${t("ui.min")} ${detail().lv})`} />
                    <Labeled label={t("stat.DPS")} value={String(Math.round(detail().dps))} color={C.dps} />
                    <Labeled label={t("label.speed")} value={String(detail().speed)} />
                    <Labeled label={t("label.rarity")} value={t(`rarity.${detail().rarity}`)} color={rarityColor(detail().rarity)} />
                    <If when={!!detail().sets}><Labeled label={t("label.set")} value={setLabel(detail().sets)} color={C.gold} /></If>
                    <If when={!!detail().cl}><Labeled label={t("req.Class")} value={t(`tree.cls_${detail().cl.toLowerCase()}`)} /></If>
                    <If when={!!detail().description}><Labeled label={t("label.description")} value={detail().description} /></If>

                    <Text style={{ color: C.gold, fontSize: 12, fontWeight: "700", paddingTop: 6 }}>{t("label.damage")}</Text>
                    <Each of={Object.keys(detail().damage)}>
                      {(k) => (
                        <If when={detail().damage[k()][0] !== 0 || detail().damage[k()][1] !== 0}>
                          <Labeled label={t(`element.${k()}`)} value={`${detail().damage[k()][0]} – ${detail().damage[k()][1]}`} />
                        </If>
                      )}
                    </Each>

                    <Text style={{ color: C.gold, fontSize: 12, fontWeight: "700", paddingTop: 6 }}>{t("label.armor")}</Text>
                    <Each of={Object.keys(detail().armor)}>
                      {(k) => (
                        <If when={detail().armor[k()][0] !== 0 || detail().armor[k()][1] !== 0}>
                          <Labeled label={t(`element.${k()}`)} value={`${detail().armor[k()][0]} – ${detail().armor[k()][1]}`} />
                        </If>
                      )}
                    </Each>

                    <Text style={{ color: C.gold, fontSize: 12, fontWeight: "700", paddingTop: 6 }}>{t("label.requirements")}</Text>
                    <Each of={Object.keys(detail().requires)}>
                      {(k) => (
                        <If when={detail().requires[k()] !== 0}>
                          <Labeled label={t(`req.${k()}`)} value={String(detail().requires[k()])} />
                        </If>
                      )}
                    </Each>

                    <If when={detail().sockets[0] !== 0 || detail().sockets[1] !== 0}>
                      <Labeled label={t("label.sockets")} value={`${detail().sockets[0]} / ${detail().sockets[1]}`} />
                    </If>
                    <If when={detail().block !== 0}>
                      <Labeled label={t("label.block")} value={`${detail().block}%`} />
                    </If>

                    <If when={detail().effects.length > 0}>
                      <Text style={{ color: C.gold, fontSize: 12, fontWeight: "700", paddingTop: 6 }}>{t("label.random")}</Text>
                      <Each of={detail().effects}>
                        {(e) => <Text style={{ color: "#a8d8a0", fontSize: 12, paddingLeft: 8 }}>{e()}</Text>}
                      </Each>
                    </If>

                    <If when={detail().setBonuses.length > 0}>
                      <View style={{ flexDirection: "row", alignItems: "baseline", gap: 6, paddingTop: 6 }}>
                        <Text style={{ color: C.gold, fontSize: 12, fontWeight: "700" }}>{t("label.setbonuses")}</Text>
                        <If when={!!detail().sets}>
                          <Text style={{ color: "#d7b4f5", fontSize: 12 }}>{setLabel(detail().sets)}</Text>
                        </If>
                      </View>
                      <Each of={detail().setBonuses}>
                        {(b) => <Text style={{ color: "#d7b4f5", fontSize: 12, paddingLeft: 8 }}>{`(${b().count}) ${b().text}`}</Text>}
                      </Each>
                    </If>

                    <If when={Object.keys(detail().names).length > 1}>
                      <Text style={{ color: C.gold, fontSize: 12, fontWeight: "700", paddingTop: 6 }}>{t("label.allnames")}</Text>
                      <Each of={Object.keys(detail().names)}>
                        {(k) => <Labeled label={k()} value={detail().names[k()]} />}
                      </Each>
                    </If>

                    <Text style={{ color: C.gold, fontSize: 12, fontWeight: "700", paddingTop: 6 }}>{t("label.consolemodel")}</Text>
                    <CopyField
                      label={t("label.console")}
                      value={detail().c}
                      copyLabel={t("ui.copy")}
                      onCopy={() => {
                        Clipboard.writeText(detail().c);
                        toast.set(t("ui.copied"));
                      }}
                    />
                    <Labeled label={t("label.model")} value={detail().model} />
                  </View>
                </If>

                <If when={showText()}>
                  <Text style={{ color: C.text, fontSize: 12, fontFamily: "monospace" }}>{cardText()}</Text>
                </If>
              </View>
            </Scroll>
          </If>
          <If when={!detail().c}>
            <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
              <Text style={{ color: C.faint, fontSize: 13 }}>{t("ui.select_item")}</Text>
            </View>
          </If>
        </View>
      </View>

      <View style={{ height: 24, flexDirection: "row", alignItems: "center", gap: 14, paddingHorizontal: 10, backgroundColor: C.panel, borderTopWidth: 1, borderTopColor: C.line }}>
        <Text style={{ color: C.muted, fontSize: 11 }}>
          {tNode(OPT.tree.find((x) => x.id === node()) ?? OPT.tree[0])}
        </Text>
        <Text style={{ color: C.muted, fontSize: 11 }}>{total()} / {OPT.counts.items} {t("ui.items")}</Text>
        <Text style={{ color: C.faint, fontSize: 11 }}>{rows().length} {t("ui.shown")}</Text>
        <Text style={{ color: C.muted, fontSize: 11 }}>{filters().length + raritySel().length} {t("ui.filters")}</Text>
        <View style={{ flex: 1 }} />
        <Text style={{ color: C.gold, fontSize: 11 }}>{toast()}</Text>
      </View>

      <If when={about()}>
        <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: "#000000cc", alignItems: "center", justifyContent: "center" }}>
          <View style={{ width: 420, padding: 22, borderRadius: 10, backgroundColor: C.panel, borderWidth: 1, borderColor: C.line, gap: 8 }}>
            <Text style={{ color: C.gold, fontSize: 20, fontWeight: "700" }}>Torchlight II Item Database</Text>
            <Text style={{ color: C.text, fontSize: 13 }}>v1.05 (eng) · Rust + GPUI + TSX reimplementation</Text>
            <Text style={{ color: C.muted, fontSize: 12 }}>Original: MyTorchlight.ru / Abramoff, 2013–2014 (Delphi 7 + ADO/Jet)</Text>
            <Text style={{ color: C.muted, fontSize: 12 }}>Data: base.mdb exported with mdbtools; icons from ./icons</Text>
            <Link href={GITHUB_URL} accessibilityLabel="GitHub">
              <Text style={{ color: C.rare, fontSize: 12 }}>{GITHUB_URL}</Text>
            </Link>
            <Text style={{ color: C.muted, fontSize: 12 }}>Right panel: Lock freezes the card for comparison. Favorites persist via NSH Storage.</Text>
            <View style={{ height: 8 }} />
            <Btn label={t("ui.ok")} onPress={() => about.set(false)} />
          </View>
        </View>
      </If>
    </View>
  );
}

mount(App);
