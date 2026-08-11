from pathlib import Path
import pickle
import re

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

INDEX_PATH = Path("data/processed/faiss.index")
CHUNKS_PATH = Path("data/processed/chunks.pkl")


class Retriever:

    def __init__(self):
        print("Loading embedding model...")
        self.model = SentenceTransformer(MODEL_NAME)

        print("Loading FAISS index...")
        self.index = faiss.read_index(str(INDEX_PATH))

        print("Loading chunk metadata...")
        with open(CHUNKS_PATH, "rb") as f:
            self.chunks = pickle.load(f)

        print(f"Loaded {self.index.ntotal} vectors")
        print(f"Loaded {len(self.chunks)} chunks")

    def _tokenize(self, text):
        text = text.lower()

        # Normalize numbers:
        # 117,154 -> 117154
        # 1,234,567 -> 1234567
        text = re.sub(r"(?<=\d),(?=\d)", "", text)

        return set(
            re.findall(r"\b[a-zA-Z0-9]+\b", text)
        )

    def _extract_period(self, query):
        """
        Extract fiscal period information from queries such as:

        Q1 FY23
        FY23 Q1
        Q2 FY24
        FY25 Q3
        """

        query = query.lower()

        quarter_match = re.search(
            r"\bq([1-4])\b",
            query
        )

        year_match = re.search(
            r"\bfy\s*([0-9]{2,4})\b",
            query
        )

        quarter = None
        fiscal_year = None

        if quarter_match:
            quarter = f"Q{quarter_match.group(1)}"

        if year_match:
            year = year_match.group(1)

            if len(year) == 4:
                year = year[-2:]

            fiscal_year = f"FY{year}"

        return fiscal_year, quarter

    def _period_score(self, query, source_file):
        """
        Score how well the source filename matches
        the fiscal period requested by the user.
        """

        fiscal_year, quarter = self._extract_period(query)

        source = source_file.upper()

        score = 0.0

        if fiscal_year and fiscal_year in source:
            score += 0.5

        if quarter and quarter in source:
            score += 0.5

        return score

    def search(self, query: str, top_k: int = 5):

        # --------------------------------------------------
        # 1. Semantic retrieval
        # --------------------------------------------------

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        # Retrieve more candidates for reranking
        candidate_k = min(20, self.index.ntotal)

        scores, indices = self.index.search(
            query_embedding,
            candidate_k
        )

        query_tokens = self._tokenize(query)

        candidates = []

        for score, index in zip(scores[0], indices[0]):

            if index == -1:
                continue

            chunk = self.chunks[index]

            text_tokens = self._tokenize(
                chunk["text"]
            )

            # --------------------------------------------------
            # 2. Keyword overlap
            # --------------------------------------------------

            if query_tokens:
                overlap = len(
                    query_tokens.intersection(text_tokens)
                ) / len(query_tokens)
            else:
                overlap = 0.0

            # --------------------------------------------------
            # 3. Fiscal period matching
            # --------------------------------------------------

            period_score = self._period_score(
                query,
                chunk["source_file"]
            )

            # --------------------------------------------------
            # 4. Hybrid score
            # --------------------------------------------------

            hybrid_score = (
                0.45 * float(score)
                + 0.25 * float(overlap)
                + 0.30 * float(period_score)
            )

            candidates.append(
                {
                    "text": chunk["text"],
                    "source_file": chunk["source_file"],
                    "page_number": chunk["page_number"],
                    "score": float(score),
                    "keyword_score": float(overlap),
                    "period_score": float(period_score),
                    "hybrid_score": float(hybrid_score),
                }
            )

        # --------------------------------------------------
        # 5. Rerank
        # --------------------------------------------------

        candidates.sort(
            key=lambda x: x["hybrid_score"],
            reverse=True
        )

        return candidates[:top_k]