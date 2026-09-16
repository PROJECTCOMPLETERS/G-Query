from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import box, shape


REFERENCE_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "reference"
)

OUTPUT_DIR = REFERENCE_DIR / "clipped"


AOI = {
    "west": 80.14946980509461,
    "south": 12.999552021555084,
    "east": 80.30037494242235,
    "north": 13.150459305199394,
}


def clip_geojson(
    input_path: Path,
    output_path: Path,
    aoi,
) -> None:

    print(f"Processing {input_path.name}...")

    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    aoi_geometry = box(
        aoi["west"],
        aoi["south"],
        aoi["east"],
        aoi["north"],
    )

    output_features = []

    for feature in data.get("features", []):

        geometry_data = feature.get("geometry")

        if not geometry_data:
            continue

        try:
            geometry = shape(geometry_data)
        except Exception:
            continue

        if geometry.is_empty:
            continue

        if not geometry.intersects(aoi_geometry):
            continue

        output_features.append(feature)

    output = {
        "type": "FeatureCollection",
        "features": output_features,
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(output, file)

    print(
        f"{input_path.name}: "
        f"{len(output_features)} features → "
        f"{output_path}"
    )


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    clip_geojson(
        REFERENCE_DIR / "roads.geojson",
        OUTPUT_DIR / "roads.geojson",
        AOI,
    )

    clip_geojson(
        REFERENCE_DIR / "buildings.geojson",
        OUTPUT_DIR / "buildings.geojson",
        AOI,
    )


if __name__ == "__main__":
    main()