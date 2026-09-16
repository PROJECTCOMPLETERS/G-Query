from pathlib import Path

from data_engine import (
    ReferenceLayer,
    ReferenceLayerRegistry,
)


REFERENCE_DATA_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "reference"
)


def get_reference_layer_registry(
) -> ReferenceLayerRegistry:

    registry = ReferenceLayerRegistry()

    registry.register(
        ReferenceLayer(
            layer_id="roads",
            name="Roads",
            source_path=(
                REFERENCE_DATA_DIR
                / "roads.geojson"
            ),
            source_crs="EPSG:4326",
            category="transportation",
        )
    )

    registry.register(
        ReferenceLayer(
            layer_id="buildings",
            name="Buildings",
            source_path=(
                REFERENCE_DATA_DIR
                / "buildings.geojson"
            ),
            source_crs="EPSG:4326",
            category="building",
        )
    )

    registry.register(
        ReferenceLayer(
            layer_id="water",
            name="Water",
            source_path=(
                REFERENCE_DATA_DIR
                / "water.geojson"
            ),
            source_crs="EPSG:4326",
            category="water",
        )
    )

    return registry