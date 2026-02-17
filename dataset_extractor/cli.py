import os
from http.server import HTTPServer
from pathlib import Path

from dataset_extractor.dataset_catalog import (
    extract_csv_datasets,
    fetch_data_catalog,
    write_csv,
)
from dataset_extractor.download_server import DatasetDownloadHandler

CATALOG_URL = "https://opendata.worcesterma.gov/data.json"
CATALOG_FILE = Path("data/worcester-datasets.csv")


def get_catalog():
    if CATALOG_FILE.exists():
        print(f"Catalog already exists at {CATALOG_FILE}, skipping fetch.")
        return
    catalog = fetch_data_catalog(CATALOG_URL)
    datasets = extract_csv_datasets(catalog)
    write_csv(datasets, CATALOG_FILE)


def main():
    """Start the server."""
    port = 8000

    # Change to project root (parent of Dataset-Extractor)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    get_catalog()
    server = HTTPServer(("localhost", port), DatasetDownloadHandler)

    print(f"\n{'=' * 60}")
    print("  Worcester Dataset Downloader")
    print(f"{'=' * 60}")
    print(f"\n  Server running at: http://localhost:{port}")
    print(f"  Open in browser: http://localhost:{port}/Dataset_Extractor/")
    print(f"  Download directory: {Path('data/raw').absolute()}")
    print(f"  CSV file location: {CATALOG_FILE.absolute()}")
    print("\n  Press Ctrl+C to stop the server\n")
    print(f"{'=' * 60}\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.shutdown()
        print("Server stopped.")


if __name__ == "__main__":
    main()
