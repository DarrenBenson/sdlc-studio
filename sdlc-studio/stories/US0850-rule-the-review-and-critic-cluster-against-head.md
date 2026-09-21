# US0850: rule the review-and-critic cluster against HEAD

> **Status:** Review
> **Delivers:** CR0591
> **Created:** 2026-09-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/change-requests, sdlc-studio/rfcs
> **Epic:** EP0257
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** rule the review-and-critic cluster against HEAD
**So that** CR0591 is delivered by work that can be planned and checked

## Acceptance Criteria

This story rules the **review and critic** cluster: 8 of the 38 requests the audit covers
(CR0503, CR0509, CR0512, CR0529, CR0550, CR0555, CR0556, CR0565). The cluster is the unit of work because judging whether one of these is still wanted
is far cheaper with its siblings in view - several describe the same pressure from different
angles, and a request that looked alive alone is often visibly superseded beside its neighbours.

### AC1: every request in this cluster carries a dated `audit ruling` row naming one of the four outcomes

- **Given** the 8 requests above, each read against HEAD
- **When** the audit has run
- **Then** every one carries a dated `audit ruling` revision row naming exactly one outcome - already delivered by other work, overtaken by events, still wanted and correctly In Progress, or still wanted but never started - and the row states WHY in terms a later reader can check. A request left In Progress is a RULING that it is still wanted, recorded as such, not the absence of a decision
- **Mutant:** rule only the requests that turn out to be closeable and leave the survivors untouched - the count falls, the lane goes quiet, and the ones still In Progress are indistinguishable afterwards from the ones nobody read. That is a sweep measured by its body count, which D0186 already names as the wrong instrument
- **Verify:** shell python3 -c "import pathlib,re,sys; ids='CR0503 CR0509 CR0512 CR0529 CR0550 CR0555 CR0556 CR0565'.split(); bad=[i for i in ids if not any(re.search(r'^\| 2026-\d\d-\d\d \| audit ruling \|', p.read_text(encoding='utf-8'), re.M) for p in pathlib.Path('sdlc-studio').rglob(i+'*.md'))]; print('unruled:', bad) if bad else None; sys.exit(1 if bad else 0)"
- **Verified:** yes (2026-09-21)

### AC2: a request ruled already-delivered names the unit that delivered it, and the claim was checked by execution

- **Given** any request in this cluster ruled `already delivered by other work`
- **When** its ruling row is read
- **Then** it names the unit that delivered it, so the claim is checkable rather than asserted - and the premise was verified against HEAD by running the thing, not by reading two titles and finding them similar
- **Mutant:** accept a title match as evidence of delivery - this project has a recorded case of five closed bugs that were never defects, and CR0557 exists because an aggregate sat six weeks until its premises had quietly stopped being true
- **Verify:** shell python3 -c "import pathlib,re,sys; ids='CR0503 CR0509 CR0512 CR0529 CR0550 CR0555 CR0556 CR0565'.split(); rows=[]; [rows.append(m) for i in ids for p in pathlib.Path('sdlc-studio').rglob(i+'*.md') for m in re.findall(r'^\\| 2026-\\d\\d-\\d\\d \\| audit ruling \\| (.+)$', p.read_text(encoding='utf-8'), re.M) if 'already delivered' in m.lower()]; print('already-delivered rulings checked:', len(rows)); bad=[m[:60] for m in rows if not re.search(r'\\b(US|BG|CR)\\d{4}\\b', m)]; print('unnamed:', bad) if bad else None; sys.exit(1 if bad else 0)"
- **Verified:** yes (2026-09-21)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | rule only the requests that turn out to be closeable and leave the survivors untouched - the count falls, the lane goes quiet, and the ones still In Progress are indistinguishable afterwards from the ones nobody read. That is a sweep measured by its body count, which D0186 already names as the wrong instrument | every request in this cluster carries a dated `audit ruling` row naming one of the four outcomes |
| AC2 | accept a title match as evidence of delivery - this project has a recorded case of five closed bugs that were never defects, and CR0557 exists because an aggregate sat six weeks until its premises had quietly stopped being true | a request ruled already-delivered names the unit that delivered it, and the claim was checked by execution |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | plan review REJECT | AC2's verifier was VACUOUSLY GREEN and the plan review proved it: it matched `already delivered` case-sensitively while every ruling written by this run says `ALREADY DELIVERED`, so the comprehension yielded nothing and exit 0 was guaranteed whatever the rulings said. Fifth verifier in this run to pass for a reason unrelated to its claim. It now matches case-insensitively and PRINTS how many rulings it checked, so a vacuous pass is visible in the output rather than indistinguishable from a real one. |
| 2026-09-21 | plan review REJECT | Second finding recorded rather than repaired, because it cannot be: AC2's mutant is `accept a title match as evidence of delivery`, and a title-matched ruling would still cite a unit id, so no textual check can tell it from a verified one. The verifier can only prove a delivery claim NAMES its unit; that the claim is TRUE was established by execution in the delivery review, which confirmed US0671-US0676 Done and the revert-check and depth machinery present before CR0547/CR0548 were closed. The criterion's machine-checkable half and its human half are now stated separately instead of the first being presented as if it covered the second. |
