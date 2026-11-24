# BG1073: critic.py record writes a reviewer's findings verbatim into a ledger the repository's markdownlint refuses, so a finding quoting an email-shaped name blocks the next commit

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py, changelog.d/BG1073.md
> **Evidence:** 2026-10-19 commit of US1075's round-1 repair: `sdlc-studio/reviews/critic-verdicts.md:1619:3928 error MD034/no-bare-urls Bare URL used [Context: "boundary-push@gatehost.test"]`; worked round with `<!-- markdownlint-disable MD034 -->` in the ledger's header. Reproduced at cecc9dfe in a fresh project, 2026-11-24.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T12:42:14Z

## Summary

`critic.py record` appends each verdict's ISSUES text to sdlc-studio/reviews/critic-verdicts.md as a table cell. It escapes underscores and asterisks, and since 3d6f4210 (US1134) it puts a bare `http(s)://` URL in a code span (`_code_urls`), but it leaves an email-shaped token and a `www.` address bare. US1075's round-1 verdict quoted the suite name `boundary-push@gatehost.test`, markdownlint's MD034 (no bare URLs) read it as an email address, and the pre-commit markdown lane refused the commit carrying the ledger. The verdict cannot be rewritten (the ledger is append-only and a reviewer's words are never edited), so this repository's ledger disables MD034 by a header directive. The ledger header `critic.py` writes for a new project carries no such directive, so a consuming project meets the same refusal.

## Steps to Reproduce

1. In a fresh project, `critic.py record --unit US0001 --verdict reject --reviewer qa-seat --author eng-seat --issues "[new] the suite boundary-push@gatehost.test failed"`.
2. `markdownlint --config .markdownlint.json sdlc-studio/reviews/critic-verdicts.md` reports `MD034/no-bare-urls` on `boundary-push@gatehost.test`. The same holds for `[new] see www.example.com for it`; `[new] see https://example.com/x` is written in a code span and lints clean.

## Proposed Fix

Extend critic.py's ledger-cell escape (`_code_urls`, called from the record path) to put an email-shaped token and a bare `www.` address in a code span outside existing spans, as it already does an `http(s)://` URL, leaving a token already in a code span or angle brackets as written.

## Acceptance Criteria

- [ ] **AC1** Given a fresh project, when `critic.py record` writes a REJECT whose finding quotes `boundary-push@gatehost.test` outside a code span, then the ledger passes markdownlint under the repository's config with no MD034 finding, and the recorded finding still names the token. Fails on: the token is written bare and markdownlint reports MD034/no-bare-urls.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py::CriticLedgerBareUrlTests::test_an_email_shaped_finding_lints
- [ ] **AC2** Given a fresh project, when `critic.py record` writes a finding quoting `www.example.com` outside a code span, then the ledger passes markdownlint with no MD034 finding. Fails on: the address is written bare and markdownlint reports MD034.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py::CriticLedgerBareUrlTests::test_a_www_address_finding_lints
- [ ] **AC3** Given findings quoting an email inside a code span, an email in angle brackets and an `https://` URL, when `critic.py record` writes them, then each is written exactly as it is written today and the ledger lints clean. Fails on: a widened escape that wraps an already spanned or bracketed token again, writing nested backticks that break the row (this guard holds today).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py::CriticLedgerBareUrlTests::test_a_spanned_or_bracketed_token_is_left_as_written

## Impact

A verdict that quotes an email-shaped name blocks the commit that records it until someone edits the ledger's header by hand.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe; a bare `http(s)://` URL is already code-spanned (3d6f4210), an email shape and a `www.` address are not; criteria split into the two shapes plus a guard on spanned tokens, each naming its test node; Affects drops test_critic.py; Points stay 1 |
