# Steps - Execution Checklist for Maximum Score

> Làm theo thứ tự. Sau mỗi phase, chạy lệnh kiểm chứng tương ứng trước khi chuyển phase tiếp theo.

## Phase 0 - Chuẩn bị repo gốc

- [ ] Clone hoặc mở đúng repo gốc: `longgoodboy/Day09_2A202600939_KieuDucLong`.
- [ ] Kiểm tra yêu cầu nộp bài:

```bash
git status
ls
cat Lab-assignment-checklist.md
```

- [ ] Tạo thư mục assignment đúng yêu cầu:

```bash
mkdir -p Lab_Assignment/workers Lab_Assignment/contracts Lab_Assignment/data/docs Lab_Assignment/artifacts/traces Lab_Assignment/docs Lab_Assignment/reports/individual
```

- [ ] Tạo `Lab_Assignment/workers/__init__.py`.
- [ ] Nếu chưa có, tạo `Lab-Solution.md` ở root để trả lời phần lab trên lớp.
- [ ] Không đặt code assignment rải rác ngoài `Lab_Assignment/`.

## Phase 1 - Data docs nền tảng

Tạo 5 tài liệu nội bộ trong `Lab_Assignment/data/docs/`.

- [ ] `p1_sla.md`: có P1 notification, channel, deadline escalation, no-response-after-10-minutes rule.
- [ ] `refund_policy.md`: có refund window, policy version/date logic, Flash Sale rule, manufacturer defect exception, store credit percentage.
- [ ] `access_control_sop.md`: có Level 2/Level 3, emergency path, contractor temporary access, approver/final approver.
- [ ] `hr_remote_work.md`: có probation remote rule, approval, day limit.
- [ ] `password_security_faq.md`: có password rotation days và warning days.

Acceptance check:

```bash
find Lab_Assignment/data/docs -maxdepth 1 -type f
```

## Phase 2 - Retrieval worker

File: `Lab_Assignment/workers/retrieval.py`

- [ ] Implement `load_documents(docs_dir)` đọc markdown và return list/dict mới.
- [ ] Implement keyword index theo topic: `p1_sla`, `refund`, `access`, `hr_remote`, `password`.
- [ ] Implement `run(question: str, context: dict | None = None) -> dict`.
- [ ] Output gồm `chunks`, `sources`, `confidence`, `trace`.
- [ ] Nếu không match, return `chunks=[]`, `sources=[]`, confidence thấp để synthesis abstain.
- [ ] Thêm `if __name__ == "__main__"` để test độc lập.

Acceptance check:

```bash
cd Lab_Assignment
python workers/retrieval.py
```

Manual test cases:

- [ ] P1/SLA question trả về `p1_sla.md`.
- [ ] Level 2/Level 3 access question trả về `access_control_sop.md`.
- [ ] Refund/Flash Sale question trả về `refund_policy.md`.
- [ ] Probation remote question trả về `hr_remote_work.md`.
- [ ] Password question trả về `password_security_faq.md`.
- [ ] Unknown financial penalty question không bịa source, confidence thấp.

## Phase 3 - MCP server/tools

File: `Lab_Assignment/mcp_server.py`

- [ ] Implement tool functions dạng Python callable trước; MCP/mock wrapper sau nếu cần.
- [ ] `search_kb(query)` trả danh sách tài liệu/chunks liên quan.
- [ ] `check_access_permission(role, level, emergency, contractor)` trả approval path deterministic.
- [ ] `get_ticket_info(ticket_id=None, priority=None)` trả mock info cho P1.
- [ ] `create_ticket(title, priority, description)` trả mock ticket id/result.
- [ ] Mỗi tool return dict có `tool_name`, `input_summary`, `result`, `sources` nếu có.
- [ ] Thêm `if __name__ == "__main__"` chạy demo ít nhất 2 tools.

Acceptance check:

```bash
cd Lab_Assignment
python mcp_server.py
```

Done when:

- [ ] Có ít nhất 2 tools hoạt động.
- [ ] Tool output parse được như dict/JSON.
- [ ] Tool access trả đúng Level 2/Level 3/contractor/emergency path.

## Phase 4 - Policy Tool worker

File: `Lab_Assignment/workers/policy_tool.py`

- [ ] Import và gọi tool thật từ `mcp_server.py`.
- [ ] Implement `run(question: str, context: dict | None = None) -> dict`.
- [ ] Xử lý Flash Sale + manufacturer defect + 7 ngày: exception lỗi NSX thắng rule không hoàn tiền thông thường.
- [ ] Xử lý digital product refund bằng exception thay vì trả lời chung.
- [ ] Xử lý Level 3 emergency access: số approver và final approver.
- [ ] Xử lý contractor Level 2 temporary access: quyền tạm thời, emergency path, approver.
- [ ] Xử lý store credit percentage theo tài liệu.
- [ ] Output gồm `policy_result`, `decision`, `sources`, `mcp_tools_used`, `confidence`, `trace`.
- [ ] Trace có `mcp_tool_called` và `mcp_result`.

Acceptance check:

```bash
cd Lab_Assignment
python workers/policy_tool.py
```

Manual test cases:

- [ ] Flash Sale manufacturer defect route dùng refund/access source phù hợp.
- [ ] Level 3 emergency access gọi `check_access_permission`.
- [ ] Contractor Level 2 temporary access gọi MCP và trả đúng approver.
- [ ] Store credit trả đúng percentage, không bịa.

## Phase 5 - Synthesis worker

File: `Lab_Assignment/workers/synthesis.py`

- [ ] Implement `run(question, retrieval_result=None, policy_result=None, context=None) -> dict`.
- [ ] Tổng hợp câu trả lời từ chunks + policy_result.
- [ ] Luôn cite source bằng filename/source name khi có bằng chứng.
- [ ] Nếu không có source hoặc confidence thấp, abstain rõ.
- [ ] Không bịa số tiền, mức phạt, SLA, approver nếu tài liệu không có.
- [ ] Có fallback rule-based; không phụ thuộc hoàn toàn vào LLM/API key.
- [ ] Output gồm `final_answer`, `sources`, `confidence`.

Acceptance check:

```bash
cd Lab_Assignment
python workers/synthesis.py
```

Done when:

- [ ] gq07/unknown penalty abstain đúng.
- [ ] Known policy answer có source.
- [ ] Không crash khi retrieval/policy result rỗng.

## Phase 6 - Supervisor graph

File: `Lab_Assignment/graph.py`

- [ ] Import worker thật:

```python
from workers import retrieval, policy_tool, synthesis
```

- [ ] Implement `classify_route(question)` deterministic theo routing contract.
- [ ] Implement `run(question: str) -> dict` hoặc `answer_question(question: str) -> dict`.
- [ ] Route P1/SLA/ticket/incident -> retrieval + synthesis.
- [ ] Route refund/access/contractor/emergency -> policy + retrieval + synthesis.
- [ ] Route P1 + access -> retrieval + policy + synthesis.
- [ ] Route unknown -> retrieval thấp + synthesis abstain.
- [ ] Output có đủ final fields:
  - `final_answer`
  - `retrieved_sources`
  - `supervisor_route`
  - `route_reason`
  - `workers_called`
  - `mcp_tools_used`
  - `confidence`
  - `hitl_triggered`
- [ ] `route_reason` luôn cụ thể.
- [ ] `if __name__ == "__main__"` chạy demo 5 câu đại diện.

Acceptance check:

```bash
cd Lab_Assignment
python graph.py
```

Done when:

- [ ] Graph không dùng placeholder.
- [ ] `workers_called` đúng theo route.
- [ ] `mcp_tools_used` được merge từ policy worker.

## Phase 7 - Eval trace và grading artifact

File: `Lab_Assignment/eval_trace.py`

- [ ] Define 15 test questions, trong đó có 10 grading questions `gq01`-`gq10`.
- [ ] Implement `run_eval(questions)` gọi `graph.run`/`answer_question`.
- [ ] Sinh trace JSON vào `artifacts/traces/` cho từng câu.
- [ ] Implement `--grading` sinh `artifacts/grading_run.jsonl` đúng 10 dòng.
- [ ] Implement `--analyze` summarize route/workers/confidence/MCP usage.
- [ ] Implement `--compare` tạo metrics single vs multi nếu cần cho docs.
- [ ] Validate schema sau khi sinh JSONL.

Required JSONL fields:

```text
id, question, answer, sources, supervisor_route, route_reason,
workers_called, mcp_tools_used, confidence, hitl_triggered, timestamp
```

Acceptance check:

```bash
cd Lab_Assignment
python eval_trace.py
python eval_trace.py --grading
python eval_trace.py --analyze
python eval_trace.py --compare
```

JSONL validation:

```bash
python - <<'PY'
import json
required = [
    "id", "question", "answer", "sources", "supervisor_route",
    "route_reason", "workers_called", "mcp_tools_used",
    "confidence", "hitl_triggered", "timestamp"
]
with open("artifacts/grading_run.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f]
assert len(rows) == 10
for row in rows:
    for key in required:
        assert key in row, f"Missing {key} in {row.get('id')}"
    assert row["route_reason"] and row["route_reason"] != "unknown"
    assert isinstance(row["sources"], list)
    assert isinstance(row["workers_called"], list)
    assert isinstance(row["mcp_tools_used"], list)
    assert 0 <= float(row["confidence"]) <= 1
print("grading_run.jsonl is valid")
PY
```

Done when:

- [ ] JSONL parse được.
- [ ] Có đúng 10 records grading.
- [ ] Có ít nhất 1 record dùng MCP tool thật.
- [ ] gq07 answer là abstain.
- [ ] gq09 có retrieval + policy + synthesis.

## Phase 8 - Worker contracts

File: `Lab_Assignment/contracts/worker_contracts.yaml`

- [ ] Ghi contract cho `retrieval_worker`.
- [ ] Ghi contract cho `policy_tool_worker`.
- [ ] Ghi contract cho `synthesis_worker`.
- [ ] Ghi contract cho MCP tools.
- [ ] Mô tả input/output/failure behavior/confidence semantics.
- [ ] Không để TODO/template text.

Acceptance check:

```bash
grep -R "TODO\|placeholder" Lab_Assignment/contracts || true
```

## Phase 9 - Documentation

Folder: `Lab_Assignment/docs/`

- [ ] `system_architecture.md`: mô tả architecture, diagram, modules, data flow, trace flow.
- [ ] `routing_decisions.md`: bảng route cho gq01-gq10 dựa trên trace thật.
- [ ] `single_vs_multi_comparison.md`: so sánh Day08 single-agent với Day09 multi-agent bằng metrics thật.
- [ ] Docs phải cite artifact/trace/file cụ thể, không viết chung chung.
- [ ] Không còn TODO/template.

Acceptance check:

```bash
grep -R "TODO\|placeholder" Lab_Assignment/docs || true
```

## Phase 10 - Reports

Files:

- `Lab_Assignment/reports/group_report.md`
- `Lab_Assignment/reports/individual/kieu_duc_long.md`

Group report:

- [ ] Mục tiêu bài lab.
- [ ] Kiến trúc Supervisor -> Workers -> MCP -> Synthesis.
- [ ] Phân công vai trò.
- [ ] Kết quả test/eval.
- [ ] Rủi ro và cách xử lý.
- [ ] Lessons learned.

Individual report:

- [ ] 500-800 từ.
- [ ] Nêu rõ file/function đã làm.
- [ ] Cite trace/grading examples cụ thể.
- [ ] Nêu vấn đề gặp và cách khắc phục.
- [ ] Không viết chung chung.

## Phase 11 - Lab solution file

File root: `Lab-Solution.md`

- [ ] Giải các bài lab trên lớp theo `CODELAB.md`/`exercises/`.
- [ ] Tóm tắt Stage 1-5: Direct LLM, RAG/Tools, ReAct Agent, Multi-Agent, Distributed A2A.
- [ ] Nêu bài tập đã hoàn thành và cách chạy.
- [ ] Link tới `Lab_Assignment/` như phần assignment chính.

Acceptance check:

```bash
Test-Path Lab-Solution.md
```

## Phase 12 - Final verification before submit

Chạy toàn bộ từ root:

```bash
cd Lab_Assignment
python graph.py
python workers/retrieval.py
python workers/policy_tool.py
python workers/synthesis.py
python mcp_server.py
python eval_trace.py
python eval_trace.py --grading
python eval_trace.py --analyze
python eval_trace.py --compare
```

Kiểm tra file bắt buộc:

```bash
cd ..
Test-Path Lab-Solution.md
Test-Path Lab_Assignment/graph.py
Test-Path Lab_Assignment/mcp_server.py
Test-Path Lab_Assignment/eval_trace.py
Test-Path Lab_Assignment/workers/retrieval.py
Test-Path Lab_Assignment/workers/policy_tool.py
Test-Path Lab_Assignment/workers/synthesis.py
Test-Path Lab_Assignment/contracts/worker_contracts.yaml
Test-Path Lab_Assignment/artifacts/grading_run.jsonl
Test-Path Lab_Assignment/docs/system_architecture.md
Test-Path Lab_Assignment/docs/routing_decisions.md
Test-Path Lab_Assignment/docs/single_vs_multi_comparison.md
Test-Path Lab_Assignment/reports/group_report.md
Test-Path Lab_Assignment/reports/individual/kieu_duc_long.md
```

Không nộp nếu còn:

- [ ] Placeholder answer.
- [ ] TODO trong contract/docs/report.
- [ ] Trace thiếu `route_reason`.
- [ ] Câu trả lời không có source khi có tài liệu.
- [ ] gq07 bịa thông tin.
- [ ] gq09 không multi-hop.
- [ ] `grading_run.jsonl` không parse được JSON.
- [ ] Hardcoded API key/secret.

## Phase 13 - Git hygiene and submission

- [ ] Kiểm tra status:

```bash
git status --short
```

- [ ] Kiểm tra diff trước khi nộp:

```bash
git diff -- Lab-Solution.md Lab_Assignment
```

- [ ] Đảm bảo `.env`, API key, secret không bị commit.
- [ ] Commit message theo conventional commit:

```bash
git add Lab-Solution.md Lab_Assignment
git commit -m "feat: add day09 multi-agent lab assignment"
```

- [ ] Nếu cần push:

```bash
git push -u origin main
```

## Priority checklist cuối cùng

P0 bắt buộc:

- [ ] `graph.py` gọi worker thật.
- [ ] End-to-end chạy không crash.
- [ ] `grading_run.jsonl` đúng schema.
- [ ] gq07 abstain.
- [ ] gq09 multi-hop.

P1 rất quan trọng:

- [ ] Retrieval fallback keyword.
- [ ] Synthesis fallback khi LLM lỗi.
- [ ] MCP tool call có trace.
- [ ] Contracts cập nhật actual implementation.

P2 tối ưu điểm:

- [ ] Docs có metrics thật.
- [ ] Individual report có bằng chứng cụ thể.
- [ ] Confidence score không hard-code một giá trị duy nhất.
- [ ] Bonus MCP/trace nếu còn thời gian.
