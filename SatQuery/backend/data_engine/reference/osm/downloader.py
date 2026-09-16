from __future__ import annotations

import json
from pathlib import Path

from data_engine.reference.osm.client import query_overpass
from data_engine.reference.osm.converter import osm_to_geojson


def download_layer(
    query: str,
    layer_type: str,
    output_path: str | Path,
) -> None:

    print(f"Downloading {layer_type}...")

    osm_data = query_overpass(query)

    geojson = osm_to_geojson(
        osm_data,
        layer_type,
    )

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            geojson,
            file,
            indent=2,
        )

    print(
        f"{layer_type}: "
        f"{len(geojson['features'])} features saved "
        f"to {output_path}"
    )