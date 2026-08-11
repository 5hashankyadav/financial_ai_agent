from pathlib import Path
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.ingestion.pdf_parser import extract_text_from_directory
from app.ingestion.chunker import chunk_documents


MODEL_NAME = "all-MiniLM-L6-v2"

PDF_DIRECTORY = "data/raw/quarterly"

INDEX_PATH = Path("data/processed/faiss.index")
CHUNKS_PATH = Path("data/processed/chunks.pkl")


def build_vector_store():
    print("=" * 60)
    print("BUILDING VECTOR STORE")
    print("=" * 60)

    # 1. Extract PDF pages
    print("\nExtracting PDF documents...")
    documents = extract_text_from_directory(PDF_DIRECTORY)

    print(f"Pages extracted: {len(documents)}")

    # 2. Create chunks
    print("\nCreating chunks...")
    chunks = chunk_documents(documents)

    if not chunks:
        raise ValueError("No chunks were created.")

    print(f"Chunks created: {len(chunks)}")

    # 3. Load embedding model
    print("\nLoading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    # 4. Extract text from chunks
    texts = [chunk["text"] for chunk in chunks]

    # 5. Generate normalized embeddings
    print(f"\nGenerating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print(f"Embedding shape: {embeddings.shape}")

    # 6. Create cosine-similarity FAISS index
    dimension = embeddings.shape[1]

    print("\nCreating FAISS index...")
    print(f"Dimension: {dimension}")
    print("Similarity: cosine")

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # 7. Save index and chunk metadata
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    # 8. Summary
    print()
    print("=" * 60)
    print("VECTOR STORE CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"Pages:               {len(documents)}")
    print(f"Chunks:              {len(chunks)}")
    print(f"Embedding dimension: {dimension}")
    print(f"FAISS vectors:       {index.ntotal}")
    print("Similarity:           cosine")
    print(f"Index:                {INDEX_PATH}")
    print(f"Chunk metadata:       {CHUNKS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    build_vector_store()