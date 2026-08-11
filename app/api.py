import logging
import uuid
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

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
# Custom exceptions
# --------------------------------------------------

class AgentProcessingError(Exception):
    """Raised when the financial agent cannot process a request."""


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Financial AI Agent",
    description="AI-powered financial analysis and RAG API",
    version="1.0.0",
)


# --------------------------------------------------
# Request ID middleware
# --------------------------------------------------

@app.middleware("http")
async def add_request_id(request: Request, call_next):

    request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    logger.info(
        "Request started | request_id=%s | method=%s | path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed | request_id=%s | status=%s",
        request_id,
        response.status_code,
    )

    return response


# --------------------------------------------------
# Agent processing error handler
# --------------------------------------------------

@app.exception_handler(AgentProcessingError)
async def agent_processing_error_handler(
    request: Request,
    exc: AgentProcessingError,
):

    request_id = getattr(
        request.state,
        "request_id",
        "unknown",
    )

    logger.error(
        "Financial agent processing error | request_id=%s | error=%s",
        request_id,
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "An internal error occurred while "
                "processing the question."
            )
        },
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
    question: str = Field(
        ...,
        description="Financial question to analyze.",
    )


class Source(BaseModel):
    source_file: str
    source_sheet: str | None = None
    source_row: int | None = None


class AskResponse(BaseModel):
    question: str = Field(
        ...,
        description="The original question",
    )

    route: str = Field(
        ...,
        description="The route taken to answer the question",
    )

    answer: str = Field(
        ...,
        description="The answer to the question",
    )

    sources: list[Source] = Field(
        ...,
        description="List of sources used to generate the answer",
    )


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

@app.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a financial question",
    description=(
        "Analyze a financial question using structured financial data, "
        "retrieval-augmented generation, or a hybrid approach."
    ),
    responses={
        400: {
            "description": "Question cannot be empty.",
        },
        422: {
            "description": "Invalid request format.",
        },
    },
)
def ask(
    request: Request,
    body: AskRequest,
    agent: FinancialAgent = Depends(get_agent),
):

    question = body.question.strip()

    request_id = request.state.request_id

    # --------------------------------------------------
    # Validate question
    # --------------------------------------------------

    if not question:

        logger.warning(
            "Empty question | request_id=%s",
            request_id,
        )

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # --------------------------------------------------
    # Log incoming question
    # --------------------------------------------------

    logger.info(
        "Received question | request_id=%s | question=%s",
        request_id,
        question,
    )

    # --------------------------------------------------
    # Process question
    # --------------------------------------------------

    try:

        result = agent.ask(question)

        logger.info(
            "Question classified | request_id=%s | route=%s",
            request_id,
            result["route"],
        )

        return {
            "question": question,
            "route": result["route"],
            "answer": result["answer"],
            "sources": result.get("sources", []),
        }

    except Exception as exc:

        logger.exception(
            "Error while processing question | "
            "request_id=%s | error=%s",
            request_id,
            exc,
        )

        raise AgentProcessingError(
            "Failed to process financial question."
        ) from exc