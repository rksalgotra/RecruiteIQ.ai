from sqlalchemy.orm import Session
from core.models_db import Skill


def extract_skills_from_text(text: str, db: Session):
    text = text.lower()
    skills = db.query(Skill).all()

    matched = []

    for skill in skills:
        if skill.normalized_name in text:
            matched.append(skill)

    return matched