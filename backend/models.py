"""
ReqTracer, Data models
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
import uuid
import json


@dataclass
class DocumentChunk:
    """A chunk of text extracted from a document."""
    text: str
    source: str  # filename
    page: int
    section: str = ""
    chunk_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self):
        return asdict(self)


@dataclass
class Requirement:
    """A structured requirement extracted from a document."""
    req_id: str  # e.g. REQ-001
    title: str
    description: str
    req_type: str  # functional, performance, interface, security
    priority: str  # high, medium, low
    source: str  # filename
    page: int
    section: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class TestCase:
    """A structured test case generated from a requirement."""
    tc_id: str  # e.g. TC-001
    req_id: str  # linked requirement
    goal: str
    prerequisites: str
    procedure: str
    inputs_signals: str
    thresholds_oracles: str
    expected_pass: str
    expected_fail: str

    def to_dict(self):
        return asdict(self)


@dataclass
class QAResult:
    """Result of a RAG question-answering query."""
    question: str
    answer: str
    citations: List[dict] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class Document:
    """Metadata for an uploaded document."""
    doc_id: str
    filename: str
    num_pages: int
    num_chunks: int
    num_requirements: int = 0
    num_test_cases: int = 0

    def to_dict(self):
        return asdict(self)
