<!--
Template: Release Gate Checklist
Purpose: Pre-tag verification an operator walks through before cutting a version.
Load: Referenced from SKILL.md "See Also" and help/help.md "Release Cycle" subsection.
Related: reference-reconcile.md (drift check), reference-verify.md (AC verification), reference-operator-heuristics.md (memory-drift + CLI-localisation patterns)
-->

# Release Gate Checklist

> Walk through this list before you run `git tag v…` and push. Every item below is here because some project, somewhere, shipped without it and caused an incident. Skip an item only if you can articulate *why it does not apply to this release*.

**Release:** `v{{version}}`
**Base:** `{{previous_tag}}`
**Aggregated PR (if any):** `#{{pr_number}}`
**Operator:** `{{operator}}`
**Date:** `{{date}}`

---

## 1. Local build + test

- [ ] Typecheck (e.g. `npx tsc --noEmit`, `mypy`, `go vet`, etc.) – **zero** errors
- [ ] Full test suite – **all** pass; record the count: `_____ tests, _____ files`
- [ ] Skill checks (skill repo only): `validate_skill.py` (frontmatter spec),
      `check_versions.py --strict` (all version homes + CHANGELOG topmost
      release match), `check_budgets.py` (line budgets), `check_links.py`
      (anchors) – all green. `npm run lint` covers the first three without
      `--strict`; run the strict version check explicitly pre-tag.
- [ ] Eval scenarios (skill repo only): run the `evals/` scenarios per
      `evals/README.md`; record results in the release notes. Any failed
      expected behaviour blocks the tag.
- [ ] Integration / E2E suite green on at least one host – record which: `_____________`
- [ ] **E2E specs for this release's navigable surfaces are mutation-checked** – each new/changed critical-path spec was seen to **fail** when the feature is broken on purpose (unset the delivering field, stub the component, invert the guard), then restored. A green E2E that cannot fail is not a gate: an assertion derived from the same source it checks (e.g. `data-wired` vs `data-pending` from one boolean), or an `if/else` whose only reachable branch is a trivial `expect(0).toBe(0)`, passes over a dead feature. Any surface fed by a loader/enrichment/adapter needs at least one spec that drives the **real data path** to the render site, not hand-built props. See `reference-test-best-practices.md#assertion-integrity`.
- [ ] `/sdlc-studio reconcile --dry-run` – zero drift remaining
- [ ] **Archive terminal index rows for this release** – if reconcile printed an
  `index-bloat` advisory, run `scripts/archive.py archive --type <t> --release <tag>`
  for each named type. Live indexes stay bounded (progressive disclosure); rows move
  to `<type>/archive/`, files stay put, census unaffected. Re-run reconcile: zero drift.
- [ ] **Grep tests for pinned version literals** before tagging. A test that asserts `body.version === 'X.Y.Z'` (or equivalent hard-coded string) is a release-bump landmine: the test passes locally against the old version, CI breaks on the release-prep commit, and you spend a CI roundtrip chasing it. Fix: assert the *shape* (semver regex, or type-of-string) rather than the literal – or read the expected value from `package.json` / equivalent manifest. Grep pattern to run pre-tag: the current version string across the test tree. Any hit that isn't a deliberate historical fixture should be migrated to a shape assertion.

## 2. Adversarial review

- [ ] Adversarial / nit-level review pass (e.g. `/ultrareview`, or a dedicated code-review agent) run on the aggregated PR. If the release bundles multiple PRs, pick the one that touches the most surface area.
  - [ ] Each finding triaged: `fix-now` / `follow-up-artifact` / `wontfix-with-reason`
  - [ ] Every `follow-up-artifact` (CR, bug, story) actually filed, with a link back to the review session id
- [ ] `/sdlc-studio review --quick` passes (or findings triaged as above)
- [ ] `/sdlc-studio code review --story <every In-Review story>` – no Critical findings open

## 3. Spec-to-reality consistency

- [ ] PRD / TRD / TSD currency – Last Updated date within the current release window
- [ ] Project README / top-level docs: version string and any numeric claims (test counts, file counts, etc.) match reality – see `reference-reconcile.md#numeric-claim-drift`
- [ ] CHANGELOG (or release notes) lists every shipped **Epic + CR + Bug** by ID
- [ ] `/sdlc-studio status --brief` pillar percentages match what the PR actually landed

## 4. Deploy rehearsal

- [ ] Deploy / release script has a dry-run path and it's green (golden-fixture tests if the project has them)
- [ ] Rollback path tested at least once within the last 3 releases – note the date: `_____________`
- [ ] Release notes draft reviewed by one persona via `/sdlc-studio consult <persona>`
- [ ] **When the deploy tooling itself has changed since the last deploy** (new script, new healthcheck logic, new rollback path), **dry-run it against the CURRENT deployed version first** – not just the new one. Tooling bugs that depend on a code path introduced in the previous release are invisible until the tool is first *used* against that release. Catch them in a rehearsal where rolling back just means "continue running the version already in production," rather than in a deploy where rollback meets the same bug. If the tooling is new, also dry-run it once with `--skip-apply` or equivalent against the new release to exercise the pre-flight checks without mutating state.

## 5. Operator memory refresh

- [ ] Re-read any memory notes that reference config flags, topology, or version-gated behaviour. Before citing a memory note, inspect the current code – confirm the flag / path it names still exists and the regime described still holds. See `reference-operator-heuristics.md#memory-entry-drift` for the full pattern.
- [ ] If any memory note references a pre-release regime that the release changes, update the note *before* tagging. Don't ship a release whose first consequence is invalidating your own operator notes.

## 6. Post-tag (after `git push --tags`)

- [ ] CI artefact / container published and tag reachable
- [ ] Production deploy orchestrated via script (not hand-driven unless the script itself is what's being released)
- [ ] Post-deploy smoke: at least one functional call against the running service succeeded – **not** just a liveness endpoint. Health signals can stay green while every downstream call fails.
- [ ] Consumers of any programmatic interface that changed are briefed – see `reference-operator-heuristics.md#post-release-briefing`

## 7. If the deploy failed mid-flight

If the tag was cut and the artefact was published but the deploy never reached production (healthcheck timed out, rollback fired cleanly, smoke failed), hold here rather than force-retagging:

- [ ] **Do NOT force-delete + re-push the tag.** Even though nothing consumed the tagged artefact in production, the tag + published image / package is a historical record. Force-moving a tag on an immutable registry is error-prone, and some registries (e.g. container registries with tag-immutability policies) will refuse the overwrite entirely.
- [ ] **Diagnose + fix the blocker** – commit + push + verify CI green on a fresh commit. If the blocker is a pre-existing bug in the previously-deployed release, file it as its own bug artefact (don't fold silently).
- [ ] **Cut a hotfix version.** If the failed tag was `vX.Y.N`, tag the fix as `vX.Y.(N+1)`. The failed tag stays in place, annotated.
- [ ] **Annotate the lineage in PRD / TRD / TSD changelogs:** the `vX.Y.N` changelog row gets a "tagged but NEVER deployed – [root cause]; re-cut as vX.Y.(N+1)" note; the new `vX.Y.(N+1)` row lists the fixes and notes it includes the original `vX.Y.N` bundle.
- [ ] Deploy the hotfix via the same pipeline. Resume the checklist from section 1 for the new tag.

This preserves audit trail cleanly. Anyone looking at the git history later sees exactly what happened; anyone consulting the registry sees that `vX.Y.N` exists but was superseded with a reason.

## 8. Majors only (a breaking release: `vN.0.0`)

Run this section IN ADDITION to sections 1-7 when the leading version number changes. A major
carries breaking changes and a migration; a patch does not. Skipping these is how a breaking
release ships with no way for an existing project to move across it.

- [ ] **Breaking-change inventory named in the CHANGELOG.** Every breaking change is listed
  explicitly under the major's heading (not folded into "various improvements"), each with the
  before/after and the migration action a consumer must take.
- [ ] **Migration rehearsed on at least two real projects, evidence linked.** The upgrade path was
  run dry-run end to end against two real consuming projects (not just a fixture), findings filed
  as bugs/CRs, and the rehearsal record is linked from the release notes. A migration only a
  fixture has seen is untested. Any rc-blocking finding must be fixed and re-rehearsed first.
- [ ] **Eval scenarios re-run for the new major.** The `evals/` scenarios pass against the major's
  behaviour, not the prior major's; record the run in the release notes.
- [ ] **README / docs say the new major in the right places.** The version string, the "current
  major" statements, and any migration guide all name `vN`; no doc still describes the superseded
  regime as current.
- [ ] **rc first, from a green gate, with a soak.** Cut `vN.0.0-rc.1` from a fully green gate
  (sections 1-7 plus the above), soak it for the release's stated window, and only then cut the
  final `vN.0.0`. The rc-tag decision is a checklist read: green gate, migration rehearsed, backlog
  complete, open-bug count 0 - not a judgement call.

---

## Sign-off

```text
[ ] All items above checked OR explicitly waived with reason.
[ ] Waivers (if any):
    - Item X.Y: waived because ...
[ ] Tagged: {{version}} @ {{commit_sha}}
[ ] Deployed: {{deploy_targets}}
```

---

## Why this checklist exists

Each section above addresses a class of incident that has been observed in real projects. The supporting evidence – project names, bug IDs, dated post-mortems – lives in each project's own `sdlc-studio/.local/lessons.md`. This template stays generic so it transfers cleanly between projects.

| Section | Incident class it closes |
| --- | --- |
| 1. Build/test | CI failures discovered *after* tag, when the operator trusted their IDE / incremental runner |
| 1. Version-literal landmine | Tests with hardcoded `'X.Y.Z'` version assertions break CI on every release-prep commit; shape assertions are stable across bumps |
| 2. Adversarial review | Line-level nits (stale counts, hardcoded literals, regex gaps, flag-guard edge cases) that design-focused reviews routinely miss |
| 3. Spec-to-reality | Numeric claims in prose docs drifting silently across multiple releases |
| 4. Deploy rehearsal | Deploy-script bugs caught only when production rollback is the test |
| 4. Tooling-vs-previous-release | Pre-existing bugs in the deployed release only surface when new tooling is first exercised against them – caught safely in rehearsal, not live |
| 5. Memory refresh | Operator memory notes that were correct pre-change and misleading post-change |
| 6. Post-tag smoke | Health endpoints green while the real call path is broken – consumers are the first to notice, not the operator |
| 7. Hotfix-over-retag | Force-retagging is destructive on immutable registries AND loses audit trail; hotfix-version + annotated changelog is safer and cleaner |
| 8. Majors only | A breaking release shipping with no rehearsed migration, an unlisted breaking change, or docs still describing the old major - leaving consumers unable to move across the version |
