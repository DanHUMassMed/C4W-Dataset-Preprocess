import argparse
import sys

from .processor import CSVProcessor


def main():
    parser = argparse.ArgumentParser(description="Normalize addresses in a CSV file.")
    parser.add_argument(
        "--input", "-i", required=True, help="Path to the input CSV file."
    )
    parser.add_argument(
        "--output", "-o", required=True, help="Path to the output CSV file."
    )
    parser.add_argument(
        "--address-column",
        "-c",
        default="Address",
        help="Name of the column containing the address (default: 'Address')",
    )

    args = parser.parse_args()

    print(f"Input: {args.input}")
    print(f"Output: {args.output}")

    try:
        processor = CSVProcessor(
            args.input, args.output, address_column=args.address_column
        )
        processor.process()
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
