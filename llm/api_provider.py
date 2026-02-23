# llm/api_provider.py

import requests
from llm.explanation_provider import ExplanationProvider


class APIExplanationProvider(ExplanationProvider):

    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    def generate(self, candidate_score):

        prompt = f"""
        Candidate: {candidate_score.candidate_name}

        Final Score: {candidate_score.final_score}
        Skill Match Score: {candidate_score.skill_match_score}
        Experience Score: {candidate_score.experience_score}
        Embedding Similarity: {candidate_score.embedding_score}

        Matched Skills: {candidate_score.matched_skills}
        Missing Skills: {candidate_score.missing_skills}

        Provide a professional recruiter-style evaluation summary.
        """

        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",  # example
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        return "Explanation unavailable."