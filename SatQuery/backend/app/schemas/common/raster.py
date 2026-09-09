from pydantic import BaseModel


class RasterBand(BaseModel):
    index: int
    name: str
    dtype: str
    width: int
    height: int
    nodata: float | None = None


class Raster(BaseModel):
    width: int
    height: int
    band_count: int
    bands: list[RasterBand]
    dtypes: list[str]
    band_names: list[str]
    nodata: float | None = None
    resolution: list[float] | None = None