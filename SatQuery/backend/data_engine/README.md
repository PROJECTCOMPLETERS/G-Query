# SatQuery Data Engine — Phase 1

Initial implementation of Rubin's P1-001 through P1-004:

- supported file detection: GeoTIFF, JPG, PNG
- local file validation
- GeoTIFF loading with Rasterio
- JPG/PNG loading with Pillow
- JSON-serializable metadata extraction
- CRS and WGS84 bounds for GeoTIFFs
- explicit `map_ready` status when georeferencing is unavailable

Dependencies: `rasterio`, `Pillow`, `numpy`.

Run the inspection script from the repository root:

```powershell
python scripts/inspect_geotiff.py path\to\image.tif
```

Run tests:

```powershell
pytest tests/data_engine/test_ingestion.py
```
