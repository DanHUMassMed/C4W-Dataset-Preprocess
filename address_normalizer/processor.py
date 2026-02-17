import csv
import logging
from pathlib import Path

from .extraction.pipeline import AddressPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CSVProcessor:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.pipeline = AddressPipeline()

    def process(self):
        if not self.input_path.exists():
            logger.error(f"Input file not found: {self.input_path}")
            return

        logger.info(f"Starting processing of {self.input_path}")

        try:
            with open(self.input_path, encoding="utf-8", errors="replace") as infile:
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames

                # new columns to append
                new_cols = [
                    "street_number",
                    "street_range_to",
                    "street_extension",
                    "street_name",
                    "street_type",
                    "unit",
                    "city",
                    "state",
                    "zip_code",
                ]

                # Prepare output fields
                out_fields = list(fieldnames) + new_cols

                rows_to_write = []
                total_rows = 0
                success_count = 0

                for row in reader:
                    total_rows += 1
                    raw_address = row.get("Address", "")

                    # Run Pipeline
                    data = self.pipeline.run(raw_address)

                    # Enrich row
                    row["street_number"] = data.get("street_number", "")
                    row["street_range_to"] = data.get("street_range_to", "")
                    row["street_extension"] = data.get("street_extension", "")
                    row["street_name"] = data.get("street_name", "")
                    row["street_type"] = data.get("street_type", "")
                    row["unit"] = data.get("unit", "")
                    row["city"] = data.get("city", "")
                    row["state"] = data.get("state", "")
                    row["zip_code"] = data.get("zip_code", "")

                    # Determine Status
                    # Simple heuristic: if we have number and name, it's a success?
                    # Or check if address_line is mostly empty?
                    if data.get("street_number") and data.get("street_name"):
                        success_count += 1

                    rows_to_write.append(row)

                    if total_rows % 1000 == 0:
                        logger.info(f"Processed {total_rows} rows...")

                # Write output
                self.output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(
                    self.output_path, mode="w", encoding="utf-8", newline=""
                ) as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=out_fields)
                    writer.writeheader()
                    writer.writerows(rows_to_write)

                logger.info(
                    f"Completed! Processed {total_rows} rows. Success rate: {success_count / total_rows:.2%}"
                )
                logger.info(f"Output saved to {self.output_path}")

        except Exception as e:
            logger.error(f"Failed to process CSV: {e}")
            raise
