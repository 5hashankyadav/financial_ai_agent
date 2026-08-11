import numpy as np

from app.retrieval.retriever import Retriever


def test_extract_period():

    retriever = Retriever.__new__(Retriever)

    fiscal_year, quarter = retriever._extract_period(
        "What was revenue in Q3 FY25?"
    )

    assert fiscal_year == "FY25"
    assert quarter == "Q3"


def test_period_score():

    retriever = Retriever.__new__(Retriever)

    score = retriever._period_score(
        "What was revenue in Q3 FY25?",
        "FY25_Q3.pdf",
    )

    assert score == 1.0


def test_tokenize_normalizes_numbers():

    retriever = Retriever.__new__(Retriever)

    tokens = retriever._tokenize(
        "Apple reported 117,154 million."
    )

    assert "117154" in tokens
    assert "apple" in tokens
    assert "million" in tokens


def test_search_reranks_period_match():

    retriever = Retriever.__new__(Retriever)

    class MockModel:

        def encode(
            self,
            queries,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ):
            return np.array(
                [[1.0, 0.0]],
                dtype="float32",
            )

    class MockIndex:

        ntotal = 2

        def search(self, embedding, candidate_k):

            scores = np.array(
                [[0.90, 0.80]],
                dtype="float32",
            )

            indices = np.array(
                [[0, 1]],
                dtype="int64",
            )

            return scores, indices

    retriever.model = MockModel()
    retriever.index = MockIndex()

    retriever.chunks = [
        {
            "text": "Revenue was 100 million.",
            "source_file": "FY24_Q3.pdf",
            "page_number": 1,
        },
        {
            "text": "Revenue was 200 million in Q3 FY25.",
            "source_file": "FY25_Q3.pdf",
            "page_number": 2,
        },
    ]

    results = retriever.search(
        "What was revenue in Q3 FY25?",
        top_k=2,
    )

    assert len(results) == 2

    assert results[0]["source_file"] == "FY25_Q3.pdf"
    assert results[0]["period_score"] == 1.0

    assert results[0]["hybrid_score"] > results[1]["hybrid_score"]