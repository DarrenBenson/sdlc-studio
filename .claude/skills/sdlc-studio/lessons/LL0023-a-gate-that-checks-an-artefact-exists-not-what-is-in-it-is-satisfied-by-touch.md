---

id: LL0023
title: A gate that checks an artefact exists, not what is in it, is satisfied by touch
tags: [gate, false-green, ceremony, bug-class, silent-failure, process]
added: 2026-07-14
origin: BG0123 - the retro gate passes a 0-byte file
---

**Lesson.** A ceremony gate that tests for a FILE rather than for CONTENT does not enforce the ceremony; it enforces the filename. The retro leg was `present = bool(list(retros.glob(f'{retro_id}*.md')))`, so an empty `RETRO9999.md` returned '[PASS] retro: batch retro RETRO9999 present'. The one gate that existed to make the retrospective un-skippable was the one an agent could satisfy with `touch`.

This is the same failure as [[LL0008]] wearing a different hat: the gate reported a success it did not achieve. And it is [[LL0015]]: it caught the total case (no file at all) and nothing else, which is the case that never happens - people who skip the ceremony under a gate produce the artefact, they do not omit it.

The rule: a gate on an artefact must assert on the artefact's CONTENT - the sections that must be present, the minimum substance, and above all the DISPOSITION of what it contains (was anything acted on?). Existence is not evidence.

The tell that you are about to build one of these: there is no deterministic tool that produces or validates the artefact, so the gate has nothing to check but the filesystem. Build the tool first; a gate is only as good as the thing it can interrogate.

Corollary for the reviewer: to test a ceremony gate, produce the emptiest artefact that satisfies its letter and check it fails ([[LL0010]] - validate a defence using the bug it defends against).

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
