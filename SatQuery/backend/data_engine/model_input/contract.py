"""Contract for handing validated/prepared observations to Model Engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"


def build_model_input(
    *,
    observation_id: str,
    observation: dict[str, Any],
    prepared_path: str | Path | None = None,
    tensor: Any = None,
    preprocessing: list[str] | None = None,
) -> dict[str, Any]:
    """Build the generic Data Engine -> Model Engine input contract.

    The Data Engine supplies validated/prepared data plus stable metadata.
    ``tensor`` is optional because tensor construction is model-specific and
    is finalized by the Phase 3 model implementation. A prepared raster path
    is the generic, model-agnostic handoff representation.

    At least one of ``prepared_path`` or ``tensor`` must be supplied.
    """
    if not str(observation_id).strip():
        raise ValueError("observation_id must be provided.")

    if observation.get("valid") is not True:
        raise ValueError("Only valid Data Engine observations can be handed off.")

    if prepared_path is None and tensor is None:
        raise ValueError("Provide prepared_path or tensor for model handoff.")

    raster = observation.get("raster", {})
    spatial = observation.get("spatial", {})
    acquisition = observation.get("acquisition", {})

    return {
        "schema_version": SCHEMA_VERSION,
        "observation_id": observation_id,
        "input": {
            "type": "prepared_raster" if prepared_path is not None else "tensor",
            "path": str(Path(prepared_path)) if prepared_path is not None else None,
            "tensor": tensor,
        },
        "metadata": {
            "raster": raster,
            "spatial": spatial,
            "acquisition": acquisition,
            "band_validation": observation.get("band_validation", {}),
        },
        "preprocessing": list(preprocessing or []),
    }
