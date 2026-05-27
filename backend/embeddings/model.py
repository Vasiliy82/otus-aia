from __future__ import annotations

from functools import lru_cache

import numpy as np

from backend.config import EMBEDDING_DIM, EMBEDDING_MODEL


class EmbeddingModel:
    def __init__(self, model_name: str = EMBEDDING_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    @property
    def dimension(self) -> int:
        return int(self._model.get_embedding_dimension())

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(vectors, dtype=np.float32)

    def encode_one(self, text: str) -> list[float]:
        vec = self.encode([text])[0]
        if vec.shape[0] != EMBEDDING_DIM:
            raise ValueError(
                f"Model dimension {vec.shape[0]} != configured EMBEDDING_DIM={EMBEDDING_DIM}"
            )
        return vec.tolist()


@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel()
