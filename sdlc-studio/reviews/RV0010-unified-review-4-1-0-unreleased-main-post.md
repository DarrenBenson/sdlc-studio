# RV-0010: Unified Review - 4.1.0 + unreleased main - post-audit consolidation

> **Date:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Review type:** Unified PRD/TRD/TSD/Persona consolidation
> **Reviewer:** Claude Fable 5 (agent); evidence base: the 2026-07-16 adversarial audit (wf_9903a6e6-53a, every cited finding survived a 3-vote refute panel) plus fresh `review_prep.py` / index census
> **Triggered by:** operator-invoked `/sdlc-studio review` immediately after the full project-profile audit filed BG0152-BG0174 and CR0280-CR0306
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21
> **Predecessor unified:** RV0001 (2026-06-20); interleaved: RV0006-RV0008 repository reviews, RV0009 sprint-close

## Scope

All four required legs (PRD, TRD, TSD, Persona - present, none waived per `review_prep.py
required_legs`), cross-document consistency, RFC scan, CR staleness, agent-instructions
hygiene. No PVD (single-repo project). CODE leg out of scope as always.

## Findings

### PRD leg - 65%

The v4.1.0 scope is documented accurately and its features are implemented and gated. The
document fails on **currency**: it is one sprint behind committed `main` in seven
triple-verified places. It teaches the retired Effort/S-M-L estimator as live and gates
recalibration on two defects fixed 2026-07-14 (CR0280); its coverage clause promises
exhaustive `[Unreleased]` marking while ~14 Done epics of shipped features (EP0033-EP0047:
refine, two-backlog gates, issue/triage, migrate, close-down enforcement, and more) appear
nowhere in the tables (CR0281); the security NFR denies the shipped network surface
(CR0282); Section 9's configuration reference is wrong on four counts (CR0285); the data
architecture places the evidence ledger in gitignored `.local` when it moved to committed
`retros/evidence/` (BG0156); the breakdown-gate AC enumerates size vocabularies the gate
does not accept (BG0157); and the extracted-specs status note contradicts the epic index it
sits above (BG0168).

**Product Owner sign-off: PRD requirements satisfied: yes for the v4.1.0 released scope
(features documented are implemented and verified); no as a migration blueprint for current
`main` - gaps tracked as CR0280-CR0282, CR0285, BG0156-BG0157, BG0168.**

### TRD leg - 65%

Architecture-as-described matches the code for the released scope; the shipped scripts,
their read/write contracts, and the ADR history remain substantially real. Verified drift:
§6's data architecture predates the issue type, story Blocked status, inbox triage lane and
two-backlog model (CR0290); ADR-008 claims collision-proof ids where the implementation is
2 random chars in a ~17-minute bucket with the cross-machine case unguarded (CR0286);
critic is misfiled among never-mutate helpers while it appends two committed verdict logs
non-atomically (CR0289); §5 rule 5's enumerated write surface omits at least five shipped
writers (CR0296); the pinned census counts have rotted again (CR0302); the Migrations
section denies the three-script migration surface the TRD itself lists elsewhere (CR0304);
ADR-010's documented opt-out disarms only one of the three close lanes it claims to (BG0166 -
shared with the gate code).

**Verdict: architecture current for released scope; §6/ADR wording drift tracked as
CR0286, CR0289-CR0290, CR0296, CR0302, CR0304.**

### TSD leg - 70%

The test estate itself is healthy: full suite 2553 green at sprint close, `verify_ac`
reports 432 ACs verified / 0 failed across 178 stories, and CI blocks on an 80% coverage
floor plus a bandit scan. The document is wrong about its own gates in both directions: it
says coverage is "not wired into CI" and "no dedicated security scanner is wired" while
both run as blocking steps (CR0287); its per-script test-module gate is a phantom no sweep
enforces, already violated by six modules (BG0162); its gate lane tables mark two advisory
lanes Blocking and omit two shipped lanes (BG0170); the test-noise leg runs hook-only, not
in CI (CR0291); the write-confinement target is backed by a suite snapshotting exactly one
writer (CR0300); and the eval gate cannot see a wholly-ungraded scenario (BG0167).

**Verdict: estate healthy, document diverges from its own enforcement - tracked as CR0287,
CR0291, CR0300, BG0162, BG0167, BG0170.**

### Persona leg - 40%

The weakest leg. The Cooper registry (`personas/`) defines two personas - Maya Okafor
(solo founder-engineer, Primary) and Trevor Hale (enterprise delivery manager) - and
`review_prep.py` finds **both unused: referenced in no PRD section, consulted on no CR or
story** (`referenced_in_prd: []`, `unused: [Maya Okafor, Trevor Hale]`). Story workflows
still read only the legacy `personas.md`, so the registry with the declared Primary is
unreachable from story generation (CR0283). The amigo cast is the uncustomised shipped
default, grounded in a fictional shopping-list project, sitting in the retired
`personas/amigos/` home the repo's own migrator warns about (CR0292). `validate` gives this
layout a silent clean pass (CR0297). No duplicates, no broken cross-references. The amigo
*seats* do load-bearing work (the RV0009 sprint-close adversarial pass was a seat run); the
named personas do not.

**Verdict: personas are not load-bearing - make them so or archive them; tracked as
CR0283, CR0292, CR0297.**

### RFC scan

44 RFCs: 38 Accepted, 4 Draft, 1 Superseded, 0 In Review. No Draft stalled >14 days
(RFC0036/0040/0043/0044 all dated 2026-07-14..16). Accepted-side hygiene problems are
already filed: RFC0018/0022/0023 delivered but every design decision still listed Open with
contradicting leanings (BG0161); RFC0034 and RFC0038 both Accepted with opposite canonical
sizing decisions, no supersession marking (CR0288); the 2026-07-14 tranche Accepted with
file_finding's boilerplate "Act on this finding or keep status quo" Open rows (CR0295).

### CR staleness

306 CRs: 73 Complete, 32 Proposed, 1 In Progress, 5 Superseded. **No Proposed CR is stale**
(none older than 2026-07-14; 27 of the 32 were filed today by the audit). The one In
Progress CR (CR0272, command-surface cleanup) has slice 2 outstanding - correctly open.
BG0169 (CR0273 Superseded with no successor pointer) remains the one lifecycle-hygiene
defect, filed.

### Agent-instructions hygiene

`validate.py instructions`: clean (errors=0, warnings=0).

## Cross-Document Consistency

| Check | Result | Detail |
| --- | --- | --- |
| PRD -> TRD coverage | WARN | Both docs cover released scope; the ~14 unreleased Done epics are absent from BOTH, so coverage of current main is unassessable until CR0281/CR0290 land |
| TRD -> TSD coverage | WARN | Per-script test-module invariant is a phantom gate (BG0162); write-confinement target backed by one snapshot (CR0300) |
| PRD NFR -> TSD gates | WARN | Security NFR denies the shipped network surface (CR0282) while TSD denies the shipped bandit/coverage gates (CR0287) - the NFR-to-gate chain is broken in prose, intact in CI |
| PRD -> Persona refs | FAIL | PRD references no persona in the registry; the declared Primary (Maya Okafor) is absent from PRD S1/S2 |
| Persona -> CR/Story activity | FAIL | Both registry personas unused - no consult or reference within the 90-day window (they are 26 days old and never consulted) |
| Persona -> Persona consistency | PASS | No duplicates, no broken cross-references, index present |

## Persona Consultation

- **Maya Okafor (solo founder-engineer, Primary):** the sprint report and honest cost
  measurement serve her directly - she runs lean and needs true spend, not avoided-cost
  theatre. Her push-back trigger fires on the spec rot: a solo adopter rebuilds from the
  PRD/TRD blueprint, and today's blueprint teaches a falsified estimator (CR0280). Fix the
  blueprint before the next release.
- **Trevor Hale (enterprise delivery manager):** CAB-grade auditability is his need; the
  preserved sprint-close record (RV0009), operator sign-off, and the audit's evidence-cited
  filings satisfy it. His concern: TSD misdescribing its own blocking gates (CR0287) is
  exactly what an enterprise auditor would find first.
- Both personas' own standing is a finding: neither has ever been consulted on a CR/story
  (this section is their first). CR0283/CR0292/CR0297 decide whether they become
  load-bearing or are archived.

## Auto-Fixes Applied This Review

None required. Index counts and status rows were already reconciled during the audit's
filing pass (`reconcile.py detect`: drift_items=0 before and after this review). All
content divergences are judgement-bearing and already tracked as sized CRs/bugs - editing
spec prose here would preempt the sized backlog work (CR0280-CR0304).

## Priority Actions

1. Fix the four High bugs in the shipped scripts: BG0152 (per-attempt telemetry has no
   production writer), BG0153 (multi-record cost merge), BG0154 (decisions ledger atomic
   write), BG0155 (corrupt baseline disarms close-down).
2. Land the spec-refresh cluster before the 5.0.0 release: CR0280-CR0282, CR0285 (PRD),
   CR0286/CR0290/CR0296/CR0302/CR0304 (TRD), CR0287 (TSD) - the freeze window to
   ~2026-07-21 is the natural slot.
3. Decide the persona layer: CR0283 + CR0292 + CR0297 (make the registry load-bearing from
   story generation, customise or retire the default amigo cast).
4. BG0173 (refute-panel quorum) before the next audit run - it guards every future audit
   verdict.
5. Commit the in-flight EP0048/US0172-US0176 sprint work sitting uncommitted on the tree.

## Production State

| Aspect | State |
| --- | --- |
| Version live | v4.1.0 (released 2026-07-14); release freeze until ~2026-07-21 |
| Unreleased | All post-4.1.0 work on `main` under `[Unreleased]`; additive |
| Test suite | 2553 tests green at sprint close; AC verification 432/432 |
| Coverage gate (CI) | Blocking >=80% on runtime scripts + blocking bandit scan (TSD wrongly denies both - CR0287) |
| Workspace | 746 artefacts validate clean (0 errors); reconcile drift 0 |

## Verdict

The **code and its gates are healthy; the documents of record are one sprint behind them.**
Delivery outran synthesis: since the 2026-07-14 PRD/TRD/TSD refresh, two sprints landed
(RFC0038 finale, RFC0035/EP0048) plus fourteen epics of earlier unreleased work, and no
review digested them into the specs. That is exactly the symptom trigger
`reference-review.md` names, and today's audit priced the repair (~91 points filed). The
persona layer is the standing exception: not drifted but never load-bearing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Unified review (post-audit consolidation); LATEST.md rewritten from this record |
