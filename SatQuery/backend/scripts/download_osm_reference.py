from pathlib import Path

from data_engine.reference.osm.downloader import download_layer


AOI = {
    "west": 80.14946980509461,
    "south": 12.999552021555084,
    "east": 80.30037494242235,
    "north": 13.150459305199394,
}


BASE_DIR = Path(__file__).resolve().parents[1]

REFERENCE_DIR = BASE_DIR / "data" / "reference"


def bbox() -> str:
    return (
        f"{AOI['south']},"
        f"{AOI['west']},"
        f"{AOI['north']},"
        f"{AOI['east']}"
    )


def main():

    bounds = bbox()

    # -------------------------
    # ROADS
    # -------------------------

    roads_query = f"""
    [out:json][timeout:120];

    way["highway"]({bounds});

    out geom;
    """

    download_layer(
        query=roads_query,
        layer_type="roads",
        output_path=REFERENCE_DIR / "roads.geojson",
    )

    # -------------------------
    # BUILDINGS
    # -------------------------

    buildings_query = f"""
    [out:json][timeout:120];

    way["building"]({bounds});

    out geom;
    """

    download_layer(
        query=buildings_query,
        layer_type="buildings",
        output_path=REFERENCE_DIR / "buildings.geojson",
    )

    # -------------------------
    # WATER
    # -------------------------

    water_query = f"""
    [out:json][timeout:120];

    (
        way["natural"="water"]({bounds});
        way["waterway"]({bounds});
    );

    out geom;
    """

    download_layer(
        query=water_query,
        layer_type="water",
        output_path=REFERENCE_DIR / "water.geojson",
    )


if __name__ == "__main__":
    main()