# BG0446: a fenced markdown example holding an unquoted Status line drops a spec as a version home and silently swallows its real version drift

> **Status:** Fixed
> **Severity:** Critical
> **Points:** 2
> **Affects:** tools/check_versions.py, tools/tests/test_check_versions.py
> **Evidence:** Severity is Critical because of what this guard is for. `check_versions` is a release gate: it is the thing that stops a version-drifted tree being tagged. The failure is silent and exit 0, it is triggered by ordinary technical writing rather than by anything that looks like tampering, and it targets precisely the documents most likely to contain an artefact-header example - the PRD, TRD and TSD, which are three of the seven version homes it checks.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** round-2 spec-guard reviewer (independent, isolated worktree), mechanism corrected by author; agent; v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`check_versions._is_superseded` reads a file's first 4000 characters, skips blockquoted lines, and returns on the first non-quoted `**Status:**` it finds. It has no notion of a fenced code block. A spec that DOCUMENTS an artefact header - showing `**Status:** Superseded` inside a fenced markdown example, which is ordinary technical writing and which these specs already do - is read as declaring ITSELF superseded. The file is then dropped as a version home, and any real version drift it carries goes with it. The guard exits 0 and prints that versions are consistent. The code's own comment shows the author reasoned about exactly this class and closed only the blockquoted half of it.

## Steps to Reproduce

Executed at d7a1ad8f, 2026-07-30, as a control pair against the live `sdlc-studio/tsd.md`, restored byte-identical afterwards.

CONTROL - real drift, nothing else changed. Set the Version home to a wrong value, then run the guard:

```text
sdlc-studio/tsd.md:  > **Version:** 5.0.0   ->   > **Version:** 1.2.3

$ python3 tools/check_versions.py
exit=1, and the output names sdlc-studio/tsd.md=1.2.3
```

MUTANT - the SAME drift, plus a fenced markdown example inserted near the head of the
file. The fence below is shown with a leading dot on its markers so it can be quoted here;
in the real file they are ordinary backtick fences:

```text
.```markdown
**Status:** Superseded
.```

$ python3 tools/check_versions.py
exit=0, and tsd.md is not named at all
```

The drift is identical in both runs. Only the presence of a documentation example changes the verdict, and it changes it from caught to clean.

Note on the mechanism, because the first two reproduction attempts FAILED and the distinction matters for the fix: the Status line inside the fence must be UNQUOTED. A `> **Status:** Superseded` inside a fence is correctly skipped by the existing blockquote guard, so the obvious spelling of the attack does not work and an inattentive check would wrongly refute this bug.

Found by the round-2 spec-guard reviewer (independent, isolated worktree). Its stated reproduction used the quoted form and does NOT reproduce; the finding is real but its mechanism is restated here from the author's own control pair.

## Proposed Fix

Strip fenced code blocks before scanning for the document's own status, exactly as the blockquote form is already skipped. Both are the same class - a line that is displayed rather than asserted - and the comment above the loop already articulates the principle ('a quoted header describes something else'); a fenced header describes something else for identical reasons.

Pin it with a control pair rather than a single assertion: a test that a spec carrying real version drift AND a fenced artefact-header example is still reported. A test asserting only that the fenced example is ignored would pass over a guard that ignores everything.

While there: `from_spec` reads the same 4000-character head with the same fence-blindness, so a fenced `**Version:** 9.9.9` example is a candidate for the mirror-image defect - a documentation example being read as the file's real version. Check it in the same slice.

> **Verification depth:** functional - proven by a control pair executed against the live tsd.md and pinned as a fixture: identical drift, exit=1 without the example and exit=0 with it before the fix, exit=1 in both after. Three mutants KILLED, including a straight revert.

## Acceptance Criteria

### AC1: a fenced Status example no longer drops a version home or hides its drift

- **Given** a spec carrying real version drift, once with and once without a fenced artefact-header example in its head
- **When** check_versions runs over each
- **Then** both report the drift - asserted as a control pair, because the drift is identical in both halves and only the example differs; without the control half a guard that had stopped checking anything would also pass
- **Verify:** pytest tools/tests/test_check_versions.py::DiscoveredHomesTests::test_a_fenced_status_example_does_not_drop_a_home_and_hide_its_drift
- **Verified:** yes (2026-07-30)

### AC2: a fenced Version example is not read as the document's own version

- **Given** a spec whose head documents an artefact header showing a different version
- **When** from_spec reads it
- **Then** the document's real version is returned - the mirror image of the same defect, milder because it reports a wrong version rather than dropping a home, closed in the same place rather than left for the next reviewer
- **Verify:** pytest tools/tests/test_check_versions.py::DiscoveredHomesTests::test_a_fenced_version_example_is_not_read_as_the_documents_version
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | round-2 spec-guard reviewer (independent, isolated worktree), mechanism corrected by author | Filed |
