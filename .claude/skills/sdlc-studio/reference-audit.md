# SDLC Studio Reference - Adversarial Audit

The portable methodology for `audit`: a multi-agent adversarial pressure-test over a
project's whole artifact graph that hunts for **weakness and incoherence** (not just
consistency), verifies every candidate with an independent refute panel, and files the
survivors as Bugs / CRs / RFCs. Tool-neutral - any AGENTS.md-capable harness can drive
it (Option A).

<!-- Load when: running an adversarial audit, or building/extending a lens profile -->

## Reading Guide

| Section | When to read |
| --- | --- |
| Pipeline | Running an audit end to end |
| Lens profiles | Choosing or extending what gets pressure-tested |
| Refute panel | Tuning the false-positive guard |
| Taxonomy & filing | Turning survivors into Bug/CR/RFC artifacts |
| Budget | Capping cost on a large project |

## Why It Exists {#audit-why}

The cheap quality passes check **consistency**: `review` consolidates PRD/TRD/TSD/
persona, `reconcile` fixes status/index drift, `verify_ac` checks AC against code. None
hunt adversarially for weakness - vague or untestable AC, requirements with no
acceptance signal, architecture drifted from code, rotted ADRs, personas never
consulted, spec-vs-code gaps, broken traceability. `audit` is the adversarial superset;
it composes with the others, it does not replace them.

## Pipeline {#audit-pipeline}

```text
find  ──►  verify  ──►  merge  ──►  file
(lenses,   (refute     (dedup +    (Bug/CR/RFC via
 loop-     panel,      classify)    file_finding.py,
 until-dry) N-of-M)                 triage or auto)
```

0. **Recall (seed the lenses).** `scripts/lessons.py rank` first. The ranked lessons ARE
   lenses - the classes this codebase has already paid for, hardest-biting first - and an
   audit that does not know what has bitten before re-derives it or misses it. Add the top
   bug-class lessons to the profile's lens set before finding anything. An audit is a search
   for what you have not thought of; the registry is a list of what you *have*, and forgot.
1. **Find.** For each lens in the profile, run a finder agent that returns candidate
   findings. Re-run each lens **until-dry** (K consecutive rounds with nothing new,
   K=2 default) so the tail is not missed.
2. **Verify (refute panel).** For each candidate, spawn N independent skeptics, each
   prompted to **refute** it. A candidate survives only on **>=M of N** (default
   3-vote, survive on >=2/3). The refute rate is the feature: the two proving runs
   refuted ~59% and ~47% - plausible-but-wrong items correctly killed.
3. **Merge.** Dedup survivors across lenses by file+claim; collapse near-duplicates.
4. **File.** Classify each by the standard rule (below) and write it with
   `scripts/file_finding.py` (deterministic ID + structured artifact + index sync).
   Default to **triage-then-approve** for the project profile (the 2nd run showed
   auto-filing produced shallow artifacts); auto-file is opt-in.

## Lens Profiles {#audit-profiles}

A profile is a set of lenses. Two ship; projects can extend.

### Project profile (default) {#audit-project-profile}

Per-artifact-type lenses + cross-artifact coherence:

| Artifact | Adversarial lens |
| --- | --- |
| PRD | untestable/vague requirements; features with no acceptance signal; scope contradictions |
| TRD | architecture-vs-code drift; unjustified choices; rotted ADRs; missing failure/scaling story |
| TSD | coverage gaps; NFRs with no gate; gates that do not run |
| Personas | not load-bearing; contradictory needs; stale; duplicate |
| Epics/Stories | ambiguous AC; no edge cases; AC not machine-checkable; Ready criteria unmet |
| Code | does not satisfy claimed AC; correctness/security smells; pattern violations |
| Design/RFC | open decisions rotting; accepted-without-spawned-CRs; options never weighed |
| Cross-artifact | broken PRD->epic->story->code->test traceability; epic Done with non-Done stories |

### Skill profile {#audit-skill-profile}

For auditing an agent skill itself - the four lenses proven on 2026-06-20:
over-engineering, token-economy, determinism, external-benchmark. Packaged as a
loadable pack at `templates/audit-profiles/skill.md` (each row is a finder lens).

### Extending {#audit-extend}

A profile is just a lens list (artifact/area + the adversarial question). Add a lens by
appending a row; a project declares extra lenses in its own audit harness prompt.

## Refute Panel {#audit-refute}

The guard against false positives. Per candidate, N skeptics each try to **refute**;
keep only those that survive >=M votes (D3: 3-vote >=2/3 proven; N-of-M configurable;
per-severity thresholds optional). Skeptics default to "refuted=true if uncertain" so
the burden is on the finding to survive. Give skeptics distinct lenses (correctness,
does-it-reproduce, is-it-already-handled) rather than N identical prompts.

## Taxonomy & Filing {#audit-taxonomy}

Classify each survivor by the standard rule:

- **Bug** - something is broken or wrong now (a false claim, a dangling ref, a test
  that does not test). Has Steps to Reproduce + Proposed Fix.
- **CR** - a concrete, agreed improvement to a settled area. Has acceptance criteria.
- **RFC** - an unsettled design question with real options to weigh. Has options +
  open decision.

File with the deterministic filer, which refuses a hollow artifact:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/file_finding.py" file --type cr \
  --title "..." --priority High --ctype Improvement --summary "..." \
  --impact "who this affects and what breaks" --points 5 \
  --affects "src/one.py, src/two.py" \
  --ac "concrete, checkable criterion" --ac "..."
```

It allocates the ID, renders the structured artifact, stamps the authorship of record
(`--author "Name; type; version"`, defaulting to the invoking agent), appends the index
row, and recomputes the index counts. A CR without an impact statement and a `--points`
size is refused, because the validator refuses it too. Triage first (review the
survivors), then file the approved set.

## Budget {#audit-budget}

The skill-profile run cost ~6M tokens / 221 agents; the project run ~245 agents. Cap it:
`--budget` (token ceiling), a loop-until-dry round limit, and `--scope prd,trd,...` to
narrow. Run on demand, not in CI. Always `log()` what a cap dropped so partial coverage
is not read as complete.

## Proven Runs {#audit-proven}

- **Skill profile (2026-06-20):** 4 lenses, loop-until-dry -> 69 candidates in 3
  rounds -> 3-vote refute -> 28 survivors (41 refuted, ~59%) -> 18 filed (4 Bug, 8 CR,
  6 RFC). 221 agents, ~6M tokens, ~27 min.
- **Project profile (2026-06-20):** 76 -> 40 -> 23 (36 refuted). 245 agents. Surfaced
  two improvements now baked in: triage-default for the project profile, and the filer
  producing rich (not shallow) artifacts.

## See Also {#audit-see-also}

| Document | Relationship |
| --- | --- |
| `reference-review.md` | the cheap consistency pass audit composes with |
| `reference-reconcile.md` | drift detection / index sync (filer reuses its count pass) |
| `reference-verify.md` | executable AC verification |
| `reference-rfc.md` | the RFC lifecycle survivors enter |
| `scripts/file_finding.py` | the deterministic Bug/CR/RFC filer |
| `templates/automation/audit-*.md` | the portable finder / refute / classify prompt harness |
