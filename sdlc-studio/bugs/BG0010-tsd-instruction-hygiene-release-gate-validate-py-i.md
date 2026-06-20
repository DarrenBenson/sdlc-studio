# BG-0010: TSD instruction-hygiene release gate (validate.py instructions) is wired into no CI or npm script

> **Status:** Open
> **Severity:** High
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

The TSD lists 'Instruction hygiene | validate.py instructions passes | Yes (release)' as a blocking gate and says the pre-release stage runs it, but no npm script or workflow invokes validate.py.

## Problem

tsd.md:247 and tsd.md:328-330 present instruction hygiene as an enforced release gate. The validate.py instructions subcommand exists, but it is absent from package.json scripts (only lint:skill runs the unrelated validate_skill.py) and from .github/workflows/lint.yml. The documented blocking gate has zero automation behind it, so AGENTS.md/CLAUDE.md drift can reach a release.

## Proposed Fix

Add an npm script (e.g. lint:instructions running validate.py instructions) and call it from the lint chain or a release workflow, then cite that script in the TSD; or restate the TSD to describe instruction hygiene as a manual pre-release check rather than an automated 'Yes (release)' gate.

## Evidence

tsd.md:247 'Instruction hygiene | validate.py instructions passes | Yes (release)' vs package.json scripts and .github/workflows/lint.yml containing no validate.py invocation

## Impact

The TSD's gate-traceability claims an enforced control that does not run; instruction-file drift can reach a release despite the TSD asserting it is gated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: tsd) |
