from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mcp_server


def _has(question: str, *words: str) -> bool:
    q = question.lower()
    return any(word.lower() in q for word in words)


def run(question: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    q = question.lower()
    mcp_calls: list[dict[str, Any]] = []
    sources: list[str] = []
    decisions: list[str] = []

    if _has(q, "access", "level", "contractor", "emergency"):
        level_match = re.search(r"level\s*([23])", q)
        level = level_match.group(1) if level_match else ("3" if "level 3" in q else "2")
        tool_result = mcp_server.check_access_permission(
            role="contractor" if "contractor" in q else "employee",
            level=level,
            emergency="emergency" in q,
            contractor="contractor" in q,
        )
        mcp_calls.append(tool_result)
        sources.extend(tool_result["sources"])
        result = tool_result["result"]
        decisions.append(
            f"{result['level']} approval path: {', '.join(result['approval_path'])}; final approver: {result['final_approver']}; expiry: {result['expiry']}."
        )

    if _has(q, "refund", "hoan", "flash", "digital", "store", "credit", "defect", "manufacturer"):
        kb = mcp_server.search_kb(question)
        mcp_calls.append(kb)
        sources.extend(kb["sources"])
        if "flash" in q and ("defect" in q or "manufacturer" in q):
            decisions.append("Flash Sale normally blocks refunds, but verified manufacturer defect within 7 days is an explicit refund exception.")
        elif "digital" in q:
            decisions.append("Digital product refund requires an exception such as duplicate charge, failed delivery, or verified technical defect.")
        elif "store" in q or "credit" in q:
            decisions.append("Approved store credit is 80% of the original paid amount.")
        else:
            decisions.append("Standard eligible physical-product refunds are allowed within 7 days.")

    if _has(q, "p1", "ticket", "incident"):
        ticket = mcp_server.get_ticket_info(priority="P1")
        mcp_calls.append(ticket)
        sources.extend(ticket["sources"])
        decisions.append("P1 ticket requires acknowledgement within 10 minutes and updates every 15 minutes.")

    unique_sources = list(dict.fromkeys(sources))
    if not decisions:
        return {"policy_result": "No conditional policy rule matched.", "decision": "no_policy_match", "sources": [], "mcp_tools_used": [], "confidence": 0.1, "trace": {"worker": "policy_tool_worker", "mcp_calls": []}}
    return {
        "policy_result": " ".join(decisions),
        "decision": "policy_rule_applied",
        "sources": unique_sources,
        "mcp_tools_used": [call["tool_name"] for call in mcp_calls],
        "confidence": 0.88,
        "trace": {"worker": "policy_tool_worker", "mcp_tool_called": [call["tool_name"] for call in mcp_calls], "mcp_result": mcp_calls},
    }


if __name__ == "__main__":
    for sample in ["Flash Sale manufacturer defect refund", "Level 3 emergency access", "contractor Level 2 temporary access", "store credit percentage"]:
        print(sample, "=>", run(sample))
