"""
ReqTracer, Document Parser
Handles PDF and DOCX parsing with table extraction.
"""
import os
import re
from typing import List
from models import DocumentChunk

# ─── PDF Parsing ────────────────────────────────────────────────────
def parse_pdf(filepath: str) -> List[DocumentChunk]:
    """Parse a PDF file into document chunks."""
    import fitz  # PyMuPDF
    import pdfplumber

    filename = os.path.basename(filepath)
    chunks: List[DocumentChunk] = []

    # Extract text with PyMuPDF (better for text)
    doc = fitz.open(filepath)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            # Split into paragraphs
            paragraphs = _split_into_paragraphs(text)
            for para in paragraphs:
                if len(para.strip()) > 20:
                    section = _detect_section(para)
                    chunks.append(DocumentChunk(
                        text=para.strip(),
                        source=filename,
                        page=page_num + 1,
                        section=section
                    ))
    doc.close()

    # Extract tables with pdfplumber
    try:
        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    table_text = _table_to_text(table)
                    if table_text.strip():
                        chunks.append(DocumentChunk(
                            text=table_text,
                            source=filename,
                            page=page_num + 1,
                            section="[Table]"
                        ))
    except Exception:
        pass  # Tables are optional

    return chunks


# ─── DOCX Parsing ───────────────────────────────────────────────────
def parse_docx(filepath: str) -> List[DocumentChunk]:
    """Parse a DOCX file into document chunks."""
    from docx import Document

    filename = os.path.basename(filepath)
    chunks: List[DocumentChunk] = []
    doc = Document(filepath)

    current_section = ""
    current_text = ""
    page_estimate = 1

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            if current_text.strip() and len(current_text.strip()) > 20:
                chunks.append(DocumentChunk(
                    text=current_text.strip(),
                    source=filename,
                    page=page_estimate,
                    section=current_section
                ))
                current_text = ""
            continue

        # Check if heading
        if para.style and para.style.name and 'Heading' in para.style.name:
            if current_text.strip() and len(current_text.strip()) > 20:
                chunks.append(DocumentChunk(
                    text=current_text.strip(),
                    source=filename,
                    page=page_estimate,
                    section=current_section
                ))
                current_text = ""
            current_section = text
        else:
            current_text += text + "\n"

        # Rough page estimation (every ~3000 chars ≈ 1 page)
        if len(current_text) > 3000:
            page_estimate += 1

    # Don't forget the last chunk
    if current_text.strip() and len(current_text.strip()) > 20:
        chunks.append(DocumentChunk(
            text=current_text.strip(),
            source=filename,
            page=page_estimate,
            section=current_section
        ))

    # Extract tables
    for i, table in enumerate(doc.tables):
        table_text = _docx_table_to_text(table)
        if table_text.strip():
            chunks.append(DocumentChunk(
                text=table_text,
                source=filename,
                page=1,
                section="[Table]"
            ))

    return chunks


# ─── Helpers ────────────────────────────────────────────────────────
def _split_into_paragraphs(text: str) -> List[str]:
    """Split text into meaningful paragraphs."""
    paragraphs = re.split(r'\n\s*\n', text)
    result = []
    for p in paragraphs:
        p = p.strip()
        if p:
            # Further split very long paragraphs
            if len(p) > 1500:
                sentences = re.split(r'(?<=[.!?])\s+', p)
                current = ""
                for s in sentences:
                    if len(current) + len(s) > 800:
                        if current:
                            result.append(current)
                        current = s
                    else:
                        current += " " + s if current else s
                if current:
                    result.append(current)
            else:
                result.append(p)
    return result


def _detect_section(text: str) -> str:
    """Try to detect section headers from text."""
    lines = text.split('\n')
    first_line = lines[0].strip()
    # Check if first line looks like a heading
    if len(first_line) < 100 and (
        first_line.isupper() or
        re.match(r'^\d+[\.\)]\s+', first_line) or
        re.match(r'^[A-Z][a-z]', first_line) and len(first_line) < 60
    ):
        return first_line
    return ""


def _table_to_text(table: list) -> str:
    """Convert a pdfplumber table to readable text."""
    if not table:
        return ""
    rows = []
    for row in table:
        cells = [str(c).strip() if c else "" for c in row]
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def _docx_table_to_text(table) -> str:
    """Convert a python-docx table to readable text."""
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def parse_document(filepath: str) -> List[DocumentChunk]:
    """Parse any supported document format."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return parse_pdf(filepath)
    elif ext in ('.docx', '.doc'):
        return parse_docx(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
