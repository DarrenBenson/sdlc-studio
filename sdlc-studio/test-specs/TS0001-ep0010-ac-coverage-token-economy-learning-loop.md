# TS0001: EP0010 AC coverage - token economy + learning loop

> **Status:** Ready
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new

## Overview

The epic-scope test specification for EP0010. It shifts the AC-to-test bridge left: every story AC
is mapped here to a planned test case (the `pytest -k` title each story's `Verify:` line points at),
so implementation binds tests to this matrix by construction rather than reverse-engineering it at
delivery. Documentation-only ACs are verified manually plus the link/style guards.

## Scope

### Stories Covered

| Story                                                                                        | Title                                                                | Priority |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------- |
| [US0040](../../stories/US0040-index-archive-writer-terminal-status-vocab-flag-dry.md)        | index-archive writer + terminal-status vocab flag + dry-run (CR0125) | Medium   |
| [US0041](../../stories/US0041-next-id-archive-union-guard-so-archived-ids.md)                | next_id archive-union guard (CR0125)                                 | Medium   |
| [US0042](../../stories/US0042-retro-hard-close-gate-sprint-close-fails-loud.md)              | retro hard close-gate (CR0129)                                       | Medium   |
| [US0043](../../stories/US0043-lessons-re-validation-verb-close-obsolete-lessons-by.md)       | lessons re-validation verb (CR0129)                                  | Medium   |
| [US0044](../../stories/US0044-rolling-lessons-summary-generator-sprint-start-read-cr0129.md) | rolling LESSONS-SUMMARY generator + sprint-start read (CR0129)       | Medium   |
| [US0045](../../stories/US0045-agentic-wave-worktree-doctrine-doc-enrichment-cr0126.md)       | agentic-wave worktree doctrine doc (CR0126)                          | Medium   |
| [US0046](../../stories/US0046-pre-deploy-readiness-checklist-doc-cr0127.md)                  | pre-deploy readiness checklist doc (CR0127)                          | Medium   |
| [US0047](../../stories/US0047-restore-the-runtime-scripts-coverage-gate-to-green.md)         | restore the runtime-scripts coverage gate to green on CI             | Medium   |
| [US0048](../../stories/US0048-adopt-dependabot-ci-action-bumps-actions-checkout-v7.md)       | adopt Dependabot CI action bumps (checkout v7, setup-python v6)      | Medium   |
| [US0049](../../stories/US0049-blocker-sweep-detection-now-unblocked-units-in-repo.md)        | blocker-sweep detection (in-repo + cross-repo via PVD) (CR0130)      | Medium   |
| [US0050](../../stories/US0050-wire-the-blocker-sweep-before-sprint-planning-advisory.md)     | wire the blocker sweep pre-plan + reconcile lane (CR0130)            | Medium   |

### AC Coverage Matrix

| Story  | AC  | Description                                                    | Test Cases    | Status  |
| ------ | --- | -------------------------------------------------------------- | ------------- | ------- |
| US0040 | AC1 | writer relocates terminal rows; idempotent                     | TC01          | Planned |
| US0040 | AC2 | terminal set from status_vocab flag; Built active              | TC02          | Planned |
| US0040 | AC3 | dry-run writes nothing; fail-loud on unclassifiable row        | TC03          | Planned |
| US0040 | AC4 | reconcile drift 0; summary equals census after archive         | TC04          | Planned |
| US0041 | AC1 | next_id unions archive sub-indexes                             | TC05          | Planned |
| US0041 | AC2 | archived id never reused even if file removed                  | TC06          | Planned |
| US0042 | AC1 | close fails loud without a batch retro                         | TC07          | Planned |
| US0042 | AC2 | close passes with the retro present                            | TC08          | Planned |
| US0043 | AC1 | re-validation verb lists/closes open lessons                   | TC09          | Planned |
| US0043 | AC2 | re-validation idempotent                                       | TC10          | Planned |
| US0044 | AC1 | LESSONS-SUMMARY generator refreshes the committed digest       | TC11          | Planned |
| US0044 | AC2 | summary regenerates deterministically                          | TC12          | Planned |
| US0044 | AC3 | sprint start reads the summary; reference-sprint.md updated    | TC13 (manual) | Planned |
| US0045 | AC1 | agentic-wave doctrine documented                               | TC14 (manual) | Planned |
| US0045 | AC2 | link + style guards pass                                       | TC15          | Planned |
| US0046 | AC1 | pre-deploy checklist documented                                | TC16 (manual) | Planned |
| US0046 | AC2 | link + style guards pass                                       | TC17          | Planned |
| US0047 | AC1 | coverage gate passes (>= 80%) in the CI environment            | TC18          | Planned |
| US0047 | AC2 | local-vs-CI discrepancy identified and removed                 | TC19 (manual) | Planned |
| US0048 | AC1 | lint.yml references checkout v7 and setup-python v6            | TC20          | Planned |
| US0048 | AC2 | CI green; Dependabot PRs #25/#26 merged or closed              | TC21 (manual) | Planned |
| US0049 | AC1 | sweep collects every blocker signal + reports referents        | TC22          | Planned |
| US0049 | AC2 | in-repo referents resolve by census; now-unblocked reported    | TC23          | Planned |
| US0049 | AC3 | cross-repo referents resolve via PVD manifest repos[].path     | TC24          | Planned |
| US0049 | AC4 | fail loud; never false-clear an unresolved/unreadable referent | TC25          | Planned |
| US0050 | AC1 | sweep runs before sprint planning (pre-plan step)              | TC26          | Planned |
| US0050 | AC2 | advisory reconcile lane reports stale-blocked units            | TC27          | Planned |
| US0050 | AC3 | proposes Blocked -> Ready; never auto-transitions              | TC28          | Planned |

**Coverage:** 28/28 ACs covered

### Test Types Required

| Type        | Required | Rationale                                                                                                                                   |
| ----------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit        | Yes      | The archive writer, next_id union, close-gate, re-validation and summary verbs are pure-stdlib script logic, best covered by unittest cases |
| Integration | Yes      | TC04 exercises writer then reconcile end-to-end; TC07/TC08 exercise the close path                                                          |
| E2E         | No       | No runtime/service surface; the skill is CLI + markdown                                                                                     |

---

## Environment

| Requirement       | Details                                                                |
| ----------------- | ---------------------------------------------------------------------- |
| Prerequisites     | Python 3.10+, the repo's existing unittest suite under `scripts/tests` |
| External Services | None                                                                   |
| Test Data         | Fixture index/lessons trees built in tmpdir per test (no shared state) |

---

## Test Cases

### TC01: archive writer relocates terminal rows, idempotent

**Type:** Unit | **Priority:** High | **Story:** US0040

| Step  | Action                                                    | Expected Result                                    |
| ----- | --------------------------------------------------------- | -------------------------------------------------- |
| Given | a fixture type dir with active and terminal rows          | live `_index.md` present                           |
| When  | the archive writer runs, then runs again                  | terminal rows move to `archive/_index-{period}.md` |
| Then  | live index holds active rows + summary; re-run is a no-op | idempotent                                         |

**Assertions:**

- [ ] terminal rows absent from the live index, present in the archive sub-index
- [ ] active rows and the canonical summary block remain in the live index
- [ ] second run reports zero moves

---

### TC02: terminal set derived from status_vocab flag

**Type:** Unit | **Priority:** High | **Story:** US0040

| Step  | Action                                                       | Expected Result                                        |
| ----- | ------------------------------------------------------------ | ------------------------------------------------------ |
| Given | type vocabs where CR includes Built and Complete             | vocab metadata flags absorbing states                  |
| When  | the writer classifies rows                                   | Built is active, Complete/Rejected/Superseded terminal |
| Then  | classification comes from `status_vocab`, not a literal list | no hardcoded set                                       |

**Assertions:**

- [ ] CR `Built` row stays in the live index
- [ ] story `Done`/`Won't Implement`/`Superseded` rows archived

---

### TC03: dry-run writes nothing; fail-loud on unclassifiable row

**Type:** Unit | **Priority:** High | **Story:** US0040

| Step  | Action                                                                 | Expected Result                     |
| ----- | ---------------------------------------------------------------------- | ----------------------------------- |
| Given | a fixture with a row whose status is not in vocab                      | unclassifiable row present          |
| When  | the writer runs with --dry-run, then for real                          | dry-run prints counts + target path |
| Then  | dry-run writes nothing; the real run aborts non-zero, no partial write | fail loud (LL0008)                  |

**Assertions:**

- [ ] dry-run leaves all files byte-identical
- [ ] the real run exits non-zero and writes nothing on the unclassifiable row

---

### TC04: reconcile clean after archive

**Type:** Integration | **Priority:** High | **Story:** US0040

| Step  | Action                                                      | Expected Result          |
| ----- | ----------------------------------------------------------- | ------------------------ |
| Given | a fixture repo with terminal rows                           | reconcile drift 0 before |
| When  | the writer archives terminal rows                           | rows relocated           |
| Then  | `reconcile detect` drift 0; live summary equals full census | census preserved         |

**Assertions:**

- [ ] drift_items == 0 after archive
- [ ] summary totals equal the unioned census count

---

### TC05: next_id unions archive sub-indexes

**Type:** Unit | **Priority:** High | **Story:** US0041

| Step  | Action                                | Expected Result             |
| ----- | ------------------------------------- | --------------------------- |
| Given | an archived sub-index containing id N | live index lacks N          |
| When  | next_id computes the guard set        | archive rows are unioned in |
| Then  | N is seen as taken                    | guard mirrors parse_index   |

**Assertions:**

- [ ] next id is greater than the max archived id

---

### TC06: archived id never reused even if file removed

**Type:** Unit | **Priority:** High | **Story:** US0041

| Step  | Action                                      | Expected Result              |
| ----- | ------------------------------------------- | ---------------------------- |
| Given | id N archived and its artefact file deleted | only the archive row remains |
| When  | next_id runs                                | archive union still sees N   |
| Then  | N is not reallocated                        | no id reuse                  |

**Assertions:**

- [ ] allocated id != N

---

### TC07: close fails loud without a batch retro

**Type:** Integration | **Priority:** High | **Story:** US0042

| Step  | Action                                        | Expected Result |
| ----- | --------------------------------------------- | --------------- |
| Given | a batch with no `retros/RETRO{next}.md`       | retro absent    |
| When  | the sprint close runs                         | gate evaluates  |
| Then  | close returns non-zero with no success report | fail loud       |

**Assertions:**

- [ ] exit code non-zero
- [ ] no "sprint complete" success line emitted

---

### TC08: close passes with the retro present

**Type:** Integration | **Priority:** High | **Story:** US0042

| Step  | Action                                       | Expected Result                    |
| ----- | -------------------------------------------- | ---------------------------------- |
| Given | the batch retro exists and reconcile drift 0 | preconditions met                  |
| When  | the sprint close runs                        | gate evaluates                     |
| Then  | close passes                                 | mirrors the reconcile-drift-0 gate |

**Assertions:**

- [ ] exit code zero with the retro present

---

### TC09: lessons re-validation verb lists and closes open lessons

**Type:** Unit | **Priority:** High | **Story:** US0043

| Step  | Action                                                         | Expected Result        |
| ----- | -------------------------------------------------------------- | ---------------------- |
| Given | a lessons file with open entries                               | open lessons present   |
| When  | the re-validation verb runs and an entry is confirmed obsolete | closure recorded       |
| Then  | the entry transitions to closed/superseded                     | validity-based closure |

**Assertions:**

- [ ] the obsolete entry is marked closed
- [ ] still-valid entries are untouched

---

### TC10: re-validation idempotent

**Type:** Unit | **Priority:** Medium | **Story:** US0043

| Step  | Action                              | Expected Result          |
| ----- | ----------------------------------- | ------------------------ |
| Given | a lessons file already re-validated | no open obsolete entries |
| When  | the verb runs again                 | nothing to close         |
| Then  | the file is unchanged               | idempotent               |

**Assertions:**

- [ ] second run closes zero entries and leaves the file byte-identical

---

### TC11: LESSONS-SUMMARY generator refreshes the committed digest

**Type:** Unit | **Priority:** High | **Story:** US0044

| Step  | Action                                                        | Expected Result                     |
| ----- | ------------------------------------------------------------- | ----------------------------------- |
| Given | a fixture set of still-valid lessons                          | lessons present                     |
| When  | the summary generator runs                                    | `retros/LESSONS-SUMMARY.md` written |
| Then  | the digest reflects the valid lessons; it is a committed path | not under `.local/`                 |

**Assertions:**

- [ ] the summary file is created outside `.local/`
- [ ] every still-valid lesson appears in the digest

---

### TC12: summary regenerates deterministically

**Type:** Unit | **Priority:** High | **Story:** US0044

| Step  | Action                         | Expected Result |
| ----- | ------------------------------ | --------------- |
| Given | the same fixture lesson set    | fixed input     |
| When  | the generator runs twice       | two outputs     |
| Then  | the outputs are byte-identical | deterministic   |

**Assertions:**

- [ ] run-to-run output is identical

---

### TC13: sprint start reads the summary (manual)

**Type:** Manual | **Priority:** Medium | **Story:** US0044

| Step  | Action                               | Expected Result                                          |
| ----- | ------------------------------------ | -------------------------------------------------------- |
| Given | `reference-sprint.md` step 7         | the lifecycle described                                  |
| When  | a reviewer reads the start step      | it reads `LESSONS-SUMMARY.md` + recall, not the full log |
| Then  | the doc describes the full lifecycle | manual confirmation                                      |

**Assertions:**

- [ ] reference-sprint.md step 7 names the summary read at sprint start

---

### TC14: agentic-wave doctrine documented (manual)

**Type:** Manual | **Priority:** Medium | **Story:** US0045

| Step  | Action                                       | Expected Result                                                                    |
| ----- | -------------------------------------------- | ---------------------------------------------------------------------------------- |
| Given | `reference-agentic-lessons.md`               | the file                                                                           |
| When  | a reviewer checks the Wave Structure section | commit-per-wave, single-agent default, cherry-pick order, forward-scaffold present |
| Then  | the four rules are documented                | manual confirmation                                                                |

**Assertions:**

- [ ] all four rules appear with their rationale

---

### TC15: link + style guards pass (US0045)

**Type:** Unit | **Priority:** Medium | **Story:** US0045

| Step  | Action                                          | Expected Result                       |
| ----- | ----------------------------------------------- | ------------------------------------- |
| Given | the edited doc                                  | committed                             |
| When  | `npm run lint:links && npm run lint:style` runs | guards execute                        |
| Then  | both pass                                       | no broken anchors or style violations |

**Assertions:**

- [ ] lint:links and lint:style exit zero

---

### TC16: pre-deploy checklist documented (manual)

**Type:** Manual | **Priority:** Medium | **Story:** US0046

| Step  | Action                                     | Expected Result                                                               |
| ----- | ------------------------------------------ | ----------------------------------------------------------------------------- |
| Given | `reference-deploy-readiness.md`            | the file                                                                      |
| When  | a reviewer checks the Pre-Deploy Checklist | env-key diff, persistent-volume assertion, heredoc, crypto round-trip present |
| Then  | the four items are documented              | manual confirmation                                                           |

**Assertions:**

- [ ] all four checklist items appear

---

### TC17: link + style guards pass (US0046)

**Type:** Unit | **Priority:** Medium | **Story:** US0046

| Step  | Action                                          | Expected Result                       |
| ----- | ----------------------------------------------- | ------------------------------------- |
| Given | the edited doc                                  | committed                             |
| When  | `npm run lint:links && npm run lint:style` runs | guards execute                        |
| Then  | both pass                                       | no broken anchors or style violations |

**Assertions:**

- [ ] lint:links and lint:style exit zero

---

### TC18: coverage gate passes in the CI environment

**Type:** Integration | **Priority:** High | **Story:** US0047

| Step  | Action                                                     | Expected Result   |
| ----- | ---------------------------------------------------------- | ----------------- |
| Given | the runtime-scripts test suite under CI                    | tests run         |
| When  | `coverage run ... && coverage report --fail-under=80` runs | coverage computed |
| Then  | runtime-scripts coverage is >= 80%; the gate exits zero    | CI green          |

**Assertions:**

- [ ] the coverage gate exits zero in the CI environment

---

### TC19: local-vs-CI discrepancy removed (manual)

**Type:** Manual | **Priority:** Medium | **Story:** US0047

| Step  | Action                                 | Expected Result                              |
| ----- | -------------------------------------- | -------------------------------------------- |
| Given | tests that silently skip on CI         | the discrepancy source                       |
| When  | a reviewer checks the fix              | skipped tests run or paths covered otherwise |
| Then  | the root cause is documented in US0047 | manual confirmation                          |

**Assertions:**

- [ ] the local-83%-vs-CI-red root cause is named and resolved

---

### TC20: workflow references bumped action versions

**Type:** Unit | **Priority:** High | **Story:** US0048

| Step  | Action                                                   | Expected Result  |
| ----- | -------------------------------------------------------- | ---------------- |
| Given | `.github/workflows/lint.yml`                             | the workflow     |
| When  | the grep verifier runs                                   | versions checked |
| Then  | checkout@v7 and setup-python@v6 present; no v6/v5 remain | bumps adopted    |

**Assertions:**

- [ ] no `actions/checkout@v6` or `actions/setup-python@v5` remain

---

### TC21: CI green and Dependabot PRs resolved (manual)

**Type:** Manual | **Priority:** Medium | **Story:** US0048

| Step  | Action                                                          | Expected Result     |
| ----- | --------------------------------------------------------------- | ------------------- |
| Given | the bumped workflow on a green coverage gate                    | preconditions met   |
| When  | CI runs and the PRs are reviewed                                | checks pass         |
| Then  | CI is green; PRs #25 and #26 are merged or closed as superseded | manual confirmation |

**Assertions:**

- [ ] PRs #25 and #26 are closed/merged with CI green

---

### TC22: sweep collects every blocker signal

**Type:** Unit | **Priority:** High | **Story:** US0049

| Step  | Action                                                             | Expected Result       |
| ----- | ------------------------------------------------------------------ | --------------------- |
| Given | units with Status Blocked, Depends on, and epic Blocked By         | mixed blocker signals |
| When  | the sweep runs                                                     | signals collected     |
| Then  | every blocked unit is reported with its referents and their status | full coverage         |

**Assertions:**

- [ ] each blocker signal type is collected and reported

---

### TC23: in-repo unblock detected

**Type:** Unit | **Priority:** High | **Story:** US0049

| Step  | Action                                                | Expected Result    |
| ----- | ----------------------------------------------------- | ------------------ |
| Given | a Blocked unit whose in-repo referent is now terminal | referent delivered |
| When  | the sweep resolves referents by census                | status read        |
| Then  | the unit is reported as a now-unblocked candidate     | unblock detected   |

**Assertions:**

- [ ] the unit appears in the now-unblocked list

---

### TC24: cross-repo unblock via PVD manifest

**Type:** Integration | **Priority:** High | **Story:** US0049

| Step  | Action                                                        | Expected Result            |
| ----- | ------------------------------------------------------------- | -------------------------- |
| Given | a fixture manifest and a referent delivered in a sibling repo | cross-repo blocker cleared |
| When  | the sweep resolves through repos[].path                       | sibling repo read          |
| Then  | the unit is reported as now-unblocked                         | cross-repo detection works |

**Assertions:**

- [ ] a blocker cleared in a sibling repo is detected via the manifest

---

### TC25: fail loud, never false-clear

**Type:** Unit | **Priority:** High | **Story:** US0049

| Step  | Action                                                                                                   | Expected Result       |
| ----- | -------------------------------------------------------------------------------------------------------- | --------------------- |
| Given | a referent that is missing, unreadable, or unknown-status                                                | unresolvable referent |
| When  | the sweep runs                                                                                           | resolution attempted  |
| Then  | the unit is reported still-blocked or as an error; never cleared; an unreadable cross-repo path is named | LL0008                |

**Assertions:**

- [ ] an unresolved/unreadable referent never yields a now-unblocked verdict

---

### TC26: sweep runs before sprint planning

**Type:** Integration | **Priority:** High | **Story:** US0050

| Step  | Action                                             | Expected Result       |
| ----- | -------------------------------------------------- | --------------------- |
| Given | a unit unblocked since the last plan               | newly eligible        |
| When  | sprint planning runs the pre-plan sweep            | sweep fires first     |
| Then  | the newly-unblocked unit is eligible for the batch | pre-plan wiring works |

**Assertions:**

- [ ] the pre-plan sweep runs before batch selection

---

### TC27: advisory reconcile lane

**Type:** Unit | **Priority:** Medium | **Story:** US0050

| Step  | Action                                                                          | Expected Result                           |
| ----- | ------------------------------------------------------------------------------- | ----------------------------------------- |
| Given | stale-blocked units                                                             | blockers cleared but status still Blocked |
| When  | reconcile runs the blocker lane                                                 | lane reports                              |
| Then  | stale-blocked units are reported; advisory, never blocking the reconcile result | advisory lane                             |

**Assertions:**

- [ ] the lane is advisory and does not change the reconcile exit verdict

---

### TC28: proposes but never auto-transitions

**Type:** Unit | **Priority:** High | **Story:** US0050

| Step  | Action                                                     | Expected Result    |
| ----- | ---------------------------------------------------------- | ------------------ |
| Given | a now-unblocked candidate                                  | eligible for Ready |
| When  | the sweep reports it                                       | candidate proposed |
| Then  | no status is changed; the gated transition stays the actor | proposal only      |

**Assertions:**

- [ ] the sweep changes no status; transition remains the only mutator

---

## Fixtures

```yaml
index_tree:
  type: change-requests
  active_rows: [CR9001 (Proposed), CR9002 (In Progress)]
  terminal_rows: [CR9003 (Complete), CR9004 (Rejected)]
lessons_tree:
  open: [L-9001 valid, L-9002 obsolete]
  expected_summary: digest of still-valid entries only
```

---

## Automation Status

| TC   | Title                                  | Status  | Implementation |
| ---- | -------------------------------------- | ------- | -------------- |
| TC01 | archive writer relocates terminal rows | Pending | -              |
| TC02 | terminal set from status_vocab         | Pending | -              |
| TC03 | dry-run + fail-loud                    | Pending | -              |
| TC04 | reconcile clean after archive          | Pending | -              |
| TC05 | next_id unions archive                 | Pending | -              |
| TC06 | archived id never reused               | Pending | -              |
| TC07 | close fails loud without retro         | Pending | -              |
| TC08 | close passes with retro                | Pending | -              |
| TC09 | re-validation lists/closes             | Pending | -              |
| TC10 | re-validation idempotent               | Pending | -              |
| TC11 | summary generator                      | Pending | -              |
| TC12 | summary deterministic                  | Pending | -              |
| TC13 | sprint start reads summary             | Manual  | -              |
| TC14 | agentic doctrine documented            | Manual  | -              |
| TC15 | lint guards (US0045)                   | Pending | -              |
| TC16 | pre-deploy checklist documented        | Manual  | -              |
| TC17 | lint guards (US0046)                   | Pending | -              |
| TC18 | coverage gate passes on CI             | Pending | -              |
| TC19 | local-vs-CI discrepancy removed        | Manual  | -              |
| TC20 | workflow references bumped versions    | Pending | -              |
| TC21 | CI green; Dependabot PRs resolved      | Manual  | -              |
| TC22 | sweep collects blocker signals         | Pending | -              |
| TC23 | in-repo unblock detected               | Pending | -              |
| TC24 | cross-repo unblock via PVD             | Pending | -              |
| TC25 | fail loud, never false-clear           | Pending | -              |
| TC26 | sweep runs before planning             | Pending | -              |
| TC27 | advisory reconcile lane                | Pending | -              |
| TC28 | proposes, never auto-transitions       | Pending | -              |

---

## Traceability

| Artefact | Reference                                                                                    |
| -------- | -------------------------------------------------------------------------------------------- |
| PRD      | [sdlc-studio/prd.md](../../prd.md)                                                           |
| Epic     | [EP0010](../../epics/EP0010-skill-self-improvement-token-economy-learning-loop-consuming.md) |
| TSD      | [sdlc-studio/tsd.md](../tsd.md)                                                              |

---

## Revision History

| Date       | Author | Change                                                    |
| ---------- | ------ | --------------------------------------------------------- |
| 2026-06-27 | Sam    | Initial spec - AC coverage matrix authored at design rung |
