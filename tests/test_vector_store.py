import pickle

import numpy as np

from app.retrieval import vector_store


def test_build_vector_store(monkeypatch, tmp_path):

    documents = [
        {
            "text": "Apple revenue was $94,036 million.",
            "source_file": "FY25_Q3.pdf",
            "page_number": 1,
        }
    ]

    chunks = [
        {
            "text": "Apple revenue was $94,036 million.",
            "source_file": "FY25_Q3.pdf",
            "page_number": 1,
        }
    ]

    # Mock PDF extraction
    monkeypatch.setattr(
        vector_store,
        "extract_text_from_directory",
        lambda directory: documents,
    )

    # Mock chunking
    monkeypatch.setattr(
        vector_store,
        "chunk_documents",
        lambda documents: chunks,
    )

    # Mock embedding model
    class MockModel:

        def encode(
            self,
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
            normalize_embeddings=True,
        ):
            return np.array(
                [[1.0, 0.0]],
                dtype="float32",
            )

    monkeypatch.setattr(
        vector_store,
        "SentenceTransformer",
        lambda model_name: MockModel(),
    )

    # Mock FAISS index
    class MockIndex:

        def __init__(self, dimension):
            self.dimension = dimension
            self.vectors = []

        def add(self, embeddings):
            self.vectors.extend(embeddings)

        @property
        def ntotal(self):
            return len(self.vectors)

    monkeypatch.setattr(
        vector_store.faiss,
        "IndexFlatIP",
        lambda dimension: MockIndex(dimension),
    )

    # Save the index using a simple mock
    saved_index = {}

    def mock_write_index(index, path):

        saved_index["index"] = index
        saved_index["path"] = path

    monkeypatch.setattr(
        vector_store.faiss,
        "write_index",
        mock_write_index,
    )

    # Redirect output files to temporary directory
    index_path = tmp_path / "faiss.index"
    chunks_path = tmp_path / "chunks.pkl"

    monkeypatch.setattr(
        vector_store,
        "INDEX_PATH",
        index_path,
    )

    monkeypatch.setattr(
        vector_store,
        "CHUNKS_PATH",
        chunks_path,
    )

    vector_store.build_vector_store()

    assert saved_index["index"].ntotal == 1
    assert saved_index["path"] == str(index_path)

    assert chunks_path.exists()

    with open(chunks_path, "rb") as file:
        saved_chunks = pickle.load(file)

    assert len(saved_chunks) == 1
    assert saved_chunks[0]["source_file"] == "FY25_Q3.pdf"
    assert "94,036" in saved_chunks[0]["text"]
