from app.retrieval.retriever import Retriever
from app.llm.gemini_client import GeminiClient


class FinancialRAG:

    def __init__(self):
        self.retriever = Retriever()
        self.llm = GeminiClient()

    def retrieve(self, question: str, top_k: int = 5):
        """
        Retrieve relevant document chunks without generating an answer.
        """

        results = self.retriever.search(
            question,
            top_k=top_k
        )

        return results

    def build_context(self, results):
        """
        Convert retrieved chunks into context for Gemini.
        """

        if not results:
            return "", []

        context_parts = []
        sources = []

        for result in results:

            context_parts.append(
                f"""
Source: {result['source_file']}
Page: {result['page_number']}

{result['text']}
"""
            )

            sources.append(
                {
                    "source_file": result["source_file"],
                    "page_number": result["page_number"],
                    "score": result["hybrid_score"],
                }
            )

        context = "\n".join(context_parts)

        return context, sources

    def generate_answer(
        self,
        question: str,
        context: str
    ):
        """
        Generate a grounded answer from supplied context.
        """

        return self.llm.generate_answer(
            question,
            context
        )

    def ask(self, question: str, top_k: int = 5):
        """
        Standard RAG pipeline:
        retrieval → context → Gemini.
        """

        results = self.retrieve(
            question,
            top_k=top_k
        )

        if not results:
            return {
                "answer": "I could not find relevant information.",
                "sources": []
            }

        context, sources = self.build_context(results)

        answer = self.generate_answer(
            question,
            context
        )

        return {
            "answer": answer,
            "sources": sources
        }