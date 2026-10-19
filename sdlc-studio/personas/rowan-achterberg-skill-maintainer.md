# Rowan Achterberg

> A specific person, not a type. Rowan is Primary for the repository-tooling interface; Maya
> Okafor is Primary for the shipped skill (one Primary per interface, D0379).

## Quick Reference

| Attribute | Value |
| --- | --- |
| **Cast role** | Primary |
| **Interface** | Repository tooling: this repository's `tools/`, `.githooks/` and `.github/`, and the forward-port to the installed copy. It does not ship |
| **Role** | Maintainer of the skill's source repository |
| **Context** | Pushes from a workstation shared with several agent sessions, judged on a gate host; cuts the releases consuming teams upgrade to |

## Who They Are

Rowan maintains the repository the skill is built and dogfooded in. Every change to the skill
reaches the world through Rowan's hooks, push gate, CI and release cut, and every consuming team's
upgrade starts from a tag Rowan pushed. Rowan has watched a ten-minute gate become an hour on a
workstation crowded with agent sessions, and a green suite get trusted as a green tree. What Rowan
wants from the tooling is that every gate says what it proves, what it needs and what it costs,
before the push rather than after it.

## End Goals

*What they are trying to accomplish, most important first. The design is judged against these.*

1. A push is judged against exactly the commit pushed, in minutes the work can absorb, without
   competing with agent sessions for the workstation's memory
2. A fix landed in this repository is in force in the installed copy the same day, so no fix is
   believed shipped while it runs nowhere
3. A release ships that a consuming team can upgrade to: the release boundary green, every known
   issue named, the changelog complete
4. Main is never left red and unread: a red run is read before the next push lands on top of it

## Experience Goals

*How they want to feel while using it.*

- Confident that a green gate means what it says, and that a refusal names what to fix
- Never forced to choose between a long retry and a bypass
- Told up front what a gate needs and what it will cost

## Behaviours & Context

- **Environment:** a terminal on a workstation shared with agent sessions, a gate host reached
  over ssh, and the forge's CI
- **Frequency:** several pushes a day while a run is open; a release every few weeks
- **Proficiency:** fluent in git, shell and Python; reads a hook before trusting it; would rather
  a tool refuse loudly than pass quietly

## Frustrations

*What trips them up with the current tools or status quo.*

- The push gate took 26 to 64 minutes on the workstation and was stopped twice in a week for low
  memory, against about ten minutes on a gate host (D0366, D0370)
- The gate's own 45-second cost budget is exceeded on every run, 127 seconds locally and 143 in
  CI, so its warning carries no signal (BG1065)
- A missing prerequisite found only after the suite has run for minutes (US1003, US1005)
- A push that fails on a dropped connection after the gate has already passed, so the retry pays
  the whole gate again (the keepalive `tools/enable-hooks.sh` sets)
- A scheduled CI job red for weeks with nobody reading it (BG1054)
- A mirror of the skill that drifts silently from its source (`tools/forward-port.sh --check`)

## Scenario

*A short narrative of this persona using the product to reach an End goal, in context.*

Rowan pushes a fix at the end of the afternoon while two agent sessions run on the same machine.
The pre-push hook sends exactly that commit to the gate host and streams its output back. The gate
refuses on one test and names the host's log. Rowan fixes the test and pushes again, and the host
judges it green in about ten minutes while the workstation stays free. Rowan then runs the
forward-port, and the installed copy every other project loads carries the fix before the day
ends.

## Boundaries

- **Maya Okafor is Primary for the shipped skill.** A unit that touches a shipped path
  (`.claude/skills/sdlc-studio/`) is judged against Maya. Rowan's want is met in repository-only
  surface, never by shipped surface Maya pays for.
- **The interfaces meet in the shipped gate.** `gate.py`'s push boundary ships, so a change there
  is Maya's, even when Rowan is the one who asked for it.
- **Trevor Hale is the Negative persona on both interfaces.** An approver on every change is still
  his want, not Rowan's: Rowan's goals are outcomes a unit can fail against, never a gate added
  for its own sake.
- A collision these lines cannot settle goes to the operator, and the ruling is recorded as a
  decision.

## Evidence

- End goal 1: D0366 and D0370 (the workstation and gate-host timings); CR0635 and EP0288 (the
  remote gate).
- End goal 2: AGENTS.md's forward-port section and `tools/forward-port.sh`.
- End goal 3: D0375 (the release boundary and the manual pre-tag steps); D0378 (the path to
  6.2.0).
- End goal 4: D0181 (the red-main acknowledgement); BG0709.
- The card itself: D0379, the stakeholder consult
  `sdlc-studio/reviews/consult-EP0289-stakeholders-2026-10-19.md`, and RV0028 finding PER-1.

---

- Outside contributors (`CONTRIBUTING.md`) use the same hooks and push gate and are served by this
  card; they need no card of their own.
