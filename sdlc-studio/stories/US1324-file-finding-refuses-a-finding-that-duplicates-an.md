# US1324: file_finding refuses a finding that duplicates an artefact of its type, sharing every Affects path and scoring at or above the duplicate bar, before it mints an id, unless the filer names it with --distinct-from

> **Status:** Done
> **Risk-class:** elevated
> **Delivers:** CR0745
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/reference-scripts-create.md, changelog.d/US1324.md
> **Epic:** EP0378
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** file_finding refuses a finding that duplicates an artefact of its type, sharing every Affects path and scoring at or above the duplicate bar, before it mints an id, unless the filer names it with --distinct-from
**So that** CR0745 is delivered by work that can be planned and checked

## Acceptance Criteria

"Shares every Affects path" means every path the filer declared is also in the existing artefact's `Affects`, before the filer folds in any companion test. "The bar" is the duplicate lens's own: `artifact.duplicate_candidates`, `DUP_SHARED_AFFECTS_SIM` with `DUP_MIN_SHARED_TOKENS`, read from there and never restated in `file_finding.py`.

### AC1: A duplicate sharing every Affects path at or above the bar is refused before an id is minted

- **Given** a project holding a bug whose `Affects` is `src/thing.py` and whose title the lens scores at or above the bar against a new bug title, once with that bug Open and once with it Fixed
- **When** `file_finding.py file --type bug` files the new title with `--affects src/thing.py`, and again with `--dry-run`
- **Then** every run exits 1 with nothing on stdout (no `filed` and no `would file` line), and its stderr begins `file refused:` and names the existing bug's id, its status, the shared path, the lens score and `--distinct-from <that id>` as the way to file anyway; the bugs folder and its `_index.md` are byte-identical afterwards. Fails on: today's behaviour, `filed <id>` followed by a `warning: possible duplicate of` line and exit 0; a refusal raised after the write that leaves a file or an index row; a check scoped to open bugs that lets the Fixed one through
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DuplicateRefusalTests::test_a_full_affects_duplicate_is_refused_before_an_id_is_minted
- **Verified:** yes (2026-11-23)

### AC2: --distinct-from files the finding and records the ruling on it

- **Given** the AC1 project and pair, with the existing bug Open
- **When** the new title is filed with `--distinct-from <existing id>`, and again from a `--fields-file` document carrying `"distinct_from": "<existing id>"`
- **Then** each exits 0, prints `filed <new id> -> <path>`, and the new artefact's metadata block carries `> **Distinct-from:** <existing id>`. Fails on: a flag that parses and is then dropped by the CLI's hand-enumerated flag dict, so the filing succeeds with no record of the ruling; a document key refused as unknown, so the shell-free path cannot rule at all
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DuplicateRefusalTests::test_distinct_from_files_and_records_the_ruling
- **Verified:** yes (2026-11-23)

### AC3: --distinct-from does not unlock a filing it does not rule on

- **Given** the AC1 pair, plus a second, unrelated bug in the same project
- **When** the new title is filed with `--distinct-from` naming the unrelated bug, and again naming an id that resolves to no artefact
- **Then** the first exits 1 with the AC1 refusal naming the duplicate it left unanswered, the second exits 1 with `file refused:` naming the id that does not resolve, and neither writes a file. Fails on: `--distinct-from` read as a bypass switch whatever id it names; a ruling recorded against an artefact that does not exist
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DuplicateRefusalTests::test_distinct_from_naming_another_or_no_artefact_still_refuses
- **Verified:** yes (2026-11-23)

### AC4: The refusal reads the declared paths and the lens's bar, at or above

- **Given** an existing bug sharing every declared Affects path, with one new title the lens scores exactly at `DUP_SHARED_AFFECTS_SIM` and one it scores just below it while sharing at least `DUP_MIN_SHARED_TOKENS` words; and a third new finding declaring `src/thing.py`, whose existing companion test `tests/test_thing.py` the filer folds into its Affects, against an existing bug at or above the bar that names `src/thing.py` alone
- **When** each is filed through `file_finding.py file`
- **Then** the title at the bar exits 1 refused, the title just below exits 0 with `filed <id> -> <path>` and no duplicate line, and the third exits 1 refused. Fails on: `>` where the rule says at or above; a second bar hard-coded in `file_finding.py` that drifts from the lens; a refusal keyed on shared Affects alone; an overlap judged on the completed Affects, so the companion test the tool added lets every older duplicate through
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DuplicateRefusalTests::test_the_refusal_reads_declared_paths_and_the_lens_bar_at_or_above
- **Verified:** yes (2026-11-23)

### AC5: A partial overlap, or no Affects at all, keeps today's warning

- **Given** an existing bug at or above the bar that names one of the new bug's two declared paths, and an existing CR whose title the lens scores at or above its title-only bar against a new CR, neither CR declaring an `Affects`
- **When** each new finding is filed through `file_finding.py file`
- **Then** each exits 0, prints `filed <id> -> <path>` and then the `warning: possible duplicate of <existing id>` line it prints today. Fails on: a refusal on any shared path; an every-path test that reads an empty `Affects` as sharing every path, so every Affects-less CR with a similar title is refused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DuplicateRefusalTests::test_a_partial_or_absent_affects_overlap_still_only_warns
- **Verified:** yes (2026-11-23)

### AC6: A machine caller of the library filer is not refused

- **Given** the AC1 pair
- **When** `file_finding.file_finding()` is called the way `critic.py`'s review-cap carry and `gate.py`'s red-main regression filer call it, with no override argument
- **Then** it returns the new id with `duplicate_warnings` naming the existing bug, as it does today. Fails on: the refusal placed inside the library function, where no filer is present to rule: `critic.py` re-carrying a unit files the same title over the same `Affects` (BG1682 and BG1703 are that pair for BG1534), so the second carry would raise and stop the close; and `command_audit.py`'s coverage filer, whose second finding in one run scores 0.67 against its first over the same `Affects` (`test_command_audit.py::CoverageFindingTests::test_the_first_run_files_and_the_second_adds_nothing` exercises it), would raise mid-run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::DuplicateRefusalTests::test_the_library_filer_still_files_and_warns
- **Verified:** yes (2026-11-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-23 | Claude Opus 5.5 (run twenty-three qa seat) | Groomed: authored six criteria with Verify lines, each premise run at HEAD 17dc7829; Affects widened to the reference page and this unit's fragment |
