# US0466: The ungroomed AC marker routes to the shape and the verifier guidance, help/refine.md ships, and the help-page gap is a derived lane

> **Status:** Ready
> **Delivers:** CR0439
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/help/refine.md, .claude/skills/sdlc-studio/SKILL.md, .claude/skills/sdlc-studio/scripts/doc_coverage.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py
> **Epic:** EP0170
> **Points:** 3

## User Story

**As a** agent or operator grooming a skeleton refine minted
**I want** the placeholder and the router to name where the AC shape and the verifier guidance live
**So that** I author a Verify line that can fail instead of re-deriving the shape from a story I happen to open

## Acceptance Criteria

### AC1: the ungroomed marker routes to the shape and the verifier guidance

- **Given** UNGROOMED_AC_MARKER in lib/sdlc_md.py line 69 - the single string refine writes and conformance counts, kept there so writer and counter cannot drift
- **When** the marker text is read and every skill-relative path it names is extracted and resolved on disk
- **Then** it names templates/core/story.md (the Given/When/Then/Verify block) and reference-verify.md (what makes a Verify line discriminating), and both resolve, so a rename or move breaks the test rather than the groomer; the test asserts the extracted path set is non-empty, so an over-tight extractor cannot report a pass over zero paths (LL0008)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::UngroomedMarkerTests::test_marker_names_the_story_template_and_reference_verify

### AC2: help/refine.md ships and the page lane is derived from the Type Reference

- **Given** a new doc_coverage lane resolving every command in SKILL.md's Type Reference (39 today) to help/{command}.md, its waiver set a module constant in doc_coverage.py - NOT .config.yaml, because doc_coverage returns applicable=False for any tree with no SKILL.md, so a per-project knob would configure a check no consuming project runs
- **When** the lane runs against the real skill tree
- **Then** it passes; refine resolves to a shipped help/refine.md covering the decompose-then-groom flow, whose coverage is asserted in `/sdlc-studio refine <action>` invocation form rather than a prose backtick - the same false-pass doc_coverage.py:80 already guards against for help/help.md; the waiver set is exactly {decisions, repo, migrate} (the commands that lack a page after refine lands) and refine is absent from it, so deleting the page turns the lane red
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py::HelpPageCoverageTests::test_refine_page_ships_in_invocation_form_and_is_not_waived

### AC3: a missing page, a stale waiver and an unreadable tree all fail loud

- **Given** three fixture skill trees: one whose Type Reference names a command with no help page, one whose waived command has since gained a page, one whose help/ directory is absent
- **When** the lane runs over each
- **Then** the first fails naming that command, the second fails naming the stale waiver so an exemption cannot outlive its gap (LL0015), and the third fails naming the unreadable tree rather than reporting zero gaps from a directory it never read (LL0008); each case asserts a non-zero finding count and the expected name in the detail
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py::HelpPageCoverageTests::test_missing_page_stale_waiver_and_unreadable_tree_all_fail_loud

### AC4: the Progressive Loading Guide carries a grooming row that routes to real files

- **Given** the FIRST table of SKILL.md's Progressive Loading Guide (the Task Type / Primary / Secondary / Decision table at lines 125-178) and only that table - the Template-structure and Module-loading-flags tables, and the templated ({type}, {domain}, {language}), glob, #anchor and prose-wrapped cells, are explicitly out of scope here
- **When** that table is parsed, the row whose Task Type names grooming a refine-minted skeleton is located, and the literal paths in its cells are resolved against the skill tree
- **Then** the row exists and names templates/core/story.md and reference-verify.md, and both resolve; the test asserts the row was FOUND before asserting anything about it, so an absent row fails rather than passing over an empty cell set
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py::ProgressiveLoadingGuideTests::test_grooming_row_exists_and_its_paths_resolve

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
