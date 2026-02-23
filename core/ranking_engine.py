# core/ranking_engine.py

def rank_candidates(candidate_scores):
    return sorted(
        candidate_scores,
        key=lambda x: x.final_score,
        reverse=True
    )
def calculate_final_score(skill_score, embedding_score, experience_score):
    return round(
        0.4 * skill_score +
        0.4 * embedding_score +
        0.2 * experience_score,
        3
    )


def categorize(final_score):
    if final_score >= 0.85:
        return "Strong Match"
    elif final_score >= 0.65:
        return "Moderate Match"
    return "Weak Match"