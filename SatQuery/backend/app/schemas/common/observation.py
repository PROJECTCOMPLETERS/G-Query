from pydantic import BaseModel

from app.schemas.common.acquisition import Acquisition
from app.schemas.common.file import File
from app.schemas.common.raster import Raster
from app.schemas.common.source import Source
from app.schemas.common.spatial import Spatial


class Observation(BaseModel):
    observation_id: str
    source: Source
    acquisition: Acquisition
    spatial: Spatial
    raster: Raster
    file: File