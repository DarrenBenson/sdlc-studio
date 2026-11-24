# BG1739: critic.py record refuses a finding whose bare URL is followed by an escaped semicolon

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_bare_url.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py, changelog.d/BG1739.md
> **Evidence:** run twenty-five, BG1073 qa review rounds one and two
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson (qa); persona; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T13:35:52Z

## Summary

`file_finding._BARE_URL_RE` (`file_finding.py`:1707) runs to the next space, so in `see https://example.com/a\; next` it takes the backslash into the URL's code span, leaving an odd backtick count, and `critic.py record --issues` refuses the finding (`critic._TICK_RUN` excludes a backtick after a backslash, so the span's closing backtick is read as escaped). BG1073 fixed the same shape for `www.` addresses; the http(s) pass still has it. Base behaves the same.

## Steps to Reproduce

1. `critic.py record ... --issues '[new] see https://example.com/a\; then more'`. 2. It is refused for odd backticks.

## Proposed Fix

Stop the URL match before a backslash that escapes a semicolon, as the address pass now does, and pin it.

## Acceptance Criteria

- [ ] **AC1** Given the text `see https://example.com/a\; next`, when `file_finding._code_urls` runs, then the code span is `https://example.com/a` and the `\;` stays outside it. Fails on: `_BARE_URL_RE` runs to the next space, so the span is `` `https://example.com/a\` `` and the backslash sits inside it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_bare_url.py::BareUrlTests::test_a_url_stops_before_a_backslash_that_escapes_a_semicolon
- [ ] **AC2** Given `critic.py record --issues '[new] see https://example.com/a\; then more'`, when it runs, then it records the finding and does not refuse it for an odd backtick count. Fails on: the closing backtick follows a backslash, which `critic._TICK_RUN` reads as escaped, so the span never closes and the record is refused.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py::LedgerLintTests::test_a_url_followed_by_an_escaped_semicolon_is_recorded
- [ ] **AC3** Given a URL with a backslash inside its path (`https://example.com/a`) and one ending at a plain `;`, when spanned, then the first is kept whole and the second loses only the `;` (the controls beside AC1). Fails on: a fix that cuts a URL at any backslash.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_bare_url.py::BareUrlTests::test_an_inner_backslash_stays_in_the_url_and_a_plain_semicolon_stays_outside

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | Sam Eriksson (qa) | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: executable criteria for the span, the record refusal and the controls; the repro was run: `_code_urls` gives `` `https://example.com/a\`; next ``; Affects gains test_critic_ledger_lints.py (home of BG1073's www pins); the filed Affects named a test module that the fix does not need alone |
