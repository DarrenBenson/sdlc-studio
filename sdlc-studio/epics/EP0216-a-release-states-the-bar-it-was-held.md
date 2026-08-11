# EP0216: A release states the bar it was held to and discloses, by id, every finding it ships open

> **Status:** Draft
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A release that reports only what it fixed is a release a reader cannot judge. v5.0.0 ships with open findings by an explicit ruling rather than by oversight, so the record has to carry three things a reader can check: the bar (zero open High-severity findings), the residue (every open Medium and Low, by id, with its severity), and the reason the bar moved. The disclosure is derived from the bug corpus and gated, because a hand-maintained list of one's own defects decays in exactly one direction.

## Story Breakdown

- [ ] [US0670: The release discloses every open Medium and Low finding by id, and the page is derived from the bug corpus rather than maintained by hand](../stories/US0670-the-release-discloses-every-open-medium-and-low.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
