# SC0002: v5 run 1: a new project and an upgrading project both reach a first green run

> **Status:** Queued
> **Queue rank:** 1
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Appetite:** 480min/8units
> **Scope query:** --bugs Open

## Sprint Goal

A user who has never run SDLC Studio, and a user upgrading a v4 project, both reach a planned sprint and a green gate without editing config or reading source.

## Scope rule

BG0558, BG0559, BG0560 and CR0541 once refined, plus the release-rehearsal lane this run builds.

This charter is FIRST because its four units are the only ones in the programme that a
consumer hits before they hit anything else, and because the rehearsal lane it builds is the
instrument the rest of the programme is measured by. All four were found by running the
shipped commands against throwaway fixtures during the 2026-08-09 readiness sweep, and none
of them was visible to any existing test, lane or backlog - which is the argument for building
the rehearsal rather than for fixing four bugs.

The rehearsal is the load-bearing unit. Two fixtures, driven end to end through the shipped
CLI on every gate run: a greenfield project from `init run` to a written sprint plan, and a
v4-era project from `migrate --apply` to a green `gate.py`. It must fail on the tree as it
stands today, before any of the four repairs land - a rehearsal that is green on the broken
tree is a rehearsal that proves nothing, and this repository has filed that shape twice
(BG0457, and the self-referential assertion of RUN-01KZ9315).

Scope-query caveat: `--bugs Open` resolves 49 units where this charter names four. Narrow the
batch by hand at materialise time until CR0531 lands a selector that can express a named set.

## Seat review

_Not yet reviewed._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
