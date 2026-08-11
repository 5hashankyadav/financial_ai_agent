from app.retrieval.retriever import Retriever
from app.llm.gemini_client import GeminiClient


class FinancialRAG:

    def __init__(self):
        self.retriever = Retriever()
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            self._llm = GeminiClient()
        return self._llm

    @llm.setter
    def llm(self, value):
        self._llm = value

    def retrieve(self, question: str, top_k: int = 5, role: str = "CEO", **kwargs):
        """
        Retrieve relevant document chunks without generating an answer.
        """
        try:
            return self.retriever.search(
                question,
                top_k=top_k,
                role=role,
                **kwargs
            )
        except TypeError:
            return self.retriever.search(
                question,
                top_k=top_k
            )

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

    def ask(self, question: str, top_k: int = 5, role: str = "CEO", **kwargs):
        """
        Standard RAG pipeline:
        retrieval → context → Gemini.
        """

        results = self.retrieve(
            question,
            top_k=top_k,
            role=role,
            **kwargs
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