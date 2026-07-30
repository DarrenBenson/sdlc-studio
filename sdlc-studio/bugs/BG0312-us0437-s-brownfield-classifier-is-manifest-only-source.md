# BG0312: US0437's brownfield classifier is manifest-only: source without a manifest classifies greenfield, and the verifier canno

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0
> **Audit-lens:** unknown
> **Audit-run:** wf_804ef18d

## Summary

AC2 promises brownfield for a repo 'that already contains source', but `classify_path` keys entirely off six manifest markers plus *.csproj, so a source-full repo without one (C/C++, Ruby, PHP, setup.py-only Python) classifies greenfield; the dedicated verifier only exercises pyproject.toml so it can never fail on the AC's own Given, and US0439's PRD stage then directs a real brownfield repo to the greenfield interview - the exact wrong fork the guided flow exists to avoid.

## Steps to Reproduce

Evidence (`classify_path`/`detect_stack`, lines 41-43, 77-83, 179-183; US0437 AC2 (line 30); `test_init.py`:312-318): init.py:183 'return "brownfield" if `detect_stack(...)` else "greenfield"' over the DETECT marker list only; reproduced: a repo with src/main.c and setup.py returns greenfield; the Verify test writes only pyproject.toml for its brownfield case.

## Proposed Fix

Add a fallback source-file census (extension scan) to `classify_path` when no manifest is found, and add a manifest-less brownfield case to GuidedInitTests so the AC's stated Given is actually exercised.

## Acceptance Criteria

### AC1: a repo that already contains source classifies brownfield without a manifest

- **Given** a tree with source and no recognised manifest marker - C with a header, Ruby, PHP, or a
  Python project carrying only `setup.py` - so `detect_stack` returns None
- **When** `classify_path` runs
- **Then** it answers brownfield, because the question the AC asks is whether the repo contains
  source, not whether it carries one of six manifests this skill happens to recognise
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_source_without_a_recognised_manifest_classifies_brownfield

### AC2: the classification reaches the fork it exists to drive

- **Given** a manifest-less C repo being onboarded
- **When** `start_onboarding` then `stage_prd` run
- **Then** both report the brownfield path and the directive says `prd generate`, never `prd create`
  - the PRD comes from the code instead of the operator being interviewed about a repo that exists
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_a_manifest_less_source_repo_is_sent_down_the_brownfield_prd_fork

### AC3: the census does not fire on non-source or on somebody else's code

- **Given** a repo holding only markdown, text and its own `sdlc-studio/` tree, and separately a repo
  whose only code sits under `node_modules/`, `.git/`, `.venv/` or `dist/`
- **When** `classify_path` runs
- **Then** both answer greenfield, so `init` writing its own documents cannot flip the classification
  and a vendored or built tree is never mistaken for this project's source
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_docs_and_derived_directories_do_not_make_a_repo_brownfield

### AC4: US0437's own verifier can now fail on its criterion's Given

- **Given** US0437 AC2, whose Given is a repo that already contains source
- **When** the verifier that criterion names runs
- **Then** it exercises a manifest-less source repo as well as a manifest one, so the case that was
  actually broken lives in the criterion's own verifier rather than only in a sibling test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::GuidedInitTests::test_classifies_greenfield_and_brownfield

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
| 2026-07-28 | delivery lane (RUN-01KYJZGZ) | Acceptance criteria authored; source-file census added to `classify_path` |
