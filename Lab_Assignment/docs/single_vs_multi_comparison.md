# Single vs Multi-Agent Comparison

## Single-agent baseline

A Day08-style single-agent RAG system normally retrieves evidence and answers in one step. It is simple, but routing, policy exceptions, tool usage, and trace fields are mixed together.

## Multi-agent result

The Day09 implementation separates responsibilities:

| Metric | Single-agent baseline | Multi-agent assignment |
|---|---:|---:|
| Explicit workers | 1 | 3 |
| MCP tools | 0-1 | 4 callable tools |
| Required JSONL fields | partial | 11/11 |
| Abstain path | implicit | explicit in synthesis |
| gq09 multi-hop support | weak | retrieval + policy + MCP |

## Evidence from artifacts

Run `python eval_trace.py --grading` to create `artifacts/grading_run.jsonl`. Run `python eval_trace.py --analyze` to summarize count, MCP records, and average confidence. Per-question traces in `artifacts/traces/` show route, workers called, MCP tools, and sources.
