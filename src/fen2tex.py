import io
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import chess
import chess.svg
from PIL import Image, ImageDraw
from cairosvg import svg2png

current_year = datetime.now().year


def fen2png(fen_string, img_name):
    """
    Convert FEN string to PNG image
    E.g: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1
    """
    board = chess.Board(fen=fen_string)
    svg_board = chess.svg.board(
        board=board,
        orientation=board.turn,
        colors={"margin": "transparent", "coord": "black"},
    ).encode("UTF-8")
    png_image = svg2png(bytestring=svg_board)
    pil_image = Image.open(io.BytesIO(png_image))

    if board.turn == chess.WHITE:
        color = (250, 250, 250)
    else:
        color = (0, 0, 0)

    draw = ImageDraw.Draw(pil_image)
    coords = [(375, 0), (390, 0), (390, 14), (375, 14)]
    draw.polygon(coords, fill=color, outline="grey", width=3)

    pil_image.save(img_name)


def fen2pngCustom(fen_string, img_name, svg_dir):
    custom_pieces = {}
    custom_pieces[chess.Piece(chess.PAWN, chess.WHITE)] = open("white_pawn.svg", "rb").read()
    custom_pieces[chess.Piece(chess.KNIGHT, chess.WHITE)] = open("white_knight.svg", "rb").read()
    # ...add the rest of the pieces

    board = chess.Board(fen=fen_string)
    _ = chess.svg.board(
        board=board,
        orientation=board.turn,
        pieces=custom_pieces,
        colors={"inner border": "#15781B80"},
    ).encode("UTF-8")
    return 0


def _puzzle_index(path_obj):
    try:
        return int(path_obj.stem.split("_")[1])
    except (IndexError, ValueError):
        return 0


def fen2tex(
    tex_file_name,
    img_dir,
    comments,
    title=None,
    squad=None,
    blurb=None,
    author=None,
    run_pdflatex=True,
    open_pdf=True,
):
    """
    Given a collection of FENs, generate a LaTeX file with the puzzles.
    """
    tex_path = Path(tex_file_name)
    if tex_path.suffix.lower() != ".tex":
        tex_path = tex_path.with_suffix(".tex")

    output_dir = tex_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    img_dir = Path(img_dir)
    if not img_dir.exists():
        raise FileNotFoundError(f"Image directory not found: {img_dir}")

    if title is None:
        title = input("Enter a title for the puzzle sheet: ")
    if squad is None:
        squad = input("Enter the squad name: ")
    if blurb is None:
        blurb = input("Enter a blurb for the puzzle sheet: ")
    if author is None:
        author = ""

    title = title or ""
    squad = squad or ""
    blurb = blurb or ""
    author = author.strip()
    right_header = f"{author}, {current_year}" if author else str(current_year)

    image_paths = sorted(img_dir.glob("puzzle_*.png"), key=_puzzle_index)
    if not image_paths:
        raise FileNotFoundError(f"No puzzle images found in {img_dir}")

    with tex_path.open("w") as f:
        f.write(
            r"""\documentclass[12pt]{article}
                    \usepackage[english]{babel}
                    \usepackage{graphicx}
                    \usepackage{framed}
                    \usepackage[normalem]{ulem}
                    \usepackage{amsmath}
                    \usepackage{amsthm}
                    \usepackage{amssymb}
                    \usepackage{amsfonts}
                    \usepackage{enumerate}
                    \usepackage[utf8]{inputenc}
                    \usepackage{natbib}
                    \usepackage{tikz}
                    \usepackage{float}
                    \usepackage{caption}
                    \usepackage{subcaption}
                    \usepackage{sidenotes} 
                    \usepackage{tgbonum}
                    \usepackage[a4paper,
                                bindingoffset=0in,
                                left=0.5in,
                                right=0.5in,
                                top=0.8in,
                                bottom=0.5in,
                                footskip=.25in]{geometry}
                    \usepackage{fancyhdr}
                    \fancypagestyle{plain}{%
                    \fancyhf{} % clear all header and footer fields
                    \fancyhead[RE,LO]{"""
            + squad
            + r"""}
                    \fancyhead[LE,RO]{"""
            + right_header
            + r"""}
                    \fancyfoot[C]{\thepage} % except the center
                    \renewcommand{\headrulewidth}{0pt}
                    \renewcommand{\footrulewidth}{0pt}}
                    %activate the style:
                    \pagestyle{plain}
                    \date{}
                    \title{"""
            + title
            + r"""}
                    \captionsetup{
                    justification=centering, % Caption text alignment
                    singlelinecheck=false, % Allow caption to span multiple lines
                    format=plain, % Caption formatting style
                    labelsep=colon % Separator between label and caption
                    }
                    \begin{document}
                    \maketitle
                    \centering{"""
            + blurb
            + r"""}"""
        )

        for idx, img_path in enumerate(image_paths):
            comment = comments[idx] if idx < len(comments) else ""
            img_ref = os.path.relpath(img_path, output_dir)
            img_ref = img_ref.replace(os.sep, "/")

            if idx == 0:
                f.write(
                    r"\begin{figure}[ht]"
                    + "\n"
                    + r"\begin{minipage}[b]{0.5\linewidth}"
                    + "\n"
                    + r"\centering"
                    + "\n"
                    + r"\includegraphics[width=7cm, height=7cm]{"
                    + img_ref
                    + r"}"
                    + r"\caption*{"
                    + comment
                    + r"}"
                    + "\n"
                    + r"\vspace{12ex}"
                    + "\n"
                    + r"\end{minipage}"
                    + "\n"
                )
            elif idx == 1:
                f.write(
                    r"\begin{minipage}[b]{0.5\linewidth}"
                    + "\n"
                    + r"\centering"
                    + "\n"
                    + r"\includegraphics[width=7cm, height=7cm]{"
                    + img_ref
                    + r"}"
                    + r"\caption*{"
                    + comment
                    + r"}"
                    + "\n"
                    + r"\vspace{12ex}"
                    + "\n"
                    + r"\end{minipage}"
                    + "\n"
                )
            elif idx == 2 or (idx > 6 and idx % 6 <= 2):
                f.write(
                    r"\begin{minipage}[b]{0.5\linewidth}"
                    + "\n"
                    + r"\centering"
                    + "\n"
                    + r"\includegraphics[width=7cm, height=7cm]{"
                    + img_ref
                    + r"}"
                    + r"\caption*{"
                    + comment
                    + r"}"
                    + "\n"
                    + r"\vspace{4ex}"
                    + "\n"
                    + r"\end{minipage}"
                    + "\n"
                )
            elif idx == 3 or (idx > 6 and idx % 6 == 3):
                f.write(
                    r"\begin{minipage}[b]{0.5\linewidth}"
                    + "\n"
                    + r"\centering"
                    + "\n"
                    + r"\includegraphics[width=7cm, height=7cm]{"
                    + img_ref
                    + r"}"
                    + r"\caption*{"
                    + comment
                    + r"}"
                    + "\n"
                    + r"\vspace{4ex}"
                    + "\n"
                    + r"\end{minipage}"
                    + "\n"
                    + r"\end{figure}"
                    + "\n"
                )
            elif idx == 4 or (idx > 6 and idx % 6 == 4):
                f.write(
                    r"\begin{figure}[ht]"
                    + "\n"
                    + r"\begin{minipage}[b]{0.5\linewidth}"
                    + "\n"
                    + r"\centering"
                    + "\n"
                    + r"\includegraphics[width=7cm, height=7cm]{"
                    + img_ref
                    + r"}"
                    + r"\caption*{"
                    + comment
                    + r"}"
                    + "\n"
                    + r"\vspace{4ex}"
                    + "\n"
                    + r"\end{minipage}"
                    + "\n"
                )
            elif idx == 5 or (idx == 6) or (idx > 6 and idx % 6 == 5):
                f.write(
                    r"\begin{minipage}[b]{0.5\linewidth}"
                    + "\n"
                    + r"\centering"
                    + "\n"
                    + r"\includegraphics[width=7cm, height=7cm]{"
                    + img_ref
                    + r"}"
                    + r"\caption*{"
                    + comment
                    + r"}"
                    + "\n"
                    + r"\vspace{4ex}"
                    + "\n"
                    + r"\end{minipage}"
                    + "\n"
                )

        f.write(r"""\end{document}""")

    print("tex file written!")

    pdf_file_path = tex_path.with_suffix(".pdf")

    if run_pdflatex:
        if shutil.which("pdflatex") is None:
            print("pdflatex not found; skipping PDF generation.")
        else:
            subprocess.run(["pdflatex", tex_path.name], cwd=output_dir, check=False)

    if open_pdf and pdf_file_path.exists():
        if sys.platform == "darwin":
            subprocess.run(["open", str(pdf_file_path)], check=False)
        elif os.name == "nt":
            os.startfile(str(pdf_file_path))
        elif os.name == "posix":
            subprocess.run(["xdg-open", str(pdf_file_path)], check=False)
