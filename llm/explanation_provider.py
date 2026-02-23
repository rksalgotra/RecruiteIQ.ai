# llm/explanation_provider.py

from abc import ABC, abstractmethod


class ExplanationProvider(ABC):

    @abstractmethod
    def generate(self, candidate_score):
        pass