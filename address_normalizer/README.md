# Address Normalizer

The `address_normalizer` is a Python module designed to parse, extract, and normalize raw address strings into structured geographic components. This tool is built specifically to enrich the datasets in the Worcester, MA open data catalog by splitting informal or unstructured address strings into standardized columns.

## Architecture

The system uses a **Pipeline-based Architecture** to sequentially apply rules and regular expressions to address strings.

### Core Components

1. **Extraction Pipeline (`extraction/pipeline.py`)** 
   The `AddressPipeline` manages a sequential list of modular extractors. It initializes an `ExtractionContext` and passes it through each extractor in order of priority.
   
2. **Context Object (`extraction/context.py`)**
   The `ExtractionContext` is a dataclass that serves as the shared state across the pipeline. It holds:
   - `address_line`: The active, unprocessed portion of the string.
   - `data`: A dictionary accumulating extracted components (e.g., `city`, `zip_code`, `unit`).
   - `anchors`: Used by extractors to track match positions and manipulate the string correctly.

3. **Extractors (`extraction/base.py`)**
   Each piece of semantic meaning is parsed by an independent `Extractor` (e.g., `CityExtractor`, `ZipCodeExtractor`, `StreetNumberExtractor`). Extractors conform to a Protocol and run based on an explicit integer `priority`. Extracted tokens are removed from the `address_line` or otherwise marked, while their parsed data is added directly to `context.data`.

4. **CSV Processor (`processor.py`)**
   The `CSVProcessor` class provides the bulk processing framework. It reads an input CSV file using `csv.DictReader`, extracts the `Address` column using the `AddressPipeline`, appends the newly standardized columns to the dictionary, and writes it back to an output CSV.

## Usage

### Command Line Interface

The simplest way to use the library is via the provided CLI. Use the `dataset_extractor.cli` module or run `address_normalizer.cli` directly (depending on your `pyproject.toml` configuration) to process an entire CSV file.

```bash
uv run python -m address_normalizer.cli --input data/raw/input.csv --output data/processed/normalized.csv
```

**Arguments:**
- `--input` (`-i`): Path to the single input CSV file to be processed. (Must contain an `Address` column).
- `--output` (`-o`): Path where the enriched CSV should be saved.

### Output Format

The processor enriches the outgoing CSV by appending the following parsed columns to the existing dataset columns:

- `street_number`
- `street_range_to`
- `street_extension`
- `street_name`
- `street_type`
- `unit`
- `city` (defaults to "Worcester" if not found)
- `state` (defaults to "MA" if not found)
- `zip_code`
