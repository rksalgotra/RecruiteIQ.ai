# core/scoring_engine.py

from core.embedding_engine import compute_similarity
from core.models import CandidateScore
from config import settings

class ScoringEngine:

    def __init__(self):
        self.skill_weight = settings.SKILL_WEIGHT
        self.embedding_weight = settings.EMBEDDING_WEIGHT
        self.experience_weight = settings.EXPERIENCE_WEIGHT

    def compute_skill_match(self, jd_skills, resume_skills):
        if not jd_skills:
            return 0.0, [], []

        jd_set = set(jd_skills)
        resume_set = set(resume_skills)

        matched = list(jd_set.intersection(resume_set))
        missing = list(jd_set - resume_set)

        score = len(matched) / len(jd_set)

        return score, matched, missing

    def compute_experience_match(self, jd_exp, resume_exp):
        if jd_exp == 0:
            return 1.0
        return min(resume_exp / jd_exp, 1.0)

    def score(self, jd, resume, jd_embedding, resume_embedding):

        # ---- Skill Match ----
        skill_score, matched_skills, missing_skills = self.compute_skill_match(
            jd.required_skills,
            resume.skills
        )

        # ---- Embedding Similarity ----
        embedding_score = compute_similarity(
            jd_embedding,
            resume_embedding
        )

        # ---- Experience Match ----
        experience_score = self.compute_experience_match(
            jd.min_experience,
            resume.years_experience
        )

        # ---- Final Weighted Score ----
        final_score = (
            skill_score * self.skill_weight +
            embedding_score * self.embedding_weight +
            experience_score * self.experience_weight
        )

        # ---- Confidence Score ----
        confidence_score = (
            0.5 * skill_score +
            0.5 * embedding_score
        )

        # ---- Category Classification ----
        if final_score >= 0.75:
            category = "Strong Match"
        elif final_score >= 0.55:
            category = "Moderate Match"
        else:
            category = "Weak Match"

        return CandidateScore(
            candidate_name=resume.name,
            skill_match_score=round(skill_score, 3),
            embedding_score=round(embedding_score, 3),
            experience_score=round(experience_score, 3),
            final_score=round(final_score, 3),
            category=category,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            confidence_score=round(confidence_score, 3)
        )

    def calculate_skill_match(candidate_skills, required_skills):
        matched = list(set(candidate_skills) & set(required_skills))
        missing = list(set(required_skills) - set(candidate_skills))
        score = len(matched) / len(required_skills) if required_skills else 0
        return score, matched, missing


    def calculate_experience_score(years_experience, min_required):
        if min_required == 0:
            return 1.0
        return min(years_experience / min_required, 1.0)