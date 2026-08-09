# SC0007: v5 run 8: the release is rehearsed, signed and cut

> **Status:** Queued
> **Queue rank:** 6
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Appetite:** 240min/8units
> **Scope query:** --stories Review

## Sprint Goal

v5.0.0 is tagged on a commit whose release gate was green, with release notes a reader outside this repository can use.

## Scope rule

The eight stories resting at Review awaiting reviewer-of-record sign-off (US0591 to US0596,
US0635, US0636), the three EP0171 units at Ready (US0469, US0474, US0475), and the release cut
itself.

The cut has four mechanical preconditions the release gate already names, and each has a
command: `changelog.py compose` for the 34 uncomposed fragments the gate refuses on; hand-authored
v5.0.0 release notes replacing the 4,001-line composed draft, which is currently what a user
would read; `conformance.adopt_after` decided for this repository's own 2 non-conformant units;
and `release_cut.py record-green` then `tag-check`, which refuses a tag whose commit the gate
was not green on.

The sign-offs are structurally unavailable to any authoring session and belong to the operator.
They are named here so the run is not planned as though they were build work.

Do not cut until run 1's rehearsal lane is green on both fixtures. That lane, not this
charter's checklist, is the thing that says the release works.

## Seat review

_Not yet reviewed._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
