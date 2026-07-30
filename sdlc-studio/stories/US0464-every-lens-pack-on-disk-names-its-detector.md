# US0464: Every lens pack on disk names its detector or declares manual with a reason, the column is read by header name, and the detector set covers the runners this repo ships

> **Status:** Review
> **Delivers:** CR0435
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py, .claude/skills/sdlc-studio/templates/audit-profiles/code.md, .claude/skills/sdlc-studio/templates/audit-profiles/repo.md, .claude/skills/sdlc-studio/templates/audit-profiles/skill.md, .claude/skills/sdlc-studio/templates/audit-profiles/test.md, .claude/skills/sdlc-studio/templates/audit-profiles/process.md, .claude/skills/sdlc-studio/reference-audit.md, CHANGELOG.md
> **Epic:** EP0169
> **Points:** 8

## User Story

**As a** finder agent handed a lens
**I want** every lens in every pack file to name the detector I run first, or say plainly that none exists and why
**So that** I spend model tokens on what needs judgement and can tell a real detector from a hope

## Acceptance Criteria

### AC1: AC1: the signature column is resolved by header name, not position

- **Given** the packs as they stand at three, four and five columns, and a four-column pack whose Signature is fourth with no Drawn from column
- **When** each is parsed
- **Then** every one yields its signature in the `signature` field and none leaks it into `drawn_from`, so a pack gaining the column is not silently mis-parsed the way the current `cells[4]` read would do it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::SignatureColumnTests::test_the_signature_column_is_resolved_by_header_name
- **Verified:** yes (2026-07-30)

### AC2: AC2: the detector set covers the runners this repo actually ships

- **Given** signatures opening `python3`, `bash tools/lint-style.sh`, `rg`, and `npm run lint:links`, alongside one opening `manual`
- **When** each is classified
- **Then** the first four parse as mechanical with the runner's own path argument extracted per runner shape, and only the last is non-mechanical, so a lens whose real detector is `bash tools/lint-style.sh` is not forced to declare that no detector exists
- **And** `rg` and `npm run` are not added without a caller: no pack row on disk uses either today, so this story authors at least one real pack row per shape. A widened classifier whose only exerciser is its own unit test is the `over-engineering` lens pointed at this change.
- **And** the `npm run <script>` assertion is that the key exists in `package.json`'s **`scripts` object** - deterministic, and stronger than a path check, because it proves the thing a finder would actually type resolves. Looking the key up anywhere else in `package.json` would pass on a colliding top-level key.
- **And** `rg <pattern> [path...]` takes an **optional, repeatable** path after a pattern that may be quoted or contain spaces, so extracting "the path" from the string is undecidable. Rather than a third reported state, a mechanical signature must be **runnable as declared** and a pack row whose path does not resolve is refused at authoring time - so "unresolvable" never exists at read time. A state that is reported but not enforced is the class this sprint keeps finding.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::SignatureDetectorSetTests::test_every_shipped_runner_shape_classifies_as_mechanical_and_yields_its_path
- **Verified:** yes (2026-07-30)

### AC3: AC3: every lens of every pack file carries a signature, and the list is derived

- **Given** the pack profiles the resolver reports - `profile_names()` minus `REFERENCE_PROFILES`, so the two-column `project` reference section is out of scope by construction and not by omission
- **When** each is resolved and every lens inspected
- **Then** no lens has an empty signature cell, and the check iterates the resolver's own list, so a pack added later is held to the rule without anyone remembering to add it here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::SignatureCoverageTests::test_every_lens_of_every_pack_file_carries_a_signature
- **Verified:** yes (2026-07-30)

### AC4: AC4: a mechanical signature names a path that is on disk

- **Given** each lens whose signature classifies as mechanical, across all four runner shapes
- **When** the path extracted from the signature is resolved against the repo
- **Then** it exists, so a detector written from memory is caught here rather than by the finder who runs it and gets nothing
- **And** the rule lives in **shipped code** - `readiness.py`, beside the existing "declares no lens" refusal in `resolve_profile` - with the repo's unit test calling that, not restating it. `process.md`'s own Notes and `reference-audit.md` invite a consuming project to append pack rows "stating its own signature in the same way", and a consuming project never runs this repo's unit tests: a documented, shipped extension point whose contract is enforced only in `test_audit_profiles.py` is enforced nowhere for the people it is documented for.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::SignatureCoverageTests::test_every_mechanical_signature_names_a_path_on_disk
- **Verified:** yes (2026-07-30)

### AC5: AC5: an absent detector is declared in the documented form with a reason

- **Given** each lens whose signature is not mechanical, plus a bare dash and a one-word `manual` as negative cases
- **When** the cell is inspected
- **Then** it opens with the documented `manual` token and states why no search singles the class out, and both negative cases fail, so a blank cell cannot read as a considered declaration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_profiles.py::SignatureCoverageTests::test_a_non_mechanical_signature_uses_the_manual_form_with_a_reason
- **Verified:** yes (2026-07-30)

## Notes

**The bulk of this story is authoring 15 lens signatures, which the estimate did not price.** Only
`process.md` carries a Signature column today; `code.md`, `repo.md`, `skill.md` and `test.md` carry
4, 3, 4 and 4 lenses respectively, and every one needs either a resolvable on-disk path (AC4) or a
`manual - <real reason>` stating why no search singles the class out (AC5). Fifteen considered
judgements is the work here, not the parser change.

**`SIGNATURE_DETECTORS` must stay the single authority.** `process.md`'s Signatures section states in
prose that "the documented detector token is `python3`". Widening the code to four runners and leaving
that sentence is a doc that lies; hand-editing both creates a second copy to drift. The sentence is
derived from the constant, or this pack's own `count-by-hand` lens applies to this very change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
