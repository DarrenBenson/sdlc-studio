# US0937: Work that already shipped reads Done, so the repair ledger can go and the release cut ships no notes for open stories

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories/US0891-a-commit-s-pre-commit-lanes-run-side.md, sdlc-studio/stories/US0900-a-change-request-can-be-filed-before-it.md, sdlc-studio/stories/US0904-each-lane-s-refusals-are-counted-against-the.md, sdlc-studio/epics/EP0262-commits-clear-in-ninety-seconds-and-every-constraint.md, sdlc-studio/bugs/BG0717-the-close-s-handoff-link-leaves-a-trailing.md, sdlc-studio/bugs/BG0720-the-report-s-filed-this-run-figure-names.md, sdlc-studio/change-requests/CR0545-everything-after-the-tag-is-un-tooled-no.md, sdlc-studio/change-requests/CR0560-filing-a-finding-leaves-the-disclosure-page-stale.md, sdlc-studio/stories/US0808-a-filed-medium-or-low-finding-is-already.md, sdlc-studio/epics/EP0245-filing-a-finding-leaves-the-disclosure-true.md
> **Epic:** EP0265
> **Points:** 1
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer about to cut a release
**I want** every unit whose work already shipped moved to its terminal status through `transition.py`, before the repair ledger's readers are deleted
**So that** the backlog states what is done, EP0262 closes, and the v6 changelog cut composes no fragment for a story that still reads open

## Acceptance Criteria

- **AC1:** Given US0891, US0900 and US0904, whose work shipped through BG0759, BG0756 and BG0761 and whose Verify nodes pass at HEAD (3, 2 and 5), when each is moved to Done through `transition.py` with its criteria run, then each reads Done and conformance, scoped to these three, reports its verified and critiqued stages met. Fails on: moving them after US0914 lands, when the Done guard refuses each 2026-09-24 REJECT that only a repair row answers; moving them with `--force` or by editing the Status line, which runs no criteria and leaves the verified stage unmet; superseding them, which leaves their `changelog.d/` fragments describing undelivered stories
  - **Verify:** shell python3 -c "import sys; sys.path.insert(0, '.claude/skills/sdlc-studio/scripts'); import conformance; ids=('US0891','US0900','US0904'); u={x['id']:x for x in conformance.detect_conformance('.', scope_ids=set(ids))['units']}; sys.exit(0 if all(u[i].get('status')=='Done' and u[i].get('stages', {}).get('verified') and u[i].get('stages', {}).get('critiqued') for i in ids) else 1)"
  - **Verified:** yes (2026-09-25)
- **AC2:** Given the three stories Done with their criteria run, then EP0262 reads Done and reconcile reports no drift naming it, so no epic of the lean programme stays open over delivered children. Fails on: the stories moved without their criteria run (`--force`, or Status lines edited by hand), which leaves each one's verified stage unmet even though EP0262 itself still closes; EP0262's Status written over a breakdown that reconcile does not agree with
  - **Verify:** shell grep -qE '\*\*Status:\*\* Done' sdlc-studio/epics/EP0262-commits-clear-in-ninety-seconds-and-every-constraint.md && python3 -c "import sys; sys.path.insert(0, '.claude/skills/sdlc-studio/scripts'); import conformance; ids=('US0891','US0900','US0904'); u={x['id']:x for x in conformance.detect_conformance('.', scope_ids=set(ids))['units']}; sys.exit(0 if all(u[i].get('status')=='Done' and u[i].get('stages', {}).get('verified') for i in ids) else 1)" && python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect --format json | python3 -c "import json,sys; sys.exit(1 if any('EP0262' in json.dumps(x) for x in json.load(sys.stdin).get('drift', [])) else 0)"
  - **Verified:** yes (2026-09-25)
- **AC3:** Given QA's transitions-only group, then BG0717 reads Fixed with its criteria run and stamped (fixed by US0877, 6729b4f3), BG0720, CR0545, CR0560 and US0808 read Superseded each naming what superseded it in a `Closed with findings in` field (US0875; the release workflow and v5.1.0's four assets; US0898), and EP0245 derives terminal. Fails on: closing BG0717 as Superseded, which records a delivered fix as abandoned work; moving BG0717 to Fixed with no criteria run, which leaves no `Verified:` stamp; superseding any of the four without naming its superseder
  - **Verify:** shell sh -c 'for p in "bugs/BG0717:Fixed|Verified|Closed:-" "bugs/BG0720:Superseded:US0875" "change-requests/CR0545:Superseded:release.yml" "change-requests/CR0560:Superseded:US0898" "stories/US0808:Superseded:US0898" "epics/EP0245:Done|Superseded:-"; do f=${p%%:*}; r=${p#*:}; s=${r%:*}; n=${r##*:}; grep -qE "\*\*Status:\*\* ($s)" sdlc-studio/$f-*.md || exit 1; [ "$n" = - ] || grep -qE "^> \*\*Closed with findings in:\*\* .*$n" sdlc-studio/$f-*.md || exit 1; done; grep -qE "^ *- \*\*Verified:\*\* yes" sdlc-studio/bugs/BG0717-*.md'
  - **Verified:** yes (2026-09-25)

## Notes

Wave 0; must land before US0914 (engineering proposal finding 4). No code changes: transitions only, through `transition.py` so indexes and epics derive. Merges QA's transitions-only group (qa-proposal.md: BG0717, BG0720, CR0545, CR0560, US0808, EP0245). No changelog fragment of its own: the three stories' fragments already exist. All three Verify lines fail at 013a46d0 (measured). Ratchet: adds no check.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (NEW-A) |
| 2026-09-25 | sdlc-studio US0937 | QA review round 1: AC1 and AC2 require each story's verified stage (killing the `--force` and hand-edit mutants), AC2 requires no reconcile drift naming EP0262, AC3 requires each Superseded unit's named superseder and BG0717's `Verified:` stamp; conformance is scoped to the three ids, since the whole-workspace check exits 1 on unrelated units and ran 160-200s under load, past the 120s verifier timeout; Fails-on wording corrected |
