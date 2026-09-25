# US0940: Every criterion on a Done story passes when the release gate runs it, or is retired with its reason

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories/US0021-rfc-decide-session.md, sdlc-studio/stories/US0040-index-archive-writer-terminal-status-vocab-flag-dry.md, sdlc-studio/stories/US0042-retro-hard-close-gate-sprint-close-fails-loud.md, sdlc-studio/stories/US0047-restore-the-runtime-scripts-coverage-gate-to-green.md, sdlc-studio/stories/US0052-runner-bridge-and-mutation-report-killed-vs-survived.md, sdlc-studio/stories/US0063-consolidated-audit-check-command-over-the-team-schema.md, sdlc-studio/stories/US0070-review-generate-command-with-remediation-only-security-posture.md, sdlc-studio/stories/US0080-code-quality-debt-docstrings-dedup-format-json-complexity.md, sdlc-studio/stories/US0162-drop-the-interactive-equals-unmeasured-language-for-not.md, sdlc-studio/stories/US0165-gate-grows-an-auto-detecting-close-owed-lane.md, sdlc-studio/stories/US0178-migrate-the-amigo-cast-to-personas-seats-and.md, sdlc-studio/stories/US0202-add-the-shipped-done-epics-ep0033-ep0047-to.md, sdlc-studio/stories/US0207-mark-rfc0034-superseded-by-rfc0038-cross-link-both.md, sdlc-studio/stories/US0211-refresh-or-band-the-trd-pinned-census-counts.md, sdlc-studio/stories/US0224-draw-the-report-in-the-close-ceremony-when.md, sdlc-studio/stories/US0251-command-audit-drift-back-to-0-and-check.md, sdlc-studio/stories/US0268-order-the-pre-commit-lanes-cheapest-first-so.md, sdlc-studio/stories/US0284-test-gate-s-two-real-wrapper-tests-share.md, sdlc-studio/stories/US0289-backfill-the-velocity-record-from-retro0029-marking-unmeasurable.md, sdlc-studio/stories/US0347-version-bump-to-5-0-0-across-authoritative.md, sdlc-studio/stories/US0512-a-unit-adding-a-mechanism-carries-an-acceptance.md, sdlc-studio/stories/US0666-the-rehearsal-runs-as-a-gate-lane-at.md, sdlc-studio/stories/US0854-decompose-the-four-8-point-stories-and-resolve.md, tools/verify-corpus-baseline.txt, tools/tests/test_lean_release_verify.py, changelog.d/US0940.md
> **Epic:** EP0265
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer cutting v6.0.0
**I want** the 27 criteria on Done stories that fail when executed today repaired, or retired in the D0259 pattern where the behaviour they pinned was deleted on purpose
**So that** the release gate's verify lane is green without a ruling that tolerates red evidence, and the gate leaves the tree it judged unchanged

## Acceptance Criteria

- **AC1:** Given the 27 criteria on Done stories that `gate.py --release` reports red at 013a46d0 (US0021::AC1, US0040::AC3, US0042::AC2, US0047::AC1, US0052::AC4, US0063::AC1, US0063::AC2, US0070::AC1, US0070::AC2, US0080::AC2, US0165::AC2, US0202::AC3, US0207::AC3, US0268::AC1, US0284::AC4, US0289::AC2, US0347::AC1, US0512::AC4, US0666::AC1, US0162::AC1, US0178::AC3, US0211::AC3, US0224::AC1, US0224::AC2, US0251::AC2, US0268::AC3, US0854::AC1), when each is executed through `verify_ac`, then each passes or carries `Verify: manual - retired by <this unit>: <why>` with its `Verified:` line in the D0259 pattern, and `tools/verify-corpus-baseline.txt`'s red-criteria row names none of them. Fails on: HEAD (27 red, measured: 19 in the v5.1 baseline, 8 new since); retiring a criterion whose behaviour still ships, which the reviewer checks by re-running the retired selector's intent against HEAD
  - **Verify:** pytest tools/tests/test_lean_release_verify.py::ReleaseVerifyTests::test_the_measured_red_criteria_pass_or_are_retired
- **AC2:** Given US0251 AC2, whose Verify runs `command_audit.py --write`, when it runs in a clean clone, then `git status --porcelain` is empty afterwards, and no Verify line on a Done story passes `--write` or `--apply` to a shipped script. Fails on: HEAD, where the release gate's verify lane rewrites the tracked `sdlc-studio/reviews/command-audit.md` (measured on a copy), so `record-green` would stamp a tree that differs from the commit
  - **Verify:** pytest tools/tests/test_lean_release_verify.py::ReleaseVerifyTests::test_no_verify_line_writes_a_tracked_file

## Notes

Wave 5 (file-disjoint from the EP0263 code units; it edits old artefacts' stamps and one baseline). Measured by running `gate.py --release` on a copy of 013a46d0 (1,542 s) and re-running each copy-only red in the real tree: US0357/US0358 (markdownlint), US0253 AC2 and the US0916/US0917/US0935 stamp tests pass in the real tree and are excluded. The 8 new reds: US0162 AC1, US0178 AC3 (its grep for 'retired' now matches the lean charter's own words), US0211 AC3 (TRD text cut by US0933), US0224 AC1/AC2 (test classes deleted without retiring the stamps), US0251 AC2, US0268 AC3 (hook string gone), US0854 AC1 (backlog_triage now flags US0914 and US0936 as oversized). AC1's test must never run the corpus lane itself (a criterion that runs every criterion recurses); it runs only the 27 named. US0047 AC1 and US0080 AC2 run the whole suite, so expect them retired or narrowed. If the operator rules the 19 old reds again as at v5.1 (D0186), AC1 narrows to the 8 new and the size drops to 2. Ratchet: the static `--write/--apply` scan in AC2 names its yield, the one writer found today; the baseline row already reddens both ways.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (NEW-D) |
