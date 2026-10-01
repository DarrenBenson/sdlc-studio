<!--
Template: Sprint Retro (sprint)
File: sdlc-studio/retros/RETRO{NNNN}-{slug}.md  (committed)
Three lines, written at the close. Keep: what worked and should carry on. Stop: what cost more
than it returned. Try: at most three changes for the next run - each Try item becomes a lesson
when the close extracts it. Name its failure class so a repeat is counted, not re-written:
`[LC-003] what happened` adds a hit to class LC-003 in sdlc-studio/lessons.jsonl
(`lessons.py classes` lists every code, name, state and hit count);
`[new: class name] Rule sentence. What to do differently.` records a new class, injected at
plan, build and review (`[new: class name | build, review]` narrows it). The estimates,
delivery against plan and known issues are on the sprint report; the retro does not repeat them.
Known issues carried: one row per open finding the run carries, with its stop-ship ruling
(stop-ship, not-stop-ship, accepted-risk or deferred), who ruled and when. Empty when nothing is
carried. `sprint close` fills the Run line and the table's header.
Related: reference-sprint.md, help/retro.md, help/sprint.md
-->
# RETRO-{{retro_id}}: {{sprint_title}}

> **Date:** {{date}}
> **Run:** {{run_id}}
> **Batch:** {{batch}}

## Keep

- {{keep}}

## Stop

- {{stop}}

## Try

- {{try}}

## Known issues carried

{{known_issues_table}}
