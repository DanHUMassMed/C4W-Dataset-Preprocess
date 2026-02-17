# Worcester Dataset Downloader

A simple web-based utility to browse and download datasets from Worcester MA's open data portal.

## Features

- **Browse datasets**: View all 227+ available CSV datasets with titles and descriptions
- **Selective download**: Choose which datasets to download using checkboxes
- **Bulk operations**: Select all, deselect all, or pick individual datasets
- **Robust downloading**: Automatic retries, error handling, and timeout protection
- **Progress tracking**: Visual feedback during downloads

## File Structure

```
Dataset-Extractor/
├── index.html           # Web interface for dataset selection
├── download_server.py   # Python server for handling downloads
├── dataset_catalog.py   # Extract datasets from Worcester open data
└── README.md           # This file
```

## Usage

### Step 1: Extract Dataset Catalog (if needed)

```bash
cd Dataset-Extractor
python3 dataset_catalog.py
```

This creates `data/worcester-datasets.csv` with all available datasets.

### Step 2: Start the Download Server

```bash
cd Dataset-Extractor
python3 download_server.py
```

The server will start at `http://localhost:8000`

### Step 3: Open the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

### Step 4: Select and Download

1. Browse the list of datasets
2. Check the boxes for datasets you want to download
3. Click "Download Selected"
4. Files will be saved to `data/raw/`

## Download Features

- **Automatic retries**: Up to 3 attempts per file with exponential backoff
- **Custom headers**: Includes User-Agent to avoid being blocked
- **Timeout protection**: 30-second timeout per request
- **Filename sanitization**: Removes invalid characters from filenames
- **Progress feedback**: Shows success/failure counts after download

## Troubleshooting

**Problem**: Server won't start
- **Solution**: Make sure port 8000 is available or edit `download_server.py` to use a different port

**Problem**: Downloads fail
- **Solution**: Check your internet connection; the server will automatically retry failed downloads

**Problem**: Can't see datasets
- **Solution**: Make sure `data/worcester-datasets.csv` exists; run `dataset_catalog.py` if needed

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.
