# EP0241: A kill recorded against a node the criterion does not name is reported, not counted

> **Status:** Draft
> **Derived Point Total:** 11
> **Parent:** CR0554
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0554. Delivers the work CR0554 requested.

## Story Breakdown

- [ ] [US0793: A row whose ledger kill node is not named by its criterion's `Verify:` selector reads `killed-elsewhere`](../stories/US0793-a-row-whose-ledger-kill-node-is-not.md)
- [ ] [US0794: A row whose kill node IS named reads `killed`, unchanged - the paired control](../stories/US0794-a-row-whose-kill-node-is-named-reads.md)
- [ ] [US0795: A `Verify:` line naming a whole file is compared at FILE granularity](../stories/US0795-a-verify-line-naming-a-whole-file-is.md)
- [ ] [US0796: The corpus count of `killed-elsewhere` rows is recorded as a baseline before the check blocks](../stories/US0796-the-corpus-count-of-killed-elsewhere-rows-is.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a plan row whose ledger kill node is not named by its criterion's `Verify:` selector, when `plan_execution` reports that row, then its verdict is `killed-elsewhere` and names both the node that killed it and the node the criterion asked for
- [ ] Given a plan row whose ledger kill node IS named by its criterion's `Verify:` selector, when `plan_execution` reports that row, then its verdict is `killed`, unchanged from today
- [ ] Given a criterion whose `Verify:` line names a whole file rather than a node, when a row under it is reported, then the comparison is made at file granularity rather than reported as a mismatch
- [ ] Given this repository's corpus, when the check is run over every unit with a test plan and a ledger, then the count of `killed-elsewhere` rows is recorded as a measured yield rather than asserted

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
