# CR-0299: The release-required strict version gate (check_versions.py --strict, the CHANGELOG home) is invoked by nothing executable; gate.py --release does not run it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** process
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, tools/check_versions.py, sdlc-studio/tsd.md, templates/workflows/release-gate.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

tsd.md twice marks version consistency as a blocking release gate and its pipeline stage 4 says `check_versions` must agree 'across every version home including CHANGELOG'. The CHANGELOG home is enforced only under --strict, and nothing executable passes that flag: package.json's lint:versions, the pre-commit hook and CI all run it plain; the only non-test occurrence of --strict is a prose bullet in templates/workflows/release-gate.md - a checklist a human reads, which itself admits the gap ('run the strict version check explicitly pre-tag'). gate.py --release, which exists precisely because 'two exit codes an operator had to remember to read' once let a rotted layer reach a release candidate, does not invoke `check_versions` at all - so the release-only leg holds only when someone remembers a flag (LL0027), the failure mode the same paragraph narrates. CR0233 fixed this class for `verify_ac` but never scoped `check_versions` in. Verified 3x.

## Impact

tsd.md twice marks version consistency as a blocking release gate and its pipeline stage 4 says `check_versions` must agree 'across every version home including CHANGELOG'.

## Acceptance Criteria

- [ ] gate.py --release runs `check_versions` --strict (or an equivalent mechanical release step does), so a CHANGELOG version mismatch fails the release gate with one exit code
- [ ] A test asserts gate --release fails on a CHANGELOG/version-home disagreement
- [ ] tsd.md stage-4 and gate-table wording match the mechanical reality; the release-gate.md checklist bullet becomes redundant confirmation rather than the only enforcement

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
