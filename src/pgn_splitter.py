import sys
from pathlib import Path


def split_pgn(input_file: str, max_games: int = 64) -> None:
    """
    Split a PGN file into multiple files with a maximum number of games per file.

    Args:
        input_file: Path to the input PGN file
        max_games: Maximum number of games per output file (default: 64)
    """
    # Read the entire file
    with open(input_file, "r") as f:
        content = f.read()

    # Split into individual games
    # A new game starts with an Event tag
    games = []
    current_game = []

    for line in content.split("\n"):
        # If we find a new [Event tag and we already have a game in progress
        if (
            line.strip().startswith("[Event ")
            and current_game
            and any(g.strip().startswith("[") for g in current_game)
        ):
            games.append("\n".join(current_game))
            current_game = []
        current_game.append(line)

    # Add the last game if exists
    if current_game:
        games.append("\n".join(current_game))

    # Remove any empty games (just whitespace)
    games = [game for game in games if any(line.strip() for line in game.split("\n"))]

    total_games = len(games)
    print(f"Found {total_games} games in {input_file}")

    # Calculate number of files needed
    num_files = (total_games + max_games - 1) // max_games

    # Create output files
    input_path = Path(input_file)
    base_name = input_path.stem
    extension = input_path.suffix

    for i in range(num_files):
        start_idx = i * max_games
        end_idx = min((i + 1) * max_games, total_games)

        # Create output filename: original_name_1.pgn, original_name_2.pgn, etc.
        output_file = input_path.parent / f"{base_name}_{i + 1}{extension}"

        # Write games to file, ensuring proper separation between games
        with open(output_file, "w") as f:
            f.write("\n\n".join(games[start_idx:end_idx]))
            f.write("\n")  # End file with newline

        print(f"Created {output_file} with {end_idx - start_idx} games")

    print(f"\nSplit {total_games} games into {num_files} files")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pgn_splitter.py <input_pgn_file>")
        sys.exit(1)

    split_pgn(sys.argv[1])
