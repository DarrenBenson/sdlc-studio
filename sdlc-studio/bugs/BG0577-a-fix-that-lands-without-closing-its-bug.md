# BG0577: A fix that lands without closing its bug leaves a backlog item that reads real and is not, and nothing detects it - 12% of the open bug backlog was fiction

> **Status:** Open
> **Created:** 2026-08-13
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/gate.py, tools/tests/test_backlog_integrity.py
> **Severity:** High
> **Points:** 5

## Summary

Working the open bug backlog on 2026-08-13 found that five of its forty-one units - roughly seventeen of one hundred and seventeen points, 12% - were not work at all. Two were already REPAIRED, with the repair landed and the bug never closed. Two carried premises that had EXPIRED, their counts having gone to zero without either bug being touched. One was a straight DUPLICATE of another open bug.

None of these is detectable today. `status.py points` counts open artefacts, `conformance` judges units that reached a terminal status, and neither asks whether an OPEN bug is still true. So the backlog reports a number that only ever grows more wrong, and every artefact computed from it inherits the error silently.

The cost is not the wasted points, which are recoverable. It is that the figure is load-bearing. The delivery plan approved on 2026-08-13 was sized at 117 points with a 9.3M-41M token forecast and a three-run shape derived from that total - all of it computed over a backlog now known to be 12% fiction. A capacity ceiling, a velocity rate and a run count were each chosen against a number nobody could check, and the only reason the error surfaced was that somebody read all forty-one bugs one at a time.

This is the same class the repository files hardest against - a claim nothing exercises - pointed at its own backlog rather than at its code.

## Steps to Reproduce

Measured 2026-08-13 against the 41 open bugs:

1. ALREADY REPAIRED, bug still Open.
   - BG0547 asserts the depth-parity advisory ASSIGNS `gate_warn` while the AC-verify advisory accumulates. All six assignment sites in `transition.py` `_pre_write_gates` now use the accumulating form `gate_warn = f"{gate_warn}; ..." if gate_warn else ...`.
   - BG0537 asserts `check_root_docs` reads raw lines while `check_body_links` blanks code spans. All three link passes in `tools/check_links.py` (lines 244, 282, 353) run their input through `_without_code`.

2. PREMISE EXPIRED.
   - BG0421 asserts twenty-one Open Questions reached a terminal status unanswered. Sweeping `sdlc_md.unresolved_questions` over every markdown file under `sdlc-studio/` returns 0.
   - BG0350 asserts twenty-five Done stories carry no independent critic verdict. `conformance.py check --root .` reports `588/670 conformant, 0 not, 82 exempt`.

3. DUPLICATE.
   - BG0534 and BG0563 describe one defect - `_EDIT_VERBS` in `verify_ac.py` being an enumeration - from opposite ends, with byte-identical `Affects`. One change closed both.

Each was found by reading the bug and re-running its own evidence. No command reports any of these five states.

## Proposed Fix

Two checks, both cheap, neither existing:

FIRST, a repaired-but-open detector. For each open bug, run the criteria it already carries - a bug reaching `Fixed` must have a `Verify:` line or a ticked box, and many carry one while Open. A bug whose own evidence passes is a candidate for closure and should be REPORTED, never auto-closed: whether the fix is complete is a judgement, and the point is to put it in front of somebody.

SECOND, a premise re-check on any bug whose summary states a COUNT. The four-of-five instances above all did - twenty-one questions, twenty-five stories, twenty findings, four units. Where the count is derivable, re-derive it and report the drift; where it is not, age the bug and prompt a re-read after N days.

The duplicate case is already partly covered: `sprint.py breakdown` reports shared-file clusters, and a pair with byte-identical `Affects` and a high title-token overlap is a stronger signal than a cluster. Report it at plan time, where the cost of carrying both is about to be paid.

Do NOT auto-close anything. The failure this bug describes is a backlog trusted without checking; a backlog that silently closes its own items would be the same failure with the sign reversed.

## Impact

Every plan, forecast and capacity decision computed from the backlog is wrong by an unknown margin, and the margin only grows: a bug filed today is checked at filing and never again. The measured instance is 12%, found by hand on one backlog on one day, so it is a lower bound rather than a rate.

Filed High because it defeats the estimator rather than degrading it, and because the evidence is two artefacts - an approved plan and a released version - rather than an argument. It is also the cheapest class of waste to remove: a repaired-but-open bug costs a full grooming, test-plan, review and sign-off cycle to discover, and one command to detect.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-13 | sdlc-studio | Created via `new` (deterministic) |
