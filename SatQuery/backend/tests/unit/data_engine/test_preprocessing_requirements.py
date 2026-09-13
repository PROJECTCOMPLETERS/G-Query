"""Tests for task-specific preprocessing requirements."""

from data_engine.preprocessing.requirements import (
    determine_preprocessing_requirements,
)


def test_no_spatial_preprocessing_is_required_for_compatible_data():
    result = determine_preprocessing_requirements(
        "change_analysis",
        spatial_compatibility={
            "compatible": True,
            "preprocessing_required": False,
            "preprocessing": [],
            "reasons": [],
        },
    )

    assert result["task"] == "change_analysis"
    assert result["preprocessing_required"] is False
    assert result["required_operations"] == []
    assert result["reasons"] == []


def test_spatial_preprocessing_requirements_are_propagated():
    result = determine_preprocessing_requirements(
        "change_analysis",
        spatial_compatibility={
            "compatible": False,
            "preprocessing_required": True,
            "preprocessing": [
                "reprojection",
                "resampling",
                "registration/alignment",
            ],
            "reasons": [
                "CRS mismatch.",
                "Resolution mismatch.",
                "Raster grids are not aligned.",
            ],
        },
    )

    assert result["preprocessing_required"] is True
    assert result["required_operations"] == [
        "reprojection",
        "resampling",
        "registration/alignment",
    ]
    assert result["reasons"] == [
        "CRS mismatch.",
        "Resolution mismatch.",
        "Raster grids are not aligned.",
    ]


def test_duplicate_preprocessing_operations_are_removed():
    result = determine_preprocessing_requirements(
        "image_comparison",
        spatial_compatibility={
            "preprocessing": [
                "resampling",
                "resampling",
                "reprojection",
            ],
            "reasons": [],
        },
    )

    assert result["required_operations"] == [
        "resampling",
        "reprojection",
    ]


def test_missing_spatial_compatibility_is_explained():
    result = determine_preprocessing_requirements(
        "change_analysis",
    )

    assert result["preprocessing_required"] is False
    assert result["required_operations"] == []
    assert (
        "Spatial compatibility has not been evaluated for this task."
        in result["reasons"]
    )

def test_non_spatial_task_does_not_require_spatial_preprocessing():
    """Optional spatial compatibility should not create task requirements."""

    result = determine_preprocessing_requirements(
        "object_counting",
        spatial_compatibility={
            "compatible": False,
            "preprocessing_required": True,
            "preprocessing": ["reprojection"],
            "reasons": ["CRS mismatch."],
        },
    )

    assert result["preprocessing_required"] is False
    assert result["required_operations"] == []
    assert result["reasons"] == []

def test_image_comparison_uses_spatial_preprocessing_requirements():
    """Image comparison should use spatial preprocessing requirements."""

    result = determine_preprocessing_requirements(
        "image_comparison",
        spatial_compatibility={
            "compatible": False,
            "preprocessing_required": True,
            "preprocessing": ["resampling"],
            "reasons": ["Resolution mismatch."],
        },
    )

    assert result["preprocessing_required"] is True
    assert result["required_operations"] == ["resampling"]
    assert result["reasons"] == ["Resolution mismatch."]