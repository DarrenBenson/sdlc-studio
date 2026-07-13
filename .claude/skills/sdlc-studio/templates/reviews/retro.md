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

## Metrics

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}
