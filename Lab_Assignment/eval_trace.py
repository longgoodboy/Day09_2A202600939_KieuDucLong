from __future__ import annotations

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import graph

ARTIFACTS = Path("artifacts")
TRACES = ARTIFACTS / "traces"

GRADING_QUESTIONS = [
    ("gq01", "P1 incident thì thông báo đầu tiên ở đâu và khi nào phải escalation?"),
    ("gq02", "Refund policy theo ngày mua áp dụng như thế nào cho sản phẩm eligible?"),
    ("gq03", "Level 3 emergency access cần approver nào và ai final approver?"),
    ("gq04", "Store credit được tính bao nhiêu phần trăm tiền gốc?"),
    ("gq05", "P1 escalation sau 10 phút không ai acknowledge thì làm gì?"),
    ("gq06", "Nhân viên probation có được remote work không và giới hạn bao nhiêu ngày?"),
    ("gq07", "Mức phạt tài chính cho P1 là bao nhiêu?"),
    ("gq08", "Password phải đổi sau bao nhiêu ngày và cảnh báo trước bao nhiêu ngày?"),
    ("gq09", "P1 escalation sau 10 phút và contractor cần Level 2 temporary access thì làm gì?"),
    ("gq10", "Flash Sale item bị manufacturer defect trong 7 ngày có được refund không?"),
]

EXTRA_QUESTIONS = [
    ("tq11", "Digital product refund có exception nào?"),
    ("tq12", "Access Level 2 cho contractor emergency hết hạn khi nào?"),
    ("tq13", "P1 ticket update interval là bao lâu?"),
    ("tq14", "Remote work cần approval nào?"),
    ("tq15", "Security suspected compromise password làm gì?"),
]


def _record(qid: str, question: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": qid,
        "question": question,
        "answer": result["final_answer"],
        "sources": result["retrieved_sources"],
        "supervisor_route": result["supervisor_route"],
        "route_reason": result["route_reason"],
        "workers_called": result["workers_called"],
        "mcp_tools_used": result["mcp_tools_used"],
        "confidence": result["confidence"],
        "hitl_triggered": result["hitl_triggered"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def run_eval(questions: list[tuple[str, str]]) -> list[dict[str, Any]]:
    TRACES.mkdir(parents=True, exist_ok=True)
    rows = []
    for qid, question in questions:
        result = graph.run(question)
        row = _record(qid, question, result)
        rows.append(row)
        (TRACES / f"{qid}.json").write_text(json.dumps({"record": row, "trace": result.get("trace")}, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows


def validate_rows(rows: list[dict[str, Any]], expected_count: int | None = None) -> None:
    required = {"id", "question", "answer", "sources", "supervisor_route", "route_reason", "workers_called", "mcp_tools_used", "confidence", "hitl_triggered", "timestamp"}
    if expected_count is not None:
        assert len(rows) == expected_count, f"Expected {expected_count}, got {len(rows)}"
    for row in rows:
        missing = required - set(row)
        assert not missing, f"Missing {missing} in {row.get('id')}"
        assert row["route_reason"] and row["route_reason"] != "unknown"
        assert isinstance(row["sources"], list)
        assert isinstance(row["workers_called"], list)
        assert isinstance(row["mcp_tools_used"], list)
        assert 0 <= float(row["confidence"]) <= 1


def run_grading() -> list[dict[str, Any]]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    rows = run_eval(GRADING_QUESTIONS)
    validate_rows(rows, 10)
    output = ARTIFACTS / "grading_run.jsonl"
    output.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
    return rows


def analyze() -> None:
    path = ARTIFACTS / "grading_run.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    print(json.dumps({"count": len(rows), "mcp_records": sum(bool(r["mcp_tools_used"]) for r in rows), "avg_confidence": round(sum(float(r["confidence"]) for r in rows) / len(rows), 2)}, ensure_ascii=False, indent=2))


def compare() -> None:
    print(json.dumps({"single_agent": {"workers": 1, "trace_fields": 2}, "multi_agent": {"workers": 3, "trace_fields": 11, "mcp_tools": 4}}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grading", action="store_true")
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()
    if args.grading:
        rows = run_grading()
        print(f"wrote {len(rows)} grading rows")
    elif args.analyze:
        analyze()
    elif args.compare:
        compare()
    else:
        rows = run_eval(GRADING_QUESTIONS + EXTRA_QUESTIONS)
        validate_rows(rows, 15)
        print(f"ran {len(rows)} evaluation questions")


if __name__ == "__main__":
    main()
