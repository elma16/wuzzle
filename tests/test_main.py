import pytest
import chess
from PIL import Image

import main
from fen2tex import fen2tex


def _set_input(monkeypatch, values):
    inputs = iter(values)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))


def test_is_valid_theme(tmp_path):
    themes_file = tmp_path / "themes.txt"
    themes_file.write_text("fork\npin\n")

    assert main.is_valid_theme("fork", themes_file)
    assert not main.is_valid_theme("skewer", themes_file)


def test_is_valid_theme_missing_file(tmp_path):
    missing_file = tmp_path / "missing.txt"
    assert main.is_valid_theme("anything", missing_file)


def test_get_puzzle_url():
    puzzle = "puzzle one"
    expected_url = "https://lichess.org/analysis/puzzle_one"
    assert main.get_puzzle_url(puzzle) == expected_url


def test_extract_year():
    assert main._extract_year("2021.05.06") == "2021"
    assert main._extract_year("1999-12-31") == "1999"
    assert main._extract_year("2001/02/03") == "2001"
    assert main._extract_year("2000") == "2000"
    assert main._extract_year("") == ""


def test_format_comment():
    comment = main._format_comment("White", "Black", "Event", "2020", "Nice")
    assert "\\textbf{White - Black}" in comment
    assert "Event 2020" in comment
    assert "Nice" in comment


def test_get_puzzles_from_csv(tmp_path, monkeypatch):
    csv_path = tmp_path / "puzzles.csv"
    csv_path.write_text(
        "game_index,fen,white,black,year,event\n"
        '1,"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",W,B,2020,Test Event\n'
    )

    _set_input(monkeypatch, ["1", "Comment", "no"])
    puzzles, comments = main.get_puzzles_from_csv(
        str(csv_path), n=1, verbose=True, all_puzzles=True, open_in_browser=False
    )

    assert len(puzzles) == 1
    assert comments
    assert "Test Event 2020" in comments[0]


def test_get_puzzles_from_text_file(tmp_path, monkeypatch):
    text_path = tmp_path / "puzzles.txt"
    text_path.write_text("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\n")

    _set_input(monkeypatch, ["1", "Comment"])
    puzzles, comments = main.get_puzzles_from_text_file(str(text_path), open_in_browser=False)

    assert len(puzzles) == 1
    assert comments == ["Comment"]


def test_get_puzzles_from_lichess_single_row(tmp_path, monkeypatch):
    lichess_path = tmp_path / "lichess.csv"
    lichess_path.write_text(
        "00001,rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1,"
        "e2e4,1500,50,100,1000,fork,https://lichess.org/abc/white#1,\n"
    )
    themes_path = tmp_path / "themes.txt"
    themes_path.write_text("fork\n")

    _set_input(monkeypatch, ["1", "Comment"])
    puzzles, comments = main.get_puzzles_from_lichess(
        "fork",
        n=1,
        lichess_db_path=lichess_path,
        themes_file=themes_path,
        open_in_browser=False,
    )

    assert len(puzzles) == 1
    assert comments == ["Comment"]

    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board.push_uci("e2e4")
    assert puzzles[0] == board.fen()


def test_fen2tex_writes_tex(tmp_path):
    img_dir = tmp_path / "images"
    img_dir.mkdir()

    for idx in range(2):
        img = Image.new("RGB", (64, 64), color=(255, 255, 255))
        img.save(img_dir / f"puzzle_{idx}.png")

    tex_base = tmp_path / "sheet"
    fen2tex(
        tex_base,
        img_dir,
        ["c1", "c2"],
        title="Title",
        squad="Squad",
        blurb="Blurb",
        run_pdflatex=False,
        open_pdf=False,
    )

    tex_path = tex_base.with_suffix(".tex")
    assert tex_path.exists()
    contents = tex_path.read_text()
    assert "Title" in contents
    assert "Squad" in contents


def test_find_mate_in_n_requires_stockfish(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "DEFAULT_STOCKFISH_PATH", None)
    with pytest.raises(ValueError):
        main.find_mate_in_n_puzzles(
            str(tmp_path / "games.pgn"),
            2,
            1,
            stockfish_path=None,
            open_in_browser=False,
        )
