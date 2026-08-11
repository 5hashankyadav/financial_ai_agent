from app.agent.hybrid import HybridContextBuilder
from app.retrieval.retriever import Retriever
from app.llm.gemini_client import GeminiClient


def main():

    question = "Compare Apple's revenue in Q2 FY25 and Q3 FY25."

    print("=" * 80)
    print("HYBRID ANSWER TEST")
    print("=" * 80)

    retriever = Retriever()

    print("\nRetrieving document chunks...")

    rag_results = retriever.search(
        question,
        top_k=5
    )

    print(
        f"Retrieved chunks: {len(rag_results)}"
    )

    builder = HybridContextBuilder()

    context = builder.build(
        question,
        rag_results=rag_results
    )

    llm = GeminiClient()

    answer = llm.generate_answer(
        question,
        context
    )

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(answer)


if __name__ == "__main__":
    main()