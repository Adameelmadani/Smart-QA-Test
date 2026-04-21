"""
ReqTracer, Requirements Extractor
Extracts and classifies requirements from document chunks.
"""
import re
from typing import List, Tuple
from models import DocumentChunk, Requirement


# ─── Classification Dictionaries ────────────────────────────────────
TYPE_KEYWORDS = {
    "performance": [
        "performance", "speed", "latency", "throughput", "response time",
        "bandwidth", "frequency", "Hz", "dB", "SPL", "level", "threshold",
        "maximum", "minimum", "rate", "capacity", "load", "timing",
        "delay", "ms", "seconds", "within", "less than", "greater than"
    ],
    "security": [
        "security", "authentication", "authorization", "encrypt",
        "password", "access control", "vulnerability", "firewall",
        "certificate", "token", "integrity", "confidentiality",
        "tamper", "audit", "log", "compliance"
    ],
    "interface": [
        "interface", "protocol", "API", "communication", "bus",
        "connector", "pin", "signal", "input", "output",
        "serial", "CAN", "LIN", "SPI", "I2C", "USB", "Ethernet",
        "display", "HMI", "user interface", "format", "data exchange"
    ],
    "functional": [
        "shall", "must", "function", "operate", "perform", "provide",
        "generate", "detect", "activate", "deactivate", "control",
        "monitor", "process", "calculate", "store", "display",
        "transmit", "receive", "trigger", "respond", "switch"
    ]
}

PRIORITY_KEYWORDS = {
    "high": [
        "critical", "essential", "mandatory", "safety", "shall",
        "must", "required", "vital", "crucial", "emergency",
        "fail-safe", "failsafe", "fail safe"
    ],
    "medium": [
        "should", "important", "recommended", "expected",
        "preferred", "standard", "normal"
    ],
    "low": [
        "may", "optional", "nice to have", "desired",
        "could", "consider", "if possible", "when feasible"
    ]
}


def extract_requirements(chunks: List[DocumentChunk], doc_id: str = "") -> List[Requirement]:
    """Extract requirements from document chunks."""
    requirements: List[Requirement] = []
    req_counter = 1
    seen_texts = set()

    for chunk in chunks:
        text = chunk.text
        # Look for requirement patterns
        req_texts = _find_requirement_sentences(text)

        for req_text in req_texts:
            # Deduplicate
            normalized = req_text.strip().lower()[:100]
            if normalized in seen_texts:
                continue
            seen_texts.add(normalized)

            # Classify
            req_type = _classify_type(req_text)
            priority = _classify_priority(req_text)
            title = _extract_title(req_text)

            req_id = f"REQ-{req_counter:03d}"
            req_counter += 1

            requirements.append(Requirement(
                req_id=req_id,
                title=title,
                description=req_text.strip(),
                req_type=req_type,
                priority=priority,
                source=chunk.source,
                page=chunk.page,
                section=chunk.section
            ))

    return requirements


def _find_requirement_sentences(text: str) -> List[str]:
    """Find sentences that look like requirements."""
    requirements = []

    # Pattern 1: Lines starting with REQ-xxx or similar IDs
    id_pattern = re.findall(
        r'(?:REQ|RQ|R|FR|NFR|PR|IR|SR)[-_]?\d+[:\s].*?(?:\.|$)',
        text, re.IGNORECASE | re.MULTILINE
    )
    requirements.extend(id_pattern)

    # Pattern 2: Sentences containing "shall" or "must"
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue
        lower = sentence.lower()
        if any(kw in lower for kw in ['shall', 'must', 'is required']):
            if sentence not in requirements:
                requirements.append(sentence)

    # Pattern 3: Bullet points or numbered items that look like requirements
    bullets = re.findall(
        r'(?:^|\n)\s*(?:[-•▪]\s*|\d+[.)]\s*)(.{30,}?)(?:\n|$)',
        text
    )
    for bullet in bullets:
        lower = bullet.lower()
        if any(kw in lower for kw in ['shall', 'must', 'should', 'will', 'is required']):
            if bullet not in requirements:
                requirements.append(bullet)

    # If no patterns matched but text contains requirement-like keywords
    if not requirements and len(text) > 40:
        lower = text.lower()
        if any(kw in lower for kw in ['shall', 'must', 'requirement', 'specification']):
            requirements.append(text[:500])

    return requirements


def _classify_type(text: str) -> str:
    """Classify the requirement type based on keywords."""
    lower = text.lower()
    scores = {}
    for rtype, keywords in TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in lower)
        scores[rtype] = score

    # Default to functional if no strong match
    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0:
        return "functional"
    return best_type


def _classify_priority(text: str) -> str:
    """Classify the requirement priority."""
    lower = text.lower()
    scores = {}
    for priority, keywords in PRIORITY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lower)
        scores[priority] = score

    best_priority = max(scores, key=scores.get)
    if scores[best_priority] == 0:
        return "medium"
    return best_priority


def _extract_title(text: str) -> str:
    """Extract a short title from requirement text."""
    # Try to get the first meaningful phrase
    text = text.strip()
    # Remove ID prefix if present
    text = re.sub(r'^(?:REQ|RQ|R|FR|NFR|PR|IR|SR)[-_]?\d+[:\s]*', '', text, flags=re.IGNORECASE)

    # Take first sentence or up to 80 chars
    first_sentence = re.split(r'[.!?]', text)[0].strip()
    if len(first_sentence) > 80:
        return first_sentence[:77] + "..."
    return first_sentence if first_sentence else text[:80]
