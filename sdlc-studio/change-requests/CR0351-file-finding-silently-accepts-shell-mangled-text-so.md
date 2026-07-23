# CR-0351: prose reaches the scripts through a shell argument, so a backtick silently empties the field it was documenting

> **Status:** In Progress
> **Decomposed-into:** EP0125
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/plan_review.py, .claude/skills/sdlc-studio/scripts/ledger.py, .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/templates/agent-instructions.md
> **Date:** 2026-07-19
> **Date-widened:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Every long field reaches these scripts as a shell argument. A backtick in the text is a
command substitution, so the shell runs whatever it encloses, gets nothing, and substitutes
empty before the script is even invoked. The artefact is then written and indexed with a hole
where the evidence was. Naming a command or a path is exactly what a finding is for, and
backticks are the natural way to write one.

The corruption therefore happens **outside** the scripts. No validation inside them can
prevent it; validation can only notice the damage afterwards, and only sometimes.

Originally raised against `file_finding` alone. A survey of the scripts directory found the
same shape in **13 scripts** that accept a `--summary`, `--body`, `--title`, `--text`,
`--description`, `--evidence`, `--note` or `--rationale`: `file_finding`, `artifact`,
`lessons`, `decisions`, `critic`, `handoff`, `plan_review`, `ledger`, `telemetry`, `sprint`,
`close_owed` and `audit_cost`. Only `critic` and `review_prep` offer a stdin form today, and
only for particular fields.

Documentation alone is not a fix. This has now bitten an agent that had the lesson in front
of it, twice in one session, and once produced a bug whose Summary read `US0251 AC2 runs .`
with the command gone.

## Impact

A filed finding is the durable record of something learned. Silent corruption at the moment
of filing means the record is wrong in precisely the detail that made it worth filing, and
nothing surfaces it - the artefact validates, indexes and reads as complete. Because the
missing token is usually the command, path or identifier, the reader who most needs it is the
one who cannot reconstruct it.

## Acceptance Criteria

- [ ] a shared helper in `lib/sdlc_md.py` gives every long field a form that does not transit
      a shell-quoted string: `--<field>-file PATH`, `-` for stdin, or `--from-json`, so text
      containing backticks, dollars or quotes survives verbatim
- [ ] all 13 scripts listed in Affects adopt that helper for their long fields; the existing
      argv form keeps working, so nothing that calls them today breaks
- [ ] a shared detector refuses text carrying the fingerprints of command substitution
      (collapsed double space, space before punctuation, a preposition immediately followed by
      punctuation) rather than writing it, and names the field and the likely cause
- [ ] the detector's limit is recorded, not implied: measured against the four real
      corruptions from RUN-01KXVYGR it catches three, with no false positive on a legitimate
      artefact sample. The one it misses lost a backticked token from the start of a sentence
      and left grammatical text behind, which is undetectable in principle - so the detector is
      documented as defence in depth and the file/stdin form as the actual fix
- [ ] `reference-scripts.md` documents the safe form as the default for prose, and
      `templates/agent-instructions.md` carries one line pointing consuming projects at it

## Notes

Sequencing matters: build the file/stdin form first, then the detector. A detector shipped
alone would train callers to trust a check that misses one case in four.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
| 2026-07-19 | sdlc-studio | Widened from `file_finding` to the 13 scripts sharing the defect; Size S to M; structural fix made the primary AC and the detector demoted to defence in depth, with its measured miss rate recorded |
