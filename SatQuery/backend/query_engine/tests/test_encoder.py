import numpy as np
import pytest

from query_engine.embedding.config import EmbeddingConfig
from query_engine.embedding.encoder import MultilingualE5Encoder


@pytest.fixture(scope="module")
def encoder():
    return MultilingualE5Encoder()


def test_encoder_loads(encoder):
    assert encoder.model is not None


def test_english_embedding(encoder):
    result = encoder.encode(
        "how many buildings are there?"
    )

    assert result.dimension == 384
    assert result.vector.shape == (384,)
    assert result.vector.dtype == np.float32


def test_tamil_embedding(encoder):
    result = encoder.encode(
        "இந்த படத்தில் எத்தனை கட்டிடங்கள் உள்ளன?"
    )

    assert result.dimension == 384
    assert result.vector.shape == (384,)


def test_tanglish_embedding(encoder):
    result = encoder.encode(
        "indha image la ethana buildings irukku?"
    )

    assert result.dimension == 384
    assert result.vector.shape == (384,)


def test_mixed_language_embedding(encoder):
    result = encoder.encode(
        "இந்த image ல எத்தனை buildings இருக்கு?"
    )

    assert result.dimension == 384
    assert result.vector.shape == (384,)


def test_embedding_is_normalized(encoder):
    result = encoder.encode(
        "detect buildings"
    )

    magnitude = np.linalg.norm(
        result.vector
    )

    assert np.isclose(
        magnitude,
        1.0,
        atol=1e-5,
    )


def test_empty_text_rejected(encoder):
    with pytest.raises(ValueError):
        encoder.encode("")


def test_whitespace_rejected(encoder):
    with pytest.raises(ValueError):
        encoder.encode("   ")


def test_non_string_rejected(encoder):
    with pytest.raises(TypeError):
        encoder.encode(123)


def test_config_dimension():
    config = EmbeddingConfig()

    assert config.dimension == 384
    assert config.model_name == (
        "intfloat/multilingual-e5-small"
    )