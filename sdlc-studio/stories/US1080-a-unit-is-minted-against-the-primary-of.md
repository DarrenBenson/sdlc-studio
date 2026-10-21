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

- **AC1:** Given a fixture cast of two Primary cards whose `Interface` rows each declare several paths in prose, as this repository's tooling card does, when `artifact.py new --type story` mints with no `--persona` and Affects wholly under one card's paths beside a test module and a `changelog.d/` fragment, then the minted Persona is that card's Primary, for each card; `batch` mints the same
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::InterfacePersonaMintTests::test_affects_wholly_in_one_interface_mints_its_primary
- **AC2:** Given the same cast, when the Affects touches both declared interfaces, or neither, or reaches one only through test modules and changelog fragments, then the Primary listed first in the persona index is minted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::InterfacePersonaMintTests::test_a_mixed_or_undeclared_affects_mints_the_first_primary
- **AC3:** Given an explicit `--persona`, when `new` or `batch` mints, then that persona is minted whatever the Affects
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::InterfacePersonaMintTests::test_an_explicit_persona_always_wins
- **AC4:** Given a one-Primary cast, when any Affects is minted, then the Persona is the one minted today; given two Primaries and no `Interface` row, then the first Primary is minted, stderr names the missing interface declaration, and the mint succeeds
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::InterfacePersonaMintTests::test_a_cast_without_interfaces_mints_as_before_and_warns_on_two_primaries
- **AC5:** Given this repository's own cards, when a story is minted dry-run with no `--persona`, then Affects wholly under `.githooks/` mints Rowan Achterberg and Affects under `.claude/skills/sdlc-studio/` mints Maya Okafor
  - **Verify:** pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests::test_a_mint_follows_the_live_interface_rows

## Notes

- Serves: Maya Okafor, End goal 3 (no repoint between builds; run two repointed eight units by hand, D0380).
- Delivers CR0648's mint default (EP0289:28, D0379). The consult (rec 3) fixed the shape: interfaces are project data, the cards' `Interface` rows, never paths written into shipped code; with none declared, today's behaviour holds; two Primaries with none declared warn and never refuse; paperwork does not decide, so a unit's test modules (`file_finding.is_test_path`) and changelog fragments are set aside; the default applies at mint only. A mixed unit takes the first Primary in index order, which this project lists as the shipped skill's.
- AC1 must fail on: the interface paths hard-coded; a row's second and third paths ignored.
- AC2 must fail on: a unit's own test module deciding its persona (US1081's `tools/tests/` test would mint Rowan for a registry change); a mixed unit minted against the last-matched Primary.
- AC3 must fail on: the interface default applied over an explicit `--persona` on `batch`.
- AC4 must fail on: a two-Primary cast with no interfaces refused, or minted silently.
- AC5 must fail on: the live tooling row's prose read as one path.
- Today `_resolve_persona` (artifact.py:282) takes no Affects; both callers (`new` :1140, `batch` :1306) have it. `test_persona_coherence.py` pins the pre-US1080 default ('until US1080') and changes with it. Re-estimated from 2 to 3 points at grooming. Goal review, 2026-10-21 (engineering, product and qa seats) added the multi-path fixture, the test-module rule and AC5.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | sdlc-studio | Retitled: was "A unit whose Affects is wholly repository tooling is minted against the tooling interface's Primary by default" |
| 2026-10-21 | Claude Opus 5.5 | Regroomed on the run-three goal review's two rounds (engineering, product and qa seats; D0384) |
