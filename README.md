# Financial AI Agent — Agentic Financial Assistant

An end-to-end AI-powered financial intelligence agent for querying and analyzing company quarterly reports, annual 10-K statements, and structured financial tables. Built with **FastAPI**, **SQLite**, **FAISS Vector Search**, **Sentence-Transformers**, and **Groq LLM (Llama 3.3 70B)**.

---

## 🌟 Key Features

1. **Multi-Format Data Ingestion**:
   - Ingests structured Excel (`.xlsx` / `.xls`) statements into normalized SQLite relational tables.
   - Extracts unstructured text and tables from annual and quarterly PDF reports (`.pdf`).
   - Chunks text with overlap, precomputes sentence embeddings (`all-MiniLM-L6-v2`), and indexes them using FAISS.

2. **Understanding Layer & Precomputation**:
   - **Precomputed Artifacts**: SQLite database (`financial.db`), FAISS vector index (`faiss.index`), text chunk store (`chunks.pkl`), and schema inventory (`excel_inventory.json`).
   - **Precomputed vs. On-the-Fly Trade-off**:
     - *Precomputed*: Exact numeric metric extraction, period normalization, and dense vector embeddings (drastically reduces query latency).
     - *On-the-Fly*: Hybrid reranking (combining semantic similarity + keyword overlap + fiscal period matching) and LLM response grounding.

3. **Data-Layer Role-Based Access Control (RBAC)**:
   - Enforced directly at the **database query layer** and **retrieval filtering layer**, not merely hidden in the UI.
   - **CEO**: Full access to all public and restricted financial metrics (e.g., headcount, compensation).
   - **CTO**: Access to technical & operational metrics, but restricted from headcount/compensation data.
   - **ANALYST**: Restricted to public operational metrics only.
   - Prevents data leakage when combining multiple sources or performing hybrid queries.

4. **Feedback & Learning Loop**:
   - Interactive feedback interface (Thumbs up / Thumbs down + correction memory box).
   - Records user feedback and corrections in `data/processed/feedback.json`.
   - Incorporates feedback into retrieval and few-shot correction memory to continuously improve agent answers over time.

5. **Prompt Injection Defense**:
   - `PromptGuard` security layer inspects incoming user queries for adversarial prompt overrides.
   - Sanitizes retrieved document text chunks to prevent indirect prompt injections embedded in ingested files.

6. **Web Interface & REST API**:
   - Responsive web dashboard running at `http://127.0.0.1:8000`.
   - Complete FastAPI REST API endpoints (`/ask`, `/feedback`, `/health`).

---

## 🏗 System Architecture

```text
                                  User Query
                                      |
                                      v
                          FastAPI Server / Web UI
                                      |
                                      v
                           Security PromptGuard
                                      |
                                      v
                              Financial Agent
                                      |
                    +-----------------+-----------------+
                    |                 |                 |
                    v                 v                 v
            Structured Route     Hybrid Route       RAG Route
                    |                 |                 |
                    v                 v                 v
             SQLite Database     Hybrid Retriever   FAISS RAG Search
             (Data-Layer RBAC)   (RBAC Filtered)   (RBAC Filtered)
                    |                 |                 |
                    +-----------------+-----------------+
                                      |
                                      v
                             Groq LLM (Llama 3.3)
                                      |
                                      v
                           Grounded Answer + Sources
                                      |
                                      v
                            Feedback & Learning Store
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Internet connection (for Groq API & Hugging Face embedding model)

### 1. Environment Setup
The environment configuration is specified in `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_PATH=data/processed/financial.db
FAISS_INDEX_PATH=data/processed/faiss.index
CHUNKS_PATH=data/processed/chunks.pkl
```

### 2. Run the Application
Start the FastAPI server & Web Interface:
```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```
Open your browser and navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### 3. Run Automated Tests
Run the test suite:
```bash
python -m pytest tests/
```

---

## 📈 What Fails at 100× Scale & How to Fix It

During real-world scaling (100× data volume and concurrent users), the following bottlenecks would occur:

1. **In-Memory FAISS Index & Local Pickle Storage**:
   - *Failure at Scale*: Holding vector indexes in local RAM (`faiss.index` & `chunks.pkl`) will cause Out-Of-Memory (OOM) errors as document chunks scale into millions.
   - *Production Solution*: Migrate vector storage to a distributed vector database like **Qdrant**, **Pinecone**, or **pgvector**.

2. **Single SQLite Relational File**:
   - *Failure at Scale*: SQLite handles concurrent reads well, but lacks write concurrency and distributed sharding.
   - *Production Solution*: Migrate to **PostgreSQL** with connection pooling (e.g., PgBouncer) and read replicas.

3. **Synchronous LLM API Calls**:
   - *Failure at Scale*: High concurrent user traffic will bottleneck single-threaded worker loops.
   - *Production Solution*: Implement asynchronous task queues with **Celery** / **Redis** and stream responses via WebSockets / Server-Sent Events (SSE).

4. **Embedding Generation Overhead**:
   - *Failure at Scale*: Encoding queries on the web thread can add ~100ms latency.
   - *Production Solution*: Deploy dedicated GPU embedding microservices using **Triton Inference Server** or **vLLM**.

---

## 🛡 Security & RBAC Matrix

| Role | Operational Revenue | Segment Breakdown | Headcount & Comp Data | Document Context |
|---|---|---|---|---|
| **CEO** | ✅ Allowed | ✅ Allowed | ✅ Allowed | ✅ Unfiltered |
| **CTO** | ✅ Allowed | ✅ Allowed | ❌ Denied | 🔒 Filtered |
| **ANALYST** | ✅ Allowed | ✅ Allowed | ❌ Denied | 🔒 Filtered |

---

## 📂 Project Structure

```text
financial-ai-agent/
├── app/
│   ├── agent/             # Financial Agent, Query Router, Query Parser, Comparison
│   ├── database/          # SQLite Queries & Data Access Layer
│   ├── feedback/          # Feedback Store & Correction Memory
│   ├── ingestion/         # PDF Parser, Excel Extractor, Text Chunker
│   ├── llm/               # Groq LLM Client
│   ├── rag/               # Financial RAG Pipeline
│   ├── retrieval/         # Retriever (FAISS + Keyword + Fiscal Matching)
│   ├── security/          # RBAC & Prompt Injection Guard
│   ├── api.py             # FastAPI REST Server & Static File Mount
│   └── config.py          # Environment & Application Settings
├── data/
│   ├── raw/               # Raw Excel & PDF Reports
│   └── processed/         # SQLite DB, FAISS Index, Chunks, Feedback Store
├── frontend/              # Web Dashboard (HTML, CSS, JS)
├── tests/                 # Automated Unit & Integration Tests
├── .env                   # API Keys & Configurations
├── requirements.txt       # Project Dependencies
└── README.md              # Documentation
```