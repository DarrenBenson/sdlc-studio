# BG0205: refine --into mis-distributes a request's criteria onto one sibling story

> **Status:** Fixed
> **Verification depth:** functional (two RED-first tests; reproduced and re-verified end to end in a clean workspace outside this repo)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

When a request is decomposed, refine seeds the FIRST story with the request's entire criteria list and leaves later siblings with a bare scaffold. In this run that produced stories whose ACs were another story's job: US0244 carried US0245's and US0246's criteria, and US0229 carried three epic-wide criteria verbatim from CR0320. Two independent grooming agents hit it in the same batch and both had to redistribute by hand. The seeded note says a multi-story breakdown redistributes during grooming, which documents the behaviour but not its cost: the wrong ACs look authored, so a groomer who trusts them writes tests for the wrong story, and the sibling that lost its criteria looks empty rather than mis-seeded.

## Steps to Reproduce

1. Take a request with 3 or more acceptance criteria. 2. refine it into an epic with 3 stories. 3. Read the stories: story 1 carries all the criteria, stories 2 and 3 carry placeholder scaffolds.

## Proposed Fix

Either distribute the criteria across the minted stories by best match, or seed NONE of them and put the request's criteria in the epic where they belong, with each story's ACs authored at grooming. Seeding all of them onto one story is the option that reads as authored while being wrong.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Filed |
