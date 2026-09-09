from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from PIL import Image
import pytest

from data_engine import process_file
from data_engine.exceptions import DataEngineError
from data_engine.ingestion import (
    detect_file_type,
    extract_metadata,
    validate_file,
)
from data_engine.geospatial.geometry import (
    extract_resolution,
    transform_to_dict,
    validate_resolution,
)
from data_engine.geospatial.crs import (
    has_crs,
    normalize_crs,
    validate_crs,
)

from data_engine.geospatial.coordinates import (
    transform_coordinate,
)
from data_engine.geospatial.bounding_box import (
    create_bounding_box,
    validate_bounding_box,
)

def test_geotiff_metadata(tmp_path: Path):
    path = tmp_path / "sample.tif"
    transform = from_origin(80.0, 13.1, 0.001, 0.001)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=100,
        height=100,
        count=3,
        dtype="uint8",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(np.zeros((3, 100, 100), dtype=np.uint8))
        dst.set_band_description(1, "B02")
        dst.set_band_description(2, "B03")
        dst.set_band_description(3, "B04")

    meta = extract_metadata(path)

    assert meta["input_kind"] == "geotiff"
    assert meta["band_count"] == 3
    assert meta["band_names"] == ["B02", "B03", "B04"]
    assert meta["geographic"]["source_crs"] == "EPSG:4326"
    assert meta["geographic"]["map_ready"] is True
    assert meta["geographic"]["wgs84_bounds"]["west"] == 80.0


def test_png_metadata(tmp_path: Path):
    path = tmp_path / "sample.png"

    Image.fromarray(
        np.zeros((20, 30, 3), dtype=np.uint8)
    ).save(path)

    meta = extract_metadata(path)

    assert meta["input_kind"] == "png"
    assert meta["width"] == 30
    assert meta["height"] == 20
    assert meta["band_count"] == 3
    assert meta["geographic"]["map_ready"] is False


def test_file_validation(tmp_path: Path):
    path = tmp_path / "sample.jpg"

    Image.fromarray(
        np.zeros((5, 5, 3), dtype=np.uint8)
    ).save(path)

    result = validate_file(path)

    assert result["valid"] is True
    assert detect_file_type(path).value == "jpeg"


# -------------------------------------------------------------------
# Controller tests
# -------------------------------------------------------------------


def test_controller_valid_optical_geotiff(tmp_path: Path):
    """A structurally valid optical GeoTIFF should be accepted."""

    path = tmp_path / "optical.tif"
    transform = from_origin(80.0, 13.1, 10.0, 10.0)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=100,
        height=100,
        count=3,
        dtype="uint16",
        crs="EPSG:32644",
        transform=transform,
    ) as dst:
        dst.write(
            np.zeros((3, 100, 100), dtype=np.uint16)
        )
        dst.set_band_description(1, "B02")
        dst.set_band_description(2, "B03")
        dst.set_band_description(3, "B04")

    result = process_file(path)

    assert result["valid"] is True
    assert result["raster"]["width"] == 100
    assert result["raster"]["height"] == 100
    assert result["raster"]["bands"] == 3
    assert result["raster"]["crs"] == "EPSG:32644"
    assert result["raster"]["modality"] is None

    assert result["band_validation"]["valid"] is True
    assert result["band_validation"]["same_dtype"] is True
    assert result["band_validation"]["same_dimensions"] is True

    assert result["spatial"]["map_ready"] is True
    assert result["acquisition"]["datetime"] is None


def test_controller_valid_sar(tmp_path: Path):
    """A SAR GeoTIFF with complete polarization metadata should be accepted."""

    path = tmp_path / "sar.tif"
    transform = from_origin(81.0, 13.6, 10.0, 10.0)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=100,
        height=100,
        count=2,
        dtype="float32",
        crs="EPSG:32644",
        transform=transform,
    ) as dst:
        dst.write(
            np.zeros((2, 100, 100), dtype=np.float32)
        )
        dst.set_band_description(1, "VV")
        dst.set_band_description(2, "VH")

    result = process_file(path)

    assert result["valid"] is True
    assert result["raster"]["modality"] == "sar"

    sar_validation = result["band_validation"]["sar_validation"]

    assert sar_validation["is_sar"] is True
    assert sar_validation["polarizations"] == ["VV", "VH"]
    assert sar_validation["polarization_metadata_complete"] is True
    assert sar_validation["duplicate_polarizations"] is False
    assert sar_validation["structurally_consistent"] is True
    assert sar_validation["valid"] is True


def test_controller_invalid_sar_missing_polarization(
    tmp_path: Path,
):
    """SAR with missing polarization metadata should be rejected."""

    path = tmp_path / "sar_incomplete.tif"
    transform = from_origin(81.0, 13.6, 10.0, 10.0)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=100,
        height=100,
        count=2,
        dtype="float32",
        crs="EPSG:32644",
        transform=transform,
    ) as dst:
        dst.write(
            np.zeros((2, 100, 100), dtype=np.float32)
        )
        dst.set_band_description(1, "VV")
        dst.set_band_description(2, "BAND_2")

    result = process_file(path)

    assert result["valid"] is False
    assert result["raster"]["modality"] == "sar"

    sar_validation = result["band_validation"]["sar_validation"]

    assert sar_validation["is_sar"] is True
    assert sar_validation["polarizations"] == ["VV"]
    assert sar_validation["polarization_metadata_complete"] is False
    assert sar_validation["valid"] is False

    assert (
        result["band_validation"]["reason"]
        == "SAR raster has incomplete polarization metadata."
    )


def test_controller_duplicate_sar_polarization(
    tmp_path: Path,
):
    """SAR with duplicate polarization labels should be rejected."""

    path = tmp_path / "sar_duplicate.tif"
    transform = from_origin(81.0, 13.6, 10.0, 10.0)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=100,
        height=100,
        count=2,
        dtype="float32",
        crs="EPSG:32644",
        transform=transform,
    ) as dst:
        dst.write(
            np.zeros((2, 100, 100), dtype=np.float32)
        )
        dst.set_band_description(1, "VV")
        dst.set_band_description(2, "VV")

    result = process_file(path)

    assert result["valid"] is False

    sar_validation = result["band_validation"]["sar_validation"]

    assert sar_validation["duplicate_polarizations"] is True
    assert sar_validation["valid"] is False


# -------------------------------------------------------------------
# File validation error tests
# -------------------------------------------------------------------


def test_controller_missing_file(tmp_path: Path):
    """A missing input file should raise a Data Engine error."""

    path = tmp_path / "does_not_exist.tif"

    with pytest.raises(DataEngineError):
        process_file(path)


def test_controller_empty_file(tmp_path: Path):
    """An empty input file should be rejected."""

    path = tmp_path / "empty.tif"
    path.touch()

    with pytest.raises(DataEngineError):
        process_file(path)


def test_controller_unsupported_file_type(tmp_path: Path):
    """An unsupported file extension should be rejected."""

    path = tmp_path / "sample.txt"
    path.write_text("not a satellite image")

    with pytest.raises(DataEngineError):
        process_file(path)

# -------------------------------------------------------------------
# CRS tests
# -------------------------------------------------------------------


def test_crs_normalization():
    """CRS strings should be normalized consistently."""

    assert normalize_crs("EPSG:32644") == "EPSG:32644"
    assert normalize_crs("epsg:4326") == "EPSG:4326"


def test_crs_missing():
    """Missing CRS should remain explicitly unavailable."""

    assert normalize_crs(None) is None
    assert has_crs(None) is False

    result = validate_crs(None)

    assert result["valid"] is False
    assert result["crs"] is None


def test_crs_validation():
    """A valid CRS should pass validation."""

    assert has_crs("EPSG:32644") is True

    result = validate_crs("EPSG:32644")

    assert result["valid"] is True
    assert result["crs"] == "EPSG:32644"
    assert result["reason"] is None

# -------------------------------------------------------------------
# Coordinate transformation tests
# -------------------------------------------------------------------


def test_coordinate_transformation_wgs84_to_utm():
    """WGS84 longitude/latitude should transform to UTM coordinates."""

    x, y = transform_coordinate(
        80.2249,
        13.0750,
        "EPSG:4326",
        "EPSG:32644",
    )

    assert isinstance(x, float)
    assert isinstance(y, float)

    # Chennai-area coordinates should transform to UTM zone 44N.
    assert 100000 < x < 900000
    assert 0 < y < 10000000


def test_coordinate_transformation_utm_to_wgs84():
    """UTM coordinates should transform to WGS84."""

    longitude, latitude = transform_coordinate(
        415970.10,
        1445558.30,
        "EPSG:32644",
        "EPSG:4326",
    )

    assert isinstance(longitude, float)
    assert isinstance(latitude, float)

    assert longitude == pytest.approx(80.2249, abs=1e-4)
    assert latitude == pytest.approx(13.0750, abs=1e-4)


def test_coordinate_transformation_round_trip():
    """Transforming WGS84 -> UTM -> WGS84 should preserve the point."""

    original_x = 80.2249
    original_y = 13.0750

    utm_x, utm_y = transform_coordinate(
        original_x,
        original_y,
        "EPSG:4326",
        "EPSG:32644",
    )

    result_x, result_y = transform_coordinate(
        utm_x,
        utm_y,
        "EPSG:32644",
        "EPSG:4326",
    )

    assert result_x == pytest.approx(original_x, abs=1e-5)
    assert result_y == pytest.approx(original_y, abs=1e-5)


def test_coordinate_transformation_invalid_crs():
    """An invalid CRS should raise a clear ValueError."""

    with pytest.raises(ValueError):
        transform_coordinate(
            80.2249,
            13.0750,
            "EPSG:4326",
            "EPSG:999999",
        )
# -------------------------------------------------------------------
# Bounding-box tests
# -------------------------------------------------------------------


def test_create_bounding_box():
    """A valid geographic bounding box should be created."""

    bounds = create_bounding_box(
        80.0,
        13.0,
        80.5,
        13.5,
    )

    assert bounds == {
        "west": 80.0,
        "south": 13.0,
        "east": 80.5,
        "north": 13.5,
    }


def test_validate_bounding_box():
    """A valid bounding box should pass validation."""

    result = validate_bounding_box(
        {
            "west": 80.0,
            "south": 13.0,
            "east": 80.5,
            "north": 13.5,
        }
    )

    assert result["valid"] is True
    assert result["bounds"]["west"] == 80.0
    assert result["bounds"]["north"] == 13.5
    assert result["reason"] is None


def test_bounding_box_missing():
    """Missing bounds should remain explicitly unavailable."""

    result = validate_bounding_box(None)

    assert result["valid"] is False
    assert result["bounds"] is None


def test_bounding_box_invalid_order():
    """West/east or south/north ordering should be validated."""

    with pytest.raises(ValueError):
        create_bounding_box(
            81.0,
            13.0,
            80.0,
            13.5,
        )

    with pytest.raises(ValueError):
        create_bounding_box(
            80.0,
            14.0,
            80.5,
            13.0,
        )


def test_bounding_box_invalid_coordinates():
    """Longitude and latitude limits should be enforced."""

    with pytest.raises(ValueError):
        create_bounding_box(
            181.0,
            13.0,
            182.0,
            13.5,
        )

    with pytest.raises(ValueError):
        create_bounding_box(
            80.0,
            91.0,
            80.5,
            92.0,
        )
# -------------------------------------------------------------------
# Resolution and affine-transform tests
# -------------------------------------------------------------------


def test_extract_resolution():
    """Raster resolution should be extracted from an affine transform."""

    transform = from_origin(
        80.0,
        13.1,
        10.0,
        10.0,
    )

    resolution = extract_resolution(transform)

    assert resolution == (10.0, 10.0)


def test_transform_to_dict():
    """Affine transform should be converted to a standard dictionary."""

    transform = from_origin(
        80.0,
        13.1,
        10.0,
        10.0,
    )

    result = transform_to_dict(transform)

    assert result["a"] == 10.0
    assert result["e"] == -10.0
    assert result["c"] == 80.0
    assert result["f"] == 13.1


def test_validate_resolution():
    """A valid raster resolution should pass validation."""

    result = validate_resolution([10.0, 10.0])

    assert result["valid"] is True
    assert result["resolution"] == [10.0, 10.0]
    assert result["reason"] is None


def test_validate_resolution_invalid():
    """Invalid raster resolutions should be rejected."""

    result = validate_resolution([0, 10])

    assert result["valid"] is False
    assert result["resolution"] is None


def test_validate_resolution_missing():
    """Missing resolution should remain explicitly unavailable."""

    result = validate_resolution(None)

    assert result["valid"] is False
    assert result["resolution"] is None

# -------------------------------------------------------------------
# Data Engine public interface / contract tests
# -------------------------------------------------------------------


def test_data_engine_public_entry_point():
    """process_file should be available from the public package interface."""

    from data_engine import process_file as public_process_file

    assert callable(public_process_file)


def test_data_engine_result_contract(tmp_path: Path):
    """process_file should return the standardized Data Engine structure."""

    path = tmp_path / "contract.tif"

    transform = from_origin(
        80.0,
        13.1,
        10.0,
        10.0,
    )

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=20,
        height=20,
        count=3,
        dtype="uint16",
        crs="EPSG:32644",
        transform=transform,
    ) as dst:
        dst.write(
            np.zeros((3, 20, 20), dtype=np.uint16)
        )

        dst.set_band_description(1, "B02")
        dst.set_band_description(2, "B03")
        dst.set_band_description(3, "B04")

    result = process_file(path)

    # Required top-level Data Engine sections.
    assert set(
        [
            "valid",
            "raster",
            "band_validation",
            "spatial",
            "acquisition",
        ]
    ).issubset(result.keys())

    # Required raster information.
    assert result["raster"]["width"] == 20
    assert result["raster"]["height"] == 20
    assert result["raster"]["bands"] == 3
    assert result["raster"]["crs"] == "EPSG:32644"

    # Required spatial information.
    assert "bounds" in result["spatial"]
    assert "centroid" in result["spatial"]
    assert "map_ready" in result["spatial"]

    # Acquisition metadata must not be invented.
    assert "datetime" in result["acquisition"]
    assert result["acquisition"]["datetime"] is None