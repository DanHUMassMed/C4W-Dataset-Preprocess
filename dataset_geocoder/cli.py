#!/usr/bin/env python3
import argparse

from .geocoder import geocode_csv
from .zipcoder import zipcode_csv


def main():
    parser = argparse.ArgumentParser(description="Geocode CSV using local Nominatim")
    parser.add_argument("--input", "-i", required=True, help="Input CSV file")
    parser.add_argument(
        "--output", "-o", help="Output CSV file (default: overwrite input)"
    )
    args = parser.parse_args()

    geocode_csv(input_file=args.input, output_file=args.output)
    zipcode_csv(input_file=args.input, output_file=args.output)


if __name__ == "__main__":
    main()
