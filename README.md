# tl2-dex — Torchlight II Item Database

A native reimplementation of the 2014 `TIDBI.exe` (Delphi 7 + ADO/Jet) item
browser, built with **Rust + GPUI + TSX** through
[Native Shell](https://nsh.dev) 0.4:

- **Rust** (`src/lib.rs`) owns the data: it embeds the exported `base.mdb`,
  reimplements the original SQL filters (tree categories, rarity, stat ranges,
  requirements, `texteffect LIKE` effect filters), computes DPS, serves icons
  through NSH asset URLs and persists favorites.
- **TSX** (`App.tsx`) owns the UI: tree, filter builder, virtualized result
  list, item card, search, favorites, about box.
- **GPUI** is the native renderer: `nsh run App.tsx --target gpui` opens the
  app in a GPUI window (macOS/Windows/Linux). The same entry also runs on the
  native desktop backends (`nsh run`), iOS, Android and the web.

## Layout

| Path | What |
|---|---|
| `nsh.json`, `tsconfig.json`, `Cargo.toml` | NSH app / TS / Rust crate |
| `icon.png` | app icon (`nsh.json` `"icon"`): the 2014 tool's 256 px emblem on the app's `#12141a`, 1024 px; `nsh package` derives the favicon (32), `apple-touch-icon` (180) and manifest icons (192, 512) from it |
| `App.tsx` | TSX UI, imports `Db` from `tidbi/native` |
| `src/lib.rs` | Rust native module `Db` + data/query engine + unit tests |
| `scripts/export_mdb.py` | `base.mdb` → `data/*.json` (uses `mdb-export`) |
| `scripts/export_translations.py` | game-exported multilingual names → `data/names.json` |
| `scripts/build_i18n.py` | category / rarity / stat labels → `data/i18n.json` |
| `scripts/build_affix_i18n.py` | game translation tables → localized affixes and descriptions |
| `scripts/build_set_names.py` | game translation tables → localized set names |
| `data/*.json`, `data/names.json`, `data/i18n.json`, `data/affix_i18n.json`, `data/descriptions.json`, `data/set_names.json` | generated, embedded with `include_str!` |
| `assets/icons/`, `pic/`, `base.mdb`, `TIDBI.exe` | original tool assets; the icons are the crate's NSH assets (`assets!()`), served at `asset:/@nsh-app-tl2-dex/icons/…` on every target |
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

Category, rarity, stat, requirement, element, affix-chip and interface-control
labels are maintained in `scripts/build_i18n.py` (248 keys, same seven
languages) and written to `data/i18n.json`:

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
nsh run App.tsx --target gpui   # GPUI backend
nsh run                         # native desktop backend
nsh check                       # Rust + TS type check
nsh test                        # cargo test + headless UI tests
cargo test                      # data/query unit tests
```

Needs the 0.4 CLI (`nsh --version`); `cargo test` alone needs no `nsh`.

### Web target

`nsh run --target web` also cross-compiles the Rust crate to
`wasm32-unknown-unknown`, and `zstd-sys` (through `nsh-base`) compiles C for it.
Apple's clang has no WebAssembly backend, so install Homebrew LLVM and point
cc-rs at it for that target only — in `~/.cargo/config.toml`, since a machine
path does not belong in this repository:

```toml
[env]
CC_wasm32_unknown_unknown = { value = "/opt/homebrew/opt/llvm/bin/clang", force = true }
AR_wasm32_unknown_unknown = { value = "/opt/homebrew/opt/llvm/bin/llvm-ar", force = true }
```

`force = true` is needed: the build otherwise keeps its own `llvm-ar` and
fails with `failed to find tool "llvm-ar"`. Without the LLVM clang the build
stops at `unable to create target: 'No available targets are compatible with
triple "wasm32-unknown-unknown"'`.

Icons are compiled in as assets rather than read from disk at run time, so the
web build shows them too: `nsh run` serves `asset:/@nsh-app-tl2-dex/icons/…` as
`/assets/@nsh-app-tl2-dex/icons/…`, and `nsh package` copies the same files into
the app's `nsh/assets/…`.

### Deploy (Cloudflare Workers)

`nsh package --target web` writes a static site — `index.html`,
`nsh.<digest>.wasm` (13.6 MB), `app.<digest>.js`, `assets/…` — into
`.nsh/out/tl2-dex`, 1144 files. `wrangler.jsonc` uploads that directory as a
static-only Worker: it declares no `main`, so every request is an asset and
none is billed as a Worker invocation.

```bash
npx wrangler login          # once
scripts/deploy_web.sh       # nsh package --target web + headers + deploy
```

That is `nsh package --target web`, `cp deploy/_headers .nsh/out/tl2-dex/`, and
`npx wrangler deploy`. The site fits Workers Free (20,000 files, 25 MiB per
file); the default domain is `tl2-dex.<account>.workers.dev`, and a custom domain
is added in the dashboard (Workers → the Worker → Settings → Domains).

`deploy/_headers` exists because Workers serves a static file with
`Cache-Control: public, max-age=0, must-revalidate` by default: the files whose
names carry a content digest (`nsh.<digest>.wasm`, `app.<digest>.js`,
`assets/…/<name>.<digest>.png`) are marked `immutable` for a year instead, while
`index.html` keeps the revalidating default. Checked with `wrangler dev`:
`nsh.<digest>.wasm` is served as `application/wasm` (what
`WebAssembly.compileStreaming` needs), the icons and the wasm as `immutable`,
`index.html` as `must-revalidate`.

Workers answers `/assets/@nsh-app-tl2-dex/…` with a 307 to the percent-encoded
`/assets/%40nsh-app-tl2-dex/…`; the redirect also carries the `immutable` header
and is cached, so it costs one extra request per icon on the first visit only.

Pages instead of Workers: `npx wrangler pages deploy .nsh/out/tl2-dex`.

## Features

- Tree: Armor / Weapons (one- and two-handed) / Accessories / For Pets /
  Consumables / Classes / Quest Items / 81 sets / Favorites; every category
  folds and unfolds from its arrow without changing the selected node.
- Language bar: English / 简体中文 / 繁體中文 / Русский / Deutsch / 日本語 /
  Polski. Names, tree categories, rarity, stats, requirements, unit types,
  descriptions, random enchantments, set bonuses, set names, search and the card follow it
  (search covers every language at once); the card lists all seven exported
  names.
- Search over every exported language, the item's internal id (`ConsolNAME`,
  the console name) and `DISPLAYNAME` / `iTRANSLATION`; optional "in selected
  node" restriction.
- Filter builder: rarity chips that apply on click (multiple rarities are
  OR-ed), stat ranges (Level/DPS/damage/armor/block),
  requirements (level/STR/DEX/Focus/Vitality/class), ~100 affix chips (localized
  names) with numeric ranges, "Only Set Items", AND/OR, live search, sort by
  type/level/DPS.
- Virtualized result grid with icons, rarity colors and favorite stars.
- Item card: localized name (plus English), type, level, DPS, damage/armor per
  element, requirements, sockets, random enchantments, set bonuses, all language
  names, console name, model path; picture/text toggle.
- Favorites persist to `~/Library/Application Support/com.mytorchlight.tidbi/favorites.json`
  (Windows: `%APPDATA%`); copy the console name from its field or the
  toolbar button; lock the card for comparison; about box.
- Icon names are matched case-insensitively: the database stores lowercase
  names (`icons_gem_06b`) while the 2014 asset files are mixed case
  (`icons_gem_06B.png`), which Windows resolved for the original tool.
- 18 icon names (20 items) have no file in `assets/icons/` at all; they fall
  back to `IG_skill_empty_result.png`, the same placeholder the original used.

## Differences from the original

- Data is a build-time export, not a writable Jet database. Favorites live in
  a JSON file rather than `items.favorite`.
- DPS sorting is descending (the original's `order by DPS_All` was ascending).
- The "3D Model" button is deliberately absent: the original shells out to an
  unbundled `TLMeshViewer\TLMeshViewer.exe`; the model path is shown in the
  card instead.
- The card is drawn with NSH elements, not composited from `pic/*.png` layers.
