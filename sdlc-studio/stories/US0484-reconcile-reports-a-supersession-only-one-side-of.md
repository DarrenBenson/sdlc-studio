# US0484: reconcile reports a supersession only one side of the pair records

> **Status:** Done
> **Delivers:** CR0447
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Epic:** EP0175
> **Points:** 5

## User Story

**As a** reader navigating the RFC graph
**I want** a supersession declared on one artefact and absent from its counterpart to be reported
**So that** a superseded design cannot keep reading as live from the direction that never recorded it

## Acceptance Criteria

### AC1: a one-sided supersession is reported

- **Given** an artefact declaring it supersedes another whose counterpart records nothing
- **When** reconcile detect runs
- **Then** it reports the pair and which side is missing the declaration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_one_sided_supersession_is_reported
- **Verified:** yes (2026-07-30)

### AC2: every spelling the corpus carries is recognised, including the hyphenated id form

- **Given** the eleven declaration spellings present in the corpus (measured; the six this AC first named was wrong, and five of the missing ones carry the verb in free prose) and the hyphenated id forms two of them use
- **When** each is presented to the detector
- **Then** every one is recognised against a pinned grammar that normalises the hyphenated id, so neither an unenumerated spelling nor CR-0132 style is read as an absence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_every_corpus_spelling_and_id_form_is_recognised
- **Verified:** yes (2026-07-30)

### AC3: the 11 pairs already in the corpus are waived or repaired before the kind can block

- **Given** the 11 one-sided pairs the corpus carries today (RFC0038's partial supersession of RFC0034 is NOT among them - US0476 recorded that one on both sides, so the count of 11 holds by a different composition than this AC assumed)
- **When** the detector is introduced
- **Then** each is either repaired or waived with a stated reason, so introducing the kind cannot turn a blocking lane red across a clean repository
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionLiveCorpusTests::test_the_existing_pairs_are_waived_or_repaired
- **Verified:** yes (2026-07-30)

### AC4: a deliberately partial supersession stays waivable

- **Given** a declaration superseding only part of its counterpart, which remains live in the rest
- **When** the detector runs
- **Then** it is not reported once waived, because a partial supersession is legitimate asymmetry rather than drift
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_partial_supersession_is_waivable
- **Verified:** yes (2026-07-30)

### AC5: a symmetric pair is not reported

- **Given** a pair whose both sides record the supersession
- **When** reconcile detect runs
- **Then** it reports nothing, so the detector does not manufacture work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::SupersessionTests::test_a_symmetric_pair_is_not_reported
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
| 2026-07-27 | Claude Fable 5 | ACs repaired against the independent adversarial review |
| 2026-07-30 | Claude Opus 5 | Delivered. Grammar in `lib/sdlc_md.py`, `supersession_asymmetry_drift` in `reconcile.py`, waiver ratchet in `sdlc-studio/.supersession-waivers.json`; 252 tests in `test_reconcile.py` green; 16/16 mutants killed |

## Evidence

Two of this story's own premises were measured rather than trusted, and one was wrong.

**AC2 said six spellings. There are eleven**, counted with the shipped grammar against the live
corpus. The five it missed are the ones that matter: `Superseded 2026-07-04 by [CR-0142](...)`,
`Superseded by RFC0055 (guided init).`, `Superseded by the sdlc-studio.com website.`,
`Superseded (2026-07-04, operator-approved at sprint planning).` and `Superseded 2026-06-22:` all
carry the verb in free prose inside the bold run. A field-name allowlist - the obvious
implementation, and what six spellings suggests - reads every one of them as an absence, which
reports a **recorded** supersession as drift. So the label is matched on its verb instead, and a
mutant replacing that with a three-name allowlist is killed.

**AC3's count of 11 is right, but not for the reason it gives.** It names RFC0038's partial
supersession of RFC0034 as one of the 11; US0476 already recorded that pair on both sides, so it is
not one-sided. The count holds by a different composition. Ten of the eleven run in the direction
the AC does not mention: the superseded artefact records it and the superseder does not, so a
forward-only detector would have found one of eleven.

Three findings from building it:

| Finding | Consequence |
| --- | --- |
| The template's combined `Supersedes / Superseded by:` field carries both verbs | Recording both directions manufactured a reversed phantom pair for every one of the fifteen in the corpus; the direction comes from the value |
| A declaration whose prose sits inside the bold run has an EMPTY value | Read as an unfilled template field and dropped, which lost `Superseded by the sdlc-studio.com website.` entirely; the label's trailing `:` now tells a bare field name from a whole sentence |
| A filter excluding decision rows (`D5`, `WS3`) could never fire | `ID_SEARCH_RE` needs four digits, so `D5` never reaches it. A mutant proved the guard inert and it was REMOVED rather than kept as decoration; the premise is pinned by a test on the digit floor, which is the half that actually does the work |

The 11 pre-existing pairs are waived as debt, not as legitimacy: the reason on each says the
missing half is owed work, the set may only shrink, and an entry is cleared by writing the
declaration. `reconcile detect` is clean, and a control test patches the waivers away to prove the
detector still finds all 11 - without it, a clean run is equally consistent with a detector that
scans nothing.
