# BG0669: conformance demands acceptance criteria of a story retired unbuilt, so an ungroomed story cannot be Superseded or Won't Implement without a waiver

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** backlog sweep 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

conformance.py exempts an ungroomed story from the `specified` and `verifiable` stages only while its status is in `_PRE_GROOMED_STORY_STATUS` (Proposed, Draft). A refine skeleton that is retired - Superseded or Won't Implement - leaves that set, so the gate then demands an `## Acceptance Criteria` section and a `Verify:` line of a story that will never be built, and the commit that retires it is refused. The demand is meaningless for an abandonment terminal: there is nothing to specify or verify for work nobody will do. Found retiring US0719, US0797 and US0798 in the 2026-09-15 backlog sweep (each a refine skeleton superseded by delivered work); they closed only under per-unit waivers. US0680 and US0681 retired the same way passed only because they happened to be groomed, so the gate's verdict turns on an accident of grooming, not on the retirement.

## Steps to Reproduce

1. In a throwaway workspace, create a story via refine whose criteria are the ungroomed placeholder (Status: Draft).
2. Run `conformance.py check` - the story is conformant (Draft is pre-groomed).
3. `transition.py set --id <story> --status Superseded` (or Won't Implement).
4. Run `conformance.py check` again - it now reports `<story> (Superseded): missing specified, verifiable`, and `gate.py` fails the conformance lane, so the commit carrying the retirement is refused.

## Proposed Fix

Treat the story's abandonment terminals (Won't Implement, Superseded - the non-Done members of its terminal set, derived from `sdlc_md` rather than restated) like the pre-groomed statuses for the AC stages: a story retired unbuilt needs only `decomposed`. Leave Done untouched. Then withdraw the waivers recorded for US0719, US0797 and US0798.

## Acceptance Criteria

- [ ] **AC1** An ungroomed story retired to Superseded is conformant: conformance reports no missing specified or verifiable stage for it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::RetiredUnbuiltTests::test_a_superseded_skeleton_is_conformant
- [ ] **AC2** An ungroomed story retired to Won't Implement is conformant on the same terms
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::RetiredUnbuiltTests::test_a_wont_implement_skeleton_is_conformant
- [ ] **AC3** A story at Done with no acceptance criteria is still reported missing specified and verifiable - the paired control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::RetiredUnbuiltTests::test_a_done_story_without_criteria_is_still_refused
- [ ] **AC4** The exempt set is derived from the story's terminal vocabulary, not a hand-typed list
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::RetiredUnbuiltTests::test_the_exempt_set_is_derived_from_the_vocabulary

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
