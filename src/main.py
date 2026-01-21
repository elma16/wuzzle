import argparse
import os
from pathlib import Path
from functools import reduce
import webbrowser

import pandas as pd
import chess
import chess.pgn
import chess.engine

from fen2tex import fen2tex, fen2png

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = ROOT_DIR / "data"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "output"
DEFAULT_LICHESS_DB = DEFAULT_DATA_DIR / "lichess_db_puzzle.csv"
DEFAULT_THEMES_FILE = DEFAULT_DATA_DIR / "themes-unique.txt"
DEFAULT_STOCKFISH_PATH = os.environ.get("STOCKFISH_PATH")


def open_puzzle_url(url, open_in_browser=True):
    if open_in_browser:
        webbrowser.open_new_tab(url)
    else:
        print(f"URL: {url}")


def confirm_browser_open():
    choice = input("Open browser tabs for puzzles? [Y/n]: ").strip().lower()
    return choice in ("", "y", "yes")


def validate_choice():
    while True:
        choice = input("Enter 1 to select this puzzle, 0 to pick another one: ")
        if choice == "1" or choice == "0":
            return choice
        else:
            print("Invalid choice.")


def prompt_for_comment(puzzle_number):
    return input(f"Enter a comment for puzzle {puzzle_number}: ")


def _load_themes(themes_file):
    themes_file = Path(themes_file)
    if not themes_file.exists():
        return None
    themes = []
    with themes_file.open("r") as f:
        for line in f:
            themes.extend(line.strip().split())
    return themes


def is_valid_theme(theme, themes_file=DEFAULT_THEMES_FILE):
    """
    Check if the theme is valid.
    """
    if themes_file is None:
        return True
    themes = _load_themes(themes_file)
    if themes is None:
        return True
    return theme in themes


def print_valid_themes(themes_file=DEFAULT_THEMES_FILE):
    """
    Print all valid themes.
    """
    if themes_file is None:
        print("Themes file not set.")
        return
    themes = _load_themes(themes_file)
    if themes is None:
        print(f"Themes file not found at {themes_file}")
        return
    print(themes)


def get_puzzle_url(puzzle):
    puzzle_und = puzzle.replace(" ", "_")
    return "https://lichess.org/analysis/" + puzzle_und


def get_puzzles_from_lichess(
    theme,
    n=10,
    lichess_db_path=DEFAULT_LICHESS_DB,
    themes_file=DEFAULT_THEMES_FILE,
    open_in_browser=True,
):
    """
    Get n random puzzles with the given theme.
    """
    lichess_db_path = Path(lichess_db_path)
    if not lichess_db_path.exists():
        raise FileNotFoundError(f"Lichess DB not found at {lichess_db_path}")

    df = pd.read_csv(lichess_db_path, header=None)
    expected_columns = [
        "PuzzleId",
        "FEN",
        "Moves",
        "Rating",
        "RatingDeviation",
        "Popularity",
        "NbPlays",
        "Themes",
        "GameUrl",
        "OpeningTags",
    ]
    if df.shape[1] < len(expected_columns):
        raise ValueError("Lichess DB file has an unexpected number of columns.")

    df = df.iloc[:, : len(expected_columns)]
    if str(df.iloc[0, 0]) == "PuzzleId":
        df = df.iloc[1:]
    df.columns = expected_columns

    themes_list = [t.strip() for t in theme.split(",") if t.strip()]
    themes_file = Path(themes_file) if themes_file else None

    if themes_list:
        if themes_file and themes_file.exists():
            invalid = [t for t in themes_list if not is_valid_theme(t, themes_file)]
            if invalid:
                print("Invalid theme(s): " + ", ".join(invalid))
                print("Valid themes are:")
                print_valid_themes(themes_file)
                return [], []
        else:
            print(f"Warning: themes file not found at {themes_file}; skipping validation.")

        df = reduce(
            lambda left, right: left[left["Themes"].str.contains(right, na=False)],
            themes_list,
            df,
        )

    if df.empty:
        print("No puzzles found for the selected theme(s).")
        return [], []

    puzzles = []
    comments = []
    i = 0
    while len(puzzles) < n:
        row = df.sample(n=1).iloc[0]
        fen = row["FEN"]
        url = row["GameUrl"]
        moves = row["Moves"]
        print(f"Puzzle {i + 1}:")
        print(row["Themes"])
        open_puzzle_url(url, open_in_browser=open_in_browser)
        choice = validate_choice()
        if choice == "1":
            board = chess.Board(fen)
            first_move = chess.Move.from_uci(moves.split()[0])
            board.push(first_move)
            fen = board.fen()
            puzzles.append(fen)
            comment = prompt_for_comment(i + 1)
            comments.append(comment)
            i += 1
        else:
            print("Puzzle rejected.")
    return puzzles, comments


def _column_map(columns):
    return {str(col).strip().lower(): col for col in columns}


def _get_column(column_map, *names):
    for name in names:
        key = name.lower()
        if key in column_map:
            return column_map[key]
    return None


def _extract_year(value):
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    for sep in (".", "-", "/"):
        if sep in text:
            return text.split(sep)[0]
    return text


def _format_comment(white, black, event, year, comment):
    lines = []
    if white or black:
        lines.append(f"\\textbf{{{white} - {black}}}")
    line2 = " ".join([p for p in [event, year] if p]).strip()
    if line2:
        lines.append(line2)
    if comment:
        lines.append(comment)
    if not lines:
        return ""
    return r" \\ ".join(lines)


def get_puzzles_from_csv(filename, n=10, verbose=True, all_puzzles=False, open_in_browser=True):
    """
    Get puzzles from another csv
    """
    df = pd.read_csv(filename)
    column_map = _column_map(df.columns)

    fen_col = _get_column(column_map, "fen")
    if not fen_col:
        raise ValueError("CSV must include a FEN column.")

    white_col = _get_column(column_map, "white")
    black_col = _get_column(column_map, "black")
    event_col = _get_column(column_map, "event")
    year_col = _get_column(column_map, "year")
    date_col = _get_column(column_map, "date")

    puzzles = []
    comments = []
    i = 0

    total_puzzles = len(df) if all_puzzles else n

    for _, row in df.iterrows():
        if i >= total_puzzles:
            break
        fen = str(row[fen_col]).strip()
        if not fen:
            continue
        url = get_puzzle_url(fen)
        print(f"Puzzle {i + 1}:")
        open_puzzle_url(url, open_in_browser=open_in_browser)
        choice = validate_choice()
        if choice == "1":
            puzzles.append(fen)
            white = str(row[white_col]).strip() if white_col else ""
            black = str(row[black_col]).strip() if black_col else ""
            event = str(row[event_col]).strip() if event_col else ""
            year_value = str(row[year_col]).strip() if year_col else ""
            if not year_value and date_col:
                year_value = _extract_year(row[date_col])
            comment = prompt_for_comment(i + 1)
            if verbose:
                comments.append(_format_comment(white, black, event, year_value, comment))
            else:
                comments.append(comment)
            i += 1
        else:
            print("Puzzle rejected.")

    while not all_puzzles and len(puzzles) < n:
        row = df.sample(n=1).iloc[0]
        fen = str(row[fen_col]).strip()
        if not fen:
            continue
        url = get_puzzle_url(fen)
        print(f"Puzzle {i + 1}:")
        print(fen)
        open_puzzle_url(url, open_in_browser=open_in_browser)
        choice = validate_choice()
        if choice == "1":
            puzzles.append(fen)
            white = str(row[white_col]).strip() if white_col else ""
            black = str(row[black_col]).strip() if black_col else ""
            event = str(row[event_col]).strip() if event_col else ""
            year_value = str(row[year_col]).strip() if year_col else ""
            if not year_value and date_col:
                year_value = _extract_year(row[date_col])
            comment = prompt_for_comment(i + 1)
            if verbose:
                comments.append(_format_comment(white, black, event, year_value, comment))
            else:
                comments.append(comment)
            i += 1
        else:
            print("Puzzle rejected.")

    reorder_choice = input("Would you like to reorder the puzzles? (yes/no): ")
    if reorder_choice.lower() == "yes":
        new_order = input("Enter the puzzle numbers in the new order, comma-separated: ")
        new_order_indices = [int(x) - 1 for x in new_order.split(",")]
        puzzles = [puzzles[i] for i in new_order_indices]
        comments = [comments[i] for i in new_order_indices]

    return puzzles, comments


def get_puzzles_from_text_file(filename, open_in_browser=True):
    """
    Get puzzles from a text file.
    """
    with open(filename, "r") as f:
        all_puzzles = f.readlines()
    puzzles = []
    comments = []
    for puzzle in all_puzzles:
        puzzle = puzzle.strip()
        if not puzzle:
            continue
        puzzle_und = puzzle.replace(" ", "_")
        url = "https://lichess.org/analysis/" + puzzle_und
        open_puzzle_url(url, open_in_browser=open_in_browser)
        choice = validate_choice()
        if choice == "1":
            board = chess.Board(puzzle)
            fen = board.fen()
            puzzles.append(fen)
            comment = prompt_for_comment(len(comments) + 1)
            comments.append(comment)
        else:
            print("Puzzle rejected.")
    return puzzles, comments


def find_mate_in_n_puzzles(
    pgn_file_path,
    mate_in_n,
    num_puzzles,
    stockfish_path=None,
    open_in_browser=True,
):
    puzzles = []
    comments = []
    engine_path = stockfish_path or DEFAULT_STOCKFISH_PATH
    if not engine_path:
        raise ValueError("Stockfish path not set. Use --stockfish or STOCKFISH_PATH.")

    with open(pgn_file_path, encoding="ISO-8859-1") as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None or len(puzzles) >= num_puzzles:
                break

            board = game.board()
            for move in game.mainline_moves():
                board.push(move)

            if len(board.move_stack) < mate_in_n + 1:
                continue

            engine = chess.engine.SimpleEngine.popen_uci(engine_path)
            for _ in range(mate_in_n + 1):
                if board.move_stack:
                    board.pop()

            info = engine.analyse(board, chess.engine.Limit(depth=20))
            engine.quit()

            score = info.get("score")
            if score and score.is_mate():
                mate_value = (
                    score.white().mate() if board.turn == chess.WHITE else score.black().mate()
                )

                if mate_value == mate_in_n:
                    fen = board.fen()
                    url = get_puzzle_url(fen)
                    open_puzzle_url(url, open_in_browser=open_in_browser)
                    choice = validate_choice()
                    if choice == "1":
                        puzzles.append(fen)
                        white = game.headers.get("White", "Unknown")
                        black = game.headers.get("Black", "Unknown")
                        event = game.headers.get("Event", "Unknown Event")
                        date = game.headers.get("Date", "????")
                        year = _extract_year(date)
                        comment = prompt_for_comment(len(comments) + 1)
                        full_comment = _format_comment(white, black, event, year, comment)
                        comments.append(full_comment)
                    else:
                        print("Puzzle rejected.")
    return puzzles, comments


def main():
    """
    Make a puzzle with a given theme.
    1. Get the theme as input from the argument.
    2. Find 10 random puzzles with that theme.
    3. For each FEN string, generate a PNG image.
    4. Generate a PDF file with the images.
    """
    parser = argparse.ArgumentParser(description="Generate a puzzle with a given theme.")
    parser.add_argument(
        "medium",
        type=str,
        help="The medium from which to get the puzzles. (lichess, text, csv, cql)",
    )
    parser.add_argument(
        "theme",
        type=str,
        help="The theme of the puzzle. Should be of the form theme1,theme2,theme3.",
    )
    parser.add_argument("--f", "--file", dest="f", type=str, help="The file to read from.")
    parser.add_argument("--n", type=int, help="The number of puzzles to generate.", default=10)
    parser.add_argument(
        "--mate_in_n",
        type=int,
        help="The number of moves for checkmate in the mate-in-N puzzles.",
        default=2,
    )
    parser.add_argument(
        "--all_puzzles",
        action="store_true",
        help="Whether to go through all puzzles in the csv file.",
    )
    parser.add_argument("--data-dir", type=str, help="Base data directory.")
    parser.add_argument("--lichess-db", type=str, help="Path to lichess_db_puzzle.csv.")
    parser.add_argument("--themes-file", type=str, help="Path to themes-unique.txt.")
    parser.add_argument("--output-dir", type=str, help="Output directory.")
    parser.add_argument("--stockfish", type=str, help="Path to Stockfish binary.")
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open browser tabs or PDFs.",
    )
    parser.add_argument(
        "--no-confirm-open",
        action="store_true",
        help="Do not prompt before opening browser tabs.",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Skip PDF generation with pdflatex.",
    )
    parser.add_argument("--title", type=str, help="Puzzle sheet title.")
    parser.add_argument("--squad", type=str, help="Squad name.")
    parser.add_argument("--blurb", type=str, help="Puzzle sheet blurb.")
    parser.add_argument(
        "--author",
        type=str,
        help="Author name for the PDF header (defaults to the current year only).",
    )

    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else DEFAULT_DATA_DIR
    lichess_db_path = (
        Path(args.lichess_db)
        if args.lichess_db
        else (data_dir / "0positions/csv-fen/lichess_db_puzzle.csv")
    )
    themes_file = Path(args.themes_file) if args.themes_file else (data_dir / "themes-unique.txt")
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    stockfish_path = args.stockfish or DEFAULT_STOCKFISH_PATH
    open_in_browser = not args.no_open
    open_pdf = not args.no_open
    run_pdflatex = not args.no_pdf

    if open_in_browser and not args.no_confirm_open:
        open_in_browser = confirm_browser_open()

    output_dir.mkdir(parents=True, exist_ok=True)

    all_puzzles = args.all_puzzles
    theme = args.theme
    n = args.n
    filename = args.f
    mate_in_n_value = args.mate_in_n

    try:
        if args.medium == "lichess":
            if not lichess_db_path.exists():
                print(f"Lichess DB not found at {lichess_db_path}")
                return 1
            puzzles, comments = get_puzzles_from_lichess(
                theme,
                n,
                lichess_db_path=lichess_db_path,
                themes_file=themes_file,
                open_in_browser=open_in_browser,
            )
        elif args.medium == "text":
            if not filename:
                print("--file is required when medium is 'text'.")
                return 1
            puzzles, comments = get_puzzles_from_text_file(
                filename, open_in_browser=open_in_browser
            )
        elif args.medium == "csv":
            if not filename:
                print("--file is required when medium is 'csv'.")
                return 1
            puzzles, comments = get_puzzles_from_csv(
                filename, n, False, all_puzzles, open_in_browser=open_in_browser
            )
        elif args.medium == "cql":
            if not filename:
                print("--file is required when medium is 'cql'.")
                return 1
            puzzles, comments = find_mate_in_n_puzzles(
                filename,
                mate_in_n_value,
                n,
                stockfish_path=stockfish_path,
                open_in_browser=open_in_browser,
            )
        else:
            print("Unknown medium. Use one of: lichess, text, csv, cql")
            return 1
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return 1

    if not puzzles:
        print("No puzzles selected.")
        return 1

    img_dir = output_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)

    print("Generating images...")
    for idx, puzzle in enumerate(puzzles):
        print(f"Generating image {idx}...")
        img_name = img_dir / f"puzzle_{idx}.png"
        fen2png(puzzle, str(img_name))

    safe_theme = theme.replace(",", "_").replace(" ", "_")
    tex_base = output_dir / safe_theme
    fen2tex(
        tex_base,
        img_dir,
        comments,
        title=args.title,
        squad=args.squad,
        blurb=args.blurb,
        author=args.author,
        run_pdflatex=run_pdflatex,
        open_pdf=open_pdf,
    )
    return 0


if __name__ == "__main__":
    main()
