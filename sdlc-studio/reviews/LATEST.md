<!-- close-status:begin -->
> **RUN-01M3RPSK closed goal-reached.** 7 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3RPSK, the Jonah upgrade sprint: achieved.** Goal: "Jonah's team installs v6 via
> Claude Code or Copilot CLI; migrate predicts the gate's reconcile, conformance, validate and
> floor failures." 7 of 7 batch units approved by one independent QA seat each, two of them in
> round 2 (BG0853, BG0856). BG0852 was carried at the cap into BG0856 (operator ruling), then
> moved to Fixed by a recorded override (D0288) because the cap refused its reviewer's at-HEAD
> APPROVE (BG0850).

## What landed

- **Copilot CLI gets the skill (BG0852, BG0856).** `install.sh` installs Copilot globally into
  `~/.agents/skills`, `--target auto` selects it, and the default install names a detected tool
  only when no folder it reads holds a copy (one `read_dirs` table). install.ps1 is BG0855.
- **migrate predicts the gate (BG0842, BG0843, BG0844, BG0845, BG0854).** One reconcile tally
  shared with the gate; the engagement-floor and conformance cutoffs named, an existing cutoff
  worded as a raise, author-less APPROVE rows counted apart; the `.gitignore` for `.local/` seeded;
  every item carries the gate's lane and count. On a committed v4.1-shaped project migrate and
  the gate agree on all four lanes (3/2/4/2), and git status stays clean.
- **AGENTS.md names the skill through `<skill>` (BG0853)**; migrate reports a line that names one
  tool's install folder, never rewriting it.

## What is owed

- **Filed from this run:** BG0855 (install.ps1), BG0857 (unreadable dirs read as absence), BG0858
  (ULID-only conformance failures unnamed), BG0859 (the close stops approved bugs and names a
  Review status bugs lack), BG0860 (a plan preview writes forecast rows), BG0861 (nothing opens a
  delivery batch since US0918), and eleven Lows on CR0592.
- **BG0850** is now the way a carried unit's approval is refused; this run paid it once.
- **Push** the close commits; the installed copy is forward-ported.
