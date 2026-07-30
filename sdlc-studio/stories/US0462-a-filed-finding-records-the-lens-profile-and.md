# US0462: A filed finding records the lens, profile and a resolvable audit run, validated against a register that has a real writer

> **Status:** Review
> **Delivers:** CR0435
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_audit_cost.py, .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/help/audit.md, .claude/skills/sdlc-studio/reference-scripts.md, CHANGELOG.md
> **Epic:** EP0169
> **Points:** 3

## User Story

**As an** audit filer closing out a run
**I want** each finding stamped with the lens, profile and a run id that resolves against a recorded register
**So that** a class recurring across runs can be counted mechanically instead of being defeated by a typo or recognised by whoever remembers the last run

## Acceptance Criteria

### AC1: AC1: lens, profile and run are stamped as readable metadata

- **Given** `file_finding.py file --lens accepted-without-running --profile process --audit-run <recorded id>`
- **When** the finding is filed
- **Then** the artefact carries all three as metadata fields beside the existing provenance stamp, readable without parsing the `Raised-by` prose the 108 existing findings hide the run in
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditAttributionTests::test_lens_profile_and_run_are_stamped_as_metadata
- **Verified:** yes (2026-07-30)

### AC2: AC2: a lens or profile no pack declares is refused before an id is minted

- **Given** a `--lens` name the named profile's pack does not carry, and separately a `--profile` no pack declares
- **When** filing is attempted
- **Then** each is refused by name listing what the resolver does declare, and nothing is minted - no id consumed, no index row written, matching how `check_mutation_run` refuses an unresolvable run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditAttributionTests::test_an_undeclared_lens_or_profile_is_refused_before_an_id_is_minted
- **Verified:** yes (2026-07-30)

### AC3: AC3: an audit run the register does not hold is refused before an id is minted

- **Given** an `--audit-run` id absent from the recorded audit-run register - the **git-tracked** `audit-cost` ledger under `sdlc-studio/retros/evidence/`, which `audit_cost.py record` already appends one row per finished audit run to, extended with a `run_id` field
- **When** filing is attempted
- **Then** it is refused by name pointing at the register path, and nothing is minted, so a one-character typo cannot manufacture a second distinct run id and with it a false detector-owed verdict
- **And** the register is **not** placed at `mutation.series_path`'s location: that path is `sdlc-studio/.local/`, which `.gitignore` excludes, so on any other clone the register would be empty while the findings stayed tracked - every `--audit-run` refused and `detector-owed` reporting cannot-judge for the whole corpus, permanently, everywhere but the machine that wrote it. The mutation series' **shape** is mirrored; its path is not.
- **And** a row records its provenance as `recorded` (written by `record` at close-out) or `backfilled` (asserted from prose), mirroring `mutation.PROVENANCE_REGISTERED`, so five unverifiable prose strings are never laundered into the authority AC1 reads as a distinct registered run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditRunRegisterTests::test_an_unregistered_run_id_is_refused_before_an_id_is_minted
- **Verified:** yes (2026-07-30)

### AC4: AC4: half an attribution is refused, and the derivable third is derived rather than demanded

- **Given** `--lens` supplied with no `--audit-run`, and `--audit-run` with no `--lens`
- **When** filing is attempted
- **Then** both are refused explaining that a class is counted per run, so a half-stamped finding that could never participate in the comparison is never created
- **And** a filing carrying **none** of the three still succeeds, because 923 existing findings carry none and must stay legal - the rule is all-or-none, never some
- **And** `--profile` is **optional and derived** from the lens rather than demanded: a lens name resolves to exactly one pack across `profile_names()` (verified - `accepted-without-running` occurs in one pack only), so requiring it is input the operator can get wrong. When supplied it is cross-checked and a lens/profile **mismatch** is refused, which is strictly stronger than all-three-or-none: that rule accepts a consistent-looking pair naming the wrong pack.
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditAttributionTests::test_a_lens_without_a_run_or_a_run_without_a_lens_is_refused
- **Verified:** yes (2026-07-30)

### AC5: AC5: the flags reach the command an operator actually types

- **Given** `main(["file", ...])` invoked with the new flags - the argparse surface, not the `file_finding()` function a test can call directly
- **When** a finding is filed
- **Then** the attribution is stamped, because `cmd_file` builds its `flags` dict by hand-enumerating every key: a new argparse flag absent from that dict is parsed and silently dropped, the filing succeeds unattributed, and every AC above still passes when tested against the function
- **And** `lens`, `profile` and `audit_run` are added to `FIELDS_FILE_KEYS`, since `load_fields_file` **raises** on any key outside that allowlist - and `--fields-file` is the path that does not cross a shell, so it is the one a prose-heavy audit finding must use
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditAttributionTests::test_the_flags_reach_the_cli_and_the_fields_file_path
- **Verified:** yes (2026-07-30)

## Notes

**The 108-artefact backfill was AC5 and is now its own unit.** It is a migration over git-tracked
artefacts across **five** run ids, not three, and it was self-contradicting as written: the sweep
"no artefact carries a run id in prose that is absent from its metadata field" **fails** on the real
corpus when the register is seeded with the three named ids, because `wf_b62b2ed2` (BG0375, BG0376,
BG0377) and `wf_95377bad` (BG0379) carry only unnamed ones.

Its stated rationale was also falsified by its own mechanism: `detector-owed` groups by **lens**, the
backfill supplies **run ids**, and `Raised-by` prose carries no lens - so the entire backfilled corpus
lands in cannot-judge, which is the state the AC claimed it would move the corpus out of. Deriving 108
lenses is model judgement over 108 artefacts, not a mechanical backfill, and it is priced accordingly
rather than hidden inside a 3-point story.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
