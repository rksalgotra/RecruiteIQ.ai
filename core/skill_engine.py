# core/skill_normalizer.py

import re
from typing import List

# Alias map (expand gradually)
SKILL_ALIAS_MAP = {
    "amazon web services": "aws",
    "aws cloud": "aws",
    "aws services": "aws",

    "microsoft azure": "azure",
    "ms azure": "azure",

    "nodejs": "node.js",
    "node js": "node.js",

    "reactjs": "react",
    "react.js": "react",

    "c sharp": "c#",
    "dotnet": ".net",
    "dot net": ".net",
}


def clean_skill(skill: str) -> str:
    """
    Lowercase + remove extra spaces + strip special characters.
    """
    skill = skill.lower().strip()
    skill = re.sub(r"\s+", " ", skill)
    return skill


def normalize_skill(skill: str) -> str:
    """
    Normalize a single skill using alias mapping.
    """
    skill = clean_skill(skill)
    return SKILL_ALIAS_MAP.get(skill, skill)


def normalize_skill_list(skills: List[str]) -> List[str]:
    """
    Normalize and deduplicate skill list.
    """
    normalized = [normalize_skill(skill) for skill in skills]
    return list(set(normalized))