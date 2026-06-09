import json
import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_DIR))

import graph
from workers import retrieval, policy_tool, synthesis

class LabAssignmentTests(unittest.TestCase):
    def test_retrieval_sources(self):
        cases = [
            ("P1 SLA escalation sau 10 phut", "p1_sla.md"),
            ("Level 2 contractor temporary emergency access", "access_control_sop.md"),
            ("Flash Sale manufacturer defect refund", "refund_policy.md"),
            ("probation employee remote work", "hr_remote_work.md"),
            ("password rotation warning days", "password_security_faq.md"),
        ]
        for question, source in cases:
            result = retrieval.run(question)
            self.assertIn(source, result["sources"], question)
            self.assertGreater(result["confidence"], 0.25)

    def test_policy_uses_mcp_for_access(self):
        result = policy_tool.run("Level 3 emergency access final approver")
        self.assertIn("check_access_permission", result["mcp_tools_used"])
        self.assertIn("final approver", result["policy_result"].lower())

    def test_synthesis_abstains_unknown(self):
        result = synthesis.run("Muc phat tai chinh cho P1 la bao nhieu?", {"chunks": [], "sources": [], "confidence": 0.0}, None)
        self.assertIn("Không có thông tin", result["final_answer"])
        self.assertEqual(result["sources"], [])


    def test_graph_gq07_abstains_penalty(self):
        result = graph.run("muc phat tai chinh cho P1 la bao nhieu?")
        self.assertEqual(result["supervisor_route"], "abstain")
        self.assertEqual(result["retrieved_sources"], [])
        self.assertIn("tin", result["final_answer"])

    def test_graph_gq09_multi_worker(self):
        result = graph.run("P1 escalation sau 10 phút và contractor cần Level 2 temporary access thì làm gì?")
        self.assertIn("retrieval_worker", result["workers_called"])
        self.assertIn("policy_tool_worker", result["workers_called"])
        self.assertIn("synthesis_worker", result["workers_called"])
        self.assertIn("check_access_permission", result["mcp_tools_used"])
        self.assertNotEqual(result["route_reason"], "unknown")

    def test_eval_grading_jsonl_exists_and_valid(self):
        import eval_trace
        eval_trace.run_grading()
        path = LAB_DIR / "artifacts" / "grading_run.jsonl"
        self.assertTrue(path.exists())
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(rows), 10)
        required = {"id", "question", "answer", "sources", "supervisor_route", "route_reason", "workers_called", "mcp_tools_used", "confidence", "hitl_triggered", "timestamp"}
        for row in rows:
            self.assertTrue(required.issubset(row))
            self.assertNotEqual(row["route_reason"], "unknown")

if __name__ == "__main__":
    unittest.main()
