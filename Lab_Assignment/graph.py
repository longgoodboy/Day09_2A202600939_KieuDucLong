from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import json
import unicodedata
from datetime import datetime, timezone
from typing import Any

from workers import policy_tool, retrieval, synthesis


def _normalize(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(ch) != "Mn")


def _contains(question: str, words: set[str]) -> bool:
    q = _normalize(question)
    return any(_normalize(word) in q for word in words)


def classify_route(question: str) -> dict[str, Any]:
    p1 = _contains(question, {"p1", "sla", "escalation", "ticket", "incident"})
    policy = _contains(question, {"refund", "hoan", "flash", "digital", "manufacturer", "defect", "store credit", "access", "level", "contractor", "emergency"})
    penalty_unknown = _contains(question, {"muc phat", "financial penalty", "fine", "penalty"})
    if penalty_unknown:
        return {"route": "abstain", "workers": ["retrieval_worker", "synthesis_worker"], "reason": "task asks for financial penalty information that is not covered by provided internal policy documents"}
    if p1 and policy:
        return {"route": "multi_worker", "workers": ["retrieval_worker", "policy_tool_worker", "synthesis_worker"], "reason": "task combines P1/ticket/escalation keywords with policy/access keywords"}
    if policy:
        return {"route": "policy_tool_worker", "workers": ["retrieval_worker", "policy_tool_worker", "synthesis_worker"], "reason": "task contains refund/access/exception/contractor policy keywords"}
    if p1 or _contains(question, {"remote", "password", "security", "probation"}):
        return {"route": "retrieval_worker", "workers": ["retrieval_worker", "synthesis_worker"], "reason": "task contains internal policy retrieval keywords"}
    return {"route": "abstain", "workers": ["retrieval_worker", "synthesis_worker"], "reason": "task has no matching internal policy keywords, retrieval evidence required before answering"}


def run(question: str) -> dict[str, Any]:
    route = classify_route(question)
    retrieval_result = retrieval.run(question)
    if route["route"] == "abstain":
        retrieval_result = {"chunks": [], "sources": [], "confidence": 0.0, "trace": {"worker": "retrieval_worker", "forced_abstain": True}}
    policy_result = None
    mcp_tools: list[str] = []
    if "policy_tool_worker" in route["workers"]:
        policy_result = policy_tool.run(question, {"retrieval": retrieval_result})
        mcp_tools = policy_result.get("mcp_tools_used", [])
    synthesis_result = synthesis.run(question, retrieval_result, policy_result)
    hitl = synthesis_result["confidence"] < 0.2
    return {
        "final_answer": synthesis_result["final_answer"],
        "retrieved_sources": synthesis_result["sources"],
        "supervisor_route": route["route"],
        "route_reason": route["reason"],
        "workers_called": route["workers"],
        "mcp_tools_used": mcp_tools,
        "confidence": synthesis_result["confidence"],
        "hitl_triggered": hitl,
        "trace": {"timestamp": datetime.now(timezone.utc).isoformat(), "retrieval": retrieval_result.get("trace"), "policy": (policy_result or {}).get("trace"), "route": route},
    }


answer_question = run


if __name__ == "__main__":
    samples = [
        "P1 SLA escalation sau 10 phut?",
        "Flash Sale manufacturer defect refund trong 7 ngay?",
        "Level 3 emergency access final approver?",
        "Password rotation warning days?",
        "muc phat tai chinh cho P1 la bao nhieu?",
    ]
    for sample in samples:
        print(json.dumps(run(sample), ensure_ascii=False, indent=2))
