import csv
import argparse


def extract_game_info(input_file, output_file):
    with open(input_file, "r") as file:
        data = file.read()

    items = data.split("\n\n\n")

    # Prepare the CSV file
    csv_file = open(output_file, "w", newline="")
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(["Event", "Date", "White", "Black", "Result", "FEN", "Solution"])

    for item in items:
        fields = ["Event", "Date", "White", "Black", "Result", "FEN"]
        row = []
        for field in fields:
            try:
                value = item.split(f'[{field} "')[1].split('"]')[0]
            except IndexError:
                value = ""
            row.append(value)

        solution = ""
        if "{" in item:
            solution = item.split("{", 1)[1].strip()
        row.append(solution)

        # Write the extracted information as a row in the CSV file
        csv_writer.writerow(row)

    # Close the CSV file
    csv_file.close()


def main():
    """Parse command line arguments and call extract_game_info().

    :returns: None
    """
    parser = argparse.ArgumentParser(
        description="Extract game information from a PGN file and save it to a CSV file."
    )
    parser.add_argument("input_file", type=str, help="PGN file to extract game information from.")
    parser.add_argument("output_file", type=str, help="CSV file to save game information to.")
    args = parser.parse_args()

    extract_game_info(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
