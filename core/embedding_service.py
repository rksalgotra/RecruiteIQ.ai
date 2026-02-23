from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once (singleton pattern)
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str) -> list:
    if not text:
        return None

    embedding = model.encode(text)
    return embedding.tolist()