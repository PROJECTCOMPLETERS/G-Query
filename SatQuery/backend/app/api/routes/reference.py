from fastapi import APIRouter, Depends

from app.api.dependencies import get_reference_layer_service
from app.schemas.common.error import ErrorResponse
from app.services.reference_layer_service import ReferenceLayerService


router = APIRouter(
    prefix="/datasets",
    tags=["reference-layers"],
)


@router.get(
    "/{dataset_id}/observations/{observation_id}/reference-layers",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Query reference layers for an observation",
    description=(
        "Query registered reference geospatial layers using the "
        "observation's WGS84 AOI and return intersecting features "
        "as WGS84 GeoJSON."
    ),
)
def get_reference_layers(
    dataset_id: str,
    observation_id: str,
    reference_layer_service: ReferenceLayerService = Depends(
        get_reference_layer_service
    ),
):
    return reference_layer_service.query_reference_layers(
        dataset_id=dataset_id,
        observation_id=observation_id,
    )