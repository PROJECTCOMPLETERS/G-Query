from data_engine.readiness import evaluate_data_readiness


def _optical_observation(
    *,
    valid: bool = True,
    datetime: str | None = "2026-01-14T10:00:00Z",
) -> dict:
    return {
        "valid": valid,
        "raster": {
            "modality": "optical",
        },
        "spatial": {
            "bounds": {
                "min_lon": 80.0,
                "min_lat": 13.0,
                "max_lon": 80.2,
                "max_lat": 13.2,
            }
        },
        "acquisition": {
            "datetime": datetime,
        },
    }


def _requirements(
    *,
    task: str = "object_counting",
    min_observations: int = 1,
    modality_required: bool = False,
    allowed_modalities: list[str] | None = None,
    temporal_required: bool = False,
    spatial_required: bool = False,
) -> dict:
    return {
        "schema_version": "1.0",
        "request_id": "req_001",
        "task": task,
        "inputs": {
            "min_observations": min_observations,
            "type": "image",
        },
        "modality": {
            "required": modality_required,
            "allowed": allowed_modalities or [],
        },
        "temporal": {
            "required": temporal_required,
        },
        "spatial": {
            "required": spatial_required,
        },
        "quality": {
            "valid_data": True,
            "sufficient_resolution": False,
        },
        "task_specific": {},
    }


def test_ready_when_all_requirements_are_satisfied():
    result = evaluate_data_readiness(
        request_id="req_001",
        task="object_counting",
        data_requirements=_requirements(
            modality_required=True,
            allowed_modalities=["optical"],
        ),
        observations={
            "obs_001": _optical_observation(),
        },
    )

    assert result["ready"] is True
    assert result["available_observations"] == ["obs_001"]
    assert result["missing_information"] == []
    assert result["reason"] is None


def test_not_ready_when_second_observation_is_missing():
    result = evaluate_data_readiness(
        request_id="req_002",
        task="change_analysis",
        data_requirements=_requirements(
            task="change_analysis",
            min_observations=2,
            temporal_required=True,
            spatial_required=True,
        ),
        observations={
            "obs_001": _optical_observation(),
        },
    )

    assert result["ready"] is False
    assert result["available_observations"] == ["obs_001"]
    assert "second_observation" in result["missing_information"]


def test_not_ready_when_required_modality_is_missing():
    result = evaluate_data_readiness(
        request_id="req_003",
        task="object_counting",
        data_requirements=_requirements(
            modality_required=True,
            allowed_modalities=["sar"],
        ),
        observations={
            "obs_001": _optical_observation(),
        },
    )

    assert result["ready"] is False
    assert "compatible_modality" in result["missing_information"]


def test_not_ready_when_required_temporal_information_is_missing():
    result = evaluate_data_readiness(
        request_id="req_004",
        task="change_analysis",
        data_requirements=_requirements(
            task="change_analysis",
            temporal_required=True,
        ),
        observations={
            "obs_001": _optical_observation(datetime=None),
        },
    )

    assert result["ready"] is False
    assert "acquisition_datetime" in result["missing_information"]


def test_not_ready_when_required_spatial_information_is_missing():
    observation = _optical_observation()
    observation["spatial"] = {}

    result = evaluate_data_readiness(
        request_id="req_005",
        task="change_analysis",
        data_requirements=_requirements(
            task="change_analysis",
            spatial_required=True,
        ),
        observations={
            "obs_001": observation,
        },
    )

    assert result["ready"] is False
    assert "spatial_information" in result["missing_information"]


def test_not_ready_when_observation_is_invalid():
    result = evaluate_data_readiness(
        request_id="req_006",
        task="object_counting",
        data_requirements=_requirements(),
        observations={
            "obs_001": _optical_observation(valid=False),
        },
    )

    assert result["ready"] is False
    assert "valid_data" in result["missing_information"]


def test_multiple_missing_requirements_are_reported():
    result = evaluate_data_readiness(
        request_id="req_007",
        task="change_analysis",
        data_requirements=_requirements(
            task="change_analysis",
            min_observations=2,
            modality_required=True,
            allowed_modalities=["sar"],
            temporal_required=True,
            spatial_required=True,
        ),
        observations={
            "obs_001": _optical_observation(datetime=None),
        },
    )

    assert result["ready"] is False
    assert "second_observation" in result["missing_information"]
    assert "compatible_modality" in result["missing_information"]
    assert "acquisition_datetime" in result["missing_information"]