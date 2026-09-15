# BG0674: sprint next materialises a charter's discovery items (CRs) that sprint plan then refuses, so the charter at the head of the queue produces a batch nothing can plan

> **Status:** In Progress
> **Verification depth:** functional [[derived: criteria 4; plan rows 7; executed 7; killed 7; survived 0; not-run 0; entry point 4 of 4 criteria through the shipped CLI, 0 in-process | fp 0be8c7099333 ]]
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** backlog sweep 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint.py next` resolves the head charter's scope query and materialises whatever it selects, including CRs, RFCs and Issues. `sprint plan` refuses those same units as 'DISCOVERY items, not deliverable work'. Reproduced in a throwaway clone at 51f264db: the queue head is SC0004 (query `--crs Proposed`); `next --dry-run` prints 'materialised 11 unit(s) ... CR0545, CR0523, CR0524, CR0543, CR0544, CR0557, CR0562, CR0563, CR0566, CR0567, CR0511', and `plan --crs Proposed` exits 2 'sprint plan REFUSED: 11 unit(s) are DISCOVERY items'. SC0004's query also no longer selects the CR its goal names (CR0497, now In Progress), and SC0001's has the same shape - both are separate content fixes. Found by the 2026-09-15 backlog sweep.

## Steps to Reproduce

1. In a throwaway clone, `python3 .claude/skills/sdlc-studio/scripts/sprint.py queue show` - SC0004 heads the queue with `--crs Proposed`.
2. `sprint.py next --dry-run` - it materialises 11 Proposed CRs.
3. `sprint.py plan --crs Proposed` - exit 2, the same 11 refused as discovery items.

## Proposed Fix

Apply plan's discovery refusal when `next` materialises, so a charter whose query selects discovery items is refused (or its discovery items named and excluded) at `next`, with the remedy - refine the request, or point the query at its decomposition - rather than at the plan that follows.

## Acceptance Criteria

- [ ] **AC1** In a fixture project with `two_backlog.enforce: true`, `sprint next` on a head charter whose query selects only discovery items (two Proposed CRs) exits non-zero; its stderr names each CR id and the decompose remedy (`refine.py apply --request`) - text none of `next`'s other refusals (no-query, bad-query, empty-scope, run-open) prints - and its stdout carries no `materialised N unit(s)` line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::NextRefusesDiscoveryItemsTests::test_a_discovery_only_query_is_refused_at_next
  - **Verified:** yes (2026-09-15)
- [ ] **AC2** In a fixture project with `two_backlog.enforce: true`, `sprint next` on a head charter whose query selects only deliverable units (an Open bug and a Ready story) exits 0 and its `materialised` line lists both ids - the paired control, run with enforcement on so the discovery test is actually consulted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::NextRefusesDiscoveryItemsTests::test_a_deliverable_query_materialises
  - **Verified:** yes (2026-09-15)
- [ ] **AC3** In a fixture project with `two_backlog.enforce: true`, a head charter whose query selects both kinds (an Open bug and a Proposed CR) is not refused: `sprint next` exits 0, the ids on its `materialised` line are the bug's and never the CR's, and a separate line names the CR as a discovery item that was not materialised - the stories and bugs of a mixed query are materialised, its discovery items are named and left out, and the batch is not refused whole
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::NextRefusesDiscoveryItemsTests::test_a_mixed_query_names_what_it_dropped
  - **Verified:** yes (2026-09-15)
- [ ] **AC4** In a project where `two_backlog.enforce` is off, `sprint next` materialises a CR-selecting charter as today - exit 0, the CR's id on its `materialised` line - so the refusal follows `sdlc_md.two_backlog_enforced`, the same condition `sprint plan`'s refusal reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::NextRefusesDiscoveryItemsTests::test_next_follows_the_two_backlog_condition_plan_reads
  - **Verified:** yes (2026-09-15)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint.py, print the discovery items as a warning on the next path and still return 0 with their ids in the materialised list | In a fixture project with `two_backlog.enforce: true`, `sprint next` on a head charter whose query selects only discovery items (two Proposed CRs) exits non-zero; its stderr names each CR id and the decompose remedy (`refine.py apply --request`) - text none of `next`'s other refusals (no-query, bad-query, empty-scope, run-open) prints - and its stdout carries no `materialised N unit(s)` line |
| AC1 | in .claude/skills/sdlc-studio/scripts/sprint.py, filter discovery units out of the resolved selection before the empty-scope check, so an all-CR charter falls through to the empty-scope refusal that names neither the CRs nor the refine remedy | In a fixture project with `two_backlog.enforce: true`, `sprint next` on a head charter whose query selects only discovery items (two Proposed CRs) exits non-zero; its stderr names each CR id and the decompose remedy (`refine.py apply --request`) - text none of `next`'s other refusals (no-query, bad-query, empty-scope, run-open) prints - and its stdout carries no `materialised N unit(s)` line |
| AC2 | in .claude/skills/sdlc-studio/scripts/sprint.py, invert the sdlc_md.is_discovery test applied to the charter's resolved units, so stories and bugs are the ones held back | In a fixture project with `two_backlog.enforce: true`, `sprint next` on a head charter whose query selects only deliverable units (an Open bug and a Ready story) exits 0 and its `materialised` line lists both ids - the paired control, run with enforcement on so the discovery test is actually consulted |
| AC3 | in .claude/skills/sdlc-studio/scripts/sprint.py, gate with all() over the selection's types instead of filtering per entry, returning the full selection untouched whenever one deliverable is present | In a fixture project with `two_backlog.enforce: true`, a head charter whose query selects both kinds (an Open bug and a Proposed CR) is not refused: `sprint next` exits 0, the ids on its `materialised` line are the bug's and never the CR's, and a separate line names the CR as a discovery item that was not materialised - the stories and bugs of a mixed query are materialised, its discovery items are named and left out, and the batch is not refused whole |
| AC3 | in .claude/skills/sdlc-studio/scripts/sprint.py, delete request-typed entries from units and ids without keeping them anywhere the output can print | In a fixture project with `two_backlog.enforce: true`, a head charter whose query selects both kinds (an Open bug and a Proposed CR) is not refused: `sprint next` exits 0, the ids on its `materialised` line are the bug's and never the CR's, and a separate line names the CR as a discovery item that was not materialised - the stories and bugs of a mixed query are materialised, its discovery items are named and left out, and the batch is not refused whole |
| AC3 | in .claude/skills/sdlc-studio/scripts/sprint.py, change the gate to any() and exit 2 as soon as one request-typed entry appears, discarding the deliverable entries with it | In a fixture project with `two_backlog.enforce: true`, a head charter whose query selects both kinds (an Open bug and a Proposed CR) is not refused: `sprint next` exits 0, the ids on its `materialised` line are the bug's and never the CR's, and a separate line names the CR as a discovery item that was not materialised - the stories and bugs of a mixed query are materialised, its discovery items are named and left out, and the batch is not refused whole |
| AC4 | in .claude/skills/sdlc-studio/scripts/sprint.py, drop the two_backlog_enforced condition from the next path so discovery items are held back in every project | In a project where `two_backlog.enforce` is off, `sprint next` materialises a CR-selecting charter as today - exit 0, the CR's id on its `materialised` line - so the refusal follows `sdlc_md.two_backlog_enforced`, the same condition `sprint plan`'s refusal reads |

## Coverage Rulings

| File | Line | Hash | Reason | Author | Date |
| --- | --- | --- | --- | --- | --- |
| .claude/skills/sdlc-studio/scripts/sprint.py | 10928 | b874fa1b23bb88d6 | queue show mirrors next's not-materialised line from the same helper; no criterion names queue show, and the line was exercised by hand through sprint.py queue show in a throwaway charter fixture | sdlc-studio | 2026-09-15 |
| .claude/skills/sdlc-studio/scripts/sprint.py | 10929 | b874fa1b23bb88d6 | the print half of the same queue show mirror as the line above, exercised through the CLI by hand | sdlc-studio | 2026-09-15 |
| .claude/skills/sdlc-studio/scripts/tests/test_sprint.py | 14427 | b9bf107be9f0d8aa | fixture helper: removes a config left by an earlier case; each test builds a fresh tree, so the branch is defensive | sdlc-studio | 2026-09-15 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
| 2026-09-15 | sprint plan repair 2026-09-15 | Plan review r1 repair. Design fixed: with two_backlog.enforce on, a mixed query materialises its stories and bugs and names (does not materialise) its discovery items, exit 0; an all-discovery query refuses non-zero naming the ids and the refine remedy. AC3 now states exit 0, the bug on the materialised line and the CR never on it, a separate line naming the CR, and no whole-batch refusal, with three rows: refuse only an all-discovery batch (the careless build), drop discovery entries silently, refuse the whole mixed batch. AC1 asserts the ids, the remedy text no other next refusal prints and the absent materialised line, with a new row for a filter that falls through to the empty-scope refusal. AC2 states enforcement is on in its fixture so the inverted is_discovery mutant dies. AC4 asserts the CR on the materialised line. Mutants re-anchored on sprint.py's next path rather than a resolve_head_charter/cmd_next split. |
