"""
Simple HTTP server for downloading Worcester datasets.
Serves the HTML interface and handles download requests.
"""

import json
import os
import time
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class DatasetDownloadHandler(SimpleHTTPRequestHandler):
    """Custom handler for dataset downloads."""

    def do_POST(self):
        """Handle POST requests for downloading datasets."""
        if self.path == "/download":
            self.handle_download()
        else:
            self.send_error(404, "Not Found")

    def handle_download(self):
        """Process download request for multiple datasets."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            datasets = data.get("datasets", [])

            if not datasets:
                self.send_json_response({"error": "No datasets provided"}, 400)
                return

            # Create output directory
            output_dir = Path("data/raw")
            output_dir.mkdir(parents=True, exist_ok=True)

            results = {
                "total": len(datasets),
                "successful": 0,
                "failed": 0,
                "failures": [],
            }

            # Download each dataset
            for dataset in datasets:
                url = dataset.get("url", "")
                title = dataset.get("title", "unnamed")

                if not url:
                    results["failed"] += 1
                    results["failures"].append(
                        {"title": title, "error": "No URL provided"}
                    )
                    continue

                try:
                    # Generate filename from URL
                    filename = self.get_filename_from_url(url, title)
                    filepath = output_dir / filename

                    # Download file
                    self.download_file(url, filepath)
                    results["successful"] += 1

                    print(f"✓ Downloaded: {filename}")

                except Exception as e:
                    results["failed"] += 1
                    results["failures"].append({"title": title, "error": str(e)})
                    print(f"✗ Failed: {title} - {e}")

                # Small delay to avoid overwhelming the server
                time.sleep(0.5)

            self.send_json_response(results, 200)

        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
        except Exception as e:
            self.send_json_response({"error": str(e)}, 500)

    def download_file(self, url: str, filepath: Path, max_retries: int = 3):
        """Download a file with retry logic."""
        for attempt in range(max_retries):
            try:
                # Create request with headers to avoid being blocked
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }
                req = Request(url, headers=headers)

                with urlopen(req, timeout=30) as response:
                    content = response.read()

                    # Write to file
                    with open(filepath, "wb") as f:
                        f.write(content)

                    return

            except (HTTPError, URLError) as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"  Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise Exception(
                        f"Download failed after {max_retries} attempts: {e}"
                    ) from e
            except Exception as e:
                raise Exception(f"Download error: {e}") from e

    def get_filename_from_url(self, url: str, title: str) -> str:
        """Extract filename from URL or generate from title."""
        parsed = urlparse(url)
        path = parsed.path

        # Try to get filename from URL
        if path:
            filename = Path(path).name
            if filename and "." in filename:
                return self.sanitize_filename(filename)

        # Fallback: use title + .csv
        safe_title = self.sanitize_filename(title)
        return f"{safe_title}.csv"

    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename."""

        # Replace spaces with underscores
        filename = filename.replace(" ", "_")

        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:190] + ext

        return filename

    def send_json_response(self, data: dict, status: int):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        """Custom log format."""
        if self.path != "/download":
            return  # Don't log regular file requests
        super().log_message(format, *args)
