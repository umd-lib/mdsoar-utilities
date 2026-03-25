#!/usr/bin/env python3
import argparse
import csv
import os


def preprocess_csv(input_file: str, output_file: str, lines_to_skip: int = 9) -> None:
    with open(input_file, "r", newline="", encoding="utf-8") as infile, \
         open(output_file, "w", newline="", encoding="utf-8") as outfile:

        # Skip the first N raw lines completely
        for _ in range(lines_to_skip):
            next(infile, None)

        # Now start CSV parsing from the real header
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader, None)
        if header is None:
            raise ValueError("Input file does not contain a header after skipping lines.")

        writer.writerow(header)

        for row in reader:
            writer.writerow(row)

    print(f"Preprocessed file written to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Remove the first N raw lines from a CSV file while keeping the real header."
    )
    parser.add_argument("input_csv", help="Input CSV file")
    parser.add_argument(
        "-o", "--output",
        help="Output CSV file (default: <input>_preprocessed.csv)"
    )
    parser.add_argument(
        "--lines-to-skip",
        type=int,
        default=9,
        help="Number of raw lines to skip before the real CSV header (default: 9)"
    )

    args = parser.parse_args()

    input_file = args.input_csv
    if args.output:
        output_file = args.output
    else:
        root, ext = os.path.splitext(input_file)
        output_file = f"{root}_preprocessed{ext}"

    preprocess_csv(input_file, output_file, args.lines_to_skip)


if __name__ == "__main__":
    main()