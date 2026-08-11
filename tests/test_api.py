from fastapi.testclient import TestClient

from app.api import app, get_agent


class MockFinancialAgent:

    def ask(self, question: str):

        if "net sales" in question.lower():

            return {
                "answer": (
                    "Apple's Q1 FY23 total net sales "
                    "was $117,154 million."
                ),
                "route": "structured",
                "sources": [
                    {
                        "source_file": "Q231.xls",
                        "source_sheet": "TABLE21",
                        "source_row": 24,
                    }
                ],
            }

        if "why" in question.lower():

            return {
                "answer": (
                    "Revenue decreased by $1,323 million "
                    "from Q2 FY25 to Q3 FY25."
                ),
                "route": "hybrid",
                "sources": [],
            }

        return {
            "answer": "Mock answer.",
            "route": "rag",
            "sources": [
                {
                    "source_file": "FY24_Q2.pdf",
                    "source_sheet": None,
                    "source_row": None,
                }
            ],
        }


class FailingFinancialAgent:

    def ask(self, question: str):
        raise RuntimeError("Simulated agent failure")

# --------------------------------------------------
# Override the real FinancialAgent
# --------------------------------------------------

app.dependency_overrides[get_agent] = (
    lambda: MockFinancialAgent()
)

client = TestClient(app)


# --------------------------------------------------
# Tests
# --------------------------------------------------

def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "financial-ai-agent"


def test_empty_question():

    response = client.post(
        "/ask",
        json={
            "question": ""
        },
    )

    assert response.status_code == 400

def test_missing_question():

    response = client.post(
        "/ask",
        json={},
    )

    assert response.status_code == 422


def test_invalid_question_type():

    response = client.post(
        "/ask",
        json={
            "question": 123
        },
    )

    assert response.status_code == 422

def test_structured_question():

    response = client.post(
        "/ask",
        json={
            "question": "What was Apple's net sales in Q1 FY23?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["route"] == "structured"
    assert "117,154" in data["answer"]


def test_hybrid_question():

    response = client.post(
        "/ask",
        json={
            "question": "Why did Apple's revenue change?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["route"] == "hybrid"
    assert "1,323" in data["answer"]

def test_rag_question():

    response = client.post(
        "/ask",
        json={
            "question": "What does Apple's annual report say about its business strategy?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["route"] == "rag"
    assert len(data["sources"]) > 0

def test_response_structure():

    response = client.post(
        "/ask",
        json={
            "question": "What was Apple's net sales in Q1 FY23?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "question" in data
    assert "route" in data
    assert "answer" in data
    assert "sources" in data

    assert isinstance(data["question"], str)
    assert isinstance(data["route"], str)
    assert isinstance(data["answer"], str)
    assert isinstance(data["sources"], list)


def test_whitespace_question():

    response = client.post(
        "/ask",
        json={
            "question": "   "
        },
    )

    assert response.status_code == 400

def test_agent_internal_error():

    app.dependency_overrides[get_agent] = (
        lambda: FailingFinancialAgent()
    )

    response = client.post(
        "/ask",
        json={
            "question": "What was Apple's revenue?"
        },
    )

    assert response.status_code == 500

    data = response.json()

    assert data["detail"] == (
        "An internal error occurred while processing the question."
    )

    app.dependency_overrides[get_agent] = (
        lambda: MockFinancialAgent()
    )



def test_request_id_header():

    response = client.get("/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    request_id = response.headers["X-Request-ID"]

    assert len(request_id) == 36