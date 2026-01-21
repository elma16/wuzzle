# Wuzzle CLI

Generate chess puzzle sheets from the Lichess puzzle database, CSVs, or text files.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For tests:

```bash
pip install -e ".[test]"
```

Optional country helpers:

```bash
pip install -e ".[country]"
```

## Data

The Lichess puzzle database and themes list are not included in this repo.

- Default Lichess DB path: `data/0positions/csv-fen/lichess_db_puzzle.csv`
- Default themes file: `data/themes-unique.txt`

Use `--data-dir`, `--lichess-db`, or `--themes-file` to point at your local copies.

## Lichess DB: Download + Themes

Wuzzle uses the Lichess puzzle database locally. It never downloads puzzles for you and it never uploads any data.
It reads the following columns from `lichess_db_puzzle.csv`:

- `Themes` to filter by theme name(s)
- `Moves` to apply the first move and set the puzzle position
- `FEN` to render the board image
- `GameUrl` to open the puzzle on Lichess for review

Download steps:

1. Visit the Lichess database page: `https://database.lichess.org/#puzzles`
2. Download the latest `lichess_db_puzzle.csv.zst`
3. Decompress it:

```bash
unzstd lichess_db_puzzle.csv.zst
```

4. Move it into place:

```bash
mkdir -p data/0positions/csv-fen
mv lichess_db_puzzle.csv data/0positions/csv-fen/lichess_db_puzzle.csv
```

5. Generate the theme list:

```bash
wuzzle-themes --lichess-db path/to/lichess_db_puzzle.csv --out data/themes-unique.txt
```

Make sure you comply with the Lichess database license (see the Lichess database page for details).

## Usage

```bash
python src/main.py lichess fork --n 10
python src/main.py csv _ --file data/u10-puzzle.csv --n 10
python src/main.py text _ --file puzzles.txt
```

Notes:
- The `theme` argument is required by the CLI but is only used for `lichess` mode.
- PDF export requires a LaTeX engine (e.g., `pdflatex` via TeX Live/MacTeX).
- By default, the CLI asks permission before opening browser tabs for puzzles.
- Use `--no-confirm-open` to skip the prompt and open tabs immediately.
- Use `--no-open` to prevent opening browser tabs or PDFs.
- Use `--no-pdf` to skip PDF generation.
- Use `--author` to set the PDF header author (defaults to the current year only).

After installing, you can also run:

```bash
wuzzle-cli lichess fork --n 10
```

## Tests

```bash
pytest
```

## Examples

Generate a puzzle sheet from Lichess by theme:

```bash
wuzzle-cli lichess fork --n 10
```

Generate a puzzle sheet from Lichess without opening tabs or PDFs:

```bash
wuzzle-cli lichess fork --n 10 --no-open --no-pdf
```

Generate from a custom CSV (requires a `fen` column; optional `white`, `black`, `event`, `year` or `date`):

```csv
game_index,fen,white,black,year,event
1,"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",Carlsen,Nepo,2021,World Championship
```

```bash
wuzzle-cli csv _ --file my_puzzles.csv --n 10
```

Generate from a text file with one FEN per line:

```bash
wuzzle-cli text _ --file puzzles.txt
```
