#!/usr/bin/env python3
"""Import the game-exported multilingual item names into data/names.json.

Source: `/Users/evrins/workspace/rust/tl2-save-editor/data/items.json`, which the
save editor exported from Torchlight II's `MEDIA/UNITS/ITEMS/**/*.DAT` plus its
`MEDIA/TRANSLATIONS/<LANG>/TRANSLATION.DAT` tables. Each item's `id` is the same
console name as `items.ConsolNAME` in the original TIDBI database.

Languages: English, Russian, Simplified Chinese (MANDARIN), Traditional Chinese
(TAIWANESE), German, Japanese, Polish.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    os.environ.get(
        "TL2_ITEMS_JSON",
        "/Users/evrins/workspace/rust/tl2-save-editor/data/items.json",
    )
)
OUT = ROOT / "data" / "names.json"

# Game table key -> BCP-47 style id used by the app.
LANGS = {
    "en": "en",
    "RUSSIAN": "ru",
    "MANDARIN": "zh-Hans",
    "TAIWANESE": "zh-Hant",
    "GERMAN": "de",
    "JAPANESE": "ja",
    "POLISH": "pl",
}


def main() -> None:
    items = json.loads(SOURCE.read_text(encoding="utf-8"))
    names: dict[str, dict[str, str]] = {}
    for item in items:
        consol = item.get("id")
        if not consol:
            continue
        raw = item.get("names") or {}
        entry: dict[str, str] = {}
        for game_key, lang in LANGS.items():
            value = raw.get(game_key)
            if isinstance(value, str) and value:
                entry[lang] = value
        # 52 items have no `names.en`: fall back to the English display name.
        english = item.get("display_name") or item.get("n")
        if english and "en" not in entry:
            entry["en"] = english
        if not entry:
            continue
        # Duplicate console names (two junk rows) merge; keep the fullest entry.
        merged = names.setdefault(consol, {})
        for lang, value in entry.items():
            merged.setdefault(lang, value)

    OUT.write_text(
        json.dumps(names, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    counts = {lang: sum(1 for v in names.values() if lang in v) for lang in LANGS.values()}
    print(f"  names.json {OUT.stat().st_size / 1024:8.1f} KiB, {len(names)} items")
    for lang, n in counts.items():
        print(f"    {lang:9} {n}")


if __name__ == "__main__":
    main()
