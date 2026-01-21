import lichess_themes


def test_extract_unique_themes(tmp_path):
    csv_path = tmp_path / "lichess.csv"
    csv_path.write_text(
        'id,fen,moves,1,1,1,1,"fork pin",https://lichess.org/a,tag\n'
        "id2,fen,moves,1,1,1,1,skewer,https://lichess.org/b,tag\n"
    )

    themes = lichess_themes.extract_unique_themes(csv_path)

    assert themes == ["fork", "pin", "skewer"]
