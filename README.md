# 💰 Financial AI Agent

An AI-powered financial analysis assistant that answers questions about company financials using a combination of structured SQL queries, Retrieval-Augmented Generation (RAG), and hybrid approaches — with role-based access control and a clean web UI.

---

## ✨ Features

- **Intelligent Query Routing** — Automatically classifies questions as structured, RAG, or hybrid based on keyword analysis
- **Structured Queries** — Fetches exact numerical facts (revenue, headcount, etc.) directly from a SQLite database
- **RAG Pipeline** — Uses FAISS vector search + `fastembed` embeddings to retrieve and synthesize context from financial documents (PDF/Excel)
- **Hybrid Mode** — Combines structured data with qualitative context for richer answers
- **Role-Based Access Control (RBAC)** — Three roles with different data permissions:
  | Role | Access |
  |----------|----------------------------------------------|
  | `CEO` | All metrics (public + restricted) |
  | `CTO` | Public revenue metrics only |
  | `ANALYST` | Public revenue metrics only |
- **Prompt Injection Guard** — Detects and blocks malicious or prompt-injection attempts
- **Feedback System** — Users can rate answers and submit corrections
- **Interactive Web UI** — Single-page frontend served directly by the FastAPI app
- **Docker Support** — Fully containerized for easy deployment
- **Render-ready** — Includes `render.yaml` and `Procfile` for one-click cloud deployment

---

## 🏗️ Architecture

```
financial-ai-agent/
├── app/
│   ├── agent/
│   │   ├── financial_agent.py   # Orchestrates routing + answering
│   │   ├── router.py            # Keyword-based query classifier
│   │   ├── query_parser.py      # Parses fiscal periods and metrics
│   │   ├── analysis.py          # Structured data analysis logic
│   │   ├── comparison.py        # Period-over-period comparisons
│   │   └── hybrid.py            # Hybrid context builder
│   ├── rag/
│   │   └── pipeline.py          # FAISS + fastembed RAG pipeline
│   ├── database/
│   │   └── financial_queries.py # SQLite query layer
│   ├── ingestion/               # PDF & Excel data ingestion
│   ├── retrieval/               # Vector store & chunk management
│   ├── security/
│   │   ├── rbac.py              # Role & permission definitions
│   │   └── prompt_guard.py      # Prompt injection detection
│   ├── feedback/                # Feedback storage
│   ├── config.py                # Centralized settings (env-driven)
│   └── api.py                   # FastAPI app + REST endpoints
├── frontend/
│   ├── index.html               # Web UI
│   ├── app.js                   # Frontend logic
│   └── style.css                # Styling
├── data/
│   └── processed/               # SQLite DB, FAISS index, chunks
├── scripts/                     # Ingestion & debug utilities
├── tests/                       # Pytest test suite
├── Dockerfile
├── docker-compose.yml
└── render.yaml
```

---

## 🚀 Quick Start

### Prerequisites

- Python **3.11+**
- A **Groq** or **Gemini** API key

### 1. Clone the repository

```bash
git clone https://github.com/your-username/financial-ai-agent.git
cd financial-ai-agent
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Or for Gemini:
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Processed data paths (defaults shown)
DATABASE_PATH=data/processed/financial.db
FAISS_INDEX_PATH=data/processed/faiss.index
CHUNKS_PATH=data/processed/chunks.pkl
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Ingest your financial data

Place your raw Excel/PDF financial files in `data/raw/`, then run the ingestion pipeline:

```bash
python scripts/ingest.py
```

This will build the SQLite database and FAISS vector index in `data/processed/`.

### 5. Start the server

**Linux / macOS:**
```bash
bash start_server.sh
```

**Windows:**
```bat
start_server.bat
```

**Or directly with uvicorn:**
```bash
python -m uvicorn app.api:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** in your browser.

---

## 🐳 Docker

Build and run with Docker Compose:

```bash
docker-compose up --build
```

Or build and run manually:

```bash
docker build -t financial-ai-agent .
docker run -p 8000:8000 --env-file .env financial-ai-agent
```

---

## ☁️ Deploy to Render

This project ships with a `render.yaml` for instant deployment:

1. Push the repo to GitHub
2. Go to [render.com](https://render.com) → **New Web Service** → Connect your repo
3. Render will auto-detect `render.yaml` and configure the service
4. Add your environment variables (API keys) in the Render dashboard

---

## 📡 API Reference

### `GET /health`

Health check endpoint.

```json
{ "status": "healthy", "service": "financial-ai-agent" }
```

---

### `POST /ask`

Ask a financial question.

**Request body:**
```json
{
  "question": "What was the iPhone revenue in FY2024?",
  "role": "CEO"
}
```

| Field | Type | Required | Description |
|----------|--------|----------|--------------------------------------|
| `question` | string | ✅ | The financial question to analyze |
| `role` | string | ❌ | `CEO`, `CTO`, or `ANALYST` (default: `CEO`) |

**Response:**
```json
{
  "question": "What was the iPhone revenue in FY2024?",
  "route": "structured",
  "answer": "iPhone revenue in FY2024 was $201.18 billion.",
  "sources": [
    {
      "source_file": "apple_financials.xlsx",
      "source_sheet": "Revenue",
      "source_row": 12
    }
  ]
}
```

| Field | Description |
|---------|------------------------------------------------------|
| `route` | `structured`, `rag`, `hybrid`, or `security_blocked` |
| `sources` | Data sources used to generate the answer |

---

### `POST /feedback`

Submit feedback on an answer.

**Request body:**
```json
{
  "question": "What was the iPhone revenue in FY2024?",
  "role": "CEO",
  "rating": 1,
  "route": "structured",
  "answer": "iPhone revenue in FY2024 was $201.18 billion.",
  "correction": ""
}
```

| Field | Type | Description |
|------------|--------|--------------------------------------|
| `rating` | int | `+1` for positive, `-1` for negative |
| `correction` | string | Optional corrected answer |

---

## 🔐 Security

- **RBAC**: Role normalization is enforced on every request. Invalid roles return `HTTP 400`.
- **Prompt Injection Guard**: All questions are screened by `PromptGuard` before processing. Detected attacks return a `security_blocked` route with no LLM invocation.
- **No credentials in code**: All secrets are loaded exclusively from environment variables via `python-dotenv`.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Individual script-level tests are also available in `scripts/`:

```bash
python scripts/test_agent.py
python scripts/test_rag.py
python scripts/test_hybrid.py
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|------------|------------------------------------------------------|
| Backend | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| LLM | [Groq](https://groq.com/) (`llama-3.3-70b-versatile`) / Gemini |
| Embeddings | [fastembed](https://github.com/qdrant/fastembed) (`all-MiniLM-L6-v2`) |
| Vector DB | [FAISS](https://github.com/facebookresearch/faiss) |
| Structured DB | SQLite via Python `sqlite3` |
| Data parsing | `pandas`, `PyMuPDF`, `openpyxl`, `xlrd` |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Deployment | Docker, Render |

---

## 📄 License

This project is licensed under the MIT License.
