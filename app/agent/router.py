import re


class QueryRouter:

    def classify(self, question: str) -> str:
        """
        Classify a financial question into:

        - structured: exact numerical financial facts
        - rag: qualitative/contextual questions
        - hybrid: questions requiring both
        """

        question_lower = question.lower()

        # --------------------------------------------------
        # Detect financial periods
        # --------------------------------------------------

        has_period = bool(
            re.search(
                r"\b(?:fy\s*)?(?:20\d{2}|\d{2})\b",
                question_lower
            )
            or re.search(
                r"\bq[1-4]\b",
                question_lower
            )
        )

        # --------------------------------------------------
        # Structured financial metrics
        # --------------------------------------------------

        structured_keywords = [
            "revenue",
            "sales",
            "net sales",
            "iphone revenue",
            "mac revenue",
            "ipad revenue",
            "services revenue",
            "wearables revenue",
        ]

        # --------------------------------------------------
        # Qualitative / contextual questions
        # --------------------------------------------------

        qualitative_keywords = [
            "why",
            "reason",
            "factors",
            "explain",
            "explanation",
            "performance",
            "impact",
            "outlook",
            "management",
            "commentary",
            "risk",
            "risks",
        ]

        has_structured = any(
            keyword in question_lower
            for keyword in structured_keywords
        )

        has_qualitative = any(
            keyword in question_lower
            for keyword in qualitative_keywords
        )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        if has_structured and has_qualitative:
            return "hybrid"

        if has_structured and has_period:
            return "structured"

        if has_structured:
            return "structured"

        return "rag"