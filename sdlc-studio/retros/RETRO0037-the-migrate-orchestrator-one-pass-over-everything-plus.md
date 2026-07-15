# RETRO-0037: The migrate orchestrator: one pass over everything, plus the version-stamp fix (RFC0041)

> **Date:** 2026-07-15
> **Batch:** BG0150, US0154-US0157 (EP0042, RFC0041)
> **Goal:** done
> **Delivered:** 5 / 5   **Blocked:** 0

## Delivered

- **BG0150 (3pt) - the version-stamp fix.** `project_upgrade.apply()` stamped a bogus
  `skill_version: "unknown"` when the installed SKILL.md carried no parseable version; it now warns
  and SKIPS the stamp rather than fabricating a value. Root-caused to `installed_version() or
  "unknown"`; the dry-run detection was already guarded, only the write path was not.
- **US0154 (5pt) - migrate orchestrates.** New `migrate.py` runs `project_upgrade` +
  `migrate_v3 sizing`, dry-run by default, aggregating their reports into one.
- **US0155 (5pt) - the artefact-review sweep.** Every open artefact is reviewed: an accepted
  childless request -> `refine`, a childless Issue -> `triage`, a legacy-Effort delivery unit -> a
  re-size, each named with the exact command (reusing migrate_v3's needs_* buckets).
- **US0156 (5pt) - the honest report + `--apply`.** One report split deterministic vs needs-human;
  `--apply` writes only the deterministic, reversible set and never guesses a judgement.
- **US0157 (3pt) - docs.** `reference-upgrade.md` (the migrate section + the upgrade table),
  `migrate.py` catalogue entry, SKILL/help, CHANGELOG; `migrate` placed on the audit spine map.

## Blocked / deferred

- Nothing blocked. RFC0041 reaches terminal when EP0042 + BG0150 are done. Two friction points were
  filed mid-sprint from operator reports and NOT built: CR0276 (audit must warn before a large
  fan-out) and the homelab audit's own findings (that project's, not this one's).

## What went well

- **Orchestration, not reimplementation.** `migrate` reuses `project_upgrade`, `migrate_v3` and
  reconcile wholesale - it adds the aggregation and the artefact sweep, nothing parallel. The sweep
  IS migrate_v3's needs_* buckets surfaced per-ceremony; the build was small because the pieces were
  already sound (the same pattern as the amigo-consult sprint: wire, don't rebuild).
- **Dogfooded on a real project mid-sprint.** Run against `../homelab`, `migrate` found 4 legacy-
  Effort CRs to convert and 13 needs-human items, correctly touching nothing in dry-run - a live
  proof the orchestration and the honest split work outside the fixtures.
- **BG0150 was a real, subtle bug.** The version logic EXISTED and looked complete; the gap was one
  `or "unknown"` fallback that silently fabricated a value. The fix names the honest failure instead.

## What was hard / what stalled

- **A test passed alone and failed in the full suite.** The BG0150 test monkeypatched a separately-
  imported `version_check`, but under the full suite another test's importlib load made it a
  different module instance from the one `project_upgrade` referenced - so the patch missed. Fixed by
  patching `pu.version_check` (the object the code under test actually holds). Classic importlib
  test-pollution; the lesson is to patch through the module-under-test, not a re-import.
- **Provenance tags leaked into consuming-facing files.** `(RFC…)` / `(BG…)` provenance in
  migrate.py and the reference pages tripped the style gate - traceability belongs in
  change-requests/CHANGELOG/git, not docs a consuming project reads. Caught by lint-style.
- **The honest report was dishonest on the apply path (caught in review).** `migrate` classified
  conventions from `audit()` in dry-run but from `apply()`'s free-text action strings on `--apply`,
  so an advisory (the team-offer nudge) and even the BG0150 "version NOT stamped" WARNING were
  reported as applied deterministic upgrades, and the two modes gave contradictory counts. The whole
  point of the feature is the honest split; the review caught that the split leaked. Fixed by
  classifying from `audit()` in both modes and making `audit()` honest about the BG0150 case.

## Lessons

- Monkeypatch through the module under test, not a re-import. A test that patches `import
  version_check` can miss when the code under test holds a different instance of that module (the
  full suite's importlib loads create distinct instances). Patch `<module_under_test>.dependency`,
  which is the exact object the code will look up. A green run in isolation is not proof under the
  suite.
- Orchestrate existing, tested primitives before building new ones. `migrate` is almost entirely
  glue over `project_upgrade` + `migrate_v3` + reconcile; the value was the aggregation and the
  honest deterministic-vs-needs-human split, not new migration logic. The reused pieces carried
  their own tests, so the new surface to test was thin.

## Estimate vs actual

**Not captured by the skill telemetry - but NOT unmeasurable.** The plan forecast ~525,000 tokens
(21 points x the ~25,000 seed). The actual token spend IS deterministic: the harness tracks it (a
Workflow run reports it directly - the homelab audit this session reported ~6.9M tokens; an
interactive run's total sits on the session counter). What is missing is that the skill's telemetry
only records a RUNNER-driven sprint's actual, so an interactive sprint's actual is not stamped and
no tokens-per-point is computed here. That is a capture gap, not a measurement impossibility -
tracked as CR0278. This corrects the earlier "UNMEASURED (interactive)" framing across
RETRO0029-0037, which wrongly implied the count was unknowable rather than merely un-captured.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- The token actual is knowable (harness-tracked); it is simply not yet captured into the skill's
  telemetry for an interactive sprint - CR0278 closes that so the tokens-per-point rate can be read
  for every sprint, not only runner-driven ones.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues found?**

| Finding | Disposition |
| --- | --- |
| project_upgrade stamped a bogus "unknown" version (operator report from another project) | closed: BG0150 fixed this sprint (warn + skip; regression tests), verified by re-review. |
| migrate reported advisories/warnings as applied deterministic upgrades, and dry-run/apply disagreed (found in review) | declined: no ticket - fixed this sprint (classify from audit() in both modes; audit honest about BG0150) + 4 tests, confirmed by re-review. |
| A test passed alone but failed in the full suite (importlib pollution) | declined: no ticket - fixed this sprint (patch through pu.version_check); captured as a lesson. |
| audit fans out a large multi-agent workflow with no cost warning (operator report, live) | filed: CR0276 (warn + confirm before a large adversarial fan-out) - a future sprint. |
| reconcile detects missing-index but cannot create it - the agent hand-authored one during the homelab audit | filed: CR0277 (reconcile apply creates a missing index from the template) - a future sprint. |
| migrate_v3 leaves legacy Effort beside the new Size (found in review) | declined: no ticket here - inherited migrate_v3 behaviour, out of this sprint's scope; note for the sizing workstream. |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETRO0037 -->

## Close loop (gated)

- [x] this retro exists AND passes its content check
- [x] its lessons are in the project store
- [x] open lessons re-validated
- [x] `retros/LESSONS-SUMMARY.md` regenerated

## Metrics

- Tokens: deterministic but not yet captured by the skill telemetry (harness-tracked; see CR0278) · Duration: one session · Critic rejects: 0 (APPROVE-WITH-NITS on first pass; 2 MAJOR reporting-honesty defects + 3 minor fixed same sprint; re-review APPROVE)
