import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Protocol

import pandas as pd
import requests
from tqdm import tqdm


@lru_cache(maxsize=100_000)
def geocode(address: str, base_url: str = "http://localhost:8080/search") -> dict:
    """
    Geocode a single address using local Nominatim directly via HTTP.
    """
    if not address:
        return {"latitude": None, "longitude": None, "display_name": None}

    params = {"q": address, "format": "json", "limit": 1}

    headers = {"User-Agent": "local-geocoder/1.0"}

    try:
        r = requests.get(base_url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return {"latitude": None, "longitude": None, "display_name": None}

        # Take the first result
        result = data[0]
        return {
            "latitude": result.get("lat"),
            "longitude": result.get("lon"),
            "display_name": result.get("display_name"),
        }

    except requests.RequestException as e:
        print(f"Error geocoding '{address}': {e}")
        return {"latitude": None, "longitude": None, "display_name": None}


# -------------------- Bulk geocoder --------------------
def geocode_bulk(addresses: list[str], max_workers: int = None) -> list[dict]:
    if max_workers is None:
        max_workers = min(8, os.cpu_count() or 4)

    results = [None] * len(addresses)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(geocode, addr): i for i, addr in enumerate(addresses)
        }

        for future in tqdm(
            as_completed(future_map), total=len(future_map), desc="Geocoding (bulk)"
        ):
            idx = future_map[future]
            try:
                results[idx] = future.result()
            except Exception:
                results[idx] = {
                    "latitude": None,
                    "longitude": None,
                    "display_name": None,
                }

    return results


class AddressBuilder(Protocol):
    def __call__(self, row) -> str: ...


def _safe(val) -> str:
    """Convert NaN/None to empty string, else to stripped string."""
    if pd.isna(val):
        return ""
    return str(val).strip()


def build_address(row) -> str:
    return (
        f"{_safe(row.street_number)} "
        f"{_safe(row.street_name)} "
        f"{_safe(row.street_type)}, "
        f"{_safe(row.city)}, "
        f"{_safe(row.state)} "
        f"{_safe(row.zip_code)}"
    ).strip()


# -------------------- Main geocode_csv using bulk --------------------
def geocode_csv(
    input_file: str,
    build_address: AddressBuilder = build_address,
    output_file: str | None = None,
    max_workers: int | None = None,
) -> None:

    if output_file is None:
        output_file = input_file

    df = pd.read_csv(input_file)

    # Build all addresses first
    addresses = [build_address(row) for row in df.itertuples(index=False)]

    # Bulk geocode
    results = geocode_bulk(addresses, max_workers=max_workers)

    # Assign results back to DataFrame
    df["latitude"] = [res["latitude"] for res in results]
    df["longitude"] = [res["longitude"] for res in results]
    df["display_name"] = [res["display_name"] for res in results]

    df.to_csv(output_file, index=False)
    print(f"Geocoding complete. Output saved to: {output_file}")
