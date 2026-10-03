<!-- close-status:begin -->
> **RUN-01M40TSJ closed goal-reached.** 19 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M40TSJ, the v6.1 sprint.** Goal: "Maya installs v6.1.0 and every page she reads,
> from release notes to sprint report, matches the code." The whole backlog plus the release
> paperwork (D0325), with every finding raised in the run fixed in it (D0326) and a residue
> unit to end the review loop (D0333). Every unit reviewed by an independent QA seat; the
> paperwork reviews ran each claim in a fixture rather than reading it (D0328).

## What landed

- **v6.1.0 is cut, not yet tagged.** Version homes read 6.1.0 (`check_versions --strict`), the
  changelog fragments are folded into `## [6.1.0]` (`release_cut.py changelog-cut`), the
  known-issues page discloses no open finding and the bar is met, README and INSTALL pin
  `--version v6.1.0`, and the release rehearsal passes (US0985). The tag waits on the signature
  and `gate.py --release` (D0328, D0329).
- **The paperwork matches the code.** Release notes that lead with what changed and name each
  breaking change beside its replacement (US0983, BG0935); an upgrade path from 6.0 and
  specifications with no retired surface (US0984); `migrate` names the retired handoff
  commands, and the changelog cut places their table cleanly (BG0929).
- **The close and report.** A lane return between close and sign records nothing (BG0926);
  broken transcript links no longer crash the report (BG0927, BG0932); the Minutes reason and
  the goal-note check say what is true (BG0924, BG0922); goal-review and appetite messages name
  the right key and run (BG0921, BG0930, BG0933); four unpinned behaviours and the review
  residue are pinned (BG0931, BG0936).
- **Before the sign (D0334).** The operator ruled the last reviews' five lows fixed before the tag (BG0938); reopening the closed, unsigned run needed BG0937 first, so a run closed and not yet signed can now be reopened and record the work added to it.
- **Install.** `install.ps1` defaults to the latest release as `install.sh` does, tested by
  running it under pwsh with the lookup stubbed (BG0934); main's Windows CI then caught that it
  read the release's checksum sidecar as bytes and refused every release install, fixed and
  checked against a real v6.0.0 install before the tag (BG0939, D0336).

## What is owed

- **The release:** after the signature, `gate.py --release` exit 0, `release_cut.py
  record-green` and `tag-check`, the `v6.1.0` tag and its GitHub release (D0329).
- **The website sprint** in sdlc-studio-web, groomed and ready (D0327): its backlog and the 6.1
  site update, with a check-in before the deploy.
- Every seat ruling is in the decision log (D0328, D0330-D0333, D0335, D0336); the operator's are D0325-D0327,
  D0329 and D0334.
