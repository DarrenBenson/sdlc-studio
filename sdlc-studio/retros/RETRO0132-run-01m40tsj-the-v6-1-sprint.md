# RETRO-0132: Maya installs v6.1.0 and every page she reads, from release notes to sprint report, matches the code

> **Date:** 2026-10-03
> **Run:** RUN-01M40TSJ
> **Batch:** BG0926, BG0927, BG0924, BG0921, BG0922, BG0930, BG0929, US0984, US0983, US0985, BG0931, BG0932, BG0933, BG0934, BG0935, BG0936

## Keep

- Brief each paperwork reviewer to run what the doc claims in a fixture, not to read it (D0328): the reviews of US0983, US0984 and BG0935 caught migrate over-claims, a test blind to bare file names and an install sentence a fix had made false, each by executing the claim.
- Hold the cut until every other unit's review is back: a repair after the cut would have left its fragment out of the 6.1.0 entry.
- Run the real interpreter for a script's test where the tree lacks it: BG0934's static read passed three broken defaults; real pwsh in a network-less container caught all three.

## Stop

- Reading "found issues are fixed in the run" (D0326) without a stop: each review raised new lows, so the residue unit and an operator stop (D0333) had to be added mid-run to end the loop.
- Writing a criterion's Verify pattern that the link guard reads as a link (US0985's grep), and a story text that links a file the sprint has not written yet.

## Try

- [new: a doc claim checked by reading | review] A sentence about shipped code is proven only by running the code it describes. A paperwork review runs each command, figure and replacement the doc names against a fixture before it approves; US0984's and US0983's round-1 findings were all sentences a reader would have believed.
- [LC-005] BG0922's narrowed note parser and US0984's widened test each fixed the named case and missed its neighbour (punctuation before the ratio, bare file names). Probe the forms next to the one the finding named.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
