# BG-0001: Workflow/CR status vocabulary diverges across reference table, status-flow diagram, and sdlc_md.py code

> **Status:** Closed
> **Severity:** High
> **Reporter:** Adversarial Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

The canonical status vocabulary for Workflow and CR disagrees between reference-outputs.md, its own status-flow diagram, and the runtime STATUS_VOCAB in sdlc_md.py, with no test guarding the three against each other.

## Problem

reference-outputs.md is declared the single source of truth for status vocabularies, but three definitions have silently drifted. (a) Workflow 'Complete' is injected only in the enforcement table at reference-outputs.md:224 (valid AND terminal set), yet it appears nowhere else: not in the Output Formats row (line 39), not in the status-flow diagram (189-208), and not in sdlc_md.py STATUS_VOCAB['workflow'] (lines 179-182). (b) Conversely sdlc_md.py STATUS_VOCAB['cr'] (line 176) includes 'Blocked', which the canonical CR table at reference-outputs.md:222/:36 does not list. Because validate.py and reconcile.py source vocab from sdlc_md.py, a workflow file carrying the table-sanctioned 'Complete' is flagged status-vocab by validate.py and counts as 'Unknown' in status/reconcile, while a CR marked 'Blocked' validates clean despite being non-standard per the doc. Terminal Workflows also split across two strings (Done vs Complete) so any 'is this finished' check disagrees with the census.

## Proposed Fix

Reconcile the three sources to one vocabulary per type. Decide whether Workflow 'Complete' is real: if not, remove it from reference-outputs.md:224 so it reads '...Checking, Done, Paused, Superseded | Done, Superseded'; if yes, add it to line 39, the status-flow diagram, and sdlc_md.py:179-182. Decide whether CR 'Blocked' is real: either add it to the canonical CR table (reference-outputs.md:222, :36) or drop it from sdlc_md.py:176. Then add a unit test (and ideally a tools/ CI check) that parses the Status Vocab table out of reference-outputs.md and asserts equality with STATUS_VOCAB in sdlc_md.py, so vocab drift cannot recur silently.

## Evidence

.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py:176 (cr includes Blocked) and :179-182 (workflow omits Complete) vs reference-outputs.md:224 (Workflow vocab includes Complete; line 39 omits it; line 222 CR vocab omits Blocked)

## Impact

False-positive validation errors on legitimately-Complete workflows; mis-counted workflow/CR statuses in status and reconcile dashboards; terminal workflows split across two strings; the 'single source of truth' guarantee is unenforced so every vocab edit reopens the drift. Quality risk high, token cost low.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: determinism) |
