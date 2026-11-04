#!/usr/bin/env python3
"""Export base.mdb (Jet 4) from the original TIDBI tool into data/*.json.

The Rust data layer embeds these files with `include_str!`, so the NSH app has no
runtime dependency on mdbtools / Jet / the Windows-only OLEDB provider.
Re-run after editing base.mdb:  python3 scripts/export_mdb.py
"""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MDB = ROOT / "base.mdb"
EXE = ROOT / "TIDBI.exe"
DATA = ROOT / "data"

INT_COLS = {
    "items": {
        "id", "iLEVEL", "MIN_DMG_PHYSICAL", "MAX_DMG_PHYSICAL",
        "MIN_DMG_ICE", "MAX_DMG_ICE", "MIN_DMG_FIRE", "MAX_DMG_FIRE",
        "MIN_DMG_ELECTRIC", "MAX_DMG_ELECTRIC", "MIN_DMG_POISON", "MAX_DMG_POISON",
        "MINLEVEL", "RARITY", "LEVEL_REQUIRED", "STRENGTH_REQUIRED",
        "DEXTERITY_REQUIRED", "MAGIC_REQUIRED", "DEFENSE_REQUIRED", "SOCKETS",
        "MAX_SOCKETS", "BLOCK_CHANCE", "MIN_ARM_PHYSICAL", "MAX_ARM_PHYSICAL",
        "MIN_ARM_ICE", "MAX_ARM_ICE", "MIN_ARM_FIRE", "MAX_ARM_FIRE",
        "MIN_ARM_ELECTRIC", "MAX_ARM_ELECTRIC", "MIN_ARM_POISON", "MAX_ARM_POISON",
        "MAXLEVEL",
    },
    "effects": {"id", "chislo"},
    "sets": {"id", "countset", "chislo"},
    "SetsSpisok": {
        "id", "iLEVEL", "MIN_DMG_PHYSICAL", "MAX_DMG_PHYSICAL", "MIN_DMG_ICE",
        "MAX_DMG_ICE", "MIN_DMG_FIRE", "MAX_DMG_FIRE", "MIN_DMG_ELECTRIC",
        "MAX_DMG_ELECTRIC", "MIN_DMG_POISON", "MAX_DMG_POISON", "MINLEVEL",
        "RARITY", "LEVEL_REQUIRED", "STRENGTH_REQUIRED", "DEXTERITY_REQUIRED",
        "MAGIC_REQUIRED", "DEFENSE_REQUIRED", "SOCKETS", "MAX_SOCKETS",
        "BLOCK_CHANCE", "MIN_ARM_PHYSICAL", "MAX_ARM_PHYSICAL", "MIN_ARM_ICE",
        "MAX_ARM_ICE", "MIN_ARM_FIRE", "MAX_ARM_FIRE", "MIN_ARM_ELECTRIC",
        "MAX_ARM_ELECTRIC", "MIN_ARM_POISON", "MAX_ARM_POISON", "MAXLEVEL",
        "DPS_ALL",
    },
}
FLOAT_COLS = {
    "items": {"SPEED"},
    "SetsSpisok": {"SPEED"},
}


def read_table(name: str) -> list[dict]:
    out = subprocess.check_output(
        ["mdb-export", str(MDB), name], text=True, encoding="utf-8"
    )
    reader = csv.DictReader(io.StringIO(out))
    ints = INT_COLS.get(name, set())
    floats = FLOAT_COLS.get(name, set())
    rows = []
    for raw in reader:
        row = {}
        for key, value in raw.items():
            # Missing values take the accessor's default (0 / ""), so the
            # JSON stays small: ~6 MB -> ~1.5 MB for 6050 items.
            if value is None or value == "":
                continue
            if key in ints:
                row[key] = int(float(value))
            elif key in floats:
                row[key] = float(value)
            else:
                row[key] = value
        rows.append(row)
    return rows


def write_json(name: str, value) -> None:
    path = DATA / name
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"  {name:26} {path.stat().st_size / 1024:8.1f} KiB")


def effect_patterns() -> list[dict]:
    """Reuse the original ComboBox4 filters by lifting their LIKE patterns
    out of TIDBI.exe's CODE section."""
    blob = EXE.read_bytes()
    found = []
    for match in re.finditer(rb"texteffect like '([^']{2,})'", blob):
        pattern = match.group(1).decode("latin1")
        if pattern in ("%",):
            continue
        label = pattern.replace("%", " ").strip()
        if label.startswith("+"):
            label = label[1:].lstrip()
        found.append({"label": label or "Any effect", "pattern": pattern})
    # "+% Physical Damage" is stored without wildcards in the exe.
    found.append({"label": "Physical Damage", "pattern": "+% Physical Damage"})
    # stable, deduplicated
    seen, result = set(), []
    for entry in found:
        if entry["pattern"] not in seen:
            seen.add(entry["pattern"])
            result.append(entry)
    return result


def main() -> None:
    DATA.mkdir(exist_ok=True)
    print("exporting", MDB)
    for table in ("items", "effects", "sets", "SetsSpisok"):
        write_json(table.lower() + ".json", read_table(table))
    write_json("effect_patterns.json", effect_patterns())


if __name__ == "__main__":
    main()
