# core/vector_search.py

import numpy as np
from sqlalchemy.orm import Session
from core.models_db import Resume


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_similar_resumes(db: Session, job_embedding, limit: int = 100):

    resumes = db.query(Resume).all()

    results = []

    for resume in resumes:
        similarity = cosine_similarity(job_embedding, resume.embedding)
        results.append((resume.id, resume, similarity))

    # Sort descending by similarity
    results.sort(key=lambda x: x[2], reverse=True)

    return results[:limit]