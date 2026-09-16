from app.services.dataset_service import DatasetService

from data_engine import (
    ReferenceLayerRegistry,
    query_reference_features,
)


class ReferenceLayerService:
    """
    Service responsible for querying reference geospatial layers
    against a satellite observation's AOI.
    """

    def __init__(
        self,
        dataset_service: DatasetService,
        reference_layer_registry: ReferenceLayerRegistry,
    ):
        self.dataset_service = dataset_service
        self.reference_layer_registry = reference_layer_registry

    def query_reference_layers(
        self,
        dataset_id: str,
        observation_id: str,
    ):
        # Get dataset through the existing DatasetService.
        dataset = self.dataset_service.get_dataset(dataset_id)

        # Find the requested observation inside the dataset.
        observation = next(
            (
                obs
                for obs in dataset.observations
                if obs.observation_id == observation_id
            ),
            None,
        )

        if observation is None:
            return {
                "error": "OBSERVATION_NOT_FOUND",
                "message": "Observation was not found in the dataset.",
            }

        # Convert Pydantic model to dictionary.
        observation_data = observation.model_dump()

        # Query reference layers using the observation AOI.
        return query_reference_features(
            observation=observation_data,
            layers=self.reference_layer_registry,
        )