# RETRO-0131: Maya signs a sprint report whose every figure is true, and every tool reports only what it judged

> **Date:** 2026-10-03
> **Run:** RUN-01M3ZAGE
> **Batch:** BG0911, BG0912, BG0913, BG0898, BG0899, BG0900, BG0901, BG0903, BG0904, BG0908, BG0907, BG0914, BG0905, BG0906, BG0910, US0982, BG0870, BG0871, BG0872, BG0873, BG0878, BG0882, BG0902, BG0885, US0981, BG0886, BG0887, BG0888, BG0889, BG0896, BG0915, BG0916, BG0917, BG0918, BG0919, BG0920, BG0925

## Keep

- Run the lanes one after the other and record verdicts, returns and rulings only between builds: no orchestrator commit collided with a builder this run, where RUN-01M3Y7DP had two (LC-014).
- Reviewers work in their own clone or archive under /var/tmp at a named commit, never in the main tree, so reviews run while the next builder builds.
- The repair brief's one line (US0982, CR0608): repairs answering a REJECT carried only their blocking pin, and the lows they did not carry were filed or rest in the verdicts.

## Stop

- Wording a seat ruling more narrowly than it is meant: D0323 said a bare script name counts only inside a code span, so BG0896's reviewer passed a regression in fenced blocks, filed and repaired as BG0925 under D0324.
- Losing a verdict between batches: BG0916's round-2 approve and BG0925's approve went unrecorded until the Fixed gate refused BG0916 and an audit of every unit's latest verdict found BG0925.
- Exporting full repository copies to /tmp: seven review exports exhausted its inodes and turned a builder's suite red on ENOSPC.

## Try

- [LC-005] BG0885's round-1 repair made the finding reader a true inverse and left the sibling supersession reader span-blind, so round 2 found the same defect beside it. When an encoding changes, probe every reader of it, not the one the finding named.
- [new: a page-format rule mark nothing round-trips | build, review] BG0900, BG0913 and the marks BG0898, BG0901 and BG0904 added each shipped with no file-then-revalidate test, so dropping the mark invalidates signed pages while the suite stays green. A new envelope mark ships with its round-trip pin (BG0919 holds the pattern).

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG0921 | not-stop-ship | Claude (orchestrator) | 2026-10-03 |
| BG0922 | not-stop-ship | Claude (orchestrator) | 2026-10-03 |
| BG0924 | not-stop-ship | Claude (orchestrator) | 2026-10-03 |
| BG0926 | not-stop-ship | Claude (orchestrator) | 2026-10-03 |
| BG0927 | not-stop-ship | Claude (orchestrator) | 2026-10-03 |
