from app.ingestion.pdf_parser import extract_text_from_directory


def main():
    directory = "data/raw/quarterly"

    documents = extract_text_from_directory(directory)

    print("\n" + "=" * 80)
    print("PDF INGESTION TEST")
    print("=" * 80)

    print(f"Total pages extracted: {len(documents)}")

    print("\nFirst 5 documents:")
    print("-" * 80)

    for document in documents[:5]:
        print(
            f"File: {document['source_file']} | "
            f"Page: {document['page_number']} | "
            f"Characters: {len(document['text'])}"
        )

    print("\nFirst document preview:")
    print("-" * 80)
    print(documents[0]["text"][:500])


if __name__ == "__main__":
    main()