"""Tests for temporal compatibility checks."""

from data_engine.compatibility.temporal import (
    check_temporal_compatibility,
)


def _observation(datetime_value):
    """Build a minimal observation containing acquisition metadata."""

    return {
        "acquisition": {
            "datetime": datetime_value,
        }
    }


def test_temporal_compatibility_with_chronological_observations():
    """Two valid observations should establish chronological order."""

    first = _observation("2025-01-04T05:30:00+00:00")
    second = _observation("2026-01-14T05:30:00+00:00")

    result = check_temporal_compatibility(first, second)

    assert result["compatible"] is True
    assert result["checks"]["valid_datetime_values"] is True
    assert result["checks"]["chronological_order"] == "before"
    assert result["missing_information"] == []
    assert result["reason"] is None


def test_temporal_compatibility_with_reverse_order():
    """The result should identify when the first observation is later."""

    first = _observation("2026-01-14T05:30:00+00:00")
    second = _observation("2025-01-04T05:30:00+00:00")

    result = check_temporal_compatibility(first, second)

    assert result["compatible"] is True
    assert result["checks"]["chronological_order"] == "after"


def test_temporal_compatibility_with_same_datetime():
    """Identical acquisition times should be recognized explicitly."""

    first = _observation("2025-01-04T05:30:00+00:00")
    second = _observation("2025-01-04T05:30:00+00:00")

    result = check_temporal_compatibility(first, second)

    assert result["compatible"] is True
    assert result["checks"]["chronological_order"] == "same"


def test_temporal_compatibility_missing_first_datetime():
    """Missing first-observation time should prevent confirmation."""

    first = _observation(None)
    second = _observation("2026-01-14T05:30:00+00:00")

    result = check_temporal_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["first_datetime_available"] is False
    assert result["checks"]["second_datetime_available"] is True
    assert "first_observation_datetime" in result["missing_information"]


def test_temporal_compatibility_missing_second_datetime():
    """Missing second-observation time should prevent confirmation."""

    first = _observation("2025-01-04T05:30:00+00:00")
    second = _observation(None)

    result = check_temporal_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["first_datetime_available"] is True
    assert result["checks"]["second_datetime_available"] is False
    assert "second_observation_datetime" in result["missing_information"]


def test_temporal_compatibility_invalid_datetime():
    """Invalid datetime metadata should be reported as invalid."""

    first = _observation("not-a-date")
    second = _observation("2026-01-14T05:30:00+00:00")

    result = check_temporal_compatibility(first, second)

    assert result["compatible"] is False
    assert result["checks"]["valid_datetime_values"] is False
    assert "first_observation_datetime" in result["invalid_information"]
    