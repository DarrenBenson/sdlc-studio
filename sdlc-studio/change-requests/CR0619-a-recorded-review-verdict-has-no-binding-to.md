# CR-0619: A recorded review verdict has no binding to the reviewer's own output - the orchestrator transcribes it into the file critic.py record reads

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0280
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T10:59:25Z

## Summary

`critic.py brief` tells the reviewer to RETURN a verdict block, and `critic.py record --from-verdict FILE` records whatever text the caller puts in FILE. In practice the orchestrator (often the session that also dispatched the authors) re-types or condenses the reviewer's returned text into that file - in a consuming project's RUN-01M4BHCT about 35 verdicts were recorded this way, some condensed for length and some with separators re-written so `record` would accept them. Nothing ties the ledger row to what the independent reviewer actually said, so the author-is-not-reviewer guarantee rests on the transcriber's honesty, and a softened finding or a dropped BLOCKING line would be invisible. The brief already carries a fingerprint; the verdict does not.

## Impact

The independent-review ledger can be edited between the reviewer and the record without trace.

## Acceptance Criteria

- [ ] The brief names a verdict file path for the reviewer to write itself, record reads that file and stores a hash of its exact bytes (and the reviewer's session id when known) on the ledger row
- [ ] record warns when the verdict file was last written by a process other than the reviewing session, or when the recorded text differs from the reviewer-written file
- [ ] A verdict whose recording session is the session that authored the unit is refused, or recorded and shown on the ledger as a self-review, whatever seat name it carries

## Triage

- Confirmed in this repo's own session on 2026-10-08: every verdict recorded today went through a file the orchestrator wrote from the reviewer's returned text (`critic.py record --from-verdict`), and two (BG0989 round 2, BG0994) had trailing commentary moved into the bug file because `record` refuses anything after `BLOCKING: none`. Nothing on the ledger row binds it to the reviewer's own output.
- Priority Medium and size M stand. Strongly related to BG0950 (`record` refuses commentary after BLOCKING, the refusal that pushes orchestrators to re-shape the reviewer's text): a reviewer-written verdict file, as proposed here, removes the transcription step BG0950's refusals currently force. Refine the two together.

## Further evidence (2026-10-08)

- Operator-relayed assessment of a consuming project's Sprint 0 (sdlc-studio-lens): 'The critic record names Tomas Reinholt as the QA reviewer on all eleven units. I wrote those verdicts in the same session that wrote the code.' Confirmed in `critic.py record` (critic.py:3316): the only self-review check compares the `--author` and `--reviewer` strings, both chosen by the caller, so the authoring session recording a verdict under a seat's name is ledgered as independent.
- This session's own recording on 2026-10-08 hit BG0950's refusals twice more: commentary after `BLOCKING: none`, and semicolons inside a finding, which `record` splits as findings and refuses as untagged. Each needed the reviewer to re-emit its block.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Claude Opus 5.5 | Raised |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: confirmed; private project names generalised; relations recorded |
| 2026-10-08 | Claude Opus 5.5 (triage) | Further evidence from a consuming project: the authoring session recorded every verdict under a seat's name; AC added |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Amend BG0950 with an AC4 before it is built: prose after `BLOCKING: none`, and a trailing `RULINGS:` line, record unedited. The panel recommends yes; without it, story 1's premise fails on the commonest APPROVE that carries commentary.
- Amend BG1003 so its decision is written as an `authorised:<Dnnnn>` token in the ninth `Source` column, and so that, if it lands first, it creates that column with story 2's grammar. That way 6.2 changes the ledger shape once.
- Story 6, when it ships, refuses a flow that passes today: a transcribed verdict recorded from a main thread that edited the unit fails Done. The panel recommends shipping it as a refusal, announced in the changelog (Jonah Reyes's End goal 4), since a self-review already never clears Done.
