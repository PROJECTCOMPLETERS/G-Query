from app.schemas.query import StructuredQuery


from app.services.task_engine import (
    InvalidTaskError,
    TaskEngine,
    UnsupportedTaskError,
)
def test_task_engine_object_counting():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_400",
        question="How many buildings are in this image?",
        intent="object_counting",
        entities=["building"],
        modality="optical",
    )

    requirements = engine.build_data_requirements(query)

    assert requirements.task == "object_counting"
    assert requirements.inputs.min_observations == 1
    assert requirements.modality.allowed == ["optical"]
    assert requirements.quality.sufficient_resolution is True
    assert "object_detection" in requirements.task_specific[
        "requested_capabilities"
    ]
    assert "counting" in requirements.task_specific[
        "requested_capabilities"
    ]


def test_task_engine_change_detection():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_401",
        question="Compare these two images for changes",
        intent="change_detection",
        inputs=[
            {"input_id": "obs_001"},
            {"input_id": "obs_002"},
        ],
    )

    requirements = engine.build_data_requirements(query)

    assert requirements.task == "change_detection"
    assert requirements.inputs.min_observations == 2
    assert requirements.modality.allowed == ["optical", "sar"]
    assert requirements.temporal.required is True
    assert requirements.spatial.required is True
    assert requirements.task_specific[
        "requested_capabilities"
    ] == ["change_detection"]


def test_task_engine_image_understanding():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_402",
        question="Describe this satellite image",
        intent="image_understanding",
    )

    requirements = engine.build_data_requirements(query)

    assert requirements.task == "image_understanding"
    assert requirements.inputs.min_observations == 1
    assert requirements.task_specific[
        "requested_capabilities"
    ] == ["image_understanding"]


def test_task_engine_rejects_unsupported_task():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_403",
        question="Predict next year's exact crop yield",
        intent="crop_yield_prediction",
    )

    try:
        engine.identify_task(query)
        assert False, "Expected UnsupportedTaskError"
    except UnsupportedTaskError:
        pass


def test_task_engine_rejects_missing_intent():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_404",
        question="Analyze this image",
        intent="",
    )

    try:
        engine.identify_task(query)
        assert False, "Expected InvalidTaskError"
    except InvalidTaskError:
        pass
def test_task_engine_detects_missing_observation():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_405",
        question="How many buildings are in this image?",
        intent="object_counting",
        entities=["building"],
        modality="optical",
    )

    clarification = engine.check_requirements(query)

    assert clarification is not None
    assert clarification.status == "needs_clarification"
    assert clarification.request_id == "req_405"
    assert len(clarification.missing_information) == 1


def test_task_engine_accepts_available_observation():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_406",
        question="How many buildings are in this image?",
        intent="object_counting",
        entities=["building"],
        inputs=[
            {"input_id": "obs_001", "type": "image"}
        ],
        modality="optical",
    )

    clarification = engine.check_requirements(query)

    assert clarification is None


def test_change_detection_requires_two_observations():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_407",
        question="Compare these two images",
        intent="change_detection",
        inputs=[
            {"input_id": "obs_001", "type": "image"}
        ],
    )

    clarification = engine.check_requirements(query)

    assert clarification is not None
    assert clarification.status == "needs_clarification"
    assert "2 observation" in (
        clarification.missing_information[0]
    )
def test_change_detection_accepts_complete_temporal_and_spatial_info():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_408",
        question="Compare these two satellite images for changes",
        intent="change_detection",
        inputs=[
            {"input_id": "obs_001", "type": "image"},
            {"input_id": "obs_002", "type": "image"},
        ],
        temporal={
            "required": True,
            "information": {
                "start_time": "2026-01-01",
                "end_time": "2026-06-01",
            },
        },
        spatial={
            "required": True,
            "information": {
                "region": "Chennai",
            },
        },
    )

    clarification = engine.check_requirements(query)

    assert clarification is None


def test_change_detection_missing_temporal_information():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_409",
        question="Compare these two satellite images for changes",
        intent="change_detection",
        inputs=[
            {"input_id": "obs_001", "type": "image"},
            {"input_id": "obs_002", "type": "image"},
        ],
        spatial={
            "required": True,
            "information": {
                "region": "Chennai",
            },
        },
    )

    clarification = engine.check_requirements(query)

    assert clarification is not None
    assert clarification.status == "needs_clarification"
    assert "Temporal information is required." in (
        clarification.missing_information
    )


def test_change_detection_missing_spatial_information():
    engine = TaskEngine()

    query = StructuredQuery(
        request_id="req_410",
        question="Compare these two satellite images for changes",
        intent="change_detection",
        inputs=[
            {"input_id": "obs_001", "type": "image"},
            {"input_id": "obs_002", "type": "image"},
        ],
        temporal={
            "required": True,
            "information": {
                "start_time": "2026-01-01",
                "end_time": "2026-06-01",
            },
        },
    )

    clarification = engine.check_requirements(query)

    assert clarification is not None
    assert clarification.status == "needs_clarification"
    assert "Spatial information is required." in (
        clarification.missing_information
    )