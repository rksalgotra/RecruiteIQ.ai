# core/embedding_engine.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import settings
import os

# Optional HuggingFace token
if settings.HF_TOKEN:
    os.environ["HF_TOKEN"] = settings.HF_TOKEN

# Load local embedding model once at startup
model = SentenceTransformer(settings.EMBEDDING_MODEL)


async def generate_embedding_batch(text_list):
    """
    Async-compatible local embedding batch.
    """
    embeddings = model.encode(
        text_list,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embeddings.tolist()


def generate_embedding(text: str):
    return model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    ).tolist()


def compute_similarity(vec1, vec2) -> float:
    return float(cosine_similarity(
        [vec1],
        [vec2]
    )[0][0])