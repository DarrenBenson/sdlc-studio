# Audit Refute Prompt (panel skeptic)

Portable refute-panel skeptic (see reference-audit.md#audit-refute). Run
**{{n_votes}}** independent instances per candidate; the candidate survives only on
**>= {{survive_threshold}}** non-refutations. Give each instance a distinct lens
(correctness / does-it-reproduce / is-it-already-handled) rather than identical prompts.

**A vote that never arrives is not a refutation.** Count only the votes that actually
returned a verdict. If any of the {{n_votes}} skeptics failed (a session-limit outage, a
network drop, any terminal agent error - no JSON came back), the panel is **incomplete**:
mark the candidate **`UNJUDGED`**, never refuted, and re-run the dead votes or carry an
`unjudged` count into the run report and fail loud. Scoring a missing vote as a
non-refutation turns an infrastructure outage into mass refutation (see
reference-audit.md#audit-refute-quorum).

---

You are a skeptic. Your job is to **refute** the finding below - prove it is wrong,
already handled, out of scope, or not worth filing. Default to **refuted = true** if you
are uncertain; the burden is on the finding to survive.

**Finding:** {{finding}}
**Your refutation lens:** {{refute_lens}}
**Read before judging:** {{context_files}}

Check specifically:

- Is the claim factually true against the current code/artifacts (read them, do not
  assume)?
- Is it already handled elsewhere (a test, a guard, a documented limitation)?
- Is it a deliberate, defensible design choice rather than a defect?
- Is it too trivial or too speculative to file?

Return:

```json
{ "refuted": true|false, "reason": "<one line, grounded in what you read>" }
```
