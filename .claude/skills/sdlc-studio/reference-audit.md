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

A profile is a set of lenses. Six ship; projects can extend. Every one of them is
wired to the same refute panel - the profile chooses the lenses, never whether a
plausible-but-wrong finding gets filed.

| Profile | Lens pack | Hunts | Refute panel |
| --- | --- | --- | --- |
| `project` | this file, `#audit-project-profile` | the artefact graph: per-type lenses plus cross-artefact coherence (default) | shared |
| `skill` | `templates/audit-profiles/skill.md` | an agent skill itself: over-engineering, token-economy, determinism, external-benchmark | shared |
| `repo` | `templates/audit-profiles/repo.md` | an existing repository, zero setup: architecture, code-quality, defensive-security | shared |
| `code` | `templates/audit-profiles/code.md` | an implementation: correctness, security-smells, pattern-violations, ac-drift | shared |
| `test` | `templates/audit-profiles/test.md` | the claims code makes about itself: can-it-fail, reaches-the-code, docstring-vs-assertion, incidentally-green | shared |
| `process` | `templates/audit-profiles/process.md` | the way a delivery was produced: path-from-memory, count-by-hand, accepted-without-running, repair-without-plan, skipped-preflight | shared |

Resolve one with `scripts/audit.py profile --name repo`, which reports the pack's lenses
and its refute threshold; a name no profile declares is refused, naming the ones that
exist, rather than running an empty lens set.

### Project profile (default) {#audit-project-profile}

> **Refute panel:** shared - 3 skeptics per candidate, survive on >= 2 of 3
> (`#audit-refute`). This profile does not opt out.

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

### Repo profile {#audit-repo-profile}

The zero-setup pass over an existing repository - the try-before-you-adopt path on code
with no artefact graph yet. Three legs: architecture, code-quality, defensive-security.
Packaged at `templates/audit-profiles/repo.md`, which also carries the binding
remediation-only security posture (location, weakness class, impact and fix; no
proof-of-concept payload; a committed secret reported by location plus rotation, with the
value left where it is). Findings file as Bugs or CRs through `file_finding.py`.

### Code profile {#audit-code-profile}

For auditing an implementation rather than the specs around it: correctness,
security-smells, pattern-violations, ac-drift. Packaged at
`templates/audit-profiles/code.md`. The `ac-drift` lens needs the unit's acceptance
criteria in the finder's context, not the diff alone.

### Test profile {#audit-test-profile}

The qualitative backstop to a mutation run, hunting the claims code and tests make about
themselves: can-it-fail, reaches-the-code, docstring-vs-assertion, incidentally-green.
Packaged at `templates/audit-profiles/test.md`. A mutant proves a test can fail; nothing
mechanical detects a docstring that lies, which is what this pack is for. Its default
scope is **source and tests together**, because prose asserting a property the code lacks
sits in source at least as often as in a test file. Each lens cites the recorded failure
modes it was drawn from (`lessons/_index.md`); read those entries into the finder's
context, and give any lens appended later the same evidence.

### Process profile {#audit-process-profile}

The sibling to `test`: where `test` attacks the claims code makes about itself, `process`
attacks the way the delivery was produced. The class is uniform - **work done before the
contract it depends on was established** - and it is the failure this skill exists to
prevent, so a delivery unaudited for it rests on the author's discipline alone. Packaged at
`templates/audit-profiles/process.md`. Five lenses, each drawn from a recorded failure this
project produced: path-from-memory, count-by-hand, accepted-without-running,
repair-without-plan, skipped-preflight.

Each lens names its **signature** - the mechanical detector a finder runs before reasoning,
or a plain statement that none exists. A mechanical signature opens with a documented
detector token (`python3`, a skill script run over the workspace) and names only paths on
disk, so a cell cannot claim a command or a file that is not there; where no search singles
the class out, the signature opens with `manual` - and states why, which puts the absence
where a reader can weigh it rather than where it reads like a check and is not one. Three of
the five are mechanical (a path resolved against the tree, a count against the census, a
verifier that selected nothing); two are honestly manual (whether a repair was attacked
before it was written, and whether a cheaper form was looked for first, are readings of
process, not states on disk). A declared detector cannot be shown to fire on its own incident
by any test the pack ships - that is a manual run over a commit range, recorded in the run
report.

Each lens cites the recorded failure it was drawn from (`lessons/_index.md`); read those
entries into the finder's context, and give any lens appended later the same evidence and its
own signature. A lens the shipped registry cannot resolve is a dangling reference in every
consuming project, so the pack cites only ids that ship.

### Extending {#audit-extend}

A profile is just a lens list (artifact/area + the adversarial question). Add a lens by
appending a row; a project declares extra lenses in its own audit harness prompt.

## Refute Panel {#audit-refute}

The guard against false positives. Per candidate, N skeptics each try to **refute**;
keep only those that survive >=M votes (D3: 3-vote >=2/3 proven; N-of-M configurable;
per-severity thresholds optional). Skeptics default to "refuted=true if uncertain" so
the burden is on the finding to survive. Give skeptics distinct lenses (correctness,
does-it-reproduce, is-it-already-handled) rather than N identical prompts.

### A dead vote is not a refutation {#audit-refute-quorum}

A skeptic agent can **fail to return a verdict** - a session-limit outage, a network drop,
any terminal agent error. That absence is not evidence against the finding, and must never
be counted as a refutation. The failure mode is silent and severe: count only the votes that
arrived against the fixed threshold and an outage that kills all N skeptics scores every
candidate 0-non-refutations = mass-**refuted**, so the run reports the wrong survivor set as a
finished verdict (observed live: 95 skeptics died mid-run, 34/46 reported; a re-run of the
dead votes gave 61/19 - 27 verified findings had been silently mislabelled refuted).

The rule:

- A candidate's verdict is **valid only when all N votes arrived** (or the threshold is scaled
  to the arrived votes with a minimum quorum - e.g. survive on >=2/3 of *arrived*, refuse a
  verdict on fewer than 2 arrived).
- An **incomplete panel marks the candidate `UNJUDGED`**, never refuted and never survived.
- The run report **must carry an `unjudged` count** alongside survived/refuted, and **fail
  loud** (or auto-resume the dead votes) when it is non-zero. A survivors/refuted split with a
  hidden unjudged tail is not a finished audit - it is a truncated one wearing a complete face.

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

**File or decline, never neither.** Every candidate that survives the panel is either
filed through `file_finding.py` or declined with a stated reason in the run report.
Silence on a survivor is not an answer: an unmentioned candidate is indistinguishable
from one nobody looked at, and the reason is what a later reader needs when the same
candidate resurfaces.

## Budget {#audit-budget}

The skill-profile run cost ~6M tokens / 221 agents; the project run ~245 agents. Cap it:
`--budget` (token ceiling), a loop-until-dry round limit, and `--scope prd,trd,...` to
narrow. Run on demand, not in CI. Always `log()` what a cap dropped so partial coverage
is not read as complete.

### Capped-out candidates are carried, not counted {#audit-carryover}

A count is not a work item. When the verification cap drops candidates the finders already
grounded, **write each dropped candidate out in full** - `title`, `file`, `claim`, `evidence`,
`lens`, `severity`, the same record shape the finder returned - as a JSON array to a durable
carry-over file, `.local/audit-carryover-<date>.json`. Logging only how many were dropped is not
enough: the records themselves live in the harness's session-local journal and die with the
session, and a grounded candidate is cheap to re-derive badly and expensive to re-derive well.

The drop order is itself unvalidated - the cap keeps the highest finder-assigned severities, and
that severity has not been through a refute panel at the moment it decides what survives. So the
tail is unverified work, not rejected work.

The close-out report must then name the carry-over file's path and give the one scoped command
that verifies just those candidates, skipping the find phase entirely:

```bash
/sdlc-studio audit --carryover .local/audit-carryover-<date>.json
```

A follow-up run pointed at the file takes its records as the candidate pool and goes straight to
the refute panels - no finder lenses run, so the carried tail costs refute agents only.

### Pre-flight cost gate (confirm before a large fan-out) {#audit-preflight}

An audit can spend millions of tokens across hundreds of agents, and the harness only flags a
"Large workflow" AFTER it has launched. So **before invoking the fan-out, present the estimate and,
above a threshold, get the operator's go-ahead** - never surprise them mid-run. The steps:

1. Scope the run (lenses, rounds, refute votes) - narrower with `--scope`.
2. Estimate the cost: `scripts/audit_cost.py run --lenses <n> [--rounds N --votes N]`. It reports
   `~agents · ~tokens · ~minutes`, a **large / small** verdict, and the **basis** it used - the
   median of the runs recorded in the evidence ledger, or the shipped constants when the ledger
   holds none yet. Order of magnitude, not a promise: the finder and candidate counts are known
   only once it runs.
3. **If the estimate is `large`** (>= ~50 agents or >= ~1M tokens): show the operator the estimate
   and the scope, and wait for an explicit go-ahead before launching the Workflow. A **small**
   scoped audit (a couple of lenses, one round) runs **without ceremony** - the gate is for the
   expensive runs, not every audit.
4. When the run finishes, **record** the actuals against the estimate with `audit_cost.py record`
   - do not only report them in chat, where the measurement dies with the session:

   ```bash
   python3 "$CLAUDE_SKILL_DIR/scripts/audit_cost.py" record \
     --lenses 7 --rounds 3 --votes 3 \
     --est-agents 217 --est-tokens 7800000 \
     --actual-agents 265 --actual-tokens 12400000 --actual-minutes 95 \
     --notes "an outage forced a partial rerun"
   ```

   The row lands in the committed evidence ledger under `sdlc-studio/retros/evidence/`, sharded
   by day, and the next estimate is calibrated from the medians of what is recorded there. Note
   what made the run unusual: an estimate cannot carry a contingency for a cause nobody wrote
   down. Also record a run that came in UNDER its estimate - a ledger holding only the expensive
   surprises calibrates upwards for ever.

This is a confirmation gate, not a cap - `--budget` and the round limit above still bound the run
itself.

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
