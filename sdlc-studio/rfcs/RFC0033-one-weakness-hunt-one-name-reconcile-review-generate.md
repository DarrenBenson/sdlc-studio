# RFC-0033: One weakness-hunt, one name: reconcile review generate, the adversarial audit, and the audit collision

> **Status:** Accepted
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

Option **A** - fold to one adversarial `audit` with profiles, refute panel included - **accepted**.
It is the only option that makes the strong tool the discoverable one. All five decisions below are
resolved.

## Open Decisions

| # | Decision | Resolution | Status |
| --- | --- | --- | --- |
| D1 | The three-way name collision on the `audit` stem. | **Rename the two deterministic scripts.** `audit.py` (sprint pre-flight readiness) -> `readiness.py`; `audit_check.py` (schema linter) -> `schema_check.py`. This frees `audit` for the user-facing adversarial weakness-hunt. Both are internal - the renames touch the gate and sprint call sites and the tests, no public surface. | Decided |
| D2 | Fold `review generate` into `audit`, or keep both. | **Fold.** The zero-setup repo review becomes `audit --profile repo`, alongside project and code profiles, and gains the refute panel it lacks today. `review` keeps only the consistency job. One name per weakness-hunt. | Decided |
| D3 | The public rename of `review generate`. | **Remove immediately, no alias.** The command is not well-known (model-invoked; users say "review this repo" in plain language), so a permanent alias would be more clutter than kindness. `review generate` is deleted and the README + `docs/why-sdlc-studio.md` + `docs/existing-users.md` switch to `audit --profile repo`. | Decided |
| D4 | Does the on-ramp get the refute panel? | **Yes** - resolved by D2's fold. Every profile, including `repo`, runs the N-of-M refutation. This session's BG0124 (a confident false finding a refute pass would have caught) is the evidence that an "advisory" on-ramp without it still costs. | Decided |
| D5 | Verb, if not `audit`. | **Moot** - resolved by D1. With the deterministic scripts renamed off the stem, the user command is `audit`, the name RFC0002 accepted. | Decided |

## Workstream (spawned on acceptance)

Per the repo's RFC-vs-CR rule, this accepted RFC spawns its CRs rather than being actioned directly.
D1 gates the rest. Implementation is a public-surface change (removing a documented command, editing
the README), so it lands under the freeze on `main` unreleased and ships with v4.2 - it is not a
this-week production release.

- **CR (D1):** rename `audit.py` -> `readiness.py` and `audit_check.py` -> `schema_check.py`, update
  every call site (gate, sprint), tests and `reference-scripts.md`. Unblocks the stem.
- **CR (D2, D4, D5):** build the `audit` command - `help/audit.md`, Type Reference row, catalogue
  entry, the `repo`/`project`/`code` profiles, and the refute panel wired to the finder legs. Makes
  RFC0002's accepted command discoverable and invokable at last.
- **CR (D3):** retire `review generate` - fold its three legs into `audit --profile repo`, delete the
  command, and switch the README and the two docs pages to `audit`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
