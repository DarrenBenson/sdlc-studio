<!--
Load when: /sdlc-studio audit, "pressure-test the project", "hunt for weaknesses"
Dependencies: SKILL.md (always loaded first)
Related: reference-audit.md, templates/automation/audit-finder.md, templates/automation/audit-refute.md
-->

# /sdlc-studio audit - the adversarial pressure-test

## You can just ask

| Just say... | Runs |
| --- | --- |
| "Adversarially audit the whole project" | the project-profile fan-out (`reference-audit.md`) |
| "Pressure-test just the PRD and TRD" | a scoped audit (`--scope prd,trd`) |
| "Audit this skill itself" | the skill profile (`templates/audit-profiles/skill.md`) |
| "What would this audit cost before I launch it?" | `audit_cost.py --lenses <n>` |

A multi-agent adversarial pressure-test over the whole artifact graph. It hunts for
**weakness and incoherence** - not just consistency - verifies every candidate with an
independent refute panel, and files the survivors as Bugs / CRs / RFCs. It composes with
the cheap passes (`review`, `reconcile`, `verify`); it does not replace them.

`audit` is driven by agents from the portable methodology in `reference-audit.md` (Option
A - any AGENTS.md-capable harness runs it). Read that reference before launching; this
page is the entry point and the pre-flight gate.

## The pre-flight cost gate (do this first)

An audit can spend millions of tokens across hundreds of agents, and the harness only
flags a "Large workflow" **after** it has launched. So estimate and confirm **before** the
fan-out:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/audit_cost.py" --lenses 8 --rounds 2 --votes 3
```

It reports `~agents · ~tokens · ~minutes` and a **large / small** verdict:

- **large** (>= ~50 agents or >= ~1M tokens): show the operator the estimate and the
  scope, and wait for an explicit go-ahead before launching.
- **small** (a couple of lenses, one round): run without ceremony - the gate is for the
  expensive runs, not every audit.

It is a confirmation gate, not a cap; `--budget` and the round limit bound the run itself.

## The pipeline

```text
find  ──►  verify  ──►  merge  ──►  file
(lenses,   (refute     (dedup +    (Bug/CR/RFC via
 until-dry) panel,      classify)   file_finding.py)
            N-of-M)
```

1. **Recall first** - `scripts/lessons.py rank`; the ranked lessons ARE lenses.
2. **Find** - one finder agent per lens (`templates/automation/audit-finder.md`), each
   re-run until-dry (K=2 rounds with nothing new).
3. **Verify** - N skeptics per candidate refute it; survive on >= M of N (default 3-vote,
   >= 2/3). A vote that never arrives is not a refutation - an incomplete panel marks the
   candidate `UNJUDGED`, never refuted (`reference-audit.md#audit-refute-quorum`).
4. **Merge** - dedup survivors by file + claim.
5. **File** - **triage-then-approve is the default** for the project profile (auto-file
   produced shallow artifacts); auto-file is opt-in. File with `file_finding.py`, which
   refuses a hollow artifact.

## Profiles

Six ship. The profile chooses the lenses; every one of them runs through the same refute
panel, so the choice never changes whether a plausible-but-wrong finding gets filed.

| Profile | Invocation | Lenses | Pack |
| --- | --- | --- | --- |
| `project` | `audit` (default) | per-artifact-type (PRD, TRD, TSD, personas, epics/stories, code, design/RFC) plus cross-artifact traceability | `reference-audit.md#audit-project-profile` |
| `skill` | `audit --profile skill` | over-engineering, token-economy, determinism, external-benchmark | `templates/audit-profiles/skill.md` |
| `repo` | `audit --profile repo` | architecture, code-quality, defensive-security | `templates/audit-profiles/repo.md` |
| `code` | `audit --profile code` | correctness, security-smells, pattern-violations, ac-drift | `templates/audit-profiles/code.md` |
| `test` | `audit --profile test` | can-it-fail, reaches-the-code, docstring-vs-assertion, incidentally-green (source and tests together) | `templates/audit-profiles/test.md` |
| `process` | `audit --profile process` | path-from-memory, count-by-hand, accepted-without-running, repair-without-plan, skipped-preflight (each names its detector or declares none) | `templates/audit-profiles/process.md` |

Resolve a pack before launching, and see its lenses and refute threshold:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/audit.py" profile --name repo
```

A name no profile declares is refused, naming the ones that exist - an audit never runs an
empty lens set.

### The zero-setup path on an existing repo

`audit --profile repo` is the try-before-you-adopt entry point: point it at a repository
that has never run sdlc-studio, and it hunts the three legs, verifies each candidate
through the refute panel, and files the survivors as Bugs or CRs with tool-allocated ids.
Security findings are remediation-only - location, weakness class, realistic impact and a
concrete fix, no proof-of-concept payload, and a committed secret reported by location
plus rotation with the value left where it is. The wording is binding and lives in the
pack (`templates/audit-profiles/repo.md`).

Narrow a run with `--scope prd,trd,...`. Run on demand, never in CI, and always log what a
cap dropped so partial coverage is not read as complete.

## See Also

- `reference-audit.md` - the full methodology (pipeline, lens profiles, refute panel, filing)
- `templates/automation/audit-finder.md` - the finder-agent prompt
- `templates/automation/audit-refute.md` - the refute-panel skeptic prompt
- `scripts/file_finding.py` - the deterministic filer for survivors
