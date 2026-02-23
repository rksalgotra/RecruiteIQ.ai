from sqlalchemy.orm import Session
from sqlalchemy import select
from core.models_db import Resume


def find_similar_resumes(db: Session, embedding: list, limit: int = 5):

    stmt = (
        select(
            Resume.id,
            Resume.candidate_name,
            (1 - Resume.embedding.cosine_distance(embedding)).label("similarity")
        )
        .order_by(Resume.embedding.cosine_distance(embedding))
        .limit(limit)
    )

    result = db.execute(stmt)

    return result.all()