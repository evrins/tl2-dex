# TIDBI — Torchlight II Item Database

A native reimplementation of the 2014 `TIDBI.exe` (Delphi 7 + ADO/Jet) item
browser, built with **Rust + GPUI + TSX** through
[Native Shell](https://nsh.dev) 0.3:

- **Rust** (`src/lib.rs`) owns the data: it embeds the exported `base.mdb`,
  reimplements the original SQL filters (tree categories, rarity, stat ranges,
  requirements, `texteffect LIKE` effect filters), computes DPS, serves icons as
  `data:` URIs and persists favorites.
- **TSX** (`App.tsx`) owns the UI: tree, filter builder, virtualized result
  list, item card, search, favorites, about box.
- **GPUI** is the native renderer: `nsh run App.tsx --target gpui` opens the
  app in a GPUI window (macOS/Windows/Linux). The same entry also runs on the
  native desktop backends (`nsh run`), iOS, Android and the web.

## Layout

| Path | What |
|---|---|
| `nsh.json`, `tsconfig.json`, `Cargo.toml` | NSH app / TS / Rust crate |
| `App.tsx` | TSX UI, imports `Db` from `tidbi/native` |
| `src/lib.rs` | Rust native module `Db` + data/query engine + unit tests |
| `scripts/export_mdb.py` | `base.mdb` → `data/*.json` (uses `mdb-export`) |
| `scripts/export_translations.py` | game-exported multilingual names → `data/names.json` |
| `scripts/build_i18n.py` | category / rarity / stat labels → `data/i18n.json` |
| `scripts/build_affix_i18n.py` | game translation tables → localized affixes and descriptions |
| `scripts/build_set_names.py` | game translation tables → localized set names |
| `data/*.json`, `data/names.json`, `data/i18n.json`, `data/affix_i18n.json`, `data/descriptions.json`, `data/set_names.json` | generated, embedded with `include_str!` |
| `icons/`, `pic/`, `base.mdb`, `TIDBI.exe` | original tool assets (icons are read at runtime) |
| `App.test.tsx` | headless UI tests |

## Data pipeline

The original app needs 32-bit Windows + `Microsoft.Jet.OLEDB.4.0`. Here the
Access file is converted once so the app has no runtime database dependency:

```bash
brew install mdbtools          # or any provider of `mdb-export`
python3 scripts/export_mdb.py  # rewrites data/*.json
```

`scripts/export_mdb.py` also lifts the ~100 original `texteffect like '…'`
filter patterns straight out of `TIDBI.exe`, so the effect filter has the same
options as the 2014 tool.

### Multilingual names

The save editor's game export (`/Users/evrins/workspace/rust/tl2-save-editor/
data/items.json`, built from `MEDIA/UNITS/ITEMS/**/*.DAT` +
`MEDIA/TRANSLATIONS/<LANG>/TRANSLATION.DAT`) carries seven names per item. It is
keyed by the same console name as `items.ConsolNAME`:

```bash
python3 scripts/export_translations.py   # rewrites data/names.json
# or: TL2_ITEMS_JSON=/path/to/items.json python3 scripts/export_translations.py
```

Languages: `en`, `ru`, `zh-Hans` (MANDARIN), `zh-Hant` (TAIWANESE), `de`, `ja`,
`pl`. 6185 console names match (6037 of the 6050 items in `base.mdb`); missing
names fall back to English and then to the original database columns.

Category, rarity, stat, requirement and element labels are maintained in
`scripts/build_i18n.py` (117 keys, same seven languages) and written to
`data/i18n.json`:

```bash
python3 scripts/build_i18n.py   # rewrites data/i18n.json
```

`UNITTYPE` values such as `Rare Crossbows` are composed at render time from the
localized rarity and category (e.g. `稀有 · 弩`); tree nodes, pickers, table
headers and the item card all read the same table.

### Descriptions and affixes

Affix lines (`effects.texteffect`, `sets.texteffect`) and item descriptions
(`items.DESCRIPTION`) are English in `base.mdb`. The game's own translations are
in `MEDIA/TRANSLATIONS/<LANG>/TRANSLATION.DAT` inside `DATA.PAK`; extract them
with the save editor, then build the two tables:

```bash
# from /Users/evrins/workspace/rust/tl2-save-editor
./target/debug/tl2-save-editor unpack \
  "$HOME/Library/Application Support/Steam/steamapps/common/Torchlight II/Torchlight2.app/Contents/Resources/PAKS/DATA.PAK" \
  -o /tmp/tl2-trans --prefix MEDIA/TRANSLATIONS/

# in this project
python3 scripts/build_affix_i18n.py --translations /tmp/tl2-trans/TRANSLATIONS
```

`data/affix_i18n.json` covers all 2062 distinct affix/set lines in all six
non-English languages: each English line is matched against the game's
`[VALUE]` / `[DURATION]` / `[DMGTYPE]` / `[NAME]` templates, captures are
substituted into the localized template, `[DMGTYPE]` uses the localized element
name, and `Weapon:` / `Armor/Trinket:` prefixes are localized too.
`data/descriptions.json` covers 1785 of the 1894 distinct descriptions (the
rest fall back to English). Both are read by `Db.detail`, so the card's
Description, Random enchantments and Set bonuses follow the language bar.

Set names are generated separately, keyed by the raw `SetsSpisok.DISPLAYNAME`
and `items.SETS` strings (all 81 sets have a translation in every language):

```bash
python3 scripts/build_set_names.py --translations /tmp/tl2-trans/TRANSLATIONS
```

`data/set_names.json` is returned by `Db.options` as `setNames`; the tree's set
nodes, the card's Set field and the text card all resolve through it.

## Run

```bash
/Users/evrins/.nsh/bin/nsh run App.tsx --target gpui   # GPUI backend
/Users/evrins/.nsh/bin/nsh run                         # native desktop backend
/Users/evrins/.nsh/bin/nsh check                       # Rust + TS type check
/Users/evrins/.nsh/bin/nsh test                        # cargo test + headless UI tests
cargo test                                             # data/query unit tests
```

Use the 0.3 CLI explicitly if an older `nsh` (0.2) is earlier on `PATH`:
`~/.nsh/bin/nsh --version`. NSH 0.2 rejects the generated `nsh-*` `^0.3.0`
dependencies.

## Features

- Tree: Armor / Weapons (one- and two-handed) / Accessories / For Pets /
  Consumables / Classes / Quest Items / 81 sets / Favorites; every category
  folds and unfolds from its arrow without changing the selected node.
- Language bar: English / 简体中文 / 繁體中文 / Русский / Deutsch / 日本語 /
  Polski. Names, tree categories, rarity, stats, requirements, unit types,
  descriptions, random enchantments, set bonuses, set names, search and the card follow it
  (search covers every language at once); the card lists all seven exported
  names.
- Search over every exported language plus `DISPLAYNAME` / `iTRANSLATION`;
  optional "in selected node" restriction.
- Filter builder: rarity, stat ranges (Level/DPS/damage/armor/block),
  requirements (level/STR/DEX/Focus/Vitality/class), ~100 effect patterns with
  numeric ranges, "Only Set Items", AND/OR, live search, sort by type/level/DPS.
- Virtualized result grid with icons, rarity colors and favorite stars.
- Item card: localized name (plus English), type, level, DPS, damage/armor per
  element, requirements, sockets, random enchantments, set bonuses, all language
  names, console name, model path; picture/text toggle.
- Favorites persist to `~/Library/Application Support/com.mytorchlight.tidbi/favorites.json`
  (Windows: `%APPDATA%`); copy the console name from its field or the
  toolbar button; lock the card for comparison; about box.
- 66 icon names in the original data have no file in `icons/`; they fall back
  to `IG_skill_empty_result.png`, the same placeholder the original used.

## Differences from the original

- Data is a build-time export, not a writable Jet database. Favorites live in
  a JSON file rather than `items.favorite`.
- DPS sorting is descending (the original's `order by DPS_All` was ascending).
- The "3D Model" button is deliberately absent: the original shells out to an
  unbundled `TLMeshViewer\TLMeshViewer.exe`; the model path is shown in the
  card instead.
- The card is drawn with NSH elements, not composited from `pic/*.png` layers.
