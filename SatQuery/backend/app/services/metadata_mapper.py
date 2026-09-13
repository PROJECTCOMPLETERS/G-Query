from app.schemas.common.acquisition import Acquisition
from app.schemas.common.file import File
from app.schemas.common.observation import Observation
from app.schemas.common.raster import Raster, RasterBand
from app.schemas.common.source import Source
from app.schemas.common.spatial import BoundingBox, Spatial


def metadata_to_observation(
    metadata: dict,
    file_id: str,
    filename: str,
    media_type: str | None,
    size_bytes: int,
) -> Observation:
    source_data = metadata["source"]
    geographic = metadata["geographic"]

    source = Source(
    kind=source_data["kind"],
    locator=file_id,
    display_name=filename,
    media_type=media_type,
)

    acquisition = Acquisition(
        datetime=None,
    )

    native_bounds = geographic.get("native_bounds")
    wgs84_bounds = geographic.get("wgs84_bounds")

    spatial = Spatial(
        crs_status=geographic["crs_status"],
        source_crs=geographic.get("source_crs"),
        native_bounds=(
            BoundingBox(**native_bounds)
            if native_bounds is not None
            else None
        ),
        wgs84_bounds=(
            BoundingBox(**wgs84_bounds)
            if wgs84_bounds is not None
            else None
        ),
        footprint_geojson=geographic.get("footprint_geojson"),
        centroid_wgs84=geographic.get("centroid_wgs84"),
        map_ready=geographic["map_ready"],
        map_unavailable_reason=geographic.get(
            "map_unavailable_reason"
        ),
        transform=metadata.get("transform"),
    )

    raster = Raster(
        width=metadata["width"],
        height=metadata["height"],
        band_count=metadata["band_count"],
        bands=[
            RasterBand(**band)
            for band in metadata["bands"]
        ],
        dtypes=metadata["dtypes"],
        band_names=metadata["band_names"],
        nodata=metadata.get("nodata"),
        resolution=metadata.get("resolution"),
    )

    file = File(
        file_id=file_id,
        filename=filename,
        media_type=media_type,
        input_kind=metadata["input_kind"],
        driver=metadata.get("driver"),
        size_bytes=size_bytes,
        tags=metadata.get("tags", {}),
    )

    return Observation(
        observation_id=file_id,
        source=source,
        acquisition=acquisition,
        spatial=spatial,
        raster=raster,
        file=file,
    )