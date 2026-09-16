import math


WEST = 80.14946980509461
SOUTH = 12.999552021555084
EAST = 80.30037494242235
NORTH = 13.150459305199394


def lon_to_tile_x(lon: float, zoom: int) -> int:
    n = 2 ** zoom
    return int(
        (lon + 180.0) / 360.0 * n
    )


def lat_to_tile_y(lat: float, zoom: int) -> int:
    lat_rad = math.radians(lat)
    n = 2 ** zoom

    return int(
        (
            1
            - math.asinh(
                math.tan(lat_rad)
            ) / math.pi
        )
        / 2
        * n
    )


def main():

    for zoom in [12, 13, 14, 15, 16]:

        west_x = lon_to_tile_x(
            WEST,
            zoom,
        )

        east_x = lon_to_tile_x(
            EAST,
            zoom,
        )

        north_y = lat_to_tile_y(
            NORTH,
            zoom,
        )

        south_y = lat_to_tile_y(
            SOUTH,
            zoom,
        )

        print(
            f"\nZoom {zoom}"
        )

        print(
            f"X: {west_x} → {east_x}"
        )

        print(
            f"Y: {north_y} → {south_y}"
        )


if __name__ == "__main__":
    main()