import json
import os
import time
from pathlib import Path

from app.config import BASE_DIR

FEEDBACK_FILE = BASE_DIR / "data" / "processed" / "feedback.json"


class FeedbackStore:
    def __init__(self, filepath: Path = FEEDBACK_FILE):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not self.filepath.parent.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save_feedback(
        self,
        question: str,
        role: str,
        rating: int,  # +1 for positive, -1 for negative
        route: str = "",
        answer: str = "",
        correction: str = "",
    ) -> dict:
        entry = {
            "question": question.strip(),
            "role": role,
            "rating": rating,
            "route": route,
            "answer": answer,
            "correction": correction.strip(),
            "timestamp": time.time(),
        }

        feedbacks = self.get_all_feedback()
        feedbacks.append(entry)

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, indent=2)

        return entry

    def get_all_feedback(self) -> list[dict]:
        if not self.filepath.exists():
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def get_corrections_for_question(self, question: str) -> list[str]:
        """
        Retrieve user corrections for queries matching keywords in the input question.
        Used for few-shot correction memory in LLM prompts.
        """
        question_words = set(question.lower().split())
        corrections = []
        for item in self.get_all_feedback():
            if item.get("correction") and item.get("rating", 0) < 0:
                item_words = set(item.get("question", "").lower().split())
                if question_words.intersection(item_words):
                    corrections.append(item["correction"])
        return corrections
