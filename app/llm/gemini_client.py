from google import genai

from app.config import settings


class GeminiClient:

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set in the .env file."
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = settings.GEMINI_MODEL

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:

        prompt = f"""
You are a financial analysis assistant.

Answer the user's question using ONLY the financial
information provided in the context below.

Rules:

1. Do not invent financial figures.
2. Do not use outside knowledge.
3. If the context does not contain enough information,
   say that the information is not available in the
   provided documents.
4. Be concise and precise.
5. Preserve the units used in the financial statements.
6. When possible, mention the source document and page.

## Financial Context:

{context}

User Question:
{question}

Answer:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text