# ReqTracer, AI Requirements & Test Plan Platform

> **AI-powered requirements engineering tool** that reads specifications (PDF/DOCX), extracts structured requirements, answers questions with citations (RAG), generates traceable test plans, and exports to Excel/JSON.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Features

| Feature | Description |
|---------|-------------|
| **Document Import** | PDF and DOCX parsing with table extraction |
| **Requirements Extraction** | Auto-extracts REQ-IDs, classifies type (functional/performance/interface/security) and priority |
| **RAG Q/A** | Ask questions and get answers with source citations (FAISS + sentence-transformers) |
| **Test Generation** | Generates structured test cases (Goal, Prerequisites, Procedure, Inputs, Oracles, Pass/Fail) |
| **Traceability** | Full REQ ↔ TC mapping matrix |
| **Export** | Excel (.xlsx with 3 sheets) and JSON export |
| **Domain Packs** | Pre-built specs: Automotive (AVAS), Energy (Smart Grid), Railway (Signaling) |

---

## Quick Start

### Option 1: Local (pip)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Generate domain packs (demo data)
python domain_packs_generator.py

# 3. Start the server
python main.py
```

Open **http://localhost:8000** in your browser.

### Option 2: Docker Compose

```bash
docker compose up --build
```

Open **http://localhost:8000**.

---

## Demo Walkthrough

1. **Upload** → Click a domain pack (e.g., "Automotive, AVAS") or upload your own PDF/DOCX
2. **Requirements** → View extracted requirements with type/priority badges, use filters
3. **Q/A** → Ask: *"What are the sound level requirements?"* → Get answer with page citations
4. **Tests** → Click "Generate" → View structured test cases with expandable details
5. **Export** → Download Excel (3 sheets: Requirements, Tests, Trace) or JSON

---

## Architecture

```
Projet/
├── backend/
│   ├── main.py                    # FastAPI app + API endpoints
│   ├── models.py                  # Data models (Requirement, TestCase, etc.)
│   ├── parser.py                  # PDF/DOCX parser + table extraction
│   ├── requirements_extractor.py  # Requirement detection & classification
│   ├── rag.py                     # RAG pipeline (FAISS + embeddings)
│   ├── test_generator.py          # Test case generation engine
│   ├── exporter.py                # Excel/JSON export
│   ├── domain_packs_generator.py  # Synthetic spec generator
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── index.html                 # Single-page application
│   ├── styles.css                 # White + orange design system
│   └── app.js                     # Frontend logic
├── domain_packs/                  # Generated sample specifications
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **NLP/AI**: sentence-transformers (`all-MiniLM-L6-v2`), FAISS (vector search)
- **Parsing**: PyMuPDF, python-docx, pdfplumber
- **Export**: openpyxl (Excel), JSON
- **Frontend**: Vanilla HTML/CSS/JS (no framework dependency)
- **Deploy**: Docker Compose

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload PDF/DOCX |
| `/api/documents` | GET | List documents |
| `/api/documents/{id}` | DELETE | Delete document |
| `/api/requirements/{id}` | GET | Get requirements |
| `/api/qa` | POST | Ask question (RAG) |
| `/api/generate-tests/{id}` | POST | Generate test cases |
| `/api/test-cases/{id}` | GET | Get test cases |
| `/api/export/{id}/{format}` | GET | Export (excel/json) |
| `/api/domain-packs` | GET | List domain packs |
| `/api/load-domain-pack/{name}` | POST | Load domain pack |
| `/api/stats` | GET | System statistics |

---

## Limitations (v1)

- Extractive Q/A only (no LLM generation), works offline, no API keys needed
- Requirements extraction uses heuristics (pattern + keyword matching)
- Test generation is template-based, not AI-generated
- In-memory storage (data resets on server restart)
- Embedding model downloads on first run (~90 MB)
