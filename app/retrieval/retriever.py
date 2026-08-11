import pickle
import re

from app.config import settings

import faiss
import numpy as np
from fastembed import TextEmbedding


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

INDEX_PATH = settings.FAISS_INDEX_PATH
CHUNKS_PATH = settings.CHUNKS_PATH


class Retriever:

    def __init__(self):
        print("Loading embedding model...")
        self.model = TextEmbedding(MODEL_NAME)

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

    def search(self, query: str, top_k: int = 5, role: str = "CEO"):
        from app.security.rbac import normalize_role, Role
        from app.security.prompt_guard import PromptGuard

        normalized_role = normalize_role(role)
        restricted_keywords = {"headcount", "compensation", "salary", "executive compensation", "stock awards"}

        # --------------------------------------------------
        # 1. Semantic retrieval
        # --------------------------------------------------

        query_embedding = np.array(
            list(self.model.embed([query])),
            dtype="float32"
        )

        # Retrieve more candidates for reranking
        candidate_k = min(25, self.index.ntotal)

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
            text = chunk["text"]

            # Data-layer RBAC filtering on text chunks
            if normalized_role != Role.CEO:
                text_lower = text.lower()
                if any(kw in text_lower for kw in restricted_keywords):
                    continue

            # Sanitize chunk against indirect prompt injection
            sanitized_text = PromptGuard.sanitize_text(text)

            text_tokens = self._tokenize(sanitized_text)

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

            source_file = chunk.get("source_file") or chunk.get("metadata", {}).get("file_name", "")
            period_score = self._period_score(
                query,
                source_file
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
                    "text": sanitized_text,
                    "source_file": source_file,
                    "page_number": chunk.get("page_number") or chunk.get("metadata", {}).get("page_number", 1),
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