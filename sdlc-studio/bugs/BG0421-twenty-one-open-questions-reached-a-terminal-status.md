# BG0421: Twenty-one Open Questions reached a terminal status unanswered, and are now owned here rather than given rulings nobody made

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** sdlc-studio/stories, sdlc-studio/change-requests, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** US0465's gate, run over the workspace, finds 21 unresolved Open Questions on 12 artefacts that all reached a terminal status: US0003, US0288, US0289, US0290, US0291, US0292, US0293, US0297, US0298, US0299, US0300 (Done) and CR0019 (Superseded). Nine further artefacts flagged on the first pass were FALSE POSITIVES the gate itself was corrected for - `- [ ] None - behaviour fully extracted from scripts/x.py` is the template saying there are none, and `Ruled by D0052: ...` is a ruling recorded on the item.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

This bug exists so that twenty-one questions stop being invisible without being given answers nobody actually gave.

Every one is on an artefact that reached Done or Superseded. Most ask something the parent request left undefined - CR0284 asked for a flag "when a token total is supplyable" without defining supplyable; CR0347 required the analysis to include "the test files a unit will touch" without saying how to tell a file a unit will legitimately create from one it merely names; CR0354 did not say how a seat verdict reaches the planner, nor whether a plan with no Sprint Goal is refused. The delivery made a choice in each case. Whether that choice is the RIGHT answer to the question is exactly what nobody recorded.

The honest options were three, and two of them are worse.

Writing a ruling for each from what the code now does would be inventing the decision after the fact and stamping it as though someone had made it. That is the false-evidence class this project files bugs about, and it would be done at scale, into the permanent record, on twenty-one items.

Leaving them unticked keeps them honest and leaves the gate red, which means the gate cannot be turned on - and a gate that cannot be turned on protects nothing going forward.

So they are OWNED here instead. Each item cites this bug. The claim being made on those artefacts is precisely "this question was not answered, and the debt is tracked at BG-XXXX" - which is true, checkable, and does not pretend to be a ruling.

CR0019's three are a different case worth naming separately: it is SUPERSEDED, and its questions are design alternatives (grouping key, whether to archive files or only rows, whether to promote to an RFC) that the supersession made moot. Those want a ruling of 'moot, superseded by' rather than an owner, and that is the one place a real ruling can be written without inventing anything.

## Steps to Reproduce

1. Run `validate.py check` and count the `open-question` findings: 21 across 12 artefacts.
2. Read any of them - each asks something its parent request left undefined.
3. Read the artefact's Status: every one is Done or Superseded.

## Proposed Fix

1. **Resolve CR0019's three by ruling**, because the supersession genuinely settles them: a superseded design's alternatives are moot, and naming the artefact that superseded it is a real answer rather than a reconstructed one.
2. **Own the remaining eighteen by citation**, so the gate can be switched on with a true record: the item says the question was not answered and points here.
3. **Answer them properly, in batches, as the code they concern is next touched.** A question about how `wsjf-inputs.json` ages is answerable by whoever next opens that path; answering all eighteen in one sitting is how a reconstruction happens.
4. **Do not close this bug by ticking.** It closes when each of the eighteen carries either a real ruling or its own follow-up - which is the same bar the gate applies, applied to this bug's own residue.

## Acceptance Criteria

- [ ] Each of CR0019's three questions carries a ruling of moot, naming the artefact that superseded it - a real answer, not a reconstructed one.
- [ ] Each remaining question cites this bug, so the record states the question was not answered and names where the debt is tracked.
- [ ] `validate.py check` reports no `open-question` finding, so the gate US0465 builds can be enforced going forward.
- [ ] This bug closes only when each owned question carries a real ruling or its own follow-up artefact - it is not closed by ticking, and the same bar the gate applies is applied to its own residue.
- [ ] A test asserts the gate still refuses an artefact whose question is ticked while citing an id that resolves to nothing, so citing THIS bug is a real claim rather than a way past the check.

## Impact

The immediate effect is that the gate US0465 builds can be turned on. Without this the workspace is red and the guard is dead weight - it would protect nothing going forward while the historical debt sat unfixed.

The wider point is about what a record is for. Twenty-one questions on shipped work were invisible: nothing enumerated them, no gate refused them, and the artefacts read as settled. Making them visible and owned is worth more than making them look answered, and it is the difference this project's whole argument rests on.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
