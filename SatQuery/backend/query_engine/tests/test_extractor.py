import pytest

from query_engine.entities.extractor import EntityExtractor


@pytest.fixture
def extractor():
    return EntityExtractor()


def get_entity_values(result):
    return {
        entity.value
        for entity in result.entities
    }


def get_slot_values(result):
    return {
        slot.value
        for slot in result.slots
    }


# ============================================================
# BASIC OBJECT EXTRACTION
# ============================================================


def test_extract_building(extractor):

    result = extractor.extract(
        "count the buildings"
    )

    assert "building" in get_entity_values(
        result
    )


def test_extract_road(extractor):

    result = extractor.extract(
        "detect roads"
    )

    assert "road" in get_entity_values(
        result
    )


def test_extract_multiple_objects(extractor):

    result = extractor.extract(
        "detect buildings and roads"
    )

    values = get_entity_values(result)

    assert "building" in values
    assert "road" in values


# ============================================================
# INPUT REFERENCES
# ============================================================


def test_extract_current_image(extractor):

    result = extractor.extract(
        "what is shown in this image"
    )

    assert "current_image" in get_slot_values(
        result
    )


def test_extract_multiple_images(extractor):

    result = extractor.extract(
        "compare these two images"
    )

    assert "multiple_images" in get_slot_values(
        result
    )


def test_extract_first_image(extractor):

    result = extractor.extract(
        "use the first image"
    )

    assert "first_image" in get_slot_values(
        result
    )


def test_extract_second_image(extractor):

    result = extractor.extract(
        "use the second image"
    )

    assert "second_image" in get_slot_values(
        result
    )


# ============================================================
# TEMPORAL REFERENCES
# ============================================================


def test_extract_before(extractor):

    result = extractor.extract(
        "compare the area before"
    )

    assert "before" in get_slot_values(
        result
    )


def test_extract_after(extractor):

    result = extractor.extract(
        "compare the area after"
    )

    assert "after" in get_slot_values(
        result
    )


def test_extract_over_time(extractor):

    result = extractor.extract(
        "has this area changed over time"
    )

    assert "over_time" in get_slot_values(
        result
    )


# ============================================================
# MULTIPLE INFORMATION TYPES
# ============================================================


def test_extract_objects_and_input_reference(
    extractor,
):

    result = extractor.extract(
        "count buildings in this image"
    )

    entities = get_entity_values(result)
    slots = get_slot_values(result)

    assert "building" in entities
    assert "current_image" in slots


def test_extract_comparison_information(
    extractor,
):

    result = extractor.extract(
        "compare these two images"
    )

    slots = get_slot_values(result)

    assert "multiple_images" in slots


# ============================================================
# VALIDATION
# ============================================================


def test_empty_text_fails(extractor):

    with pytest.raises(ValueError):
        extractor.extract("")


def test_whitespace_fails(extractor):

    with pytest.raises(ValueError):
        extractor.extract("   ")


def test_non_string_fails(extractor):

    with pytest.raises(TypeError):
        extractor.extract(None)