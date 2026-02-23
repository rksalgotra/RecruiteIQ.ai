# core/parser.py

import re
import spacy
from typing import List

nlp = spacy.load("en_core_web_sm")

COMMON_SKILLS = [
    "python", "sql", "aws", "docker", "kubernetes",
    "java", "javascript", "react", "node", "machine learning"
]


def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found = []
    for skill in COMMON_SKILLS:
        if skill in text_lower:
            found.append(skill)
    return list(set(found))


def extract_experience(text: str) -> float:
    matches = re.findall(r"(\d+)\+?\s+years", text.lower())
    if matches:
        return max([float(x) for x in matches])
    return 0.0