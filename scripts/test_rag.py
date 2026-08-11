from app.rag.pipeline import FinancialRAG


def main():

    rag = FinancialRAG()

    question = "What was Apple's net sales in Q1 FY23?"

    result = rag.ask(question)

    print("\n" + "=" * 80)
    print("QUESTION")
    print("=" * 80)
    print(question)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(result["answer"])

    print("\n" + "=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in result["sources"]:
        print(
            f"{source['source_file']} | "
            f"Page {source['page_number']} | "
            f"Score {source['score']:.4f}"
        )


if __name__ == "__main__":
    main()