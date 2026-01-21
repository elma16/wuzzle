import argparse
import csv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_LICHESS_DB = ROOT_DIR / "data/0positions/csv-fen/lichess_db_puzzle.csv"
DEFAULT_OUT = ROOT_DIR / "data/themes-unique.txt"


def iter_themes(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                continue
            if row[0] == "PuzzleId":
                continue
            if len(row) <= 7:
                continue
            themes_field = row[7].strip()
            if not themes_field:
                continue
            for theme in themes_field.split():
                yield theme


def extract_unique_themes(csv_path):
    return sorted(set(iter_themes(csv_path)))


def main():
    parser = argparse.ArgumentParser(
        description="Extract unique themes from the Lichess puzzle database."
    )
    parser.add_argument(
        "--lichess-db",
        type=str,
        default=str(DEFAULT_LICHESS_DB),
        help="Path to lichess_db_puzzle.csv.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(DEFAULT_OUT),
        help="Output path for themes-unique.txt.",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print themes to stdout in addition to writing the file.",
    )
    args = parser.parse_args()

    csv_path = Path(args.lichess_db)
    if not csv_path.exists():
        raise SystemExit(f"Lichess DB not found at {csv_path}")

    themes = extract_unique_themes(csv_path)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(themes) + "\n")

    if args.print:
        for theme in themes:
            print(theme)

    print(f"Wrote {len(themes)} themes to {out_path}")


if __name__ == "__main__":
    main()
