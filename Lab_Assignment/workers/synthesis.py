from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Any

ABSTAIN_PREFIX = "Không có thông tin trong tài liệu nội bộ được cung cấp để xác định"


def run(question: str, retrieval_result: dict[str, Any] | None = None, policy_result: dict[str, Any] | None = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
    retrieval_result = retrieval_result or {"chunks": [], "sources": [], "confidence": 0.0}
    policy_result = policy_result or None
    sources = list(dict.fromkeys((retrieval_result.get("sources") or []) + ((policy_result or {}).get("sources") or [])))
    confidence = max(float(retrieval_result.get("confidence", 0.0)), float((policy_result or {}).get("confidence", 0.0)))

    if not sources or confidence < 0.2:
        return {"final_answer": f"{ABSTAIN_PREFIX} câu hỏi: {question}.", "sources": [], "confidence": min(confidence, 0.19)}

    parts: list[str] = []
    if policy_result and policy_result.get("decision") != "no_policy_match":
        parts.append(policy_result["policy_result"])
    for chunk in retrieval_result.get("chunks", [])[:2]:
        text = " ".join(chunk["text"].split())
        parts.append(f"Nguồn {chunk['source']}: {text[:320]}")
    answer = "\n".join(f"- {part}" for part in parts if part)
    answer += "\n- Sources: " + ", ".join(sources)
    return {"final_answer": answer, "sources": sources, "confidence": round(min(0.95, confidence), 2)}


if __name__ == "__main__":
    print(run("unknown", {"chunks": [], "sources": [], "confidence": 0.0}, None))
