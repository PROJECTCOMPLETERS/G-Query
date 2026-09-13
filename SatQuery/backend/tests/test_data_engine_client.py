from io import BytesIO

from app.schemas.data_engine import DataReadiness, DataRequirements
from app.schemas.query import ObservationInput
from app.services.data_engine_client import RealDataEngineClient


class FakeStoredFile(BytesIO):
    filename = "sample.tif"


class FakeFileStorage:
    def __init__(self):
        self.files = {
            "file_001": FakeStoredFile(b"fake-raster-data")
        }

    def get(self, file_id: str):
        return self.files.get(file_id)


def test_data_engine_client_returns_data_readiness(monkeypatch):
    processed_observation = {
        "valid": True,
        "raster": {
            "modality": "optical",
        },
        "spatial": {
            "bounds": [80.0, 13.0, 80.1, 13.1],
        },
        "acquisition": {
            "datetime": "2026-01-01T00:00:00",
        },
    }

    def fake_process_file(path):
        assert path.exists()
        return processed_observation

    def fake_evaluate_data_readiness(
        *,
        request_id,
        task,
        data_requirements,
        observations,
    ):
        assert request_id == "req_500"
        assert task == "object_counting"
        assert "obs_001" in observations

        return {
            "schema_version": "1.0",
            "request_id": request_id,
            "ready": True,
            "available_observations": ["obs_001"],
            "missing_information": [],
            "reason": None,
        }

    monkeypatch.setattr(
        "app.services.data_engine_client.process_file",
        fake_process_file,
    )

    monkeypatch.setattr(
        "app.services.data_engine_client.evaluate_data_readiness",
        fake_evaluate_data_readiness,
    )

    storage = FakeFileStorage()
    client = RealDataEngineClient(storage)

    requirements = DataRequirements(
        request_id="req_500",
        task="object_counting",
    )

    observations = [
        ObservationInput(
            input_id="obs_001",
            file_id="file_001",
            type="image",
        )
    ]

    readiness = client.check_readiness(
        request_id="req_500",
        task="object_counting",
        requirements=requirements,
        observations=observations,
    )

    assert isinstance(readiness, DataReadiness)
    assert readiness.ready is True
    assert readiness.available_observations == ["obs_001"]