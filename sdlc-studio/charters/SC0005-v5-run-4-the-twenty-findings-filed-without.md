# SC0005: v5 run 4: the twenty findings filed without criteria are given criteria, and the backlog becomes plannable

> **Status:** Queued
> **Queue rank:** 4
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Appetite:** 240min/8units
> **Scope query:** --worklist (the ungroomed set, both types - see Scope rule)

## Premise re-measured 2026-08-16

The title says **twenty**. The shipped reader says **ten**, and names them: US0625, US0626,
US0627, US0628, US0646, US0647, US0648, US0649, US0650, US0651 - every one a Draft story, so the
whole set sits inside one batch rather than spread across the backlog.

`sprint breakdown --stories Draft --stories Ready` over 19 units reports 10 ungroomed. The other
ten the title counted have been groomed or closed since it was written, and nothing updated it.

Recorded rather than corrected in the title, because a charter is a decision with a date on it
and the drift is the fact worth keeping: this is the fourth recorded count this run that measured
differently from its artefact - the debt list that held eight already-fixed names, the backlog
that was 12% fiction, the 4.5x that measured 0.98x. D0136 priced this charter at twenty units
when it set the v5 bar; at ten, the run it describes is half the size that ruling assumed.

## Sprint Goal

No open delivery unit is unplannable: every one carries acceptance criteria that state what passing is, rather than restating the finding.

## Scope rule

**Amended 2026-08-16, before the run opened, on an adversarial goal review.** The 20 bug ids
below are all terminal now - BG0350 Won't Fix, BG0534 Superseded, the rest Fixed - so the scope
they declared authorises nothing, and the `--bugs Open` query authorised no story at all. A
charter whose scope has emptied does not become a licence for whatever batch is convenient; it
gets amended, on the record, before it is planned against.

The scope is now the ungroomed set as the shipped reader measures it, of EITHER type - 12 units,
45 points: US0625, US0626, US0627, US0628, US0646, US0647, US0648, US0649, US0650, US0651,
BG0490, BG0493.

The two bugs are in scope because they are ungroomed, which is what this charter is about; the
operator's ruling that they are triaged rather than built is untouched by giving them criteria.

Superseded scope, kept because a reader needs to see what emptied: BG0350, BG0469, BG0486,
BG0488, BG0490, BG0491, BG0493, BG0497, BG0508, BG0509, BG0512, BG0519, BG0522, BG0523, BG0526,
BG0528, BG0529, BG0531, BG0532, BG0534.

This is a grooming run, not a delivery run, and it exists as its own charter because the
operator's decision of 2026-08-09 - zero open bugs at tag - cannot be planned without it. Nine
of the twenty carry no criteria at all; eleven carry criteria every one of which was tool-derived
from the finding's own prose, which restates the summary and so states nothing about passing.

The known cost is recorded rather than discovered: `refine --into` output carries placeholder
criteria, and grooming is unestimated work on top of the points. Expect this run to change the
programme's remaining point total, and re-forecast the later charters from its result rather
than from today's 161.

Nothing is delivered here. A unit leaving this run is Ready, not Fixed.

## Seat review

_Not yet reviewed._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
