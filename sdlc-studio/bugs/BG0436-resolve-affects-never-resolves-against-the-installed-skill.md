# BG0436: resolve_affects never resolves against the installed skill dir, so detector-owed --file tracebacks on every default install

> **Status:** Fixed
> **Verification depth:** functional (resolved from an EMPTY fixture root, so only the loaded skill dir can satisfy it; absent-path control and the derivation both pinned)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_detector_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py
> **Evidence:** Executed by an independent reviewer on two identical roots differing only in whether the skill is vendored; the mechanism is confirmed statically here (resolve_affects has two candidate bases, neither of them SKILL_DIR).
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`resolve_affects` resolves a declared path against `root` and `root/.claude/skills/sdlc-studio` only - never the skill dir the run is actually loaded from - although its own docstring says 'or the installed skill dir'. `detector-owed --file` declares the owed unit's Affects as `.claude/skills/sdlc-studio/templates/audit-profiles/<profile>.md`, which therefore resolves only in a project that VENDORS the skill in-tree. `install.sh` defaults to `--global`, so in every other project the path resolves to nothing and the pre-mint Affects check raises an uncaught ValueError: the operator gets a Python stack trace, not a message. The story's own fixture manufactures that path inside the audited root, which is exactly the shape that conceals it. Sub-case: for an owed lens with no pack the declared Affects is a DIRECTORY, which passes only because `resolve_affects` accepts one - the fictional-footprint class the code comment says it was fixing.

## Steps to Reproduce

1. Build a consuming project with no vendored skill and two findings sharing a lens across two registered runs.
2. `readiness.py --root <project> detector-owed --file`.
3. Uncaught ValueError from `file_owed_detectors`; no CR minted, no message.

## Proposed Fix

Resolve an Affects path against the loaded `SKILL_DIR` as the docstring already promises, and make the shipped-payload path declaration relative to that. Handle the no-pack case with a real file footprint or no Affects rather than a directory.

## Acceptance Criteria

### AC1: a shipped-payload path resolves without vendoring

- **Given** a project that does NOT vendor the skill into its tree
- **When** an Affects naming shipped payload is resolved
- **Then** it resolves against the LOADED skill dir, as the docstring already promised - because everywhere but this repo it silently resolved to nothing, and an Affects that resolves to nothing reads as an ungroomed unit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::ResolveAffectsSkillDirTests::test_a_shipped_payload_path_resolves_without_vendoring
- **Verified:** yes (2026-08-02)

### AC2: a genuinely absent path still resolves to nothing

- **Given** a path that exists nowhere
- **When** it is resolved
- **Then** it is None, so greenfield paths keep reading as absent and the grooming gate still catches a declared file nobody has written
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::ResolveAffectsSkillDirTests::test_a_genuinely_absent_path_still_resolves_to_nothing
- **Verified:** yes (2026-08-02)

### AC3: the loaded skill dir is derived, not assumed

- **Given** the module's own location
- **When** the skill dir is taken
- **Then** it is derived from there, because the skill runs from an INSTALLED copy in every consuming project and a hardcoded repo path would resolve only here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::ResolveAffectsSkillDirTests::test_the_loaded_skill_dir_is_derived_not_assumed
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
