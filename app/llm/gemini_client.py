from groq import Groq

from app.config import settings


class GeminiClient:

    def __init__(self):

        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set in the .env file."
            )

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        model = settings.GROQ_MODEL
        if model == "llama3-70b-8192":
            model = "llama-3.3-70b-versatile"

        self.model = model

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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content