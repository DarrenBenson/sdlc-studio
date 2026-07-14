# RV-0008: Repository review: sdlc-studio skill scripts (architecture, code quality, security)

> **Date:** 2026-07-14
> **Created-by:** sdlc-studio new

## Scope

Three-leg review of the skill's own source: 58 Python scripts under `scripts/` sharing a
1,163-line `lib/sdlc_md.py`, `install.sh` / `install.ps1`, the `tools/` guards, and 73 test files
(2041 tests, green). Legs: architecture, code quality/correctness, defensive security. Run as
`review generate`.

**This was the first review run with the lesson lenses wired (CR0242).** Each leg opened from the
ranked cross-project registry - LL0004 (x45) and LL0008 (x35) at the top - and each was bound by
LL0024: reproduce through the public path, and find the guard before reporting. All three legs
returned a "what I checked and found already guarded" list, which is the discipline working.

## Method note (the missing refute panel)

`review generate` has no refute panel; the adversarial `audit` does (see RFC0033). So every
load-bearing finding was verified by hand through the public CLI before filing. That pass earned
its keep: one architecture finding was declined as speculative (it does not reproduce on the
shipped index layout), and one of the reviewer's own repro commands did not actually run first time
and was redone rather than reported on. A confident false finding costs downstream (LL0024, and
BG0124 earlier this session).

## Findings

**Security: sound.** No High/Critical. The installer verifies a SHA-256 before extraction (parity
across `.sh`/`.ps1`), the sweep only ever removes a directory passing the `is_skill_copy` identity
guard and stages-then-swaps atomically, the AC-verifier `shell=True` is a documented and gated
trust boundary, the http verb blocks non-http(s) schemes and uses no `-L`, and Actions are
SHA-pinned with least-privilege tokens. Two low hardening notes filed (CR0250).

**Code quality: exceptionally hardened.** No false-green, swallowed-failure, or can't-fail-test
bugs in the load-bearing gates. The one under-tested surface is the `grep` verifier verb (BG0125,
BG0128).

**Architecture: solid core, seam-level duplication.** `lib/sdlc_md.py` is a real single source of
truth; the findings are where a second code path re-implements what a first already owns.

| Filed | Sev | Finding |
| --- | --- | --- |
| BG0125 | Medium | `grep` verb: documented `path_glob` example false-REDs; verb has zero test coverage |
| BG0126 | Medium | `meta_new` allocates always-sequential ids without `allocation_lock` |
| BG0127 | Medium | Several `_index.md` writers bypass `atomic_write` |
| BG0128 | Low | `grep` verb: `rg` vs `grep -rqE` dialect swap makes a verdict environment-dependent |
| CR0248 | P2 | Two divergent `archive` writers with incompatible layouts (LL0016) |
| CR0249 | P3 | Per-type status vocab triplicated instead of derived from `sdlc_md` |
| CR0250 | P3 | Security hardening: http host allowlist default + rolling-install checksum note |
| CR0251 | P4 | Friction: `verify_ac run` has no `--file` flag (it is `--story`) |

**Declined (recorded, not filed):** new-row placement (`find_data_header` vs reconcile's scored
master-table selection) can disagree only if a project adds a trailing id-bearing view table after
the master; it does not reproduce on the shipped layout, so it is latent-hypothetical, not a bug.

**Process finding -> RFC0033.** The run surfaced that `audit` (RFC0002, Accepted) was never made
discoverable, while `review generate` grew up beside it doing the same job without the refute
panel. Raised as RFC0033 to reconcile the three-way `audit` overload.

**Persona note.** `review_prep` reports all 3 personas defined but unreferenced in the PRD (Persona
Index, Maya Okafor, Trevor Hale). Not filed here - it is a document-review (`review`) concern, not
a code finding.

## Verdict

The skill's own code is in strong shape: the security posture is sound and the correctness gates
hold under adversarial reading. The real signal is at the module seams - a handful of second code
paths (`archive`, `meta_new`, index writers, the `grep` verb) that re-implement or skip what the
shared library already does correctly, and one accepted-but-unshipped command (`audit`). Eight
findings filed, all verified through the public path; one declined; one process RFC raised.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio; agent; v1 | Created via `new` (deterministic) |
| 2026-07-14 | sdlc-studio; agent; v1 | Report written: 3 legs, 8 findings filed, 1 declined, RFC0033 raised |
