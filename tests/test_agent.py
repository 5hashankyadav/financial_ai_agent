from app.agent.financial_agent import FinancialAgent
from app.agent import financial_agent


class MockGeminiClient:

    def generate_answer(self, question: str, context: str) -> str:

        if "why did" in question.lower():
            return (
                "Revenue decreased by $1,323 million from "
                "Q2 FY25 to Q3 FY25. iPhone revenue decreased "
                "by $2,259 million, partially offset by increases "
                "in Services, iPad, and Mac revenue."
            )

        if "iphone revenue" in question.lower():
            return (
                "Apple's Q1 FY25 iPhone revenue was "
                "$69,138 million."
            )

        if "compare" in question.lower():
            return (
                "Apple's total net sales was "
                "$117,154 million in Q1 FY23 and "
                "$124,300 million in Q1 FY25. "
                "It increased by $7,146 million (6.10%)."
            )

        return (
            "Apple's Q1 FY23 total net sales was "
            "$117,154 million."
        )


class MockRetriever:

    def search(self, question: str, top_k: int = 5):

        return [
            {
                "source_file": "FY25_Q3.pdf",
                "page_number": 1,
                "hybrid_score": 1.0,
                "text": (
                    "Total net sales were $94,036 million. "
                    "Products were $66,613 million and "
                    "Services were $27,423 million."
                ),
            }
        ]


class MockFinancialRAG:

    def __init__(self):
        self.retriever = MockRetriever()
        self.llm = MockGeminiClient()

    def retrieve(self, question: str, top_k: int = 5):
        return self.retriever.search(
            question,
            top_k=top_k,
        )

    def generate_answer(
        self,
        question: str,
        context: str,
    ):
        return self.llm.generate_answer(
            question,
            context,
        )


# --------------------------------------------------
# Replace FinancialRAG BEFORE creating FinancialAgent
# --------------------------------------------------

financial_agent.FinancialRAG = MockFinancialRAG

agent = FinancialAgent()


# --------------------------------------------------
# Tests
# --------------------------------------------------

def test_structured_revenue():

    result = agent.ask(
        "What was Apple's net sales in Q1 FY23?"
    )

    assert result["route"] == "structured"
    assert "117,154" in result["answer"]


def test_structured_product_revenue():

    result = agent.ask(
        "What was Apple's iPhone revenue in Q1 FY25?"
    )

    assert result["route"] == "structured"
    assert "69,138" in result["answer"]


def test_comparison():

    result = agent.ask(
        "Compare Apple's revenue in Q1 FY23 and Q1 FY25."
    )

    assert result["route"] == "structured"
    assert "117,154" in result["answer"]
    assert "124,300" in result["answer"]
    assert "7,146" in result["answer"]


def test_hybrid_revenue_drivers():

    result = agent.ask(
        "Why did Apple's revenue change?"
    )

    assert result["route"] == "hybrid"
    assert "1,323" in result["answer"]
    assert "2,259" in result["answer"]