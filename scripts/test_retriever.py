from app.retrieval.retriever import Retriever


def main():
    retriever = Retriever()

    query = "What was Apple's net sales in Q1 FY23?"

    print()
    print("=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)

    results = retriever.search(query, top_k=5)

    for i, result in enumerate(results, start=1):
        print()
        print(f"RESULT {i}")
        print("-" * 70)
        print(f"Source: {result['source_file']}")
        print(f"Page: {result['page_number']}")
        print(f"Distance: {result['distance']:.4f}")
        print()
        print(result["text"][:800])


if __name__ == "__main__":
    main()