# 🤖 Financial AI Agent

> An enterprise-grade AI-powered financial analysis platform with agentic reasoning, multi-source RAG, data-layer RBAC, and a real-time corporate intelligence terminal.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-financial--ai--agent-brightgreen?style=for-the-badge&logo=render)](https://financial-ai-agent-3xzs.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-orange?style=for-the-badge)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 🌐 Live Demo

**[https://financial-ai-agent-3xzs.onrender.com](https://financial-ai-agent-3xzs.onrender.com)**

> ⚠️ Hosted on Render free tier — first request may take ~30 seconds to wake up.

---

## 📋 Overview

The **Financial AI Agent** is a production-ready intelligent financial assistant that answers natural language questions about Apple Inc.'s financial performance. It combines:

- **Structured SQL queries** over quarterly earnings data (Excel ingestion)
- **Semantic vector search** over official SEC 10-K and 10-Q PDF filings (FAISS RAG)
- **Hybrid reasoning** that fuses SQL facts with document commentary
- **Data-layer RBAC** that restricts sensitive metrics based on user role
- **Self-improving feedback loop** that captures corrections and ratings

---

## ✨ Key Features

### 🧠 Agentic Multi-Route Query System
The agent intelligently classifies every query and routes it to the optimal retrieval strategy:

| Route | When Used | Example Query |
|---|---|---|
| **Structured SQL** | Exact quantitative metrics | *"What was iPhone revenue in Q1 FY25?"* |
| **Document RAG** | Strategy, narrative, qualitative | *"What is Apple's approach to services growth?"* |
| **Hybrid Analysis** | Combined facts + commentary | *"Why did revenue change from Q2 to Q3 FY24?"* |

### 🔒 Data-Layer Role-Based Access Control (RBAC)
Security is enforced **at the database and vector store level** — not just in prompt instructions.

| Role | Revenue & Financials | Headcount | Executive Compensation |
|---|---|---|---|
| **CEO** | ✅ Full Access | ✅ Full Access | ✅ Full Access |
| **CTO** | ✅ Full Access | 🔴 Restricted | 🔴 Restricted |
| **ANALYST** | ✅ Full Access | 🔴 Restricted | 🔴 Restricted |

### 📊 Official SEC Data Coverage
- **Apple Inc. Form 10-K FY2024**: 164,000 employees (headcount)
- **Apple Inc. Form 10-K FY2023**: 161,000 employees (headcount)
- **Share-Based Compensation**: $8,830M (FY2024)
- **Quarterly Revenue Breakdown**: iPhone, Mac, iPad, Services, Wearables (FY23–FY25)

### 🛡️ Prompt Injection Guard
Detects and blocks adversarial prompts that attempt to override system instructions or extract restricted data.

### 🔁 Self-Improving Feedback Loop
Users can rate responses (👍 Accurate / 👎 Incorrect) and submit corrections, which are persisted to a feedback store and used to improve future responses.

---

## 🏗️ Architecture

```
financial-ai-agent/
├── app/
│   ├── agent/
│   │   ├── financial_agent.py     # Core orchestrator agent
│   │   ├── router.py              # Query classification & routing
│   │   ├── query_parser.py        # NLP metric + period extraction
│   │   └── comparison_engine.py  # Period-over-period delta calculations
│   ├── database/
│   │   └── financial_queries.py  # SQLite query helpers
│   ├── rag/
│   │   └── pipeline.py            # Hybrid RAG pipeline
│   ├── retrieval/
│   │   ├── retriever.py           # FAISS vector retriever + RBAC filter
│   │   └── vector_store.py        # FAISS index builder
│   ├── security/
│   │   ├── rbac.py                # Role-based metric access control
│   │   └── prompt_guard.py        # Prompt injection defense
│   ├── feedback/
│   │   └── feedback_store.py      # User feedback persistence
│   ├── llm/
│   │   └── gemini_client.py       # Groq LLaMA 3.3 70B client
│   ├── ingestion/
│   │   └── excel_ingester.py      # Excel → SQLite ingestion pipeline
│   └── api.py                     # FastAPI REST endpoints
├── data/
│   ├── raw/                       # Source Excel + PDF filings
│   └── processed/
│       ├── financial.db           # SQLite database
│       ├── faiss.index            # FAISS vector index
│       └── chunks.pkl             # Document chunk metadata
├── frontend/
│   ├── index.html                 # Corporate terminal UI
│   ├── style.css                  # Monochrome design system
│   └── app.js                     # Interactive dashboard logic
├── tests/                         # 65 unit & integration tests
├── Dockerfile                     # Container definition
├── render.yaml                    # Render cloud deployment config
└── requirements.txt               # Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Groq API Key](https://console.groq.com) (free)

### 1. Clone the Repository
```bash
git clone https://github.com/5hashankyadav/financial_ai_agent.git
cd financial_ai_agent
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the project root:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```
Get your free API key at [https://console.groq.com](https://console.groq.com)

### 4. Run the Server
**Windows:**
```bash
start_server.bat
```

**Mac/Linux:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**Manual:**
```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Open the Dashboard
Navigate to **[http://localhost:8000](http://localhost:8000)**

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

**65 / 65 tests passing** covering:
- Query parser and router classification
- SQL metric retrieval
- FAISS vector search and reranking
- RBAC enforcement (per-role metric access)
- Prompt injection detection
- Feedback store persistence
- FastAPI endpoint integration tests

---

## 🔌 API Reference

### `POST /ask`
Ask a financial question.

**Request:**
```json
{
  "question": "What was Apple's total revenue in Q1 FY25?",
  "role": "CEO",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "answer": "Apple's total revenue in Q1 FY25 was $124,300M...",
  "route": "structured",
  "sources": ["Q1_FY25_10Q.pdf"],
  "confidence": 0.97,
  "session_id": "abc-123"
}
```

---

### `POST /feedback`
Submit a rating or correction on a response.

**Request:**
```json
{
  "session_id": "abc-123",
  "rating": "thumbs_up",
  "correction": null
}
```

---

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## ☁️ Cloud Deployment (Render)

This project is pre-configured for zero-config deployment on [Render.com](https://render.com):

1. Fork this repository to your GitHub account.
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service**.
3. Connect your forked repository.
4. Add environment variable: `GROQ_API_KEY` = your Groq API key.
5. Click **Create Web Service**.

Render auto-detects `render.yaml` and configures the build and start commands.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq API — LLaMA 3.3 70B Versatile |
| **Embeddings** | `sentence-transformers` — `all-MiniLM-L6-v2` |
| **Vector Store** | FAISS (CPU) |
| **Database** | SQLite |
| **API Framework** | FastAPI + Uvicorn |
| **PDF Parsing** | PyMuPDF |
| **Excel Parsing** | Pandas + OpenPyXL + xlrd |
| **Security** | Custom RBAC + Prompt Guard |
| **Frontend** | Vanilla HTML/CSS/JS (Zero dependencies) |
| **Deployment** | Render.com (Docker) |

---

## 📄 Data Sources

All financial data is sourced from official public filings:

- **Apple Inc. Annual Reports (10-K)**: FY2022, FY2023, FY2024
- **Apple Inc. Quarterly Reports (10-Q)**: Q1–Q3 FY2023, FY2024, FY2025
- **Apple Earnings Excel Workbooks**: Official investor relations downloads

---

## 📸 Screenshots

### Corporate Intelligence Terminal
The dashboard features a luxury monochrome (black & white) design with:
- Natural language query input with quick-prompt chips
- Role selector (CEO / CTO / ANALYST)
- Source document attribution cards
- Query history with search capability
- Feedback rating system

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 👤 Author

**Shashank Yadav**
- GitHub: [@5hashankyadav](https://github.com/5hashankyadav)
- Live Project: [financial-ai-agent-3xzs.onrender.com](https://financial-ai-agent-3xzs.onrender.com)

---

*Built as part of an AI Agent Developer technical assignment — demonstrating production-grade agentic AI, secure data access patterns, and cloud deployment.*