# US0838: refine runs a stakeholder consult over the epic and its stories and records it as an artefact naming the units it covered

> **Status:** Draft
> **Delivers:** RFC0058
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Epic:** EP0256
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** solo founder-engineer whose stories are written by an agent
**I want** refine to produce a stakeholder consult, or a recorded reason it did not, before an epic leaves refine
**So that** intent is checked where a finding becomes a criterion rather than rework

## Acceptance Criteria

D1 settled where the consult runs: at refine, per epic or CR, before grooming. D0211 settled what
refine owes: a consult or a written skip, and this refusal is the ONLY gate in EP0256. The consult
itself is run by the agent, one persona per fresh context; refine's four jobs are to refuse a
decomposition that produced neither, to stamp the document with the units it minted, to refuse a
document that cannot show it ran outside this session, and to degrade to a recorded skip where no
personas exist. D3 - what the artefact must carry for the gate to count it - is OPEN, and this story
assumes the minimum US0840 reads: a `> **Units:**` line, one verdict row per persona, and one
context line per consulted persona. It checks those three and nothing else.

### AC1: apply refuses a decomposition that produced neither a consult nor a written skip, before it mints anything

- **Given** a fixture tree holding a refinable CR, three stakeholder persona cards under `sdlc-studio/personas/`, and a two-story breakdown file
- **When** `refine.py apply --request <CR> --epic-title "..." --breakdown <path>` runs through `main` with neither `--consult <path>` nor `--consult-skip "<reason>"`
- **Then** it exits 2, stderr names both exits, and the tree is untouched - no epic file, no story file, and no `Decomposed-into:` line on the request - the same fail-empty discipline refine already applies to an unresolvable `Affects`; the same invocation with `--consult-skip "the epic is repo-only tooling no persona reads"` exits 0 and writes that reason verbatim onto the epic as a `> **Consult:** skipped - <reason>` line
- **Mutant:** print the requirement as a warning and mint anyway - the epic exists, D0211's gate holds nothing, and the skip costs no reason
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::StakeholderConsultGateTests::test_apply_refuses_without_a_consult_or_a_written_skip

### AC2: the recorded artefact names the units the refine minted, and the epic points at it

- **Given** the same fixture and a consult document written over the request and its proposed breakdown, whose `> **Units:**` line names the request id alone
- **When** apply runs with `--consult <path>`
- **Then** it exits 0 and REWRITES that line to the ids it minted - the epic id then every story id, in mint order - and writes a `> **Consult:**` line on the epic naming the document's path; the agent's own unit list is overwritten, never merged, so no id the refine did not mint survives on it
- **Mutant:** record the path on the epic and leave the document's unit list as written - the artefact then names the request, and no later reader (US0839's trigger, US0841's close report, US0842's yield) can say which units a consult covered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::StakeholderConsultGateTests::test_apply_stamps_the_consult_with_the_units_it_minted

### AC3: a consult with no fresh-context provenance does not count as a consult

- **Given** two consult documents over the same request: one whose persona sections carry no per-persona context field, and one carrying a context line per consulted persona naming the isolated run each verdict came from
- **When** apply runs with `--consult <path>` on each, in fresh copies of the fixture
- **Then** the first exits 2, names the document and the personas whose context line is missing, gives the remedy, and mints nothing; the second exits 0 and mints - the paired positive control, so the refusal is the missing field and not the file
- **Mutant:** accept any readable document as a consult - the gate then passes when the session that has just written the stories answers as three hats in its own context, which is a machine for rubber-stamping at scale; `critic record` already refuses a verdict carrying no brief provenance for this reason
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::StakeholderConsultGateTests::test_a_consult_without_fresh_context_provenance_is_refused

### AC4: a project with no personas authored records a skip, never a refusal

- **Given** a fixture tree with no persona card under `sdlc-studio/personas/` - every project's first run - and the same request and breakdown
- **When** apply runs with neither `--consult` nor `--consult-skip`
- **Then** it exits 0, mints the epic and its stories, and writes the skip itself as `> **Consult:** skipped - no stakeholder personas authored`, so the skip is recorded rather than assumed; the only difference from AC1's refusing run is the persona directory
- **Mutant:** refuse whenever no consult document is given - a greenfield `init` then stops at a gate on an artefact the project cannot yet produce, and the first thing an adopter meets is a refusal they cannot satisfy
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::StakeholderConsultGateTests::test_no_personas_degrades_to_a_recorded_skip

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
