# core/scoring_engine.py

from core.embedding_engine import compute_similarity
from core.models import CandidateScore
from core.skill_normalizer import normalize_skill_list
from config import settings


class ScoringEngine:
    """
    Enterprise-grade multi-dimensional scoring engine.
    Combines:
    - Required skill match
    - Optional skill bonus
    - Embedding similarity
    - Experience alignment
    """

    def __init__(self):
        # Core weights (should sum close to 1.0)
        self.required_skill_weight = settings.SKILL_WEIGHT
        self.embedding_weight = settings.EMBEDDING_WEIGHT
        self.experience_weight = settings.EXPERIENCE_WEIGHT

        # Optional skill bonus weight
        self.optional_skill_weight = getattr(
            settings, "OPTIONAL_SKILL_WEIGHT", 0.1
        )

        # Soft constraint configuration
        self.required_skill_threshold = getattr(
            settings, "REQUIRED_SKILL_THRESHOLD", 0.4
        )
        self.penalty_factor = getattr(
            settings, "LOW_SKILL_PENALTY", 0.7
        )

    # -----------------------------------------------------
    # Required Skill Match
    # -----------------------------------------------------
    def compute_required_skill_match(self, jd_required, resume_skills):
        if not jd_required:
            return 1.0, [], []

        jd_required = normalize_skill_list(jd_required)
        resume_skills = normalize_skill_list(resume_skills)

        jd_set = set(jd_required)
        resume_set = set(resume_skills)

        matched = list(jd_set & resume_set)
        missing = list(jd_set - resume_set)

        score = len(matched) / len(jd_set)

        return score, matched, missing

    # -----------------------------------------------------
    # Optional Skill Match
    # -----------------------------------------------------
    def compute_optional_skill_match(self, jd_optional, resume_skills):
        if not jd_optional:
            return 0.0, []

        jd_optional = normalize_skill_list(jd_optional)
        resume_skills = normalize_skill_list(resume_skills)

        jd_set = set(jd_optional)
        resume_set = set(resume_skills)

        matched = list(jd_set & resume_set)
        score = len(matched) / len(jd_set)

        return score, matched

    # -----------------------------------------------------
    # Experience Match
    # -----------------------------------------------------
    def compute_experience_match(self, jd_exp, resume_exp):
        if not jd_exp or jd_exp == 0:
            return 1.0

        return min(resume_exp / jd_exp, 1.0)

    # -----------------------------------------------------
    # Main Scoring Pipeline
    # -----------------------------------------------------
    def score(self, jd, resume, jd_embedding, resume_embedding):

        # ---- Required Skills ----
        required_score, matched_required, missing_required = \
            self.compute_required_skill_match(
                jd.required_skills,
                resume.skills
            )

        # ---- Optional Skills ----
        optional_score, matched_optional = \
            self.compute_optional_skill_match(
                getattr(jd, "optional_skills", []),
                resume.skills
            )

        # ---- Embedding Similarity ----
        embedding_score = compute_similarity(
            jd_embedding,
            resume_embedding
        )

        # ---- Experience ----
        experience_score = self.compute_experience_match(
            jd.min_experience,
            resume.years_experience
        )

        # ---- Weighted Aggregation ----
        final_score = (
            required_score * self.required_skill_weight +
            optional_score * self.optional_skill_weight +
            embedding_score * self.embedding_weight +
            experience_score * self.experience_weight
        )

        # ---- Soft Hard Constraint ----
        if required_score < self.required_skill_threshold:
            final_score *= self.penalty_factor

        # ---- Bound Score (Safety) ----
        final_score = max(min(final_score, 1.0), 0.0)

        # ---- Confidence ----
        confidence_score = (
            0.6 * required_score +
            0.4 * embedding_score
        )

        # ---- Category ----
        if final_score >= 0.75:
            category = "Strong Match"
        elif final_score >= 0.55:
            category = "Moderate Match"
        else:
            category = "Weak Match"

        return CandidateScore(
            candidate_name=resume.name,
            skill_match_score=round(required_score, 3),
            optional_skill_score=round(optional_score, 3),
            embedding_score=round(embedding_score, 3),
            experience_score=round(experience_score, 3),
            final_score=round(final_score, 3),
            confidence_score=round(confidence_score, 3),
            category=category,
            matched_skills=matched_required,
            missing_skills=missing_required,
            matched_optional_skills=matched_optional
        )