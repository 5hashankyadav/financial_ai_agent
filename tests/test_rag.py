from app.rag.pipeline import FinancialRAG


def test_build_context():

    rag = FinancialRAG.__new__(FinancialRAG)

    results = [
        {
            "source_file": "FY25_Q3.pdf",
            "page_number": 1,
            "hybrid_score": 0.92,
            "text": "Total net sales were $94,036 million.",
        }
    ]

    context, sources = rag.build_context(results)

    assert "FY25_Q3.pdf" in context
    assert "Page: 1" in context
    assert "94,036" in context

    assert len(sources) == 1
    assert sources[0]["source_file"] == "FY25_Q3.pdf"
    assert sources[0]["page_number"] == 1
    assert sources[0]["score"] == 0.92


def test_build_context_empty_results():

    rag = FinancialRAG.__new__(FinancialRAG)

    context, sources = rag.build_context([])

    assert context == ""
    assert sources == []


def test_generate_answer():

    rag = FinancialRAG.__new__(FinancialRAG)

    class MockLLM:

        def generate_answer(self, question, context):

            assert question == "What was revenue?"
            assert "94,036" in context

            return "Revenue was $94,036 million."

    rag.llm = MockLLM()

    answer = rag.generate_answer(
        "What was revenue?",
        "Total revenue was $94,036 million.",
    )

    assert answer == "Revenue was $94,036 million."


def test_ask_rag_pipeline():

    rag = FinancialRAG.__new__(FinancialRAG)

    class MockRetriever:

        def search(self, question, top_k=5):

            assert question == "What was revenue?"
            assert top_k == 5

            return [
                {
                    "source_file": "FY25_Q3.pdf",
                    "page_number": 1,
                    "hybrid_score": 0.95,
                    "text": "Revenue was $94,036 million.",
                }
            ]

    class MockLLM:

        def generate_answer(self, question, context):

            assert question == "What was revenue?"
            assert "94,036" in context

            return "Revenue was $94,036 million."

    rag.retriever = MockRetriever()
    rag.llm = MockLLM()

    result = rag.ask("What was revenue?")

    assert result["answer"] == "Revenue was $94,036 million."
    assert len(result["sources"]) == 1
    assert result["sources"][0]["source_file"] == "FY25_Q3.pdf"


def test_ask_with_no_results():

    rag = FinancialRAG.__new__(FinancialRAG)

    class MockRetriever:

        def search(self, question, top_k=5):
            return []

    rag.retriever = MockRetriever()

    result = rag.ask("Unknown question")

    assert result["answer"] == (
        "I could not find relevant information."
    )

    assert result["sources"] == []