# RV-0019: Gate-hardening sprint - closing unified review (BG0300, BG0301, US0445)

> **Date:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

The gate-hardening sprint (BG0300, BG0301, US0445), diff base 5b5ae41f..dc3bdf2a. Reviewed by an
independent adversarial reviewer (fresh context, QA seat), independent of the author, plus the
operator as reviewer of record.

## Findings

Adversarial pass probed label-not-value/vacuous tests, gate bypasses, over/under-stripping,
repo-wide side effects, and idempotence, running each suite and mutating each fix.

- One MAJOR (repaired + mutation-proven, `dc3bdf2a`): the BG0300 manual-AC Done gate accepted ANY
  `**Verified:**` marker, so a `no` (human saw it fail) or `stale` line reached Done - reopening the
  bypass. Fixed to require a passing `yes`; `no`/`stale`/absent all block, symmetric with a red or
  stale executable verifier. New tests cover `no` and `stale`.
- One MINOR (repaired): US0445's close-tail request derivation was repo-wide, unlike the scoped epic
  derivation - a close could sweep and name unrelated derivable requests. Scoped to this run's units
  plus the epics it derived; a new test proves an out-of-scope request is left untouched.

Could not break: no two-role bypass via request derivation (children already passed their own gates;
routes through the same `transition`), BG0301's exemption genuinely non-vacuous (fixtures trip each
rule unstripped), a real `$(...)` outside a code block still flagged, all mutations caught.

## Verdict

**APPROVE** after repair. The MAJOR was found, fixed and mutation-proven before sign-off; the MINOR
was addressed; both suites and the full suite (4535) are green. Operator ratified as reviewer of
record on 2026-07-27. Sprint-level record: `reviews/sprint-review-record.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
