# CR-0612: Check a finding filed into the skill source repository against the neutrality blocklist when it is filed, not first at commit

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0277
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, tools/check_neutrality.py, tools/tests/test_check_neutrality.py
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. BG0949-BG0952 and BG0962.
> **Date:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:06Z

## Summary

Agents in consuming projects file findings straight into this repository. Five of the fifteen filed on 2026-10-06/07 (BG0949-BG0952, BG0962) named a private consuming project, and nothing objected until another session tried to commit them and the neutrality lane refused, leaving that session to generalise someone else's prose. `tools/check_neutrality.py` already holds the rule; `file_finding.py` could run it on the new artefact when the target root carries it, and refuse or rewrite there.

## Impact

Every consuming-project agent that files upstream, and every session that later commits its filings.

## Acceptance Criteria

- [ ] Filing into a root that carries the neutrality check refuses, or flags, a finding naming a blocklisted term, before any id is spent
- [ ] Filing into a root without the check behaves as today

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Raised |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Fail-closed or fail-open when the target root's checker cannot run, including a stale checkout whose checker predates `--stdin`? The panel recommends fail-closed (refuse, naming the fix: update the checkout of the skill source), per LL0008; the cost is that an agent filing into a stale clone is refused until that clone is pulled. Drafted fail-closed; the operator decides.
