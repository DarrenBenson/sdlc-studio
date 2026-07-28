# The carried lessons

A **fixed-size** set of the lessons that matter most for the next batch. Read at sprint plan, carried
into every delivery lane's brief, and given to the reviewers.

This is not a ranking and not an archive - `LESSONS-SUMMARY.md` holds all 252 open lessons and
`lessons rank` orders them by citation. This file holds a **judgement about what to carry forward**,
and it is fixed size on purpose: a set that can grow is a set nobody reads.

**The retro's obligation.** For each lesson the batch produced, ask: *is this more important than
anything already here?* If yes, it **displaces** one and the displaced lesson is named in the retro
with why it was dropped. If no, it stays in the registry and out of this file. Adding without
displacing is not an option.

**Why five.** Small enough to hold while working, large enough to cover the distinct failure classes
actually recurring. Three would force out real classes; ten stops being read. Five is a starting
judgement, not a constant - if a retro finds itself unable to displace anything, that is evidence
the number is wrong, and it should be changed deliberately rather than by drift.

---

## 1. A mechanism that reaches no caller is inert, however well it is tested

Four times in RUN-01KYJZGZ: a surface hash whose digest could never match, a selection computed by
one hook and ignored by the one that runs tests, a consumer whose producer does not exist, a
detector nothing invokes. Each had passing tests, a green gate, and an author who believed it
worked. **Write the acceptance criterion against the CALLER, not the function.** If there is no
caller yet, say so on the artefact and name the unit that will add one.

## 2. An absence is not an answer

A vote that never arrived is not a refutation. An agent that stopped is not still working. A module
whose read set measured empty does not "reach nothing". A directory git cannot enumerate is not "a
tree with no files". Every one of these shipped as a silent false-negative. **When a measurement
comes back empty, ask whether it answered or merely failed to** - and make the unknown widen the
work, never narrow it.

## 3. A repair breaks its neighbours, and a rename is cross-unit coupling

Three regressions in one repair on 2026-07-27, four rotted verifiers in the next - all by the author
who had filed the lesson. Renaming a test silently breaks every acceptance criterion pinning it.
**After a repair, run the tests the changed file can reach, not just the one you fixed**, and check
what your rename left pointing at nothing.

## 4. An enumerated list silently exempts what it forgot

The most-cited lesson in the registry (23 times) and still violated four more times across two
sprints: a version guard reaching four files but not the TRD, a placeholder sweep reading two
sections, a skip-list covering subdirectories but not the entry itself, an id grammar knowing only
the four-digit form. **Derive the set from the tree, the vocabulary or the parser** - if you are
typing a list of what to check, you are choosing what to miss.

## 5. Verify the premise before building on it

A CR withdrawn because measurement falsified its central claim; a bug filed on a false premise; a
story resting on "four unanswerable groups" that existed nowhere. **Reproduce the defect before
fixing it, and count the thing before quoting the number.** A unit built on an unverified premise
costs more than one never filed.

---

*Curated at RETRO0080 (2026-07-28). Displacement rule applies: the next retro must justify any
change against what is already here.*
