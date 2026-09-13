"""Execution pipeline for generic Data Engine spatial preparation."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Iterable

from data_engine.geospatial.reprojection import reproject_raster
from data_engine.preprocessing.normalization import normalize_raster
from data_engine.preprocessing.registration import align_raster_to_reference
from data_engine.preprocessing.resampling import resample_raster


def prepare_raster(
    input_path: str | Path,
    output_path: str | Path,
    *,
    operations: Iterable[str],
    target_crs: str | None = None,
    target_resolution: tuple[float, float] | None = None,
    reference_path: str | Path | None = None,
) -> dict[str, Any]:
    """Execute requested generic preparation operations.

    Supported operations are ``reprojection``, ``resampling``,
    ``registration/alignment`` (also ``grid alignment``), and
    ``normalization``.

    Model-specific operations such as CROMA channel ordering, 120x120 tiling,
    model statistics, model loading, and inference are deliberately excluded.
    """
    normalized_operations = [str(op).strip().lower() for op in operations]
    allowed = {
        "reprojection",
        "resampling",
        "registration/alignment",
        "grid alignment",
        "normalization",
    }
    unknown = [op for op in normalized_operations if op not in allowed]
    if unknown:
        raise ValueError(f"Unsupported preparation operation(s): {unknown}")

    input_path = Path(input_path)
    output_path = Path(output_path)
    current_path = input_path
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="satquery_prepare_") as temp_dir:
        temp_dir = Path(temp_dir)

        for index, operation in enumerate(normalized_operations):
            is_last = index == len(normalized_operations) - 1
            step_output = output_path if is_last else temp_dir / f"step_{index}.tif"

            if operation == "reprojection":
                if target_crs is None:
                    raise ValueError("target_crs is required for reprojection.")
                result = reproject_raster(
                    current_path,
                    step_output,
                    target_crs=target_crs,
                    target_resolution=(
                        target_resolution
                        if "resampling" not in normalized_operations[index + 1 :]
                        else None
                    ),
                )
            elif operation == "resampling":
                if target_resolution is None:
                    raise ValueError("target_resolution is required for resampling.")
                result = resample_raster(
                    current_path,
                    step_output,
                    target_resolution=target_resolution,
                )
            elif operation in {"registration/alignment", "grid alignment"}:
                if reference_path is None:
                    raise ValueError(
                        "reference_path is required for registration/alignment."
                    )
                result = align_raster_to_reference(
                    current_path,
                    reference_path,
                    step_output,
                )
            else:
                result = normalize_raster(current_path, step_output)

            results.append({"operation": operation, **result})
            current_path = step_output

        if not normalized_operations:
            raise ValueError("At least one preparation operation is required.")

        return {
            "path": str(current_path),
            "operations": normalized_operations,
            "steps": results,
        }
