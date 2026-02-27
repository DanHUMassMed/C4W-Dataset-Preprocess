from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import Protocol, TypedDict

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry

# Global session (shared across threads)
_session = None


def get_session():
    global _session

    if _session is None:
        session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(
            max_retries=retries,
            pool_connections=50,
            pool_maxsize=50,
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        _session = session

    return _session


@lru_cache(maxsize=100_000)
def geocode(address: str, base_url="http://localhost:8080/search") -> dict:
    if not address.strip():
        return {"latitude": None, "longitude": None, "display_name": None}

    # Only look for addresses in Worcester, MA
    min_lon, min_lat, max_lon, max_lat = -71.884043, 42.210053, -71.731237, 42.341187

    params = {
        "q": address.strip(),
        "format": "json",
        "limit": 1,
        # Nominatim bounding box (lon1, lat1, lon2, lat2)
        "viewbox": f"{min_lon},{max_lat},{max_lon},{min_lat}",  # note: top-left, bottom-right
        "bounded": 1,  # restrict results strictly to the viewbox
    }

    headers = {
        "User-Agent": "local-geocoder/1.0",
    }

    session = get_session()

    try:
        r = session.get(
            base_url,
            params=params,
            headers=headers,
            timeout=(3, 15),  # connect, read
        )

        r.raise_for_status()

        data = r.json()

        if not data:
            return {"latitude": None, "longitude": None, "display_name": None}

        result = data[0]

        return {
            "latitude": result.get("lat"),
            "longitude": result.get("lon"),
            "display_name": result.get("display_name"),
        }

    except Exception as e:
        print(f"Geocode failed: {address} -> {e}")

        return {
            "latitude": None,
            "longitude": None,
            "display_name": None,
        }


class GeocodeResult(TypedDict):
    latitude: float | None
    longitude: float | None
    display_name: str | None


# -------------------- Bulk geocoder --------------------
def geocode_bulk(
    addresses: list[str],
    max_workers: int | None = None,
) -> list[GeocodeResult]:
    if max_workers is None:
        max_workers = 1  # TODO: Investigate concurrency issue

    results: list[GeocodeResult] = [
        {
            "latitude": None,
            "longitude": None,
            "display_name": None,
        }
        for _ in addresses
    ]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(geocode, addr): i for i, addr in enumerate(addresses)
        }

        for future in tqdm(
            as_completed(future_map),
            total=len(future_map),
            desc="Geocoding (bulk)",
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


def _safe_street_type(val) -> str:
    """Convert NaN/None to empty string, else to stripped string."""
    if pd.isna(val):
        return ""
    return str(val).strip()


def build_address(row) -> str:
    parts = [
        _safe(row.street_number),
        _safe(row.street_name),
        _safe(row.street_type),
        _safe(row.city),
        _safe(row.state),
        _safe(row.zip_code),
    ]
    return " ".join(p for p in parts if p)


# -------------------- Main geocode_csv using bulk --------------------
def geocode_csv(
    input_file: str,
    build_address: AddressBuilder = build_address,
    output_file: str | None = None,
    max_workers: int | None = None,
) -> None:

    if output_file is None:
        output_file = input_file

    df = pd.read_csv(
        input_file,
        dtype={"street_number": str, "street_range_to": str, "zip_code": str},
    )

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
