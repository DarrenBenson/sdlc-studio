# BG0370: US0516's stated-absence escape hatch defeats the criteria floor US0514 and US0515 establish

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (RUN-01KYKVZM review carry-forward); agent; skill v5.0.0

## Summary

US0514 refuses a unit reaching terminal with no acceptance criteria and US0515 time-boxes the exemption to an existing baseline. US0516 has a filed finding carry criteria derived from its own evidence, and permits a stated absence when the evidence supports none. A stated absence satisfies the section check while carrying no criterion, so the floor is one sentence of prose away from being optional for every newly filed unit - which is precisely the population the floor was built for.

## Steps to Reproduce

Observed during the RUN-01KYKVZM review. File a finding whose criteria block records that no criteria could be derived, then transition it to terminal: the criteria check is satisfied and nothing was ever verifiable.

## Proposed Fix

Rule what a stated absence means at terminal. Either it is permitted at filing but refused at terminal - a unit cannot be Done on evidence it recorded as underivable - or it requires an operator waiver recorded through the waiver path, so the exemption is visible rather than self-served.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Severity Medium -> High: Verified on a fresh project: file_finding writes the stated absence AUTOMATICALLY for a thin finding, and the bug then reached Fixed with zero acceptance criteria and no refusal. This is the default path, not a deliberate act, and it defeats the criteria floor US0514 installed. |
| 2026-07-28 | Claude Opus 5 (RUN-01KYKVZM review carry-forward) | Filed |
