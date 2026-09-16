from __future__ import annotations

from typing import Any


def osm_to_geojson(
    osm_response: dict[str, Any],
    layer_type: str,
) -> dict[str, Any]:

    features = []

    for element in osm_response.get("elements", []):

        element_type = element.get("type")
        element_id = element.get("id")

        geometry = element.get("geometry")

        if not geometry:
            continue

        coordinates = [
            [point["lon"], point["lat"]]
            for point in geometry
            if "lon" in point and "lat" in point
        ]

        if len(coordinates) < 2:
            continue

        tags = element.get("tags", {})

        # Buildings and closed water features are polygons.
        if (
            layer_type in {"buildings", "water"}
            and len(coordinates) >= 4
            and coordinates[0] == coordinates[-1]
        ):
            geometry_type = "Polygon"
            geometry_coordinates = [coordinates]

        else:
            geometry_type = "LineString"
            geometry_coordinates = coordinates

        feature = {
            "type": "Feature",
            "id": f"osm-{element_type}-{element_id}",
            "geometry": {
                "type": geometry_type,
                "coordinates": geometry_coordinates,
            },
            "properties": {
                **tags,
                "osm_id": element_id,
                "osm_type": element_type,
            },
        }

        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
    }