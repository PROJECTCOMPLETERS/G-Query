from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EmbeddingResult:
    text: str
    vector: np.ndarray
    dimension: int