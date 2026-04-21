# ReqTracer, AI Requirements & Test Plan Platform

Build a local-first AI tool that reads specifications (PDF/DOCX), answers questions with citations (RAG), extracts structured requirements, generates traceable test plans, and exports to Excel/JSON.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| NLP/AI | sentence-transformers (`all-MiniLM-L6-v2`), FAISS, OpenAI/Ollama (optional) |
| Parsing | PyMuPDF (fitz), python-docx, pdfplumber (tables) |
| Export | openpyxl, json |
| Frontend | Vanilla HTML/CSS/JS (no framework) |
| Deploy | Docker Compose |

---

## Proposed Changes

### 1. Project Skeleton

#### [NEW] [requirements.txt](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/backend/requirements.txt)
All Python deps: fastapi, uvicorn, faiss-cpu, sentence-transformers, pymupdf, python-docx, pdfplumber, openpyxl, etc.

#### [NEW] [main.py](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/backend/main.py)
FastAPI app entry point. Mounts `/static` for the frontend. CORS middleware.

---

### 2. Document Parser

#### [NEW] [parser.py](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/backend/parser.py)
- `parse_pdf(path)` → list of chunks with page/section metadata
- `parse_docx(path)` → same, including table extraction
- Normalizes both formats into unified `DocumentChunk(text, source, page, section)` model

---

### 3. Requirements Extractor

#### [NEW] [requirements_extractor.py](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/backend/requirements_extractor.py)
- Pattern-based + heuristic extraction of requirements from chunks
- Assigns REQ-IDs, classifies type (functional / performance / interface / security), and priority (high/medium/low)
- Uses keyword dictionaries for classification

---

### 4. RAG Pipeline

#### [NEW] [rag.py](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/backend/rag.py)
- `build_index(chunks)` → FAISS index + metadata store
- `query(question, top_k)` → ranked passages with page/section citations
- Embedding via `sentence-transformers/all-MiniLM-L6-v2` (runs offline)
- Optional reranker (cross-encoder) for improved precision

---

### 5. Test Case Generator

#### [NEW] [test_generator.py](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/backend/test_generator.py)
- Takes structured requirements → generates test cases with fields: Goal, Prerequisites, Procedure, Inputs/Signals, Thresholds/Oracles, Expected Pass/Fail
- Template-based generation with rule engine
- Maps each test case back to its source requirement (traceability)

---

### 6. Export Engine

#### [NEW] [exporter.py](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/backend/exporter.py)
- `export_excel(requirements, test_cases)` → .xlsx with two sheets: "Tests" and "Trace"
- `export_json(requirements, test_cases)` → structured JSON
- Tests sheet: TC-ID, Goal, Prerequisites, Procedure, Inputs, Oracles, Expected
- Trace sheet: REQ-ID ↔ TC-ID mapping

---

### 7. API Endpoints (`main.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | Upload PDF/DOCX, parse & index |
| `/api/documents` | GET | List uploaded documents |
| `/api/requirements/{doc_id}` | GET | Get extracted requirements |
| `/api/qa` | POST | Ask question (RAG), get answer+citations |
| `/api/generate-tests/{doc_id}` | POST | Generate test cases |
| `/api/export/{doc_id}/{format}` | GET | Download Excel or JSON |

---

### 8. Frontend (White + Orange Premium UI)

#### [NEW] [index.html](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/frontend/index.html)
Single-page app with animated sections: Upload → Requirements → Q/A → Tests → Export

#### [NEW] [styles.css](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/frontend/styles.css)
- Color palette: white (#FFFFFF), orange (#FF6B35, #FF8C42), dark (#1A1A2E)
- Glassmorphism cards, smooth transitions, micro-animations
- Responsive grid layout

#### [NEW] [app.js](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/frontend/app.js)
- File upload with drag-and-drop + progress animation
- Requirements table with filtering/sorting
- Chat-style Q/A with citation highlights
- Test plan viewer with traceability links
- Export trigger buttons

---

### 9. Domain Packs (Synthetic Specs)

#### [NEW] Automotive pack, `domain_packs/automotive_avas.docx`
AVAS (Acoustic Vehicle Alerting System) specification with ~15 requirements covering sound levels, frequency ranges, speed thresholds.

#### [NEW] Energy pack, `domain_packs/energy_grid.docx`
Smart grid monitoring spec with ~12 requirements covering voltage monitoring, alarm thresholds, data logging.

#### [NEW] Railway pack, `domain_packs/railway_signaling.docx`
Railway signaling spec with ~12 requirements covering signal states, interlocking logic, failsafe behavior.

> **Note:** Domain packs will be generated as `.docx` files using python-docx during build.

---

### 10. Docker & Documentation

#### [NEW] [Dockerfile](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/Dockerfile)
Python 3.11, install deps, copy app, expose port 8000.

#### [NEW] [docker-compose.yml](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/docker-compose.yml)
Single service `reqtracer` with volume mount for uploads.

#### [NEW] [README.md](file:///c:/Users/Adam%20Elmadani/Desktop/Projet/README.md)
Installation (pip / Docker), launch, demo walkthrough, architecture overview, limitations.

---

## Verification Plan

### Automated (Browser-based)
1. Start server with `cd backend && python main.py`
2. Open `http://localhost:8000` in browser
3. Upload a sample domain pack document
4. Verify requirements appear in the requirements panel
5. Ask a question in the Q/A panel and verify citations appear
6. Generate test cases and verify the traceability matrix
7. Export Excel and JSON and verify downloads

### Manual
- User can try uploading their own PDF/DOCX after demo
- User can verify Excel output opens correctly in their spreadsheet app
