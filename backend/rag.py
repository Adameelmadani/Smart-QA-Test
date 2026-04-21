"""
ReqTracer, RAG Pipeline
Retrieval-Augmented Generation using FAISS + sentence-transformers.
"""
import os

# Prevent Keras 3 / TensorFlow compatibility issues — we only use PyTorch
os.environ.setdefault("KERAS_BACKEND", "torch")
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from models import DocumentChunk, QAResult

# ─── Globals ────────────────────────────────────────────────────────
_model = None
_index = None
_chunks_store: List[DocumentChunk] = []

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBED_DIM = 384


def _get_model():
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def _get_embeddings(texts: List[str]) -> np.ndarray:
    """Compute embeddings for a list of texts."""
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return np.array(embeddings, dtype=np.float32)


# ─── Index Management ───────────────────────────────────────────────
def build_index(chunks: List[DocumentChunk]) -> int:
    """Build or update the FAISS index from document chunks."""
    global _index, _chunks_store
    import faiss

    if not chunks:
        return 0

    texts = [c.text for c in chunks]
    embeddings = _get_embeddings(texts)

    if _index is None:
        _index = faiss.IndexFlatIP(EMBED_DIM)  # Inner product (cosine with normalized vecs)
        _chunks_store = []

    _index.add(embeddings)
    _chunks_store.extend(chunks)

    return len(_chunks_store)


def clear_index():
    """Clear the entire index."""
    global _index, _chunks_store
    _index = None
    _chunks_store = []


def clear_document_from_index(source: str):
    """Remove chunks for a specific document and rebuild index."""
    global _chunks_store
    _chunks_store = [c for c in _chunks_store if c.source != source]
    if _chunks_store:
        rebuild_index()
    else:
        clear_index()


def rebuild_index():
    """Rebuild the index from current chunks store."""
    global _index
    import faiss

    if not _chunks_store:
        _index = None
        return

    texts = [c.text for c in _chunks_store]
    embeddings = _get_embeddings(texts)
    _index = faiss.IndexFlatIP(EMBED_DIM)
    _index.add(embeddings)


# ─── Query ──────────────────────────────────────────────────────────
def query(question: str, top_k: int = 5) -> QAResult:
    """Query the RAG system and get an answer with citations."""
    global _index, _chunks_store

    if _index is None or len(_chunks_store) == 0:
        return QAResult(
            question=question,
            answer="No documents have been indexed yet. Please upload a document first.",
            citations=[]
        )

    # Encode question
    q_embedding = _get_embeddings([question])

    # Search
    actual_k = min(top_k, len(_chunks_store))
    scores, indices = _index.search(q_embedding, actual_k)

    # Collect results
    passages = []
    citations = []
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        if idx < 0 or idx >= len(_chunks_store):
            continue
        chunk = _chunks_store[idx]
        passages.append(chunk.text)
        citations.append({
            "rank": i + 1,
            "score": float(score),
            "text": chunk.text[:300] + ("..." if len(chunk.text) > 300 else ""),
            "source": chunk.source,
            "page": chunk.page,
            "section": chunk.section
        })

    # Generate answer from passages
    answer = _synthesize_answer(question, passages)

    return QAResult(
        question=question,
        answer=answer,
        citations=citations
    )


def _synthesize_answer(question: str, passages: List[str]) -> str:
    """Synthesize an answer from retrieved passages.
    Uses extractive approach (no external LLM needed).
    """
    if not passages:
        return "I couldn't find relevant information in the documents to answer this question."

    q_lower = question.lower()
    q_words = set(q_lower.split())
    # Remove stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'which',
                  'who', 'how', 'when', 'where', 'why', 'do', 'does', 'did',
                  'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
                  'and', 'or', 'but', 'not', 'this', 'that', 'it', 'can', 'will'}
    q_words -= stop_words

    # Score sentences from passages
    scored_sentences = []
    for passage in passages:
        sentences = [s.strip() for s in passage.replace('\n', '. ').split('.') if len(s.strip()) > 15]
        for sentence in sentences:
            s_lower = sentence.lower()
            s_words = set(s_lower.split())
            overlap = len(q_words & s_words)
            if overlap > 0:
                scored_sentences.append((overlap, sentence))

    if not scored_sentences:
        # Fallback: return the most relevant passage
        return f"Based on the documents:\n\n{passages[0][:500]}"

    # Sort by relevance and take top sentences
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for _, s in scored_sentences[:4]]

    answer = "Based on the documents:\n\n"
    answer += ". ".join(top_sentences)
    if not answer.endswith('.'):
        answer += '.'

    return answer


def get_index_stats() -> dict:
    """Return stats about the current index."""
    return {
        "total_chunks": len(_chunks_store),
        "index_built": _index is not None,
        "sources": list(set(c.source for c in _chunks_store))
    }
