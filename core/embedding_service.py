import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load .env file
load_dotenv()

# Optional: explicitly pass token
hf_token = os.getenv("HF_TOKEN")
model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

model = SentenceTransformer(model_name, token=hf_token)


def generate_embedding(text: str):
    if not text:
        return None

    embedding = model.encode(text)
    return embedding.tolist()