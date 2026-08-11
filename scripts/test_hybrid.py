from app.agent.hybrid import HybridContextBuilder
from app.rag.pipeline import FinancialRAG


def main():

    question = "Why did Apple's revenue change?"

    rag = FinancialRAG()
    builder = HybridContextBuilder()

    print("=" * 80)
    print("HYBRID CONTEXT TEST")
    print("=" * 80)

    print("\nRetrieving document chunks...")

    rag_results = rag.retrieve(
        question,
        top_k=5
    )

    print(f"Retrieved chunks: {len(rag_results)}")

    context = builder.build(
        question,
        rag_results
    )

    print("\n" + "=" * 80)
    print("COMBINED CONTEXT")
    print("=" * 80)

    print(context)


if __name__ == "__main__":
    main()