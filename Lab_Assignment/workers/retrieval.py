from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE_DIR / "data" / "docs"

TOPIC_KEYWORDS = {
    "p1_sla.md": {"p1", "sla", "escalation", "escalate", "ticket", "incident", "on-call", "10", "minutes", "phut"},
    "refund_policy.md": {"refund", "return", "hoan", "tien", "flash", "sale", "manufacturer", "defect", "digital", "store", "credit"},
    "access_control_sop.md": {"access", "level", "2", "3", "contractor", "temporary", "emergency", "approver", "security"},
    "hr_remote_work.md": {"hr", "remote", "work", "probation", "employee", "manager", "approval", "nhan", "vien"},
    "password_security_faq.md": {"password", "security", "rotation", "warning", "days", "reset", "mat", "khau"},
}


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))


def load_documents(docs_dir: Path | str = DOCS_DIR) -> list[dict[str, str]]:
    path = Path(docs_dir)
    return [
        {"source": item.name, "text": item.read_text(encoding="utf-8")}
        for item in sorted(path.glob("*.md"))
    ]


def run(question: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    query_tokens = _tokens(question)
    documents = load_documents((context or {}).get("docs_dir", DOCS_DIR))
    scored: list[tuple[int, dict[str, str]]] = []
    for doc in documents:
        keywords = TOPIC_KEYWORDS.get(doc["source"], set())
        doc_tokens = _tokens(doc["text"])
        score = len(query_tokens & keywords) * 3 + len(query_tokens & doc_tokens)
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    top = scored[:3]
    max_score = top[0][0] if top else 0
    confidence = min(0.95, round(max_score / 12, 2)) if top else 0.05
    return {
        "chunks": [{"source": doc["source"], "text": doc["text"][:900], "score": score} for score, doc in top],
        "sources": [doc["source"] for _, doc in top],
        "confidence": confidence,
        "trace": {"worker": "retrieval_worker", "query_tokens": sorted(query_tokens), "matches": [{"source": d["source"], "score": s} for s, d in top]},
    }


if __name__ == "__main__":
    for sample in ["P1 SLA escalation", "Level 2 contractor access", "Flash Sale defect refund", "probation remote", "password rotation"]:
        print(sample, "=>", run(sample))
