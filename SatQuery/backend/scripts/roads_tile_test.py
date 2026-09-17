from pathlib import Path

from data_engine.reference.tile.generator import (
    generate_tile,
)


ROOT = Path(__file__).resolve().parents[1]

REFERENCE_DIR = (
    ROOT
    / "data"
    / "reference"
)


def generate_test_layer(
    layer_name: str,
    z: int,
    x: int,
    y: int,
):
    source_file = (
        REFERENCE_DIR
        / f"{layer_name}.geojson"
    )

    output_file = (
        REFERENCE_DIR
        / f"{layer_name}_test.pbf"
    )

    print(
        f"Generating {layer_name} tile "
        f"z={z}, x={x}, y={y}"
    )

    tile = generate_tile(
        source_path=str(source_file),
        layer_name=layer_name,
        z=z,
        x=x,
        y=y,
    )

    output_file.write_bytes(tile)

    print(
        f"Tile generated: {output_file}"
    )

    print(
        f"Size: {len(tile):,} bytes"
    )


def main():
    z = 15
    x = 23686
    y = 15183

    generate_test_layer(
        layer_name="roads",
        z=z,
        x=x,
        y=y,
    )

    generate_test_layer(
        layer_name="buildings",
        z=z,
        x=x,
        y=y,
    )


if __name__ == "__main__":
    main()