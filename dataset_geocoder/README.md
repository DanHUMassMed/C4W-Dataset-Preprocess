# Dataset Geocoder

The `dataset_geocoder` is a Python module designed to append geographic coordinates and standardized zip codes to address datasets. It handles the translation of structured address components into precise geographic data using local infrastructure to ensure fast, bulk processing without relying on expensive or rate-limited external APIs.

## Architecture

The workflow is divided into two primary processing steps, executed sequentially over a dataset.

### 1. Geocoding (`geocoder.py`)

The geocoding module takes raw address components and retrieves corresponding latitude, longitude, and matched names.

*   **Local Nominatim Service**: It queries a local instance of Nominatim mapped to `http://localhost:8080/search`. This local instance allows for high-throughput bulk processing.
*   **Bounding Box Restrictions**: Queries are aggressively bounded to the Worcester, MA regional coordinates (`viewbox=[-71.884, 42.341, -71.731, 42.210]`) to reduce false positives and improve matching speed.
*   **Concurrency**: Uses a `ThreadPoolExecutor` to handle concurrent HTTP requests, controlled by a `max_workers` parameter, allowing for rapid batch fetching against the local server.
*   **Caching & Retries**: Queries are cached in memory using `lru_cache`, and the requests session integrates an `urllib3` Retry adapter to recover from potential rate limits or transient errors gracefully.

### 2. Zip Code Assignment (`zipcoder.py`)

After addresses are converted to geographic coordinates, this module determines their precise Zip Code Tabulation Area (ZCTA).

*   **Spatial Joins**: It utilizes `geopandas` to load a local Massachusetts ZCTA shapefile (from `data/external/tl_2025_ma_zcta520/`).
*   **Point Matching**: It maps the newly acquired `latitude` and `longitude` fields to Point geometries.
*   **Intersection**: Performs a spatial "within" join to identify which ZCTA polygon the coordinate falls inside, effectively assigning the accurate `zcta_zip` column to the output DataFrame.

## Usage

### Command Line Interface

The simplest way to execute the full pipeline is via the provided CLI. This command will run both the geocoding step and the zip code assignment step sequentially on the target file.

```bash
uv run python -m dataset_geocoder.cli --input data/processed/my_addresses.csv --output data/geocoded/my_addresses_geo.csv
```

**Arguments:**
*   `--input` (`-i`): Path to the single input CSV file to be processed. (Must contain components like `street_number`, `street_name`, `city`, etc., as outputted by the `address_normalizer`).
*   `--output` (`-o`): Path where the enriched CSV should be saved. *If omitted, the script will overwrite the input file inline.*

### Output Format

The target CSV will be enriched with four new columns appended to its rows:

*   `latitude`: The Y-coordinate found by Nominatim (float).
*   `longitude`: The X-coordinate found by Nominatim (float).
*   `display_name`: The formatted matching street name returned by the geocoder.
*   `zcta_zip`: The geographic Zip Code matched against the spatial polygon boundaries.
