# US1080: A unit is minted against the Primary of the interface its Affects touches, read from interface paths the project declares

> **Status:** Ready
> **Delivers:** CR0648
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/templates/personas/persona-template.md, tools/tests/test_persona_coherence.py, changelog.d/US1080.md
> **Epic:** EP0289
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor, minting a unit in a project whose registry has a Primary for each interface
**I want** `artifact.py new` and `batch` to mint a unit against the Primary of the interface its Affects touches, read from the interface paths each Primary's card declares
**So that** a unit is judged from its first review by the persona it serves, with no repoint between builds

## Acceptance Criteria

- **AC1:** Given a fixture cast of two Primary cards whose `Interface` rows declare `` `a/` `` and `` `b/` ``, when `artifact.py new --type story` mints with no `--persona` and Affects wholly under `b/` beside a `changelog.d/` fragment, then the minted Persona is the `b/` Primary, and with Affects wholly under `a/` it is the `a/` Primary; `batch` mints the same
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::InterfacePersonaMintTests::test_affects_wholly_in_one_interface_mints_its_primary
- **AC2:** Given the same cast, when the Affects touches both declared interfaces, or neither, then the Primary listed first in the persona index is minted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::InterfacePersonaMintTests::test_a_mixed_or_undeclared_affects_mints_the_first_primary
- **AC3:** Given an explicit `--persona`, when `new` or `batch` mints, then that persona is minted whatever the Affects
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::InterfacePersonaMintTests::test_an_explicit_persona_always_wins
- **AC4:** Given a one-Primary cast, when any Affects is minted, then the Persona is the one minted today; given two Primaries and no `Interface` row, then the first Primary is minted, stderr names the missing interface declaration, and the mint succeeds
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::InterfacePersonaMintTests::test_a_cast_without_interfaces_mints_as_before_and_warns_on_two_primaries

## Notes

- Serves: Maya Okafor, End goal 3 (no repoint between builds; run two repointed eight units by hand, D0380).
- Delivers CR0648's mint default (EP0289:28, D0379). The consult (rec 3) fixed the shape: interfaces are project data, the cards' `Interface` rows, never paths written into shipped code; with none declared, today's behaviour holds; two Primaries with none declared warn and never refuse; paths in no declared interface (a changelog fragment, workspace artefacts) do not decide; the default applies at mint only.
- A mixed unit takes the first Primary in index order, which this project lists as the shipped skill's (the consult's arbitration: the shipped Primary governs).
- AC1 must fail on: the interface paths hard-coded, so fixture paths `a/` and `b/` are not recognised.
- AC2 must fail on: a mixed unit minted against the last-matched Primary.
- AC3 must fail on: the interface default applied over an explicit `--persona` on `batch`.
- AC4 must fail on: a two-Primary cast with no interfaces refused, or minted silently.
- Today `_resolve_persona` (artifact.py:282) takes no Affects; both callers (`new` :1140, `batch` :1306) have it. `test_persona_coherence.py` pins the pre-US1080 default (`test_an_unnamed_mint_still_defaults_to_the_shipped_skills_primary`, 'until US1080') and changes with it. `reference-persona.md` and the template's `Interface` placeholder say how the row is read.
- Re-estimated from 2 to 3 points at grooming: the help, the reference page, the template and the coherence pin move with the code.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | sdlc-studio | Retitled: was "A unit whose Affects is wholly repository tooling is minted against the tooling interface's Primary by default" |
