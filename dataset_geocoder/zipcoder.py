# zipcoder.py
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# Path to your MA ZCTA shapefile relative to this script
SCRIPT_DIR = Path(__file__).parent
MA_ZCTA_SHP = SCRIPT_DIR / "../data/external/tl_2025_ma_zcta520/tl_2025_ma_zcta520.shp"

# Load ZCTA shapefile once
print(f"Loading MA ZCTA shapefile from: {MA_ZCTA_SHP.resolve()}")
zcta_gdf = gpd.read_file(MA_ZCTA_SHP)

# Ensure shapefile is in WGS84
if not zcta_gdf.crs.is_geographic:
    zcta_gdf = zcta_gdf.to_crs(epsg=4326)
print("Shapefile loaded.")


def add_zcta_zip(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'zcta_zip' column to df based on latitude and longitude.
    Expects df to have 'latitude' and 'longitude' columns.
    """
    # Create points GeoDataFrame
    points = gpd.GeoDataFrame(
        df,
        geometry=[
            Point(lon, lat)
            for lon, lat in zip(df["longitude"], df["latitude"], strict=True)
        ],
        crs="EPSG:4326",
    )

    # Reproject ZCTA shapefile to match points CRS
    zcta_gdf_proj = zcta_gdf.to_crs(points.crs)

    # Spatial join: points inside ZCTAs
    joined = gpd.sjoin(points, zcta_gdf_proj, how="left", predicate="within")

    # Use 'ZCTA5CE20' as the ZIP field
    df["zcta_zip"] = joined["ZCTA5CE20"]
    return df


def zipcode_csv(
    input_file: str,
    output_file: str | None = None,
) -> None:
    """
    Reads CSV with 'latitude' and 'longitude' columns and adds 'zcta_zip' column.
    """
    if output_file is None:
        output_file = input_file

    df = pd.read_csv(
        input_file,
        dtype={"street_number": str, "street_range_to": str, "zip_code": str},
    )

    df = add_zcta_zip(df)
    df.to_csv(output_file, index=False)
    print(f"ZIP assignment complete. Output saved to: {output_file}")


# -------------------- Example usage --------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Add ZCTA ZIP codes to CSV with lat/lon."
    )
    parser.add_argument(
        "input_file", help="Input CSV file with 'latitude' and 'longitude' columns"
    )
    parser.add_argument(
        "-o", "--output_file", help="Output CSV file (default overwrites input)"
    )
    args = parser.parse_args()

    zipcode_csv(args.input_file, args.output_file)
