from pathlib import Path
import fitz  # PyMuPDF


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file page by page.

    Returns:
        list[dict]: One dictionary per page containing:
            - text
            - page_number
            - source_file
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    documents = []

    pdf = fitz.open(file_path)

    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text("text").strip()

        if not text:
            continue

        documents.append(
            {
                "text": text,
                "page_number": page_number,
                "source_file": file_path.name,
            }
        )

    pdf.close()

    return documents


def extract_text_from_directory(directory):
    """
    Extract text from every PDF in a directory.
    """

    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    all_documents = []

    for pdf_file in sorted(directory.glob("*.pdf")):
        print(f"Processing {pdf_file.name}...")

        documents = extract_text_from_pdf(pdf_file)

        print(f"  Extracted {len(documents)} pages")

        all_documents.extend(documents)

    return all_documents