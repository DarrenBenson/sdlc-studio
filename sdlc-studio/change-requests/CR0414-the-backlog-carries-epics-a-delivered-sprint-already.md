# CR-0414: the backlog carries epics a delivered sprint already satisfied and nothing detects it: EP0125's shared prose-helper stories were largely built as EP0146, but built-not-closed reads the verify-report so an ungroomed skeleton with no verifiers is invisible to it

> **Status:** Proposed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/audit.py
> **Priority:** Medium
> **Type:** Feature
> **Size:** M

## Summary

{{what changes and why}}

## Impact

{{who this affects and what breaks}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |

## Detail

Found while composing Sprint 2. EP0125 ("Prose reaches every creation script without a shell",
stories US0361-US0364) sits Draft on the delivery backlog. Sprint 1 then delivered EP0146, whose
`file_finding.resolve_prose_fields` IS the shared fields-file helper US0361 asks for, adopted
across the prose writers US0361 names; and whose `shell_hazards` IS the command-substitution
fingerprint detector US0362 asks for. Neither epic references the other. Two refines, months
apart, minted the same goal twice, and a whole sprint delivered one of them without anything
noticing the other was now largely satisfied.

**Why the existing detector misses it.** EP0130's `built-not-closed` flag is deliberately
mechanical: it reads `.local/verify-report.json` and fires only where a unit's executable ACs all
pass. An ungroomed skeleton has no `Verify:` lines, so it can never appear in that report, so the
one check built for "this is already done" is structurally blind to the case that matters most -
work minted before it was groomed. The audit's `already-satisfied` lens has the same basis and the
same blindness.

The gap is SEMANTIC overlap between a planned unit and delivered work, which no mechanical
signal in the workspace currently covers. This is the two-backlog model's blind spot: refine
mints against the request, never against what has since shipped.

## Impact of the wider class

Every long-lived backlog. Here it would have wasted a 12-point epic in Sprint 2 had the overlap
not been spotted by eye. The failure mode is silent and grows with backlog age: the older the
skeleton, the likelier some later sprint satisfied it.

## Second measured instance (found during Sprint 2 grooming)

US0395 ("the scoped report merges rather than replaces") asks for behaviour that already ships:
`verify_ac.write_report(..., merge=True)` is the default and merges prior entries, `cmd_run`
passes `merge=not --fresh`, and `test_verify_ac.py::WriteReportMergeTests` already covers
accumulate / update-in-place / `--fresh` rebuild. The story was re-scoped during grooming onto the
parts genuinely absent (preserving out-of-scope freshness fields, a scoped-vs-unscoped equivalence
proof, and a refusal for `--fresh` combined with a scope, which would blank every out-of-scope
verdict).

Two instances now, found by eye in one sitting - EP0125 against the shipped EP0146, and US0395
against shipped `write_report`. Both were caught only because a human-directed grooming pass read
the source first. Nothing in the pipeline would have stopped either reaching a build.

## The wider class: a request's premise is never checked against the source

Grooming Sprint 2 surfaced a second failure mode alongside "already delivered": a request whose
stated FACT was never true, refined into sized work regardless.

- **CR0348 / EP0123** asserts a lane lints "only changed markdown". It does not: both `npm run
  lint:md` and the pre-commit `markdown` lane already glob the whole corpus. The real hole is a
  config split - `**/*.md` cannot match a dot-directory, so `.claude/**` is linted only under the
  laxer skill-local config with MD056/MD060 disabled, which is why an unescaped pipe in
  `help/sprint.md` sat green. The epic was re-groomed against the real hole.
- **US0392** (delivered last sprint) asserted telemetry.py takes note prose on the command line.
  It has no narrative flag at all; its only match is a boolean. Corrected mid-delivery.
- **US0382** asserts a root resolver must be built. `resolve_root` / `discover_root` /
  `under_root` already exist and are correct - in `verify_ac.py`, with three importers. The story
  is a promotion, not a build.

- **US0383** asserted "the 62 `--root` scripts", and the grooming pass that sized it estimated
  "~20 unanchored, 10 of them writers". The delivery MEASURED the real corpus: 64 scripts declare
  `--root`, 59 are unanchored, and 26 of those write. The story was sized against a number nobody
  had counted, and the grooming pass that was supposed to check it produced a second wrong number
  rather than a measurement. The remainder needed its own follow-up at 13 points - larger than the
  whole story it was carved out of.

Same root cause as the overlap case: `refine` mints from what the request ASSERTS, and nothing
between the assertion and the build reads the source to check it. The cost is paid twice - once
sizing fiction, once discovering it mid-sprint.

## Acceptance Criteria

- [ ] AC1: plan-time overlap detection that does not depend on verifiers
- **Given** a batch holding a unit whose title/summary closely matches work already delivered (a terminal unit, or a shipped epic touching the same Affects)
- **When** `sprint plan` runs
- **Then** it reports the candidate overlap with the delivered id, so the operator triages before the batch is built - advisory, never a refusal
- **Verify:** manual

- [ ] AC2: the report distinguishes overlap from mere file-sharing
- **Given** two units that touch the same file but do different work
- **Then** they are NOT reported as overlapping - a shared `Affects` alone is the existing cluster signal and must not be recycled as a duplicate claim
- **Verify:** manual

- [ ] AC3: the blind spot is documented where the existing detector is
- **Given** a reader of the built-not-closed behaviour
- **Then** the docs state plainly that it reads the verify-report and therefore cannot see an ungroomed unit, naming this check as the complement
- **Verify:** manual

- [ ] AC4: a request's factual premise is checked against the source before it is sized
- **Given** a request or story asserting a fact about the codebase ("only changed files are linted", "script X takes prose on the command line", "there is no shared resolver")
- **When** it is refined or planned
- **Then** the pipeline prompts for (or records) a source check of that claim, so a false premise is caught before it becomes sized work rather than mid-sprint
- **Verify:** manual
