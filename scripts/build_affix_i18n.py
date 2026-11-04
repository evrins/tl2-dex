#!/usr/bin/env python3
"""Import the game's translation tables into localized affix and description text.

The original TIDBI database stores English affix lines (`effects.texteffect`,
`sets.texteffect`) and item descriptions (`items.DESCRIPTION`). Torchlight II
ships the localized forms in `MEDIA/TRANSLATIONS/<LANG>/TRANSLATION.DAT` inside
`DATA.PAK`; `tl2-save-editor unpack --prefix MEDIA/TRANSLATIONS/` decompiles
them to UTF-16 `.DAT` text.

Affix lines are templates with placeholders (`+[VALUE]% [DMGTYPE] Damage`), so
each database line is matched against the English template, its captures are
substituted into the localized template, and `[DMGTYPE]` is rendered with the
localized element name.

```bash
# default source (adjust to your extraction):
python3 scripts/build_affix_i18n.py --translations /tmp/tl2-trans/TRANSLATIONS
```
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

LANGS = {
    "MANDARIN": "zh-Hans",
    "TAIWANESE": "zh-Hant",
    "RUSSIAN": "ru",
    "GERMAN": "de",
    "JAPANESE": "ja",
    "POLISH": "pl",
}
DURATION = {
    "en": " sec.",
    "zh-Hans": "秒",
    "zh-Hant": "秒",
    "ru": " сек.",
    "de": " Sek.",
    "ja": "秒",
    "pl": " sek.",
}
PREFIXES = {
    "Weapon: ": "affix.weapon",
    "Armor/Trinket: ": "affix.armor_trinket",
    "Armor/Trinkets: ": "affix.armor_trinket",
    "Armor: ": "affix.armor",
    "Trinket: ": "affix.trinket",
}
NUMERIC = {
    "VALUE", "VALUE1", "VALUE2", "VALUE3", "VALUE4", "VALUE5", "VALUE_OT",
    "VALUE3AND4", "VALUE1ASDURATION", "GOLD", "XP", "FAME", "RAND_INT_0_100",
    "DEFEATCOUNT", "ACQUIRE1", "ACQUIRE2", "ACQUIRECOUNT", "DEFEAT1",
    "DEFEAT1COUNT", "DEFEATCOMPLETECOUNT", "ACQUIRECOMPLETECOUNT",
    "ACQUIRE1DEPTH",
}
PLACEHOLDER = re.compile(r"\[([A-Z0-9_]+)\]")

_PAIRS: tuple[re.Pattern[str], list[tuple[str, int]], str] | None = None


def clean(text: str) -> str:
    text = re.sub(r"\|c[0-9A-Fa-f]{8}", "", text)
    text = text.replace("|u", "")
    return re.sub(r"\s+", " ", text).strip()


def normalize(text: str) -> str:
    return clean(text).replace("`", "'").replace("\u2019", "'").replace("\u2018", "'")


def parse_table(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-16")
    pairs: dict[str, str] = {}
    for match in re.finditer(
        r"<STRING>ORIGINAL:(.*?)\r?\n\s*<STRING>TRANSLATION:(.*?)\r?\n", text, re.S
    ):
        original = match.group(1).strip("\r\n")
        translated = match.group(2).strip("\r\n")
        if original and translated:
            pairs[original] = translated
    return pairs


def compile_template(template: str):
    parts: list[str] = []
    groups: list[tuple[str, int]] = []
    pos = 0
    index = 0
    for match in PLACEHOLDER.finditer(template):
        parts.append(re.escape(template[pos : match.start()]))
        name = match.group(1)
        index += 1
        if name == "DMGTYPE":
            parts.append("(Physical|Ice|Fire|Electric|Poison)")
        elif name == "DURATION":
            parts.append(r"(\d+(?:[.,]\d+)?)\s*(?:sec\.?|seconds?|minutes?|min\.?)?")
        elif name in NUMERIC:
            parts.append(r"([-+]?\d+(?:[.,]\d+)?)")
        else:
            parts.append("(.+?)")
        groups.append((name, index))
        pos = match.end()
    parts.append(re.escape(template[pos:]))
    literal = len(PLACEHOLDER.sub("", template))
    return literal, re.compile("^" + "".join(parts) + "$"), groups


def templates(pairs: dict[str, str]):
    compiled = []
    for original in pairs:
        if "[" not in original:
            continue
        literal, pattern, groups = compile_template(normalize(original))
        compiled.append((-literal, pattern, groups, original))
    compiled.sort(key=lambda item: item[0])
    return [(pattern, groups, original) for _, pattern, groups, original in compiled]


def resolve(text: str, exact: dict[str, str], tmpls):
    normalized = normalize(text)
    prefix = ""
    for candidate, key in PREFIXES.items():
        if normalized.startswith(candidate):
            prefix = key
            normalized = normalized[len(candidate) :]
            break
    if normalized in exact:
        return prefix, exact[normalized], []
    for pattern, groups, original in tmpls:
        match = pattern.match(normalized)
        if match:
            return prefix, original, [(name, match.group(index)) for name, index in groups]
    return prefix, None, []


def render(template: str, captures: list[tuple[str, str]], lang: str, table: dict[str, str]) -> str:
    values = dict(captures)
    out: list[str] = []
    pos = 0
    for match in PLACEHOLDER.finditer(template):
        out.append(template[pos : match.start()])
        name = match.group(1)
        value = values.get(name, match.group(0))
        if name == "DMGTYPE":
            elements = ELEMENTS.get(lang, {})
            out.append(elements.get(value, value))
        elif name == "DURATION":
            out.append(value + DURATION.get(lang, ""))
        elif name in ("NAME", "ITEM", "CLASS"):
            out.append(table.get(normalize(value), value))
        else:
            out.append(value)
        pos = match.end()
    out.append(template[pos:])
    return "".join(out)


def translate(text: str, tables: dict[str, dict[str, str]], tmpls, ui: dict) -> dict[str, str]:
    prefix, template, captures = resolve(text, tables["EXACT"], tmpls)
    if template is None:
        return {}
    result = {}
    for lang, table in tables.items():
        if lang == "EXACT":
            continue
        localized = table.get(normalize(template))
        if not localized:
            continue
        rendered = clean(render(localized, captures, lang, table))
        if prefix:
            rendered = f"{ui[f'{prefix}'].get(lang, '')}: {rendered}"
        result[lang] = rendered
    return result


ELEMENTS: dict[str, dict[str, str]] = {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--translations",
        type=Path,
        default=Path("/tmp/tl2-trans/TRANSLATIONS"),
    )
    args = parser.parse_args()

    tables: dict[str, dict[str, str]] = {"EXACT": {}}
    for folder, lang in LANGS.items():
        path = args.translations / folder / "TRANSLATION.DAT"
        pairs = parse_table(path)
        normalized_pairs = {normalize(original): translated for original, translated in pairs.items()}
        tables[lang] = normalized_pairs
        for original, translated in normalized_pairs.items():
            tables["EXACT"].setdefault(original, translated)

    ui = json.loads((DATA / "i18n.json").read_text(encoding="utf-8"))
    for key, values in ui.items():
        if key.startswith("element."):
            element = key.split(".", 1)[1]
            for lang, label in values.items():
                ELEMENTS.setdefault(lang, {})[element] = label

    tmpls = templates(tables["zh-Hans"])

    effects = json.loads((DATA / "effects.json").read_text(encoding="utf-8"))
    sets = json.loads((DATA / "sets.json").read_text(encoding="utf-8"))
    items = json.loads((DATA / "items.json").read_text(encoding="utf-8"))

    affix_texts = {
        row["texteffect"]
        for row in effects
        if row.get("texteffect") and row["texteffect"] != "BLANK_NO_EFFECTS"
    }
    affix_texts.update(row["texteffect"] for row in sets if row.get("texteffect"))

    affix_out: dict[str, dict[str, str]] = {}
    for text in sorted(affix_texts):
        translated = translate(text, tables, tmpls, ui)
        if translated:
            affix_out[text] = translated

    desc_texts = {
        row["DESCRIPTION"]
        for row in items
        if row.get("DESCRIPTION") and row["DESCRIPTION"].strip()
    }
    desc_out: dict[str, dict[str, str]] = {}
    for text in sorted(desc_texts):
        normalized = normalize(text)
        if normalized in tables["EXACT"]:
            entry = {}
            for lang in LANGS.values():
                translated = tables[lang].get(normalize(text))
                if translated and (not entry.get(lang)):
                    entry[lang] = clean(translated)
            if entry:
                desc_out[text] = entry

    for name, value in (("affix_i18n.json", affix_out), ("descriptions.json", desc_out)):
        path = DATA / name
        path.write_text(
            json.dumps(value, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        print(f"  {name:22} {path.stat().st_size / 1024:8.1f} KiB, {len(value)} entries")

    coverage = {
        lang: sum(1 for v in affix_out.values() if lang in v) for lang in LANGS.values()
    }
    print("  affix coverage:", coverage)


if __name__ == "__main__":
    main()
