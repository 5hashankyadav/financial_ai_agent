from app.ingestion.pdf_parser import extract_text_from_directory
from app.ingestion.chunker import chunk_documents


def main():
    documents = extract_text_from_directory(
        "data/raw/quarterly"
    )

    chunks = chunk_documents(documents)

    print("\n" + "=" * 80)
    print("CHUNKING TEST")
    print("=" * 80)

    print(f"Pages extracted: {len(documents)}")
    print(f"Chunks created: {len(chunks)}")

    print("\nFirst 5 chunks:")
    print("-" * 80)

    for i, chunk in enumerate(chunks[:5], start=1):
        print(f"\nCHUNK {i}")
        print(f"Source: {chunk['source_file']}")
        print(f"Page: {chunk['page_number']}")
        print(f"Characters: {len(chunk['text'])}")
        print(chunk["text"][:300])


if __name__ == "__main__":
    main()