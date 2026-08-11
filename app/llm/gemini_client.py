import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )


class GeminiClient:

    def __init__(self):

        self.client = genai.Client(
            api_key=API_KEY
        )

        self.model = "gemini-3.6-flash"

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:

        prompt = f"""
You are a financial analysis assistant.

Answer the user's question using ONLY the financial
information provided in the context below.

The context can contain two types of evidence:

1. STRUCTURED FINANCIAL DATA
   - This comes from the financial database.
   - Treat numerical values from this section as
     authoritative for financial calculations.

2. DOCUMENT CONTEXT
   - This comes from Apple's financial documents.
   - Use it to provide supporting evidence and
     document references.

Rules:

1. Do not invent financial figures.

2. Do not use outside knowledge.

3. Do not assume a business reason for a financial
   change unless the provided documents explicitly
   support that reason.

4. Clearly distinguish between:
   - numerical changes that are directly observable
   - explanations or causes that are explicitly stated
     in the documents

5. If the documents show that revenue changed but do
   not explain why, say so explicitly.

6. When calculating changes, percentages, increases,
   or decreases, use the STRUCTURED FINANCIAL DATA
   whenever it is available.

7. Preserve the units used in the financial statements.

8. Do not treat a comparison column in a financial
   statement as a separate database period unless the
   structured financial data explicitly identifies it.

9. When possible, cite the source document and page.

10. Be concise, precise, and professional.

11. Never present an inference as a fact.

## FINANCIAL CONTEXT

{context}

## USER QUESTION

{question}

## ANSWER

"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        return response.text