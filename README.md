# Financial AI Agent

An AI-powered financial analysis system for answering questions over quarterly financial reports using structured financial data, hybrid retrieval, and Google Gemini.

## Features

- Structured financial querying using SQLite
- PDF document ingestion
- Text chunking with overlap
- Semantic retrieval using Sentence Transformers
- FAISS vector search
- Hybrid retrieval with:
  - Semantic similarity
  - Keyword overlap
  - Fiscal-period matching
- Google Gemini-powered grounded answers
- Automatic question routing:
  - Structured
  - Hybrid
  - RAG
- Source attribution with document and page information
- FastAPI REST API
- Request ID tracking
- Request timing and structured logging
- Comprehensive automated tests

---

## Architecture

```text
                    User
                      |
                      v
                FastAPI /ask
                      |
                      v
              Financial Agent
                      |
              +-------+-------+
              |               |
              v               v
        Structured Route    RAG/Hybrid
              |               |
              v               v
        SQLite Database     Retriever
                              |
                    +---------+---------+
                    |                   |
                    v                   v
              FAISS Search       Keyword Matching
                    |                   |
                    +---------+---------+
                              |
                       Period Matching
                              |
                              v
                         Reranking
                              |
                              v
                         Context
                              |
                              v
                           Gemini
                              |
                              v
                       Grounded Answer