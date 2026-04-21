"""
ReqTracer, Main FastAPI Application
AI-based platform for requirements extraction, Q/A, and test plan generation.
"""
import os
import sys

# Prevent Keras 3 / TensorFlow compatibility issues — we only use PyTorch
os.environ["KERAS_BACKEND"] = "torch"
os.environ["TF_USE_LEGACY_KERAS"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["USE_TORCH"] = "1"
os.environ["TRANSFORMERS_NO_TF"] = "1"
import uuid
import json
import shutil
from typing import Dict, List

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import Document, Requirement, TestCase
from parser import parse_document
from requirements_extractor import extract_requirements
from rag import build_index, query as rag_query, clear_document_from_index, get_index_stats
from test_generator import generate_test_cases
from exporter import export_excel, export_json

# ─── App Setup ──────────────────────────────────────────────────────
app = FastAPI(
    title="ReqTracer",
    description="AI-based Requirements Engineering & Test Plan Generation Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Storage ────────────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# In-memory stores (per session)
documents_store: Dict[str, Document] = {}
chunks_store: Dict[str, list] = {}
requirements_store: Dict[str, List[Requirement]] = {}
test_cases_store: Dict[str, List[TestCase]] = {}

# ─── Static Files (Frontend) ───────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ─── Root → Frontend ───────────────────────────────────────────────
@app.get("/")
async def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "ReqTracer API is running. Frontend not found."}


# ─── Upload & Parse ─────────────────────────────────────────────────
@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or DOCX document for analysis."""
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.pdf', '.docx', '.doc'):
        raise HTTPException(400, "Unsupported file type. Please upload PDF or DOCX.")

    # Save file
    doc_id = str(uuid.uuid4())[:8]
    safe_name = f"{doc_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, safe_name)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        # Parse document
        chunks = parse_document(filepath)
        if not chunks:
            raise HTTPException(400, "Could not extract text from the document.")

        # Store chunks
        chunks_store[doc_id] = chunks

        # Build RAG index
        total_indexed = build_index(chunks)

        # Extract requirements
        reqs = extract_requirements(chunks, doc_id)
        requirements_store[doc_id] = reqs

        # Create document metadata
        doc = Document(
            doc_id=doc_id,
            filename=file.filename,
            num_pages=max(c.page for c in chunks),
            num_chunks=len(chunks),
            num_requirements=len(reqs)
        )
        documents_store[doc_id] = doc

        return {
            "status": "success",
            "document": doc.to_dict(),
            "message": f"Parsed {len(chunks)} chunks, extracted {len(reqs)} requirements."
        }

    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(500, f"Error processing document: {str(e)}")


# ─── Documents ──────────────────────────────────────────────────────
@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents."""
    return {
        "documents": [doc.to_dict() for doc in documents_store.values()]
    }


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get details for a specific document."""
    if doc_id not in documents_store:
        raise HTTPException(404, "Document not found.")
    return documents_store[doc_id].to_dict()


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its data."""
    if doc_id not in documents_store:
        raise HTTPException(404, "Document not found.")

    doc = documents_store[doc_id]
    clear_document_from_index(doc.filename)

    # Clean up stores
    documents_store.pop(doc_id, None)
    chunks_store.pop(doc_id, None)
    requirements_store.pop(doc_id, None)
    test_cases_store.pop(doc_id, None)

    # Remove files
    for f in os.listdir(UPLOAD_DIR):
        if f.startswith(doc_id):
            os.remove(os.path.join(UPLOAD_DIR, f))

    return {"status": "deleted", "doc_id": doc_id}


# ─── Requirements ───────────────────────────────────────────────────
@app.get("/api/requirements/{doc_id}")
async def get_requirements(doc_id: str):
    """Get extracted requirements for a document."""
    if doc_id not in documents_store:
        raise HTTPException(404, "Document not found.")

    reqs = requirements_store.get(doc_id, [])
    return {
        "doc_id": doc_id,
        "total": len(reqs),
        "requirements": [r.to_dict() for r in reqs]
    }


# ─── Q/A (RAG) ─────────────────────────────────────────────────────
@app.post("/api/qa")
async def question_answer(body: dict):
    """Ask a question about uploaded documents using RAG."""
    question = body.get("question", "").strip()
    if not question:
        raise HTTPException(400, "Question is required.")

    top_k = body.get("top_k", 5)
    result = rag_query(question, top_k=top_k)

    return result.to_dict()


# ─── Test Generation ────────────────────────────────────────────────
@app.post("/api/generate-tests/{doc_id}")
async def generate_tests(doc_id: str):
    """Generate test cases for a document's requirements."""
    if doc_id not in documents_store:
        raise HTTPException(404, "Document not found.")

    reqs = requirements_store.get(doc_id, [])
    if not reqs:
        raise HTTPException(400, "No requirements found. Upload and parse a document first.")

    test_cases = generate_test_cases(reqs)
    test_cases_store[doc_id] = test_cases

    # Update document metadata
    documents_store[doc_id].num_test_cases = len(test_cases)

    return {
        "doc_id": doc_id,
        "total_test_cases": len(test_cases),
        "test_cases": [tc.to_dict() for tc in test_cases]
    }


# ─── Test Cases Retrieval ───────────────────────────────────────────
@app.get("/api/test-cases/{doc_id}")
async def get_test_cases(doc_id: str):
    """Get generated test cases for a document."""
    if doc_id not in documents_store:
        raise HTTPException(404, "Document not found.")

    tcs = test_cases_store.get(doc_id, [])
    return {
        "doc_id": doc_id,
        "total": len(tcs),
        "test_cases": [tc.to_dict() for tc in tcs]
    }


# ─── Export ─────────────────────────────────────────────────────────
@app.get("/api/export/{doc_id}/{fmt}")
async def export_data(doc_id: str, fmt: str):
    """Export test plan as Excel or JSON."""
    if doc_id not in documents_store:
        raise HTTPException(404, "Document not found.")

    reqs = requirements_store.get(doc_id, [])
    tcs = test_cases_store.get(doc_id, [])

    if not reqs:
        raise HTTPException(400, "No requirements found for this document.")

    doc = documents_store[doc_id]
    doc_name = os.path.splitext(doc.filename)[0]

    if fmt == "excel":
        output_path = os.path.join(EXPORT_DIR, f"{doc_id}_test_plan.xlsx")
        export_excel(reqs, tcs, output_path, doc_name)
        return FileResponse(
            output_path,
            filename=f"{doc_name}_test_plan.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    elif fmt == "json":
        output_path = os.path.join(EXPORT_DIR, f"{doc_id}_test_plan.json")
        export_json(reqs, tcs, output_path, doc_name)
        return FileResponse(
            output_path,
            filename=f"{doc_name}_test_plan.json",
            media_type="application/json"
        )
    else:
        raise HTTPException(400, "Unsupported format. Use 'excel' or 'json'.")


# ─── Stats ──────────────────────────────────────────────────────────
@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    rag_stats = get_index_stats()
    return {
        "documents": len(documents_store),
        "total_requirements": sum(len(r) for r in requirements_store.values()),
        "total_test_cases": sum(len(t) for t in test_cases_store.values()),
        "rag_index": rag_stats
    }


# ─── Domain Packs ──────────────────────────────────────────────────
@app.get("/api/domain-packs")
async def list_domain_packs():
    """List available domain pack sample documents."""
    packs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "domain_packs")
    if not os.path.exists(packs_dir):
        return {"packs": []}

    packs = []
    for f in os.listdir(packs_dir):
        if f.endswith(('.docx', '.pdf')):
            name = os.path.splitext(f)[0].replace('_', ' ').title()
            packs.append({"filename": f, "name": name, "path": os.path.join(packs_dir, f)})

    return {"packs": packs}


@app.post("/api/load-domain-pack/{filename}")
async def load_domain_pack(filename: str):
    """Load a domain pack as if it were uploaded."""
    packs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "domain_packs")
    filepath = os.path.join(packs_dir, filename)

    if not os.path.exists(filepath):
        raise HTTPException(404, f"Domain pack '{filename}' not found.")

    doc_id = str(uuid.uuid4())[:8]

    # Copy to uploads
    dest = os.path.join(UPLOAD_DIR, f"{doc_id}_{filename}")
    shutil.copy2(filepath, dest)

    try:
        chunks = parse_document(dest)
        if not chunks:
            raise HTTPException(400, "Could not extract text from the domain pack.")

        chunks_store[doc_id] = chunks
        build_index(chunks)

        reqs = extract_requirements(chunks, doc_id)
        requirements_store[doc_id] = reqs

        doc = Document(
            doc_id=doc_id,
            filename=filename,
            num_pages=max(c.page for c in chunks),
            num_chunks=len(chunks),
            num_requirements=len(reqs)
        )
        documents_store[doc_id] = doc

        return {
            "status": "success",
            "document": doc.to_dict(),
            "message": f"Loaded domain pack: {filename}. {len(chunks)} chunks, {len(reqs)} requirements."
        }
    except Exception as e:
        raise HTTPException(500, f"Error loading domain pack: {str(e)}")


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  ReqTracer, AI Requirements & Test Plan Platform")
    print("  Starting server at http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)
