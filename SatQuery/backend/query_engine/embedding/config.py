from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    model_name: str = "intfloat/multilingual-e5-small"
    dimension: int = 384
    normalize_embeddings: bool = True