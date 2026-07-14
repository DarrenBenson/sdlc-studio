# RFC-0033: One weakness-hunt, one name: reconcile review generate, the adversarial audit, and the audit collision

> **Status:** Draft
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Surfaced while running `review generate` on this repo: the user expected it to be the same
thing as `audit`, and could not tell the two apart. They cannot, because the command surface is
genuinely tangled. The verb **audit** means three different things, and the strongest
weakness-hunt in the whole skill is undiscoverable.

### The current state, mapped

| Thing | What it actually is | How it is reached |
| --- | --- | --- |
| `scripts/audit.py` | **Tranche readiness** - sprint pre-flight (weak ACs, unmet deps). Deterministic. | run by `sprint`, between plan and triage |
| `scripts/audit_check.py` | **Team-schema linter** - CI-runnable schema-v3 rules with stable ids. Deterministic. | run by the gate |
| `reference-audit.md` + `templates/automation/audit-{finder,classify,refute}.md` | **The adversarial weakness-hunt** - lens profiles, `find -> verify -> merge -> file`, an N-of-M **refute panel** (a candidate survives only on >=2/3 skeptics). An agent workflow. | **nothing.** No `help/audit.md`, no Type Reference row, zero entries in `help/help.md`. |
| `review generate` (`review_generate.py`) | **Zero-setup repo review** - three legs (architecture, code quality, security), files findings as Bug/CR, writes an RV report. An agent workflow. | documented: README (x2), `docs/why-sdlc-studio.md`, `docs/existing-users.md`, `help/review.md` |

### The two problems

1. **The strong tool is a ghost.** The adversarial audit has a 145-line spec, three prompt
   templates and a refute panel - and no way to discover or invoke it. `audit` appears nowhere in
   the command catalogue.
2. **The weak tool is the documented one.** `review generate` is the same activity - hunt a repo
   for weakness, file findings - **minus the refute panel**. That panel is precisely the defence
   against a plausible-but-wrong finding; `reference-audit.md` records it killing ~59% and ~47% of
   candidates in its two proving runs. This session paid for the absence of exactly that defence:
   BG0124 was a confident false finding that a refute pass would have caught. So the discoverable
   command is the one without the safeguard, and under the new disposition gate (RFC0032) a false
   finding now manufactures work downstream.

### This finishes RFC0002, it does not re-open it

**RFC0002 is Accepted** - it promoted the adversarial-review harness into a project-agnostic
`audit` command with pluggable lens profiles. `reference-audit.md` and the three
`audit-{finder,classify,refute}.md` templates are its output. What never happened is the *last
mile*: the accepted command was never given a `help/audit.md`, a Type Reference row, or a catalogue
entry, so it is unreachable. Meanwhile `review generate` grew up beside it doing the same job
without the refute panel. So this RFC is not new design over RFC0002 - it is "ship the accepted
command's discoverability, and fold the accidental duplicate into it." D2 below is really: does
`review generate` become a *profile* of RFC0002's audit, or stay a separate lighter tool.

### Why an RFC and not a CR

Two viable shapes at least (fold vs keep-both), a public-facing rename under a release freeze, and
a three-way name collision to resolve first. That is unsettled design with cross-cutting impact -
the repo's own RFC-vs-CR rule. Raised for investigation, not yet decided.

## Design Options

- **A - Fold `review generate` into `audit`.** One adversarial weakness-hunt, invokable as
  `audit`, with the zero-setup repo pass as a **profile** (`audit --profile repo`) alongside the
  project and code profiles. It gains the refute panel; `review generate` becomes an alias. `review`
  keeps only the consistency job (PRD/TRD/TSD/Persona). One name per job. Requires renaming the two
  deterministic `audit*.py` scripts out of the way first.
- **B - Keep both, document `audit`.** Give the adversarial audit the help file, catalogue row and
  Type Reference entry it never had; leave `review generate` as the on-ramp. Least churn, no public
  rename. The overlap remains, and the weaker command stays the discoverable one.
- **C - Rename `review generate` -> `audit`, retire the doc-only pipeline.** Simplest surface, but
  it throws away the refute panel and lens profiles - the parts that make findings trustworthy.
  Deletes the defence against the bug class we hit today. Recorded for completeness; not advised.

## Recommendation

Lean A (fold to one adversarial `audit` with profiles, refute panel included), because it is the
only option that makes the strong tool the discoverable one. But every open decision below is real
and the freeze means there is no rush - this is raised to be investigated, not to be actioned this
week.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | **The three-way name collision.** `audit.py` (tranche) and `audit_check.py` (schema linter) own the `audit` stem. Before any user-facing `audit` command exists, do these get renamed (to what - `tranche`/`readiness`? `schema-check`?), or does the user command avoid the stem entirely? A rename touches the gate and sprint call sites. | Open |
| D2 | **Fold, or keep both (A vs B)?** Is `review generate` genuinely redundant with the adversarial audit, or is the zero-setup, no-refute on-ramp worth keeping precisely because it is lighter for a first look at a stranger's repo? | Open |
| D3 | **Public rename under the freeze.** `review generate` is in the README and two docs pages as the try-before-you-adopt entry point. If it becomes an alias, when does the doc change ship - with the freeze lift, or never (keep the alias forever)? An alias that is never removed is not churn but is a permanent second name. | Open |
| D4 | **Does the on-ramp get the refute panel?** If `review generate` survives as a profile, does it gain the N-of-M refutation (slower, but no false findings reach the freshly-filed backlog), or stay fast-and-loose on the argument that an on-ramp is advisory? This session's BG0124 is the evidence that "advisory" findings still cost. | Open |
| D5 | **Verb, if not `audit`.** If D1 keeps the deterministic scripts on the `audit` stem, the user command needs another verb - `weakness`, `hunt`, `review --adversarial`? The name should say "adversarial weakness-hunt", not overload a word that already means two other things. | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
