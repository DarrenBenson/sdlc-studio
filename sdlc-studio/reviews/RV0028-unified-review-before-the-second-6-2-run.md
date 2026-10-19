# RV-0028: Unified review before the second 6.2 run: PRD, TRD, TSD and personas against v6.1.0 plus 6.2 on main

> **Date:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Review type:** Unified PRD/TRD/TSD/Persona consolidation
> **Reviewer:** Claude Opus 5.5 (orchestrator), with one read-only reviewer per leg (Product Owner, Engineering, QA and Persona seats)
> **Triggered by:** D0372, the operator's ruling of 2026-10-18 that the review runs before the second 6.2 run is planned; RUN-01M4R168's close reported it overdue
> **Project version:** 6.1.0, plus the 6.2 work on main through ff54e739
> **Predecessor unified:** RV0010 (2026-07-16), the last unified document review; RV0018 and RV0019 (July) were sprint-closing reviews. No review-state record existed on this clone

## Scope

- **The four required legs:** PRD (`sdlc-studio/prd.md`, 718 lines), TRD (`sdlc-studio/trd.md`, 1155 lines), TSD (`sdlc-studio/tsd.md`, 676 lines) and Persona (`sdlc-studio/personas/`, 3 personas and 3 seat cards). No PVD (single-repo).
- **Each leg** was reviewed against the tree by a fresh read-only context, which cited a document line and the code or command that confirms or contradicts it, and checked every finding against the open Bugs and CRs.
- **The orchestrator ran:**
  - the cross-document check;
  - the CR staleness and RFC scans;
  - `validate.py instructions`;
  - `review_prep.py prep`, which marked all 3,145 artefacts as changed since the last review.
- **No auto-fixes were applied** (see Auto-fixes).

## Findings

### PRD (Product Owner)

**PRD requirements satisfied: no.** There are four gaps:

- `require_ac_verification`, which the PRD states is a gate, is read by no code (BG1063).
- The engagement floor's `adopt_after` escape fails on schema-v3 ids (BG0959).
- The jest and vitest Verify verbs cannot select a test (BG1023).
- `reconcile --scope` takes one scope, not the subset the PRD states (the PRD is corrected in CR0647).

Of the 64 features, 62 are Complete, 1 is Partial (the engagement floor) and 1 was retired under its own name (the handoff guide). All 16 [Unreleased] flags are wrong.

| ID | Sev | Where | Finding | Filed to |
| --- | --- | --- | --- | --- |
| PRD-1 | Important | prd.md:422 | Says only a story carries executable Verify lines; `sdlc_md.EXECUTES_VERIFIERS` is (story, bug) since 7479957e | CR0647 |
| PRD-2 | Important | prd.md:322, :599 | `require_ac_verification` is stated as a cascade gate; only a comment names it (constitution.py:13); the live gate is `quality.done_requires_verified` | BG1063, CR0647 |
| PRD-3 | Important | prd.md:351 | "Groomed" omits the criteria checks and the split ceiling `sprint plan` enforces | CR0647 |
| PRD-4 | Important | prd.md:650 | Cost model cites the 25,000-token seed; plans price from the measured 146,283 tokens per point | CR0647 |
| PRD-5 | Important | prd.md:202, :14 | Baseline reads v4.1.0; all 16 [Unreleased] rows shipped by v6.0.0 | CR0647 |
| PRD-6 | Important | prd.md:339 | The engagement floor is marked Complete, but its `adopt_after` escape fails on v3 ids | BG0959 (open), CR0647 |
| PRD-7 | Important | prd.md:457 | Network paths understated: the close's and release cut's `gh run list` are missing; id allocation never fetches | CR0647 |
| PRD-8 | Important | prd.md:194 | Calls the installed copy the back-port source; the repo is the source, `forward-port.sh` mirrors it, six install targets | CR0647 |
| PRD-9 | Important | prd.md:619 | One pre-commit hook "makes the whole gate un-skippable"; there are three hooks and the full suite runs at push | CR0647 |
| PRD-10 | Important | prd.md:257 | No inventory row for anything shipped since July (charter queue, rolling runs, boundary gates, risk-banded review, line coverage, release cut, constitution, report and sign) | CR0647 |
| PRD-11 | Important | prd.md:446 | `critic`, `gate` and `repo map` are listed as read-only; they write ledgers or `.local` caches | CR0647 |
| PRD-12 | Suggestion | prd.md:130 | Pinned counts (52, 41, 78, 58, ~260 lines) are stale; the census reads only the TRD | CR0647, CR0649 |
| PRD-13 | Suggestion | prd.md:595 | `lessons.loop` default shown as `loop`; it is `enforce` | CR0647 |
| PRD-14 | Suggestion | prd.md:602 | `schema_version` default shown as 3; defaults hold 2, and init seeds 3 | CR0647 |
| PRD-15 | Suggestion | prd.md:274 | Lists doc-freshness among the default lanes; it is on-demand | CR0647 |
| PRD-16 | Suggestion | prd.md:276 | "Handoff guide" row describes a retired writer; only `handoff.py show` remains | CR0647 |
| PRD-17 | Suggestion | prd.md:293 | "Sprint close-down gate" is an advisory in close_owed.py with an optional Stop hook | CR0647 |
| PRD-18 | Suggestion | prd.md:62 | The review cap omits `critic.py record --ruling` (6.2) | CR0647 |
| PRD-19 | Suggestion | prd.md:509 | Metadata still lists Effort; committed records and Issue/Charter are missing from the chain | CR0647 |
| PRD-20 | Suggestion | prd.md:561 | "No third-party packages"; PyYAML, pytest with xdist and coverage are optional dependencies | CR0647 |
| PRD-21 | Suggestion | prd.md:307 | 17 detail criteria unticked under Complete; 13 hold; Reconcile AC3's subset is wrong | CR0647 |
| PRD-22 | Suggestion | prd.md:701 | The open questions about the workspace and cost are answered by practice; promote them to decisions | CR0647 |
| PRD-23 | Suggestion | prd.md:451 | "Well under a second"; reconcile takes 14.4 s and status 6.8 s on this workspace | CR0647 |
| PRD-24 | Suggestion | prd.md:137 | Verify AC is shown Complete over the jest and vitest selection defect | BG1023 (open), CR0647 |
| PRD-25 | Suggestion | prd.md:655 | Per-ship history in feature blocks belongs in the changelog table | CR0647 |

### TRD (Engineering)

**TRD current: no.** The ADRs, script tiers, lane registries, ULID design and stated bands hold. Of the 12 ADRs, 8 are current, 3 are partly stale (003, 004, 009) and 1 (012) is accepted but not built. The hook and boundary-gate tier is not documented at all.

| ID | Sev | Where | Finding | Filed to |
| --- | --- | --- | --- | --- |
| TRD-1 | Critical | trd.md:395 | "Only a story carries an executable verifier"; bugs do, and the Fixed gate depends on it; two code comments repeat the error | CR0645 |
| TRD-2 | Important | trd.md:558 | The commit, commit-msg and pre-push gates, the boundary gates and D0180/D0181 are undocumented | CR0644 |
| TRD-3 | Important | trd.md:178 | "The gate writes nothing"; it writes `.local` cost, suite-verdict and boundary-log state; `critic brief` appends briefs.jsonl | CR0644 |
| TRD-4 | Important | trd.md:192 | Test stack given as unittest alone; pytest with xdist, coverage, PyYAML, Node and markdownlint, and bandit are in use | CR0644 |
| TRD-5 | Important | trd.md:453 | Telemetry listed under `.local`; evidence, lessons, verdict logs, reports and run records are committed; the pin passes on the legacy name | CR0645 |
| TRD-6 | Important | trd.md:449 | Run state shown as `.local` only; there is now a tracked sealed record and a close-and-sign lifecycle | CR0645 |
| TRD-7 | Important | trd.md:308 | Registry misses `charter`, epic Superseded and META_TYPES (report) | CR0645 |
| TRD-8 | Important | trd.md:260 | Three network paths; two more gh callers and the version-check GET are missing (an ADR-004 exception) | CR0645 |
| TRD-9 | Important | trd.md:616 | "Sub-second" gate; budget 45 s, measured 127 s | CR0644 |
| TRD-10 | Important | trd.md:444 | The `.local` table lists 11 of about 40 files | CR0645 |
| TRD-11 | Suggestion | trd.md:37 | Coverage line at v5.1.0; ADR-012 has no revision row | CR0645 |
| TRD-12 | Suggestion | trd.md:1047 | ADR-012 is stated in the present tense; `personas/memory/` does not exist | CR0645 |
| TRD-13 | Suggestion | trd.md:908 | ADR-009: persona_gen stamps and classifies but does not write cards; default seats ship | CR0645 |
| TRD-14 | Suggestion | trd.md:699 | ADR-003 misses `reconcile settle` at commit | CR0645 |
| TRD-15 | Suggestion | trd.md:425 | CR Size said to be mandatory at filing; it is optional since BG0756 | CR0645 |
| TRD-16 | Suggestion | trd.md:232 | 15 of 69 scripts are tracked without the executable bit the contract requires | BG1064 |
| TRD-17 | Suggestion | trd.md:351 | "Every id regex accepts both eras"; three open v3-id defects | BG0959, BG0997, BG0948 (open), CR0645 |
| TRD-18 | Suggestion | trd.md:404 | The wide-CR trigger misses a Size-L CR | BG1021 (open), CR0645 |
| TRD-19 | Suggestion | trd.md:303 | A PRD divergence note the PRD no longer has | CR0645 |
| TRD-20 | Suggestion | trd.md:528 | Install table mixes global and local paths; new installer options missing | CR0645 |
| TRD-21 | Suggestion | trd.md:199 | CI architecture undescribed (jobs, schedule, release.yml) | CR0644 |
| TRD-22 | Suggestion | trd.md:132 | tools/ and lib/ rows miss the gate, hook and release tooling and run_state.py | CR0644 |
| TRD-23 | Suggestion | trd.md:497 | `github_sync pull` lists issues to ingest; it creates no file | CR0645 |
| TRD-24 | Suggestion | trd.md:190 | `__future__` rendered as bold markers | CR0645 |
| TRD-25 | Suggestion | trd.md:136 | c4-diagrams path is wrong; `trd visualise` not named | CR0645 |

### TSD (QA)

**TSD current: no.** The gate.py lane table and the mutation, bound-lane, Fixed-gate and bandit sections are accurate. The pipeline description predates D0180 and D0181.

- **Modules:** 441 (332 skill, 109 tools).
- **Coverage:** 89% measured in CI, against the 82% stated.
- **CI's corpus-verify job** has been red for its last three scheduled runs (BG1054).

| ID | Sev | Where | Finding | Filed to |
| --- | --- | --- | --- | --- |
| TSD-1 | Critical | tsd.md:535 | One pre-commit hook "runs the whole gate"; commit-msg runs selected suites against an advisory 90 s budget, and the full suite runs at push | CR0644 |
| TSD-2 | Important | tsd.md:205 | The test-noise ratchet is held in CI's combined step, not at a normal commit or at push | CR0644 |
| TSD-3 | Important | tsd.md:182 | Coverage "roughly 82%"; CI measures 89% | CR0646, CR0649 |
| TSD-4 | Important | tsd.md:257 | "Eight checkers"; `npm run lint` chains ten (dead-flags, disclosure) | CR0644 |
| TSD-5 | Important | tsd.md:549 | A tag push does not run `gate.py --release`; record-green and tag-check are manual (ruled manual, D0375) | CR0644 |
| TSD-6 | Important | tsd.md:542 | No scheduled stage; corpus and corpus-verify jobs unnamed; corpus-verify red three runs | CR0644, BG1054 (open) |
| TSD-7 | Important | tsd.md:191 | Framework given as unittest alone; pytest, xdist, coverage, requirements-dev.txt and the 3.10 floor job missing | CR0644 |
| TSD-8 | Important | tsd.md:193 | "Seconds for the tools suite"; 517 s in CI | CR0644 |
| TSD-9 | Important | tsd.md:634 | One module per script; 196 of 332 are per-unit lean modules; helpers, markers and hooks missing | CR0646 |
| TSD-10 | Important | tsd.md:443 | Per-unit added-line coverage (`review.line_coverage`, off here) not described | CR0646 |
| TSD-11 | Important | tsd.md:384 | Security NFR names gh and Verify only; the PRD lists four paths | CR0646 |
| TSD-12 | Important | tsd.md:382 | The performance proxy's 45 s budget is exceeded on every run (143 s in CI) | BG1065, CR0644 |
| TSD-13 | Important | tsd.md:388 | The PRD's appetite breaker and ULID identity NFRs have no TSD row | CR0646 |
| TSD-14 | Suggestion | tsd.md:391 | The delivery gates (plan, Done, Fixed, close, sign) are not tabulated | CR0644 |
| TSD-15 | Suggestion | tsd.md:283 | Assertion integrity omits revert-check and stamps | CR0646, CR0624 (open) |
| TSD-16 | Suggestion | tsd.md:229 | lib/retired_surface has no dedicated test module either | CR0646 |
| TSD-17 | Suggestion | tsd.md:399 | Version consistency blocks on every commit, strictly at release | CR0644 |
| TSD-18 | Suggestion | tsd.md:275 | The link-check gap is only anchors inside artefacts | CR0646 |
| TSD-19 | Suggestion | tsd.md:263 | Two markdownlint configs and the lint-md.sh wrapper | CR0644 |
| TSD-20 | Suggestion | tsd.md:330 | Nine eval scenarios, run manually; none recorded for v6.1.0 | CR0646 |
| TSD-21 | Suggestion | tsd.md:513 | The tools tier holds installer, hook and guard tests | CR0646 |
| TSD-22 | Suggestion | tsd.md:17 | Header at the 6.0 baseline, unlisted status, history out of order | CR0646, BG1022 (open) |
| TSD-23 | Suggestion | tsd.md:411 | "gate.py is read-only"; it writes `.local` state | CR0644 |
| TSD-24 | Suggestion | tsd.md:153 | Points at an AGENTS.md section that does not exist; the bare discover reaches neither suite | CR0646 |

### Persona

**Personas current: no.** None is stale under the 90-day rule:

- All three were last consulted on 2026-09-16 and last referenced on 2026-10-12.
- There are no duplicates and no broken PRD references.
- The seat cards match the shipped amigos.

The cards have drifted from the work all the same: Maya's card was last revised 94 days ago, Trevor's 119 days ago.

| ID | Sev | Where | Finding | Filed to |
| --- | --- | --- | --- | --- |
| PER-1 | Important | personas/index.md:6-21 | No card for the skill maintainer, so repo-only work defaults to Maya (38 of 256 stories since September) | D0373, CR0648 |
| PER-2 | Important | maya card:25-63 | Unrevised 94 days; no sign step and no gate-cost frustration; still "autosprint" | CR0648 |
| PER-3 | Important | seats/product.md:23 | Product seat approves only Primary-persona goals; Jonah is a declared Secondary | BG1066 |
| PER-4 | Important | decisions.md:225 | D0211 read accepted for a retired consult gate, so no user-persona consult has a trigger | D0374 |
| PER-5 | Suggestion | reference-review.md:185 | No command builds the staleness map; `staleness_days` is read by no script | BG0966, US1057 (open) |
| PER-6 | Suggestion | prd.md:103 | O5 cites the wrong Maya goal; Jonah's End goal 4 has no outcome | CR0648 |
| PER-7 | Suggestion | artifact.py:288 | The cards will not pass the 6.2 persona standard EP0287 brings | CR0648, EP0287 |
| PER-8 | Suggestion | trevor card:29-35 | No sign-once-per-run boundary; no statement on how a Negative's objection is weighed | CR0648 |
| PER-9 | Suggestion | personas/index.md:30-36 | History out of order and incomplete; no Last updated; no link to the seats | CR0648 |
| PER-10 | Suggestion | personas.md:19 | The legacy file contradicts its own banner | CR0648 |
| PER-11 | Suggestion | US0284-US0287 | Four Done stories name a persona outside the registry (pre-CR0425) | no rework; evidence for PER-1 |

### Cross-document consistency

| Check | Result | Detail |
| --- | --- | --- |
| PRD -> TRD | Concerns | Both state the story-only verifier rule the code reversed (PRD-1, TRD-1). Both understate the network paths, and differently (PRD-7, TRD-8). The PRD names nothing shipped since July (PRD-10), and the TRD omits the hooks (TRD-2) |
| TRD -> TSD | Concerns | The hook and boundary-gate tier is missing from both (TRD-2, TSD-1). Both deny the gate's `.local` writes (TRD-3, TSD-23) |
| PRD NFR -> TSD | Concerns | Security: four PRD paths against two in the TSD (TSD-11). Scalability: no rows (TSD-13). Performance: its proxy is permanently red (TSD-12, BG1065) |
| PRD -> Persona | Pass with one gap | All 3 references resolve; the O5 citation and Jonah's End goal 4 are wrong (PER-6) |
| Persona -> CR/Story | Pass | 0 stale. Maya's count is inflated by repo-only work (PER-1) |
| Persona -> Persona | Pass | No duplicates or broken references; the index history is out of order (PER-9) |

### Change requests and RFCs

- **Proposed: 15**, including CR0644-CR0649 filed by this review. None is past the 14-day staleness line; the oldest, CR0630, is 9 days old.
- **In Progress: 25.** Every one links to a Draft epic (the refined 6.2 scope, D0356), so none is ready to close.
- **Complete: 520.**
- **RFCs:** 56 Accepted, none in Draft or In Review. Every CR an Accepted RFC names exists.
- **Agent instructions:** `validate.py instructions` reports 0 errors, 0 warnings.

### Rulings at this review

All four rulings are the operator's, given on 2026-10-19:

- **D0373:** the registry gains a skill-maintainer card, and repo-only units are minted against it.
- **D0374** (supersedes D0211): a stakeholder consult runs for any epic that changes a persona or a persona's goals. D0211's predicate-naming rule (3) stands.
- **D0375:** `gate.py --release`, record-green and tag-check stay manual pre-tag steps, and the documents describe them as manual.
- **D0376** (supersedes D0369): CR0644 joins the second 6.2 run beside EP0288 and BG1061.

### Auto-fixes

None were applied. The PRD's mechanical fixes fall in the rows CR0647 rewrites anyway: the 16 [Unreleased] flags, the 13 verified detail criteria and the engagement floor's Partial status. They land with that refresh as one reviewed change, rather than as an edit the refresh would churn.

## Verdict

**Concerns.** The PRD, TRD and TSD trail the product by about three months. The persona cards trail the work by a similar margin. In the shipped behaviour, the review found:

- the four PRD gaps;
- the dead config key (BG1063);
- the missing executable bits (BG1064);
- the saturated gate budget (BG1065);
- the Primary-only product seat (BG1066).

It also found one filing defect in its own session, the cap keyed on a sealed run (BG1067).

The single most consequential error is shared across documents: the TRD and PRD say only stories execute Verify lines, which a rebuild would act on.

Each document has a refresh request: CR0644 (the gate sections of the TRD and TSD, run two), CR0645 (TRD), CR0646 (TSD), CR0647 (PRD) and CR0648 (personas). CR0649 extends the freshness census to the PRD and TSD, so the next drift is caught when it happens rather than at the next review.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | Claude Opus 5.5 | Unified review: four legs, the cross-document check, CR and RFC scans, and the operator's rulings D0373-D0376 |
