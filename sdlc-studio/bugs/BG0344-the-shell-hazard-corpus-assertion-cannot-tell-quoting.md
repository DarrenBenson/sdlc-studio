# BG0344: The shell-hazard corpus assertion cannot tell quoting from hazard, so evidence about shell defects must be degraded to commit

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (dogfooding friction, pre-sprint check RUN-01KYHVWK); agent; skill v5.0.0

## Summary

The measured-catch-rate test asserts that no legitimate artefact field is flagged by the shell-hazard fingerprint, over the whole corpus. An artefact whose evidence QUOTES shell syntax - because the defect it reports IS about shell syntax - is therefore indistinguishable from a hazard, and blocks the commit. It happened twice on 2026-07-27: BG0305, reporting a fence-parsing defect, was flagged for an unbalanced backtick in its quoted repro, and BG0340, reporting a guard's hand-enumerated globs, was flagged for the command substitution inside the very grep line it was citing. Both were resolved by rewording the evidence into prose, so both artefacts now describe what the auditor found instead of quoting it. This is distinct from BG0301 (Fixed), which addressed aligned code.

## Steps to Reproduce

1. File a finding whose evidence quotes a shell construct - an unbalanced backtick, or a command substitution. 2. Commit. 3. The suite fails, naming the artefact field as a false positive. 4. Reword the evidence away from the literal text and the commit passes, having traded fidelity for a green gate. Note the filing path cannot itself execute the text: `file_finding`'s fields-file reads values off disk so no value crosses a shell.

## Proposed Fix

Give an artefact a way to say a field quotes shell syntax deliberately - a fenced span the fingerprint skips, or an explicit escape - so the guard keeps its zero-false-positive property without the corpus paying for it in falsified evidence. Failing that, scope the assertion to fields that can actually reach a shell, since the recommended filing path already prevents that for stored prose.

## Acceptance Criteria

### AC1: a field quoting shell syntax deliberately is not counted as a hazard

- **Given** the defect as filed in Steps to Reproduce
- **When** the repair is in place
- **Then** the behaviour is the one the Proposed Fix describes, proven by a test written red before the fix
- **Proven by:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py::QuotedShellSyntaxTests, written red before the fix and green after
- **Verified:** yes (2026-07-28, functional)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (dogfooding friction, pre-sprint check RUN-01KYHVWK) | Filed |
| 2026-07-28 | Claude Fable 5 | Delivered in RUN-01KYJZGZ; acceptance criteria authored at review against the tests that landed |
