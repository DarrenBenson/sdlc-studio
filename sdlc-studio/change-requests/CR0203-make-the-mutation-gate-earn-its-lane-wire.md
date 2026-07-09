# CR-0203: make the mutation gate earn its lane: wire a bounded run into sprint close or remove it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** process
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

gate.py:121-128 has warned 'mutation gate not run (no mutation-report.json) - advisory' on 100% of runs since mutation.py landed 2026-07-04 (no report exists anywhere; no run evidence across two full sprints). A lane that always warns trains agents to ignore [warn] - the selective-attention failure implicated in the lint breakage. Related noise: disclosure's 17 standing advisories (orphans + script-not-executable). Found by RV0007.

## Acceptance Criteria

- [ ] Either a bounded mutation.py run (e.g. --since last tag over the changed surface) is wired into sprint close/CI and produces mutation-report.json, or the gate lane is removed until something produces one
- [ ] After the change, a routine gate run emits zero permanent [warn] lines from the mutation lane
- [ ] The disclosure advisory set is triaged to zero or explicitly allowlisted (see the quality-debt CR)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Raised |
