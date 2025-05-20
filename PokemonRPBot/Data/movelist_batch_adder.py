#!/usr/bin/env python3
"""
insert_moves_minimal.py
Add a predefined list of moves to a predefined category
in every Pokémon JSON file inside a predefined folder.

    python insert_moves_minimal.py          # do it
    python insert_moves_minimal.py --dry-run   # preview, touch nothing
"""

import argparse, json, sys
from pathlib import Path

# ──────── 🔧  CHANGE THESE THREE CONSTANTS ────────
TARGET_FOLDER   = Path("./movelists")            # folder with your *.json files
TARGET_CATEGORY = "tm"                           # bucket to receive the moves
TARGET_MOVES = [
    "Agility",
    "Amnesia",
    "Attract",
    "Confide",
    "Curse",
    "Double Team",
    "Endure",
    "Facade",
    "Frustration",
    "Headbutt",
    "Helping Hand",
    "Hidden Power",
    "Iron Defense",
    "Metronome",
    "Nasty Plot",
    "Protect",
    "Rest",
    "Return",
    "Round",
    "Secret Power",
    "Sleep Talk",
    "Snore",
    "Splash",
    "Substitute",
    "Swords Dance",
    "Take Down",
    "Tera Blast",
]
# ─────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=f"Add {TARGET_MOVES} to '{TARGET_CATEGORY}' "
                    f"in every JSON file in {TARGET_FOLDER}"
    )
    p.add_argument("--dry-run", action="store_true",
                   help="show what would change but don't modify files")
    return p.parse_args()


def insert_moves(obj: dict) -> bool:
    """Return True if we actually added something."""
    bucket = obj.setdefault("moves", {}).setdefault(TARGET_CATEGORY, [])
    changed = False
    for mv in TARGET_MOVES:
        if mv not in bucket:
            bucket.append(mv)
            changed = True
    return changed


def main() -> None:
    args = parse_args()

    if not TARGET_MOVES:
        print("TARGET_MOVES is empty – nothing to do.", file=sys.stderr)
        sys.exit(1)

    if not TARGET_FOLDER.is_dir():
        print(f"{TARGET_FOLDER} is not a directory.", file=sys.stderr)
        sys.exit(1)

    files = list(TARGET_FOLDER.glob("*.json"))
    if not files:
        print(f"No JSON files found in {TARGET_FOLDER}.", file=sys.stderr)
        sys.exit(1)

    print(f"Adding {TARGET_MOVES} → '{TARGET_CATEGORY}' in {len(files)} file(s)…")

    for f in files:
        print(f"• {f.name}", end="")
        try:
            txt  = f.read_text(encoding="utf-8")
            data = json.loads(txt)
        except Exception as e:
            print(f"  ! read/parse error ({e}) – skipping")
            continue

        if insert_moves(data):
            if args.dry_run:
                print("  (would modify)")
            else:
                f.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n",
                             encoding="utf-8")
                print("  ✓ updated")
        else:
            print("  (no change)")

    print("Done.")


if __name__ == "__main__":
    main()
