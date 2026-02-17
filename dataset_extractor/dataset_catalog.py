"""
Extract Worcester MA open data catalog entries with CSV distributions.
Creates a CSV file with title, description, and accessURL for datasets.
"""

import csv
import json
import sys
from pathlib import Path
from urllib.request import urlopen

from bs4 import BeautifulSoup


def fetch_data_catalog(url: str) -> dict:
    """Fetch the Worcester MA open data catalog JSON."""
    print(f"Fetching data catalog from {url}...")
    try:
        with urlopen(url) as response:
            data = json.loads(response.read())
        print("Successfully fetched catalog")
        return data
    except Exception as e:
        print(f"Error fetching catalog: {e}")
        sys.exit(1)


def strip_html(text: str) -> str:
    """Remove HTML tags from text and clean up whitespace."""
    if not text:
        return ""

    # Parse HTML and get text
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text(separator=" ", strip=True)

    # Collapse multiple spaces
    clean_text = " ".join(clean_text.split())

    return clean_text


def extract_csv_datasets(catalog: dict) -> list[dict]:
    """
    Extract datasets that have CSV distributions.

    Returns a list of dicts with keys: title, description, accessURL
    """
    datasets = []

    # Get the dataset array
    dataset_list = catalog.get("dataset", [])
    print(f"Found {len(dataset_list)} total datasets")

    for dataset in dataset_list:
        # Check if this is a dcat:Dataset
        if dataset.get("@type") != "dcat:Dataset":
            continue

        title = dataset.get("title", "")
        description = strip_html(dataset.get("description", ""))

        # Look for CSV distribution
        distributions = dataset.get("distribution", [])

        for dist in distributions:
            # Check if this distribution has CSV format
            if dist.get("title") == "CSV" or dist.get("format") == "CSV":
                access_url = dist.get("accessURL", "")

                if access_url:
                    datasets.append(
                        {
                            "title": title,
                            "description": description,
                            "accessURL": access_url,
                        }
                    )
                    # Only take the first CSV distribution per dataset
                    break

    print(f"Found {len(datasets)} datasets with CSV distributions")
    return datasets


def write_csv(datasets: list[dict], output_file: Path):
    """Write datasets to CSV file."""
    print(f"Writing {len(datasets)} datasets to {output_file}...")

    # Create parent directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "description", "accessURL"])
        writer.writeheader()
        writer.writerows(datasets)
