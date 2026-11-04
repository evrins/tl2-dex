#!/usr/bin/env python3
"""Localize Torchlight II set names.

`SetsSpisok.DISPLAYNAME` and `items.SETS` store English set names; the game's
translation tables carry the official localized names. The output is keyed by
the raw database strings (including the `Mondon\\x19 s Vestment` variant), so
the Rust tree and card can look up a name exactly.

```bash
python3 scripts/build_set_names.py --translations /tmp/tl2-trans/TRANSLATIONS
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


def normalize(text: str) -> str:
    text = text.replace("`", "'").replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\x19", "'")
    text = re.sub(r"'\s+", "'", text)
    return re.sub(r"\s+", " ", text).strip().lower()


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--translations",
        type=Path,
        default=Path("/tmp/tl2-trans/TRANSLATIONS"),
    )
    args = parser.parse_args()

    tables: dict[str, dict[str, str]] = {}
    for folder, lang in LANGS.items():
        pairs = parse_table(args.translations / folder / "TRANSLATION.DAT")
        tables[lang] = {normalize(original): translated for original, translated in pairs.items()}

    sets = json.loads((DATA / "setsspisok.json").read_text(encoding="utf-8"))
    items = json.loads((DATA / "items.json").read_text(encoding="utf-8"))

    raw_names: set[str] = {
        row["DISPLAYNAME"] for row in sets if row.get("DISPLAYNAME")
    }
    raw_names.update(row["SETS"] for row in items if row.get("SETS"))

    out: dict[str, dict[str, str]] = {}
    missing: list[str] = []
    for raw in sorted(raw_names):
        key = normalize(raw)
        entry: dict[str, str] = {}
        for lang, table in tables.items():
            translated = table.get(key)
            if translated:
                entry[lang] = translated
        if entry:
            out[raw] = entry
        else:
            missing.append(raw)

    path = DATA / "set_names.json"
    path.write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"  set_names.json {path.stat().st_size / 1024:8.1f} KiB, {len(out)} names")
    print("  missing:", missing)


if __name__ == "__main__":
    main()
