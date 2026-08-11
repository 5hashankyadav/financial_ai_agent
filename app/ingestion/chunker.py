from typing import List, Dict


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> List[Dict]:
    """
    Split extracted PDF documents into overlapping text chunks.
    """

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []

    for document in documents:
        text = document["text"].strip()

        if not text:
            continue

        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "text": chunk_text,
                        "source_file": document["source_file"],
                        "page_number": document["page_number"],
                    }
                )

            if end >= text_length:
                break

            start = end - chunk_overlap

    return chunks