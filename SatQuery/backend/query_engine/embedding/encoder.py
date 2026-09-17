from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from query_engine.embedding.config import EmbeddingConfig
from query_engine.embedding.schemas import EmbeddingResult


@lru_cache(maxsize=1)
def _load_model(
    model_name: str,
) -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.
    """

    return SentenceTransformer(model_name)


class MultilingualE5Encoder:
    """
    Encoder based on multilingual-e5-small.
    """

    def __init__(
        self,
        config: EmbeddingConfig | None = None,
    ):
        self.config = config or EmbeddingConfig()

        self.model = _load_model(
            self.config.model_name
        )

    def encode(
        self,
        text: str,
    ) -> EmbeddingResult:
        """
        Encode a single query into a semantic vector.
        """

        if not isinstance(text, str):
            raise TypeError("text must be a string")

        text = text.strip()

        if not text:
            raise ValueError("text cannot be empty")

        # E5 models use the query: prefix for retrieval/query embeddings.
        model_input = f"query: {text}"

        vector = self.model.encode(
            model_input,
            normalize_embeddings=self.config.normalize_embeddings,
            convert_to_numpy=True,
        )

        vector = np.asarray(
            vector,
            dtype=np.float32,
        )

        if vector.ndim != 1:
            raise ValueError(
                f"Expected 1D embedding, got shape {vector.shape}"
            )

        if vector.shape[0] != self.config.dimension:
            raise ValueError(
                "Unexpected embedding dimension: "
                f"{vector.shape[0]} "
                f"(expected {self.config.dimension})"
            )

        return EmbeddingResult(
            text=text,
            vector=vector,
            dimension=int(vector.shape[0]),
        )