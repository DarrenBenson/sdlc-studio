<!-- close-status:begin -->
> **RUN-01M3BK9Y closed partial.** 35 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3CK1K, Sprint 5 of the v6 release: the lean loop runs on a fresh v6 project, and
> the release candidate is prepared.** Goal: "Maya runs the lean loop on a fresh v6 project, and
> the release candidate ships." 37 of 37 batch units delivered, each reviewed by one QA-seat
> reviewer under the two-round cap: 18 were rejected at round 1, all converged at round 2 but
> US0941, which was carried as BG0775 and landed in the same run. Verdict: achieved.
>
> Closing review of record: RETRO0125.

## What landed

- **The review record is one verdict ledger (EP0263).** The repair ledger (US0914), the sign-off
  verbs (US0919), the evidence and sprint-review verbs (US0918), the mutation ledger verbs
  (US0936) and the brief-provenance refusal (US0923) are gone; line coverage is opt-in (US0922);
  a standing REJECT clears only by a round-2 APPROVE or by carrying the unit. Every retired
  criterion is recorded in the D0259 pattern and the historic record is read frozen.
- **A fresh v6 project runs the whole loop on the shipped defaults (US0950, US0951).** `critic.py
  brief` falls back to the shipped seat card, a clean run's report hands over no false known
  issue, and the retro reads a schema v3 project's ULID ids (BG0778).
- **An upgrader crosses from v5.1 to v6 (US0925, US0938).** `migrate --apply` strips every
  retired review key and `[check:]` tag, derived from the last tag's defaults, and the release
  rehearsal walks a v5.1 project across with every tolerated gap naming an open owner (BG0785).
- **Every criterion on a Done story passes or is retired with its reason (US0940)**, and the
  verify-corpus baseline is 0.
- **The tag and the signature are honest.** The release tag is refused only for what a release
  needs (US0942); a signed report is anchored to the fingerprint its run signed (BG0775) and its
  unit rounds are windowed to the run (BG0787).
- Smaller fixes: every Verify line under a criterion runs (BG0687, BG0777), the allocation lock
  fails closed and names its errors (US0948, BG0780, BG0781), the hook shows the stamped-test
  re-read list (US0945, BG0779), close-written files pass markdownlint (US0947), a Low finding
  mints its own bug (BG0731), and the CI teardown race is traced to git 2.55's detached
  maintenance (BG0711).

## What is owed

- **Sprint 6 (EP0266): the docs and the site.** US0924 (the skill docs, several retired verbs
  still named in references), US0926 (this repo on shipped defaults), the website units, the
  whitepaper PDF, and the v6.0.0 cut.
- **Open Medium bugs filed this run**, disclosed in known issues: BG0782 (57 test modules share
  the git-maintenance race), BG0783 (run-state review rounds are write-dead), BG0784 (a role-less
  seat card is bypassed silently), BG0785 (migrate names no conformance cutoff), BG0786
  (`flow.py compute` takes 90 s and times the push gate out under load), BG0788 (signed-report
  rounds are positional; lands with CR0599).
- **CR0599 (High)**: the signature record lives in the gitignored `.local`, so only the signing
  clone can verify a signed report.
- **Commits run over the 90 s budget** on hub modules (110-171 s this run); BG0754 stays open.
