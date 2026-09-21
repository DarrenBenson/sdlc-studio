# US0849: rule the close-and-ceremony cluster against HEAD

> **Status:** Ready
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
**I want** rule the close-and-ceremony cluster against HEAD
**So that** CR0591 is delivered by work that can be planned and checked

## Acceptance Criteria

This story rules the **close and ceremony** cluster: 9 of the 38 requests the audit covers
(CR0424, CR0441, CR0499, CR0504, CR0507, CR0530, CR0531, CR0546, CR0551). The cluster is the unit of work because judging whether one of these is still wanted
is far cheaper with its siblings in view - several describe the same pressure from different
angles, and a request that looked alive alone is often visibly superseded beside its neighbours.

### AC1: every request in this cluster carries a dated `audit ruling` row naming one of the four outcomes

- **Given** the 9 requests above, each read against HEAD
- **When** the audit has run
- **Then** every one carries a dated `audit ruling` revision row naming exactly one outcome - already delivered by other work, overtaken by events, still wanted and correctly In Progress, or still wanted but never started - and the row states WHY in terms a later reader can check. A request left In Progress is a RULING that it is still wanted, recorded as such, not the absence of a decision
- **Mutant:** rule only the requests that turn out to be closeable and leave the survivors untouched - the count falls, the lane goes quiet, and the ones still In Progress are indistinguishable afterwards from the ones nobody read. That is a sweep measured by its body count, which D0186 already names as the wrong instrument
- **Verify:** shell python3 -c "import pathlib,re,sys; ids='CR0424 CR0441 CR0499 CR0504 CR0507 CR0530 CR0531 CR0546 CR0551'.split(); bad=[i for i in ids if not any(re.search(r'^\| 2026-\d\d-\d\d \| audit ruling \|', p.read_text(encoding='utf-8'), re.M) for p in pathlib.Path('sdlc-studio').rglob(i+'*.md'))]; print('unruled:', bad) if bad else None; sys.exit(1 if bad else 0)"
- **Verified:** yes (2026-09-21)

### AC2: a request ruled already-delivered names the unit that delivered it, and the claim was checked by execution

- **Given** any request in this cluster ruled `already delivered by other work`
- **When** its ruling row is read
- **Then** it names the unit that delivered it, so the claim is checkable rather than asserted - and the premise was verified against HEAD by running the thing, not by reading two titles and finding them similar
- **Mutant:** accept a title match as evidence of delivery - this project has a recorded case of five closed bugs that were never defects, and CR0557 exists because an aggregate sat six weeks until its premises had quietly stopped being true
- **Verify:** shell python3 -c "import pathlib,re,sys; ids='CR0424 CR0441 CR0499 CR0504 CR0507 CR0530 CR0531 CR0546 CR0551'.split(); bad=[]; [bad.append(i) for i in ids for p in pathlib.Path('sdlc-studio').rglob(i+'*.md') for m in re.findall(r'^\| 2026-\d\d-\d\d \| audit ruling \| (.+)$', p.read_text(encoding='utf-8'), re.M) if 'already delivered' in m and not re.search(r'\\b(US|BG|CR)\\d{4}\\b', m)]; print('unnamed:', bad) if bad else None; sys.exit(1 if bad else 0)"
- **Verified:** yes (2026-09-21)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Created via `new` (deterministic) |
