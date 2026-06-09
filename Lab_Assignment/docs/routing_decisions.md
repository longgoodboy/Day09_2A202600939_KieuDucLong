# Routing Decisions

| ID | Route | Workers | MCP Tools | Expected evidence |
|---|---|---|---|---|
| gq01 | retrieval_worker | retrieval, synthesis | none | `p1_sla.md` |
| gq02 | policy_tool_worker | retrieval, policy, synthesis | search_kb | `refund_policy.md` |
| gq03 | policy_tool_worker | retrieval, policy, synthesis | check_access_permission | `access_control_sop.md` |
| gq04 | policy_tool_worker | retrieval, policy, synthesis | search_kb | `refund_policy.md` |
| gq05 | retrieval_worker | retrieval, synthesis | none | `p1_sla.md` |
| gq06 | retrieval_worker | retrieval, synthesis | none | `hr_remote_work.md` |
| gq07 | abstain/retrieval | retrieval, synthesis | none | no source; answer abstains |
| gq08 | retrieval_worker | retrieval, synthesis | none | `password_security_faq.md` |
| gq09 | multi_worker | retrieval, policy, synthesis | check_access_permission, get_ticket_info | `p1_sla.md`, `access_control_sop.md` |
| gq10 | policy_tool_worker | retrieval, policy, synthesis | search_kb | `refund_policy.md` |

Route reasons are produced by `graph.classify_route`. The reason is never `unknown`; it states whether the question matched P1/ticket keywords, policy/access/refund keywords, both, or no internal-policy keywords.
