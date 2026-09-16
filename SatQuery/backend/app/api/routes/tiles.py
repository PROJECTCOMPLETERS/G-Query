from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.config.reference_layers import (
    get_reference_layer_registry,
)

from data_engine.reference.tile.generator import (
    generate_tile,
)


router = APIRouter(
    prefix="/tiles",
    tags=["map-tiles"],
)


SUPPORTED_TILE_LAYERS = {
    "roads",
    "buildings",
}


@router.get(
    "/{layer_id}/{z}/{x}/{y}.pbf"
)
def get_tile(
    layer_id: str,
    z: int,
    x: int,
    y: int,
):
    """
    Return a Mapbox Vector Tile for a reference layer.

    Example:
        /api/v1/tiles/roads/15/23686/15183.pbf

        /api/v1/tiles/buildings/15/23686/15183.pbf
    """

    if layer_id not in SUPPORTED_TILE_LAYERS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unsupported tile layer: "
                f"{layer_id}"
            ),
        )

    try:
        registry = (
            get_reference_layer_registry()
        )

        layer = next(
            (
                item
                for item in registry
                if item.layer_id == layer_id
            ),
            None,
        )

        if layer is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Reference layer not found: "
                    f"{layer_id}"
                ),
            )

        tile = generate_tile(
            source_path=str(
                layer.source_path
            ),
            layer_name=layer_id,
            z=z,
            x=x,
            y=y,
        )

        return Response(
            content=tile,
            media_type=(
                "application/vnd.mapbox-vector-tile"
            ),
        )

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc