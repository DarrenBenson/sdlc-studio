# CR-0516: Two mechanical tasks have no tool: review-batch findings cannot survive the shell, and no command reports backlog points

> **Status:** Complete
> **Decomposed-into:** EP0203
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S

## Summary

Two mechanical tasks with no tool, each of which forced hand-rolling in RUN-01KYX375 and each of which produced a defect while being hand-rolled. Filed under the rule that a missing tool is a gap to record, not a script to write.

GAP 1 - NO FIELDS-FILE ON `review-batch`. `--findings` takes prose on the command line, and a review finding is exactly the content most likely to carry backticks, `$(`, and quoted selectors. Two recorded verdicts this run had text eaten by shell command substitution: phrases such as reading `total` while the budget lane reads `total.selected` were silently reduced to 'reading' followed immediately by 'while the budget lane reads', with the term between them gone and the spaces that flanked it closed up, so the permanent review record is now less specific than the review was. `reference-scripts.md` already warns that backticks are command substitution and the `--fields-file` convention already exists on `decisions.py add`, `goal-review` and `artifact.py new`; `review-batch` simply lacks it.

GAP 2 - NO POINTS CENSUS. Asked how many points remain in the backlog, no tool answers. `status.py` reports counts, not points; `sprint.py breakdown --format json` reports grooming state with no points anywhere in its output; only `sprint plan` sums points, and it is a batch planner rather than a backlog query. A hand-written census was therefore written to answer a question the operator asks routinely - and being hand-written it silently included a `Won't Implement` story in its first pass.

## Impact

Anyone recording a review verdict, and anyone asked how much work is left.

GAP 1 damages the permanent record, silently and in the direction that looks fine. A finding
passed to `--findings` on the command line loses whatever a shell substitutes: two verdicts in the
run that raised this had a backticked term removed and the surrounding spaces closed up, so the
sentence still reads as English and no longer says what the reviewer said. Nothing downstream can
detect that - a verdict is not re-derivable from anything - so the loss is permanent and invisible
at the same time, which is the pairing this repository treats as worst.

GAP 2 costs a hand-rolled answer every time the question is asked, and a hand-rolled census is
wrong in ways nobody checks. The first one written for this gap counted a `Won't Implement` story
into the remaining points. Every appetite, tranche and go/no-go decision that reads "how much is
left" reads whatever that census said.

## Acceptance Criteria

- [ ] `review-batch --fields-file` stores a findings document containing backticks and `$(` verbatim, proven by reading the recorded row back and comparing byte-for-byte with the input
- [ ] A findings string passed through the shell is no longer the only path, and the help names the fields-file as the way to record text carrying shell metacharacters
- [ ] A single command answers how many points remain in the delivery backlog, split by status and by type, and excludes terminal statuses - proven against a fixture containing one `Won't Implement` unit, which must not be counted
- [ ] The points census agrees with `sprint plan`'s total over the same unit set, so two readers cannot report different sizes for one backlog

## Steps to Reproduce

GAP 1: invoke review-batch from bash with a findings string in double quotes containing two backtick-quoted terms. The recorded row loses both, because the shell performs command substitution before the tool ever sees the argument. Compare decisions.py add --fields-file, which exists for this reason.
GAP 2: run `status.py` (counts, no points), then `sprint.py breakdown --bugs Open --stories Ready --format json` and inspect its keys: mode, blocking, ungroomed, oversized, groomed, ceiling, downgraded, clusters, affects_advisories, decompose, triage, ok - no points, and no per-unit records to sum.

## Proposed Fix

GAP 1: add `--fields-file` to `review-batch`, accepting the same JSON document shape the other commands take, so a verdict's findings are stored verbatim. `-` reads from stdin, as elsewhere.
GAP 2: give the backlog census a home. Either `status.py --points` or a `breakdown` that carries per-unit records with their points, so the routine question - how much is left, by status and by type - is answered by the tooling rather than by a script written on the spot.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
