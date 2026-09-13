"""Determine task-specific preprocessing requirements."""

from __future__ import annotations

from typing import Any


SPATIAL_PREPARATION_TASKS = {
    "image_comparison",
    "change_analysis",
    "optical_optical_comparison",
    "sar_sar_comparison",
    "optical_sar_comparison",
}


def determine_preprocessing_requirements(
    task: str,
    *,
    spatial_compatibility: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Determine task-specific preprocessing requirements.

    This function describes preprocessing that may be required before
    model execution. It does not modify raster data.

    Spatial preprocessing is considered only for tasks that require
    spatial compatibility. Model-specific preprocessing is outside
    this interface.

    Args:
        task: Task identifier from the Task Engine.
        spatial_compatibility: Result returned by the spatial
            compatibility checker.

    Returns:
        Structured preprocessing requirements.
    """

    normalized_task = str(task).strip().lower()

    spatial_compatibility = spatial_compatibility or {}

    if normalized_task not in SPATIAL_PREPARATION_TASKS:
        return {
            "task": normalized_task,
            "preprocessing_required": False,
            "required_operations": [],
            "reasons": [],
        }

    if not spatial_compatibility:
        return {
            "task": normalized_task,
            "preprocessing_required": False,
            "required_operations": [],
            "reasons": [
                "Spatial compatibility has not been evaluated for this task."
            ],
        }

    operations = list(
        dict.fromkeys(
            spatial_compatibility.get("preprocessing", [])
        )
    )

    reasons = list(
        spatial_compatibility.get("reasons", [])
    )

    return {
        "task": normalized_task,
        "preprocessing_required": bool(operations),
        "required_operations": operations,
        "reasons": reasons,
    }