# BG1073: critic.py record writes a reviewer's findings verbatim into a ledger the repository's markdownlint refuses, so a finding quoting an email-shaped name blocks the next commit

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py, changelog.d/BG1073.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** 2026-10-19 commit of US1075's round-1 repair: `sdlc-studio/reviews/critic-verdicts.md:1619:3928 error MD034/no-bare-urls Bare URL used [Context: "boundary-push@gatehost.test"]`; worked round with `<!-- markdownlint-disable MD034 -->` in the ledger's header.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T12:42:14Z

## Summary

`critic.py record` appends each verdict's ISSUES text to sdlc-studio/reviews/critic-verdicts.md as a table cell. It already escapes some markdown (an earlier row reads `\_affects\_declared`), but not an email-shaped token. US1075's round-1 verdict quoted the suite name `boundary-push@gatehost.test`, markdownlint's MD034 (no bare URLs) read it as an email address, and the pre-commit markdown lane refused the commit carrying the ledger. The verdict cannot be rewritten (the ledger is append-only and a reviewer's words are never edited), so MD034 is now disabled for the ledger file by a header directive.

## Steps to Reproduce

`critic.py record --unit <id> --from-verdict <file>` with ISSUES containing `boundary-push@gatehost.test`, then `git add sdlc-studio/reviews/critic-verdicts.md && git commit` -> `FAIL markdown ... MD034/no-bare-urls Bare URL used`.

## Proposed Fix

Have the ledger writer neutralise markdown-active tokens it already knows to escape (bare URLs and email shapes, as it does underscores), or carry the MD034 directive in the ledger it creates, so a new project's ledger has it from the first row.

## Acceptance Criteria

- [ ] **AC1** A verdict whose findings quote an email-shaped or URL-shaped token is recorded into a ledger that passes markdownlint
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_ledger_lints.py -k email_shaped_finding_lints

## Impact

A verdict that quotes an email-shaped name blocks the commit that records it until someone edits the ledger's header by hand.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
