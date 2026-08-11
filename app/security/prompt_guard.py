import re

INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above) instructions",
    r"disregard (all )?(previous|above) instructions",
    r"system prompt",
    r"you are now an unrestricted",
    r"jailbreak",
    r"output the api key",
    r"print the environment variables",
    r"drop table",
    r"delete from",
    r"bypass rbac",
]


class PromptGuard:
    @staticmethod
    def inspect_query(query: str) -> bool:
        """
        Returns True if potential prompt injection or malicious input pattern is detected.
        """
        clean_query = query.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, clean_query):
                return True
        return False

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize retrieved document text to prevent indirect prompt injection from files.
        """
        sanitized = text
        for pattern in INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[REDACTED_INSTRUCTION]", sanitized, flags=re.IGNORECASE)
        return sanitized
