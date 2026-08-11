import fitz
import pytest

from app.ingestion.chunker import chunk_documents
from app.ingestion.pdf_parser import extract_text_from_pdf


def test_chunk_documents_basic():

    documents = [
        {
            "text": "A" * 100,
            "page_number": 1,
            "source_file": "test.pdf",
        }
    ]

    chunks = chunk_documents(
        documents,
        chunk_size=40,
        chunk_overlap=10,
    )

    assert len(chunks) > 1

    assert chunks[0]["source_file"] == "test.pdf"
    assert chunks[0]["page_number"] == 1


def test_chunk_documents_overlap():

    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    documents = [
        {
            "text": text,
            "page_number": 1,
            "source_file": "test.pdf",
        }
    ]

    chunks = chunk_documents(
        documents,
        chunk_size=10,
        chunk_overlap=3,
    )

    assert chunks[0]["text"] == "ABCDEFGHIJ"
    assert chunks[1]["text"].startswith("HIJ")


def test_chunk_documents_skips_empty_text():

    documents = [
        {
            "text": "   ",
            "page_number": 1,
            "source_file": "empty.pdf",
        }
    ]

    chunks = chunk_documents(documents)

    assert chunks == []


def test_chunk_documents_invalid_overlap():

    documents = [
        {
            "text": "Some text",
            "page_number": 1,
            "source_file": "test.pdf",
        }
    ]

    with pytest.raises(
        ValueError,
        match="chunk_overlap must be smaller than chunk_size",
    ):
        chunk_documents(
            documents,
            chunk_size=100,
            chunk_overlap=100,
        )


def test_extract_text_from_pdf(tmp_path):

    pdf_path = tmp_path / "test.pdf"

    pdf = fitz.open()

    page = pdf.new_page()

    page.insert_text(
        (72, 72),
        "Apple reported total net sales of $117,154 million.",
    )

    pdf.save(pdf_path)
    pdf.close()

    documents = extract_text_from_pdf(pdf_path)

    assert len(documents) == 1

    assert documents[0]["page_number"] == 1
    assert documents[0]["source_file"] == "test.pdf"
    assert "117,154" in documents[0]["text"]


def test_extract_text_from_pdf_missing_file(tmp_path):

    missing_path = tmp_path / "missing.pdf"

    with pytest.raises(
        FileNotFoundError,
        match="PDF not found",
    ):
        extract_text_from_pdf(missing_path)