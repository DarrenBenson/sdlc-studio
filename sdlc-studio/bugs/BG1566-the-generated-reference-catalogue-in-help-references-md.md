# BG1566: The generated reference catalogue in help/references.md links all 58 references to paths that do not exist

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/docgen.py, .claude/skills/sdlc-studio/help/references.md, tools/check_links.py, .claude/skills/sdlc-studio/scripts/tests/test_docgen.py, tools/tests/test_check_links.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, cross lens, survived 3 of 3 refute votes; observed at .claude/skills/sdlc-studio/help/references.md generated table, lines 67-124; writer at .claude/skills/sdlc-studio/scripts/docgen.py:213 (render_references); guard at tools/check_links.py passes 1 and 4
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:30:05Z

## Summary

The references verb of `docgen.py` renders each catalogue row as a link whose target is the bare file name, at line 213 in `render_references`. The page it writes lives in the help directory and the reference files live one directory up, so every one of the 58 links resolves to a path under help/ that does not exist; every other help page links to the parent directory. The page presents itself as the complete catalogue for discovery, so a reader or agent following any link from it reaches nothing. The links lane does not see it: `tools/check_links.py` reports success because its skill-tree pass checks only references that carry an anchor, and its file-target pass is scoped to the workspace by design. A generated page and the guard beside it therefore agree on a wrong answer.

## Steps to Reproduce

1. Open .claude/skills/sdlc-studio/help/references.md at line 67: the first row links reference-agent-prompt-template.md to the bare name reference-agent-prompt-template.md.
2. List .claude/skills/sdlc-studio/help/ and count the files whose names start with reference-: there are none.
3. Open .claude/skills/sdlc-studio/scripts/docgen.py at line 213: each row is rendered with the file name as both the link text and the link target.
4. Resolve each link target in lines 67 to 124 against the help directory: all 58 are missing.
5. Run tools/`check_links.py` from the repository root: it prints that all markdown links resolve.

## Proposed Fix

In `render_references`, write each link target relative to the page that holds it, so a row links to the reference file in the parent directory, and regenerate help/references.md with the references verb of `docgen.py`. In `tools/check_links.py`, resolve plain relative file links in shipped help pages against the linking file's directory and report a target that does not exist, keeping the existing reasons for scoping the artefact-body pass to the workspace. Add a test to `test_docgen.py` that every rendered target exists relative to the help directory, and a test to tools/tests/`test_check_links.py` that a help page linking a missing sibling file is reported while a link to an existing parent-directory file passes.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The references verb of `docgen.py` renders each catalogue row as a link whose target is the bare file name, at line 213 in `render_references`.
- [ ] **AC2** The proposed fix lands, pinned by a test: In `render_references`, write each link target relative to the page that holds it, so a row links to the reference file in the parent directory, and regenerate...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
