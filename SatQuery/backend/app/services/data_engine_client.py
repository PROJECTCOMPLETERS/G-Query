import os
import tempfile
from pathlib import Path
from typing import Any

from app.core.exceptions import SatQueryException
from app.schemas.data_engine import DataReadiness, DataRequirements
from app.schemas.query import ObservationInput
from app.storage.interfaces.file_storage import FileStorage

from data_engine.controller import process_file
from data_engine.readiness.evaluator import evaluate_data_readiness


class RealDataEngineClient:
    """
    Adapter between SatQuery orchestration and Rubin's Data Engine.

    This class does not implement Data Engine logic.
    It only prepares stored files, calls Rubin's public interfaces,
    and converts the result into the canonical backend contract.
    """

    def __init__(self, file_storage: FileStorage):
        self.file_storage = file_storage

    def check_readiness(
        self,
        request_id: str,
        task: str,
        requirements: DataRequirements,
        observations: list[ObservationInput],
    ) -> DataReadiness:
        processed_observations: dict[str, dict[str, Any]] = {}

        for observation in observations:
            if not observation.file_id:
                raise SatQueryException(
                    code="DATA_MISSING",
                    message=(
                        f"No file_id provided for observation "
                        f"{observation.input_id}."
                    ),
                )

            stored_file = self.file_storage.get(observation.file_id)

            if stored_file is None:
                raise SatQueryException(
                    code="DATA_MISSING",
                    message=(
                        f"Stored file not found for observation "
                        f"{observation.input_id}."
                    ),
                )

            suffix = Path(
                getattr(stored_file, "filename", "")
            ).suffix

            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    suffix=suffix,
                    delete=False,
                ) as temp_file:
                    temp_path = Path(temp_file.name)

                    while True:
                        chunk = stored_file.read(1024 * 1024)

                        if not chunk:
                            break

                        temp_file.write(chunk)

                processed_observations[observation.input_id] = (
                    process_file(temp_path)
                )

            finally:
                if temp_path is not None and temp_path.exists():
                    os.remove(temp_path)

        readiness = evaluate_data_readiness(
            request_id=request_id,
            task=task,
            data_requirements=requirements.model_dump(),
            observations=processed_observations,
        )

        return DataReadiness.model_validate(readiness)