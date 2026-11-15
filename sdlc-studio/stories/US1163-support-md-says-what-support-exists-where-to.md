# US1163: SUPPORT.md says what support exists, where to ask and what is not supported, naming only channels the repository has

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0702
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** SUPPORT.md, tools/check_links.py, tools/tests/test_check_links.py, tools/tests/test_support_page.py, changelog.d/US1163.md
> **Epic:** EP0310
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** sUPPORT.md says what support exists, where to ask and what is not supported, naming only channels the repository has
**So that** people who never open a terminal can follow progress without someone translating for them

## Acceptance Criteria

- **AC1:** Given SUPPORT.md, when its sections are read, then it has one for what support exists, one for where to ask and one for what is not supported.
  - **Verify:** pytest tools/tests/test_support_page.py::SupportPageTests::test_the_three_sections_are_present
- **AC2:** Given every channel SUPPORT.md names, when each is checked against the repository, then a GitHub link names only the repository's issues or its security policy (backed by .github/ISSUE_TEMPLATE/ and SECURITY.md), each issue template it names exists under .github/ISSUE_TEMPLATE/, and it gives no install command of its own but links docs/INSTALL.md.
  - **Verify:** pytest tools/tests/test_support_page.py::SupportPageTests::test_every_channel_named_exists
- **AC3:** Given tools/check_links.py, when it scans the root docs, then SUPPORT.md is among them and a SUPPORT.md link to a missing file is reported.
  - **Verify:** pytest tools/tests/test_check_links.py::RootDocsTests::test_support_md_is_a_root_doc

## Notes

- Serves Abena Osei's End goal 5 (also 6); delivers part of CR0702 (D0479).
- AC1 must fail on: the page at HEAD, which has no 'not supported' section
- AC2 must fail on: the HEAD page's `cp -r .claude/skills/sdlc-studio ~/.claude/skills/` line, or a channel (Discussions, chat, email) with nothing in the repository behind it
- AC3 must fail on: SUPPORT.md absent from ROOT_DOCS (tools/check_links.py:99)
- SUPPORT.md at HEAD (148 words) installs with `cp -r` rather than install.sh, calls CLAUDE.md 'Development guidance', and is outside check_links' ROOT_DOCS.
- If GitHub Discussions is enabled, the builder confirms it with `gh api repos/<owner>/<repo> --jq .has_discussions`, records that in the commit message, and adds it to the test's channel set; otherwise SUPPORT.md does not name it.
- Response times stay honest: best effort, maintained in spare time, unless the operator rules otherwise.
- The new test carries `# test-census-subject: SUPPORT.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
