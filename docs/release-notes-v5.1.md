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

## Known issues

The open findings are on [the disclosure page](known-issues.md), which is generated from the
bug corpus rather than maintained by hand.

**v5.1 discloses 18 open defects: 18 Medium, 0 Low.** Zero Critical, zero High.

## What is in it

Composed at the tag from `changelog.d/` by `release_cut.py changelog-cut`. Until then the
fragments are the record, one per delivered unit.
