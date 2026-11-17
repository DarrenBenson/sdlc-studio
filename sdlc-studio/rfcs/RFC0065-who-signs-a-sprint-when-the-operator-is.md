# RFC-0065: Who signs a sprint when the operator is away, and how a signed report discloses a delegated signature

> **Status:** Draft
> **Evidence:** audit AUDIT-2026-11-17, project profile, rfc lens, survived 3 of 3 refute votes; observed at sdlc-studio/decisions.md D0467, D0472, D0475, D0479 (rows dated 2026-11-12 to 2026-11-15) against sdlc-studio/rfcs/RFC0060-the-dark-factory-a-sprint-that-decides-for.md line 204 (Open Decisions, D6) and RFC0051's Decision / D0059
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:17Z

## Summary

RFC0060's open decision D6, who signs when the human is away for days, has been Open since 2026-09-21 and is being answered run by run. Decisions D0467, D0472, D0475 and D0479 each authorise the orchestrator, which is the authoring session, to run `sprint sign` with the operator's name as the principal, and D0479 extends that to every run closed during a flight. The sign check compares the typed principal string and not who typed it, so the rule that the signer sits outside the author's control is satisfied in form only. An earlier decision, D0059, made disclosure in the sprint report the price of a delegated sign-off, yet reports RPT0030 to RPT0034 carry a bare signature row with no decision id or delegation note, and their stop-ship findings read as ruled by the orchestrator. The 6.4.0 evidence pack, presented as evidence a change board accepts, is built from these reports, so the question needs one standing ruling in place of per-run authorisations.

## Design Options

- **Standing delegation with disclosure: the operator may authorise the orchestrator to sign for a named span, `sprint sign` takes the authorising decision id, and the signature block, the report and the evidence pack all state that the signature was entered under delegation**
- **Deferred signature: a run closed while the operator is away stays awaiting signature, later runs may open on top of it, and the operator signs each report in person on return; the orchestrator never enters a principal**
- **A second human principal: the project names a deputy who is outside the authoring session and may sign in the operator's absence, with the same refusal rules as the operator**
- **Out-of-band proof: `sprint sign` requires something only the operator holds, such as a signed git tag or commit, so a typed name alone no longer counts as a signature**

## Recommendation

Take the deferred signature as the default and allow standing delegation only with disclosure. A run awaiting signature should not block the next one, which removes the pressure that produced the per-run authorisations, and where the operator does delegate, the decision id must be recorded by `sprint sign` and printed in the signature block and the evidence pack. Close RFC0060 D6 with that ruling and amend the reports of record for the runs already signed under D0467 to D0479 with a disclosure line.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: Standing delegation with disclosure: the operator may authorise the orchestrator to sign for a named span, `sprint sign` takes the authorising decision id, and the signature block, the report and the evidence pack all state that the signature was entered under delegation, Deferred signature: a run closed while the operator is away stays awaiting signature, later runs may open on top of it, and the operator signs each report in person on return; the orchestrator never enters a principal, A second human principal: the project names a deputy who is outside the authoring session and may sign in the operator's absence, with the same refusal rules as the operator or Out-of-band proof: `sprint sign` requires something only the operator holds, such as a signed git tag or commit, so a typed name alone no longer counts as a signature | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
