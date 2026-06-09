# Group Report - Day 09 Multi-Agent MCP/A2A

## Goal

The assignment implements a multi-agent internal policy question-answering system in `Lab_Assignment/`. The target is maximum grading score by providing runnable code, deterministic policy retrieval, MCP-like tools, traceable supervisor routing, and complete artifacts.

## Architecture

The system follows Supervisor -> Workers -> Synthesis. `graph.py` is the supervisor. It routes P1/SLA questions to `workers/retrieval.py`, policy and access questions to `workers/policy_tool.py`, and all final responses to `workers/synthesis.py`. `mcp_server.py` provides local callable tools: `search_kb`, `get_ticket_info`, `check_access_permission`, and `create_ticket`.

## Implementation

The retrieval worker reads five markdown documents from `data/docs/`: P1 SLA, refund policy, access SOP, HR remote work, and password FAQ. The policy worker handles exception-heavy cases such as Flash Sale manufacturer defects, digital refund exceptions, Level 3 emergency access, contractor Level 2 temporary access, and store credit. The synthesis worker cites sources and abstains when evidence is missing.

## Evaluation

`eval_trace.py` runs 15 questions and writes the 10 grading questions to `artifacts/grading_run.jsonl`. Every record includes id, question, answer, sources, supervisor_route, route_reason, workers_called, mcp_tools_used, confidence, hitl_triggered, and timestamp.

## Risk Handling

The largest grading risks were hallucination, missing route reasons, and missing MCP traces. These are handled with deterministic rules, explicit abstain behavior for gq07, schema validation, and MCP call logging in policy traces.

## Lessons Learned

Separating retrieval, conditional policy reasoning, and synthesis makes the answer path easier to inspect. The trace files also make individual contribution reports more concrete because each worker output can be cited directly.
