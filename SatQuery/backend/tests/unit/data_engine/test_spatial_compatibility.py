from data_engine.compatibility.spatial import (
    check_spatial_compatibility,
)


def make_observation(
    *,
    crs="EPSG:32644",
    resolution=(10.0, 10.0),
    bounds=None,
    transform=None,
):
    if bounds is None:
        bounds = {
            "west": 80.0,
            "south": 13.0,
            "east": 80.1,
            "north": 13.1,
        }

    if transform is None:
        transform = {
            "a": 10.0,
            "b": 0.0,
            "c": 500000.0,
            "d": 0.0,
            "e": -10.0,
            "f": 1500000.0,
        }

    return {
        "raster": {
            "crs": crs,
            "resolution": list(resolution),
            "transform": transform,
        },
        "spatial": {
            "bounds": bounds,
        },
    }


def test_identical_observations_are_compatible():
    first = make_observation()
    second = make_observation()

    result = check_spatial_compatibility(first, second)

    assert result["compatible"] is True
    assert result["checks"] == {
        "crs": True,
        "resolution": True,
        "bounds": True,
        "alignment": True,
    }
    assert result["reasons"] == []


def test_crs_mismatch_requires_reprojection():
    first = make_observation(crs="EPSG:32644")
    second = make_observation(crs="EPSG:4326")

    result = check_spatial_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["crs"] is False
    assert "CRS mismatch." in result["reasons"]
    assert "reprojection" in result["preprocessing"]


def test_resolution_mismatch_requires_resampling():
    first = make_observation(resolution=(10.0, 10.0))
    second = make_observation(resolution=(20.0, 20.0))

    result = check_spatial_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["resolution"] is False
    assert "Resolution mismatch." in result["reasons"]
    assert "resampling" in result["preprocessing"]


def test_non_overlapping_bounds_are_incompatible():
    first = make_observation()

    second = make_observation(
        bounds={
            "west": 81.0,
            "south": 14.0,
            "east": 81.1,
            "north": 14.1,
        }
    )

    result = check_spatial_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["bounds"] is False
    assert (
        "Raster observations do not overlap spatially."
        in result["reasons"]
    )


def test_shifted_grid_is_not_aligned():
    first = make_observation()

    second = make_observation(
        transform={
            "a": 10.0,
            "b": 0.0,
            "c": 500005.0,
            "d": 0.0,
            "e": -10.0,
            "f": 1500000.0,
        }
    )

    result = check_spatial_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["alignment"] is False
    assert "Raster grids are not aligned." in result["reasons"]
    assert "registration/alignment" in result["preprocessing"]


def test_missing_crs_is_not_compatible():
    first = make_observation(crs=None)
    second = make_observation()

    result = check_spatial_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["crs"] is False
    assert "CRS information is missing." in result["reasons"]


def test_missing_transform_cannot_confirm_alignment():
    first = make_observation()
    second = make_observation()

    first["raster"]["transform"] = None
    second["raster"]["transform"] = None

    result = check_spatial_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["alignment"] is False
    assert (
        "Affine transform information is missing."
        in result["reasons"]
    )