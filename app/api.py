import logging
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from app.agent.financial_agent import FinancialAgent


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Financial AI Agent",
    description="AI-powered financial analysis and RAG API",
    version="1.0.0",
)


# --------------------------------------------------
# Agent dependency
# --------------------------------------------------

@lru_cache
def get_agent():
    """
    Create the FinancialAgent only when it is actually needed.

    lru_cache ensures that production uses one shared
    agent instance instead of creating a new one for
    every request.
    """
    return FinancialAgent()


# --------------------------------------------------
# Request / Response models
# --------------------------------------------------

class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    route: str
    answer: str
    sources: list


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "financial-ai-agent",
    }


# --------------------------------------------------
# Ask endpoint
# --------------------------------------------------

@app.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    agent: FinancialAgent = Depends(get_agent),
):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    logger.info(
        "Received question: %s",
        question,
    )

    try:

        result = agent.ask(question)

        logger.info(
            "Question classified as route=%s",
            result["route"],
        )

        return {
            "question": question,
            "route": result["route"],
            "answer": result["answer"],
            "sources": result.get("sources", []),
        }

    except Exception:

        logger.exception(
            "Error while processing question"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred while "
                "processing the question."
            ),
        )