# BG0463: Twenty non-blocking findings from the RUN-01KYTKA1 batch-boundary review: stale counts, dead code, unmarked truncation, over-claiming docstrings and three tests whose names promise more than they assert

> **Status:** Closed
> **Severity:** Medium
> **Closed because:** CLOSED, residue re-filed. Unbuildable as written: `verify_ac.py testplan derive --unit BG0463` refuses with "the plan would carry 0 row(s) for 4 criterion/criteria" because its items are bare `- [ ]` with no `**ACn**` ids, so no test plan can be derived and no terminal gate can read it. It is the oldest unit in the backlog, carries no re-measurement unlike its siblings BG0490 and BG0493, and is partly delivered already. Its `Affects` also welds critic.py, sprint_report.py and lib/sdlc_md.py into a single 20-point atomic block, which is a planning cost paid for a unit nobody can size. Twenty findings from a 2026-07 batch-boundary review: re-filed as one groomed unit for re-triage rather than carried as an unbuildable aggregate.
> **Points:** 5
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/critic.py, tools/check_spec_claims.py, tools/check_script_tests.py, tools/tests/test_check_versions.py, tools/tests/test_porting_doctrine.py, sdlc-studio/tsd.md, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, tools/tests/test_check_spec_claims.py, tools/tests/test_check_script_tests.py
> **Evidence:** Independent adversarial review of RUN-01KYTKA1, seven tranches, three seats, isolated worktrees. Every item below was reported as explicitly NON-blocking by the seat that found it.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The residue of the batch-boundary review: real defects that no reviewer judged worth holding a unit for. Collected as one carried unit so none is lost, and so the next sprint prices them together rather than rediscovering them one at a time.

Stale countable claims, each gating nothing: `DRIFT_KINDS (14 entries)` and a changelog's "a tuple of 17" against an actual 19; "33 today" against 53 `tools/tests` modules; "all seven close steps" in four places against a ten-step chain; "three of the chain's steps exist to DO something" against five writers; US0465 AC5's sixteen offenders against eleven stories plus one CR actually swept, with EP0010 a declared false positive and five named paths never touched.

Dead or unreachable code: `_RESOLVED_Q_RE` defined and never referenced, so the "moved under Resolved Questions" route works only by omission from the open-questions pattern; `_FENCE_RE` with a single self-reference, while `claims_in()` reads raw text, so a fenced or historical band is reported as a live claim; a blockquote skip in `check_versions.py` made unreachable by the repair beside it; `cycle_drift(root=...)` accepting a parameter it never reads.

Unmarked truncation: drops render `bits[:12]` and covered units `covered[:6]`, both with no "(+N more)" marker, while the sibling scope-creep row appends one. A silent cap reads as "that is all there was".

Over-claiming prose: `check_versions.py`'s "exactly five places"; a test docstring giving a run command that collects zero tests; a "six parents up" comment over `parents[1]`; `authority` as a decorative field no code reads; two spellings of the stop-ship constant; `NON_CEREMONY_VERBS` as a second hand-maintained list already carrying a stale entry.

Contract drift: on a project declaring no personas every reviewer renders "NO DECLARED SEAT", contradicting `seat_for`'s own documented contract that callers distinguish that from a seat-less reviewer; `check_script_tests.py` sweeps `scripts/` and `scripts/lib/` but not `scripts/hooks/`, currently benign; US0455's declared Affects omits a file its commit changed.

Missing regression cover: the batch-level reviewer contribution a comment calls load-bearing is asserted nowhere; the no-op-add carve-out has none; a stop-ship ruling on an already-Fixed finding blocks the close permanently; a US0576 fixture exercises a state the writer cannot produce.

## Steps to Reproduce

Each item was established by execution during the review - census, mutation or direct probe - and is recorded with its file and line in the seat reports for RUN-01KYTKA1. Representative measurements:

```text
DRIFT_KINDS            : claimed 14 / 17, actual 19
tools/tests modules    : claimed 33, actual 53
_CLOSE_CHAIN           : claimed 7, actual 10
_FENCE_RE              : 1 occurrence, its own definition
_RESOLVED_Q_RE         : 1 occurrence, its own definition
cycle_drift(root="/nonexistent") == cycle_drift(None)
grep '["authority"]' scripts/*.py -> no match outside the test
```

## Proposed Fix

Take them as one grooming pass rather than twenty. The counts want deriving, not correcting - each was true when written and none has a guard, which is why they drifted. The dead patterns want deleting with a note on what actually implements the route. The truncations want the marker the sibling row already has.

## Acceptance Criteria

- [ ] Every stale countable claim listed is either derived from the thing it counts or removed, so it cannot drift again silently
- [x] Every dead pattern listed is deleted, with the mechanism that actually implements its route named where it stood
- [x] Both truncated renders carry a `(+N more)` marker, matching the sibling row that already does
- [ ] Each over-claiming docstring and comment states what the code does, and the three tests whose names promise more than they assert are either strengthened to match their names or renamed to match their assertions

## Re-triage against HEAD, 2026-09-21 (RUN-01M306PY, US0853)

**There are TWENTY-FOUR claims here, not twenty.** They are stated as semicolon-separated clauses
inside five prose paragraphs, and everything that has ever counted them - including this
artefact's own summary and the request that asked for the re-triage - counted paragraphs or
bullets. That is the first finding of the re-triage, and it is the same defect that closed this
bug as unbuildable: prose that cannot be addressed one claim at a time cannot be delivered,
counted or verified.

Each claim was re-read and re-executed against HEAD. The outcome:

| Ruling | Count | Claims |
| --- | --- | --- |
| still true | 15 | 2, 3, 4, 7, 8, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23 |
| already fixed | 5 | 1, 6, 9, 10, 12 |
| never was a defect | 1 | 11 |
| unfalsifiable as written | 3 | 5, 22, 24 |

The five already fixed were closed by other work and each names it: claim 1 by US0458, claims 6,
9 and 10 by commit `0d99b0f5` (which was itself filed against this bug), claim 12 by `e3b6272d`
under BG0578/BG0490. Claim 11 was mistaken when written - the `(+N more)` marker it says is
missing is present at `sprint_report.py:1971-1973` and `git log -S` shows it was never absent;
this bug's own 2026-08-05 revision had already reached that conclusion.

The three unfalsifiable ones are not judgements deferred, they are claims that cannot be tested
as written: claim 5 counts an offender population that has since been swept out of existence,
and claims 22 and 24 name a carve-out and a fixture without naming the file, symbol or field, so
neither can be located. Each needs its subject named before it can be ruled, and none should be
carried forward as a bullet.

Two survivors are worth naming here because they are defects in the machinery rather than in
prose. Claim 7: `check_spec_claims.claims_in()` reads raw text while `_FENCE_RE` sits unused, so
a claim inside a fenced code block is read as a live claim - confirmed by execution. Claim 23: a
stop-ship ruling is never re-derived against its finding's current status, so a ruling on a
finding that has since been Fixed blocks every close, permanently.

### The twenty-four claims, ruled individually

One ruling per claim, because an aggregate verdict is what made this bug unbuildable.

1. **DRIFT_KINDS is described as 14 entries and the changelog as a tuple of 17** - ruled **already fixed** on 2026-09-21. US0458 repointed trd.md:279,699 at reconcile.DRIFT_KINDS; len(DRIFT_KINDS)==20 matches both enumerations. The surviving `tuple of 17` is CHANGELOG.md:3368, US0458's own historical entry.
2. **US0460 states the tools/tests module count as `33 today`** - ruled **still true** on 2026-09-21. `ls tools/tests/test_*.py | wc -l` = 73 against the stated 33. Filed as BG0723.
3. **prose says the close runs `all seven close steps`** - ruled **still true** on 2026-09-21. `sprint._CLOSE_CHAIN` has 10 entries. Three of the four original sites were retired; test_sprint.py:12289 still says seven. Filed as BG0723.
4. **prose says three of the chain's steps exist to DO something** - ruled **still true** on 2026-09-21. sprint.py:7412 and :7859 both still say it, beside `DRY_RUN_ACTION_STEPS = tuple(_CLOSE_CHAIN)` - all ten - so `three` describes nothing. Filed as BG0723.
5. **US0465 AC5 counts sixteen offenders against eleven stories and one CR** - ruled **unfalsifiable as written** on 2026-09-21. The offender population was swept and no longer exists to recount; the delivering commit touches one artefact, so the census cannot be reconstructed from the tree. Needs the original per-file list.
6. **_RESOLVED_Q_RE is defined and never referenced** - ruled **already fixed** on 2026-09-21. Commit 0d99b0f5 `fix(BG0463)`; the symbol no longer exists anywhere in the tree.
7. **_FENCE_RE is dead and claims_in reads raw text, so a fenced band is a live claim** - ruled **still true** on 2026-09-21. Executed: `claims_in` over a fenced band returns a live claim while `_live_lines` drops it; check() passes raw text. Filed as BG0724.
8. **the blockquote skip in check_versions is unreachable** - ruled **still true** on 2026-09-21. The regex the skip guards never matches a `>`-prefixed line - all three blockquoted forms return False. The skip changes no outcome. Filed as CR0592.
9. **cycle_drift takes a root parameter it never reads** - ruled **already fixed** on 2026-09-21. Commit 0d99b0f5; the signature is now `def cycle_drift() -> dict` at sprint_report.py:2251.
10. **drops render bits[:12] with no `(+N more)` marker** - ruled **already fixed** on 2026-09-21. Commit 0d99b0f5; sprint_report.py:1788 appends `(+{more} more)`.
11. **covered units render covered[:6] with no marker** - ruled **never was a defect** on 2026-09-21. sprint_report.py:1971-1973 computes `dropped_from_view` and appends `(+N more)`, and `git log -S` shows it was never absent. This bug's own 2026-08-05 revision reached the same conclusion.
12. **check_versions claims version lives in `exactly five places`** - ruled **already fixed** on 2026-09-21. Commit e3b6272d `fix(BG0578, BG0490)`; the docstring now says the five PLUS every tracked markdown file that declares one, pinned at tools/tests/test_check_versions.py:377.
13. **a test docstring gives a run command that collects zero tests** - ruled **still true** on 2026-09-21. tools/tests/test_check_versions.py:3-4 names a discover root containing none of its tests. Filed as BG0723.
14. **a `six parents up` comment sits over parents[1]** - ruled **still true** on 2026-09-21. tools/tests/test_check_versions.py:17-18, and the same comment at test_validate_skill.py:14 and test_check_links.py:16. Filed as BG0723.
15. **authority is a decorative field no code reads** - ruled **still true** on 2026-09-21. 22 CHECKLIST rows carry it; the only read in the tree is an assertion in test_sprint_report.py:2360. Filed as CR0592.
16. **two spellings of the stop-ship constant** - ruled **still true** on 2026-09-21. retro.STOP_SHIP is compared against bare `stop-ship` literals at sprint_report.py:2033 and :3651. Filed as BG0725.
17. **NON_CEREMONY_VERBS is a second hand-maintained list carrying a stale entry** - ruled **still true** on 2026-09-21. Executed each script's build_parser() against the list: `sprint checklist` is no longer a verb, and the guard only SUBTRACTS the list so it can never report a stale entry. Filed as BG0725.
18. **every reviewer renders NO DECLARED SEAT on a persona-less project** - ruled **still true** on 2026-09-21. critic.py:3313-3316 requires callers to distinguish the two cases; sprint_report.py:1941 renders `seat or NO DECLARED SEAT` and asks nothing. critic._seat_drift_warning is the one compliant caller. Filed as BG0726.
19. **check_script_tests does not sweep scripts/hooks/** - ruled **still true** on 2026-09-21. It globs scripts/*.py and scripts/lib/*.py only. Benign today because the one inhabitant has a partner test - which is why it would stay unnoticed. Filed as BG0727.
20. **US0455's declared Affects omits a file its commit changed** - ruled **still true** on 2026-09-21. Commit eacd23a3 `fix(US0455)` changed sdlc-studio/personas.md; US0455's Affects does not name it. Filed as BG0728.
21. **the batch-level reviewer contribution is asserted nowhere** - ruled **still true** on 2026-09-21. sprint_report.py:1946-1947 unions the reviewers into the lens count; a scan of test_sprint_report.py finds no assertion within reach of either key, so deleting the union reddens nothing. Filed as BG0729.
22. **the no-op-add carve-out has no regression cover** - ruled **unfalsifiable as written** on 2026-09-21. No `no-op add` string exists anywhere in the tree outside BG0463 itself, and the seat report holding its file:line is not in the repo. Needs the carve-out's file and symbol named.
23. **a stop-ship ruling on an already-Fixed finding blocks the close permanently** - ruled **still true** on 2026-09-21. retro.carried_issues never reads the named artefact's status and the checklist refuses while any stop_ship row stands, so the ruling outlives the finding. Filed as BG0730, the most consequential survivor.
24. **a US0576 fixture exercises a state the writer cannot produce** - ruled **unfalsifiable as written** on 2026-09-21. Needs the fixture and field named. Both candidates in SprintChecklistImpedimentTests are producible - their shapes match the writers at sprint.py:11579 and :11625.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
| 2026-08-05 | Claude Opus 5 | **Delivered NARROWED under RUN-01KZ79C1, and most of this bug was already repaired.** VERIFIED rather than assumed, item by item: `_FENCE_RE` has no references left, the `covered[:6]` row already carries its marker, and the DRIFT_KINDS counts were fixed by US0458, which made the TRD cite `reconcile.DRIFT_KINDS` instead of restating it - the surviving 'tuple of 17' is in US0458's own changelog fragment, a historical record of that change and not a live claim, so it is left alone. Genuinely still broken and now fixed: the impediments row's `bits[:12]` dropped everything past twelve unmarked while its sibling row marked it (pinned by a fixture-backed test - a dict fixture skipped silently and asserted nothing); `_RESOLVED_Q_RE` was defined and never referenced, so the 'moved under Resolved Questions' route worked by OMISSION while a pattern beside it read as though something enforced it, now deleted with the real route named where it stood; and `cycle_drift` took a `root` parameter it never read, now removed - every caller already passed nothing. NOT delivered: the remaining stale-count and over-claiming-prose items, and the contract-drift and regression-cover halves. This unit stays Open. |
| 2026-09-21 | audit ruling | RUN-01M306PY / US0853: all claims re-executed against HEAD. 24 claims found, not 20. 15 still true, 5 already fixed (each naming what fixed it), 1 never was a defect, 3 unfalsifiable as written. Survivors carried forward as their own artefacts, per US0853 AC2 - nothing stays a bullet. |
