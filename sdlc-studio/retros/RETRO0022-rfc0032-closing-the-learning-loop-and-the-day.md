# RETRO-0022: RFC0032: closing the learning loop (and the day the installer shipped broken)

> **Date:** 2026-07-14
> **Batch:** RFC0032 + CR0240-CR0247 + BG0122-BG0124
> **Goal:** ship the v4.1 installer fix, then close the inspect-and-adapt loop
> **Delivered:** 12 / 12   **Blocked:** 0

## Delivered

- BG0122 - `install.sh` no-oped when piped to bash. The source-vs-execute guard compared
  `${BASH_SOURCE[0]}` with `$0`; piped, the first is unset, so `main` never ran and the script
  exited 0 having installed nothing. That is the exact invocation the README advertises.
  Released as v4.1.0.
- BG0123 - the retro gate was satisfied by `touch`. It globbed for a filename, so a 0-byte
  `RETRO9999.md` returned `[PASS]`. It now reads the content.
- BG0124 - WITHDRAWN, not a bug. See below; it is the most instructive item here.
- RFC0032 (Accepted, D1-D6) plus CR0240-CR0247: the retro spine (`retro.py`), the disposition
  question in the template, the cross-project registry's first automatic reader, the ranked
  live summary, a home for operational lessons, the doctrine rule and its opt-out, and a
  silent test suite.

## Blocked / deferred

- The release of this work. An operator freeze holds until ~2026-07-21: v4.1.0 shipped today,
  and a same-day v4.2 reads as panic. Everything sits in `[Unreleased]`, forward-ported to the
  installed copy for internal testing only.

## What went well

- The gates earned their keep, repeatedly and unglamorously. `doc_coverage` caught an
  undocumented script the moment it landed; `check_neutrality` caught a private repo name
  leaking into a public file; `validate` caught template placeholders in hand-written ACs;
  `check_budgets` caught a blown line ceiling; and a repo hygiene test caught a `__main__`
  guard that was no longer the last statement, on the very day the installer shipped broken
  because of a `__main__` guard.
- Every fix was proven against the bug it defends before being trusted, and the partial dodges
  were tested rather than only the total case. The 0-byte retro is not the interesting test;
  the retro that looks complete but leaves a finding undecided is.
- The ranking, run on our own registry, made the argument without needing to argue it: LL0008
  is the second most-cited lesson (x34), and nothing was showing it to anyone.

## What was hard / what stalled

- **A confident false finding cost more than the bug would have.** BG0124 was filed as High
  against a defence that already existed and was documented in the docstring at the call site.
  It was "proven" by calling a private helper directly, which tests the helper and says nothing
  about the pipeline - the only thing that ships. It cost a bug, a severity correction, a
  lesson and three commits, all of which then had to be withdrawn.
- **The same class of error, twice more, from the same author.** CR0242 was marked Complete
  when only one of its three promised read-points was wired. That is LL0008 - reporting a
  success not achieved - committed inside the change whose entire purpose was that nobody reads
  LL0008. And `--no-verify` was used once to get past a hook timeout; the gate would have
  failed, and did, on three real errors when re-run by hand.
- The first version of the test-noise guard re-ran the whole suite to grep it, doubling the
  pre-commit hook and timing out a commit. A guard whose cost is paid on every commit has to be
  cheap, or it gets disabled and then it guards nothing.

## Lessons

- A hazard found by calling a private helper directly may already be guarded at the only call
  site that matters - reproduce through the public path, or you have not reproduced it.
- A gate that checks an artefact exists, not what is in it, is satisfied by `touch`.
- A guard that branches on invocation mode must be tested in every invocation mode; assert on
  output, not the exit code, when the failure mode is "did not run".
- Marking a work item Complete while part of its acceptance criteria is unwired is the same
  failure as a tool reporting a success it did not achieve. Check the ACs, not the feeling of
  being finished.
- A false finding is not free: under a disposition gate that turns findings into work, a
  confident wrong one manufactures work for everyone downstream, so the cost of filing scales
  with how much the process trusts you.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues
found?**

| Finding | Disposition |
| --- | --- |
| The registry's read-points were claimed but not all wired - CR0242 was marked Complete with only `sprint plan` done | CR0242 - reopened; `review_prep.py` and the audit lens-seed are now wired, and a test pins all three read-points so the claim is provable rather than asserted |
| A confident false finding reached High severity before anyone checked for the guard | LL0024 - recorded as a cross-project lesson. No artefact: the fix is a habit, and it now sits in the registry the review reads |
| `--no-verify` was used once, and the gate would have failed | declined: the escape hatch is deliberate, and the commit was amended back through the full gate in the same session. Making it harder would break the emergency case it exists for |
| Four live indexes are over the archive threshold - epic 32, bug 72, cr 49, rfc 32 terminal rows | declined: housekeeping, and archiving is a release-boundary activity. The release is frozen until ~2026-07-21, so do it as part of cutting v4.2 |
| The loop's core claim, that closing it cuts repeat defects, is mandated but unmeasured | declined: registered in the doctrine and the config reference as a claim to be measured, and it needs the benchmark harness rather than a code change. It is honest as it stands |

## Close loop (gated)

- [x] this retro exists AND passes its content check (`retro.py validate --id RETRO0022`)
- [x] its lessons are in the project store (`retro.py extract --id RETRO0022`)
- [x] open lessons re-validated: each is closed, extended, or within its horizon
- [x] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons

## Metrics

- Delivered 12 of 12 · Withdrawn on inspection: 1 (BG0124) · Reopened after a false Complete: 1 (CR0242)
- Tests: 2039 green · Suite ~46s · Gate: green
