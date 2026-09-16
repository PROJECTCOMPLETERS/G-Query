from __future__ import annotations

from fastapi import HTTPException

from app.config.reference_layers import (
    get_reference_layer_registry,
)

from data_engine.reference.tile.generator import (
    generate_tile,
)


class TileService:

    def __init__(self):
        self.registry = (
            get_reference_layer_registry()
        )

    def get_tile(
        self,
        layer_id: str,
        z: int,
        x: int,
        y: int,
    ) -> bytes:

        if layer_id not in {
            "roads",
            "buildings",
        }:
            raise HTTPException(
                status_code=404,
                detail="Tile layer not found",
            )

        layer = next(
            (
                item
                for item in self.registry
                if item.layer_id == layer_id
            ),
            None,
        )

        if layer is None:
            raise HTTPException(
                status_code=404,
                detail="Reference layer not found",
            )

        return generate_tile(
            source_path=str(
                layer.source_path
            ),
            layer_name=layer_id,
            z=z,
            x=x,
            y=y,
        )