from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent


def search_kb(query: str) -> dict[str, Any]:
    from workers import retrieval
    result = retrieval.run(query)
    return {"tool_name": "search_kb", "input_summary": query[:120], "result": result["chunks"], "sources": result["sources"]}


def get_ticket_info(ticket_id: str | None = None, priority: str | None = None) -> dict[str, Any]:
    label = ticket_id or (priority or "P1").upper()
    result = {"ticket_id": ticket_id or "MOCK-P1-001", "priority": label, "ack_deadline_minutes": 10, "update_interval_minutes": 15, "owner": "Incident Commander"}
    return {"tool_name": "get_ticket_info", "input_summary": f"ticket_id={ticket_id}, priority={priority}", "result": result, "sources": ["p1_sla.md"]}


def check_access_permission(role: str, level: str, emergency: bool = False, contractor: bool = False) -> dict[str, Any]:
    level_norm = str(level).replace("Level", "").strip()
    if level_norm == "3":
        approval_path = ["System Owner", "Security Manager"]
        final_approver = "Security Manager"
        expiry = "Emergency duration only; revocation time must be logged"
    elif contractor:
        approval_path = ["Business Owner", "Security"]
        final_approver = "Security"
        expiry = "24 hours for emergency temporary contractor access" if emergency else "Temporary access window approved by Security"
    else:
        approval_path = ["Manager", "Security"]
        final_approver = "Security"
        expiry = "Approved temporary duration"
    result = {"role": role, "level": f"Level {level_norm}", "emergency": emergency, "contractor": contractor, "approval_path": approval_path, "final_approver": final_approver, "expiry": expiry}
    return {"tool_name": "check_access_permission", "input_summary": f"role={role}, level={level}, emergency={emergency}, contractor={contractor}", "result": result, "sources": ["access_control_sop.md"]}


def create_ticket(title: str, priority: str, description: str) -> dict[str, Any]:
    result = {"ticket_id": f"MOCK-{priority.upper()}-001", "title": title, "priority": priority.upper(), "status": "created", "description": description[:160]}
    return {"tool_name": "create_ticket", "input_summary": f"title={title}, priority={priority}", "result": result, "sources": ["p1_sla.md"]}


if __name__ == "__main__":
    print(search_kb("P1 escalation"))
    print(check_access_permission("contractor", "2", emergency=True, contractor=True))
    print(get_ticket_info(priority="P1"))
