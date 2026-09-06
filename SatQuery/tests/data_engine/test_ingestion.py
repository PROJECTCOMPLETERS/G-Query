from pathlib import Path
import numpy as np
import rasterio
from rasterio.transform import from_origin
from PIL import Image
from data_engine.ingestion import detect_file_type, extract_metadata, validate_file


def test_geotiff_metadata(tmp_path: Path):
    path = tmp_path / "sample.tif"
    transform = from_origin(80.0, 13.1, 0.001, 0.001)
    with rasterio.open(path, "w", driver="GTiff", width=100, height=100, count=3, dtype="uint8", crs="EPSG:4326", transform=transform) as dst:
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
    Image.fromarray(np.zeros((20, 30, 3), dtype=np.uint8)).save(path)
    meta = extract_metadata(path)
    assert meta["input_kind"] == "png"
    assert meta["width"] == 30 and meta["height"] == 20
    assert meta["band_count"] == 3
    assert meta["geographic"]["map_ready"] is False


def test_file_validation(tmp_path: Path):
    path = tmp_path / "sample.jpg"
    Image.fromarray(np.zeros((5, 5, 3), dtype=np.uint8)).save(path)
    result = validate_file(path)
    assert result["valid"] is True
    assert detect_file_type(path).value == "jpeg"
