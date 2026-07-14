<!--
Template: Sprint Retro (sprint)
File: sdlc-studio/retros/RETRO{NNNN}-{slug}.md  (committed)
Written at the close of every sprint (the sprint review + retro); read at the
start of the next sprint so the loop learns. Record each lesson on the project
tier (`lessons add`); promote one to the skill tier (`lessons add --global`)
only once it clearly generalises beyond this repo, and only with
`skill_source_repo` set - see help/lessons.md.
Related: reference-sprint.md, help/lessons.md
-->
# RETRO-{{retro_id}}: {{sprint_title}}

> **Date:** {{date}}
> **Batch:** {{batch}}
> **Goal:** {{goal}}
> **Delivered:** {{n_done}} / {{n_total}}   **Blocked:** {{n_blocked}}

## Delivered

- {{unit}} - {{what_shipped}}

## Blocked / deferred

- {{unit}} - {{blocker}}

## What went well

- {{good}}

## What was hard / what stalled

- {{hard}}

## Lessons

- {{lesson}}   <!-- record it: lessons add (project tier). Promote with --global only what generalises beyond this repo -->

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it**, or **decline it with a reason**. Both are green. What does not pass is
silence - a finding written down and left to rot.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| {{finding}} | {{BG0123 / CR0456 / declined: why not}} |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}
