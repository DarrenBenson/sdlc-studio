# SDLC Studio v5.1

**The release that closes the carried list: every Medium open at v5.0.1 is disposed of or
ruled, and the disclosure page states which bar it is held to.**

v5.0.0 is the substantive release and [its notes](release-notes-v5.0.0.md) remain the place to
read what the tool does. v5.0.1 was a patch for one High-severity defect found hours after the
tag. This release is about the list those two left behind.

## The bar

**Zero open High-severity bugs at the tag, and every Medium disposed of or ruled.** A finding
either reaches a terminal status with its own verifiers passing, or it stays open carrying a
dated ruling that says why it ships. The v5.0.0 bar - zero open High - is unchanged and still
holds; this adds the Medium half, because a list that only ever grows is a disclosure nobody
can act on.

**The bar is the RULING, not the count.** An earlier form of it named a number - fewer than
sixteen disclosed - and that number is the wrong instrument: a count falls by fixing findings
or by not looking for them, and the two are indistinguishable from the outside. RUN-01M20RWX
filed all three disclosed here, every one from a review that was doing its job, and
holding a count would have made the run's own thoroughness the reason it could not ship.
What holds instead is that nothing Critical or High is open, and that every Medium on the
page carries a dated ruling naming why it ships rather than blocks (D0186, which
supersedes D0185's count promise; the other two promises D0185 made still bind).

## Known issues

The open findings are on [the disclosure page](known-issues.md), which is generated from the
bug corpus rather than maintained by hand.

**v5.1 discloses 3 open defects: 3 Medium, 0 Low.** Zero Critical, zero High.

## What is in it

Composed at the tag from `changelog.d/` by `release_cut.py changelog-cut`. Until then the
fragments are the record, one per delivered unit.
