# RFC-0018: self-check candidates vocabulary-consistency verb-taxonomy and telemetry surfacing

> **Status:** Accepted
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new

## Summary

The world-class review (v2.4.4 audit) raised three candidate improvements that are genuinely useful
but **design-level and false-positive-prone**, so they were deliberately kept out of the build and
parked here for a decision (the doc-freshness check, which clearly earned its keep, shipped in v2.5.0
as CR0073). This RFC weighs the three before any of them becomes code.

## Design Options

Each is independent - accept, decline, or defer per candidate.

### C1 - Cross-file vocabulary-consistency check

A check that flags when a domain term is used inconsistently across the artifact layers (PRD vs TRD
vs code vs tests), or when a rename (e.g. the historical "PM" -> "Product Owner") leaks unevenly
across the 46 reference files. **For:** real drift; the PM/PO mislabel needed a hand sweep (CR0065).
**Against:** the rule set is fuzzy - "inconsistent" is hard to define without a curated term list, and
a premature gate becomes noise. `check_neutrality` already guards the highest-stakes vocab
(project-name leaks). **Shape if built:** advisory only, driven by a small project-declared
`vocabulary.yaml` of canonical terms + forbidden synonyms; never a blanket NLP check.

### C2 - Subcommand verb taxonomy

The script CLIs use inconsistent verbs (`check` x7, `show` x4, `record` x4, plus `detect` / `scan` /
`run` / `preflight`). A taxonomy (e.g. `show` = read state, `check` = validate, `record` = persist)
plus a lint that flags off-taxonomy verbs. **For:** predictable UX for the agents that invoke the
skill across ecosystems. **Against:** low signal; renaming established subcommands is a breaking
change to muscle memory and any external scripting, for a polish gain. **Shape if built:** define the
taxonomy as guidance first (best-practices/command.md); only lint new commands, never rename existing.

### C3 - Telemetry surfacing

`telemetry.py` records per-run outcomes locally (`.local/telemetry.jsonl`) but nothing surfaces or
trends them. A `telemetry` read command (summary / trends) would make the skill's own quality
observable. **For:** "deterministic, measurable" is a stated value; the data already exists. **Against:**
local-only by design (privacy); a dashboard is feature scope, and the autosprint loop-count
calibration (RFC0009 WS5) is already deferred. **Shape if built:** a read-only `telemetry show`
summarising the local log; no upload, no new storage.

## Recommendation

**Defer all three; decide in a dedicated session, not under build pressure.** None is blocking and
each carries a real false-positive / scope / breaking-change risk that the over-engineering caution
(RV0004) says to weigh deliberately. If forced to rank: C1 (vocabulary) has the highest value but
needs the curated-term-list design to be safe; C3 (telemetry show) is the smallest and safest if a
need surfaces; C2 (verb taxonomy) is the lowest priority (polish, breaking).

## Open Decisions

| # | Decision | Options | Status |
| --- | --- | --- | --- |
| D1 | Vocabulary-consistency check (C1) | build (advisory, term-list-driven) / decline / defer | Resolved: DECLINED |
| D2 | Verb taxonomy + lint (C2) | guidance-only / lint-new-only / decline | Resolved: guidance-only (built) |
| D3 | Telemetry surfacing (C3) | `telemetry show` (read-only) / decline / defer | Resolved: built (`telemetry show --summary`) |

## Decision

Accepted REDUCED (decisions.md D0004; operator, 2026-07-04) - the outcome differed from the
"defer all three" recommendation once each was pressure-tested against the current tree:

- **D1 (C1 vocabulary-consistency): DECLINED.** Zero repeat incidents in two releases, and
  `check_neutrality` + `lint-style` already gate the highest-stakes names; if the class recurs its
  home is a declared `constitution.md` rule, not a new engine.
- **D2 (C2 verb taxonomy): guidance-only, built.** A verb-taxonomy guidance table landed in
  `best-practices/script.md`; existing subcommands are not renamed and there is no lint gate.
- **D3 (C3 telemetry surfacing): built.** `telemetry show --summary` ships the read-only summary
  over the local log (the raw-dump `telemetry show` predated it; the summary was the gap).

The earlier per-row leanings (defer / guidance-only / defer) are superseded by these dispositions.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
| 2026-07-16 | sdlc-studio | Wrote the accepted-reduced outcome back (per decisions.md D0004): D1 DECLINED, D2 guidance-only, D3 built; removed the stale per-row leanings that contradicted the dispositions and added a Decision section |
