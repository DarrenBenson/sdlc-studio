#!/usr/bin/env bash
# The corpus verification lane: does the repository's own evidence still hold?
#
# Two questions no per-commit lane can afford to ask, and which therefore went unasked for long
# enough that 53 acceptance criteria went red across stories already marked Done while README.md
# told readers acceptance criteria "are executable and get run" - true of the mechanism, false of
# the corpus.
#
#   dead-stamps    a criterion stamped `Verified: yes` whose selector now selects NOTHING.
#                  Cheap (~30s): resolution is by collection, one per distinct test file.
#   red-criteria   a criterion that FAILS when actually executed. Expensive (~28 minutes against
#                  a 600s budget), which is exactly why nothing ran it and the rot accumulated.
#
# Both are compared against `tools/verify-corpus-baseline.txt` and the comparison reddens in BOTH
# directions - a count above blocks as a new defect, a count below blocks as a baseline to lower.
# A lane that only ever tolerates is one that never empties.
#
#   verify-corpus.sh stamps    the cheap half only
#   verify-corpus.sh full      both (the scheduled lane)
#
# Exit status is read directly, never through a pipe: a pipe reports the last stage's status and
# this repository has read a red suite as green that way twice in one session.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$REPO/.claude/skills/sdlc-studio/scripts"
# Overridable so the lane's own LOGIC - the two-directional comparison, reading the tool's total
# rather than counting rows, refusing to read a missing total as zero - is testable without the
# ~28-minute run it wraps. A lane whose logic can only be exercised by paying its full cost is one
# whose logic never gets exercised.
BASELINE="${VERIFY_CORPUS_BASELINE:-$REPO/tools/verify-corpus-baseline.txt}"
PY="${PYTHON:-python3}"
# The lane runs the repository's own scripts and CPython writes `__pycache__` beside them, inside
# the repository. Set at the harness so a caller overriding PYTHON cannot lose it.
export PYTHONDONTWRITEBYTECODE=1

fail() { echo "corpus-verify FAILED: $*" >&2; exit 1; }

baseline_for() {
  local metric="$1" n
  n="$(sed -n "s/^${metric}|\([0-9]*\)|.*/\1/p" "$BASELINE" | head -1)"
  [ -n "$n" ] || fail "no baseline row for '$metric' in $BASELINE"
  echo "$n"
}

# Compare an observed count against its baseline, reddening in both directions.
compare() {
  local metric="$1" observed="$2" want
  want="$(baseline_for "$metric")" || exit 1
  if [ "$observed" -gt "$want" ]; then
    fail "$metric: $observed, baseline $want - $((observed - want)) NEW one(s). The write-time
  guard refuses a selector that resolves to nothing, so a rise means one was introduced by a
  hand-edit or a test rename. Find it, fix it; do not raise the baseline."
  fi
  if [ "$observed" -lt "$want" ]; then
    fail "$metric: $observed, baseline $want - $((want - observed)) fewer. Good news that must be
  BANKED: lower the '$metric' row in tools/verify-corpus-baseline.txt in this same commit, or the
  tolerance stays available to admit a different defect later."
  fi
  echo "  $metric: $observed (baseline $want) OK"
}

rehearse_stamps() {
  echo "dead stamps: criteria stamped verified whose selector selects nothing"
  local out n
  out="$($PY "$SCRIPTS/verify_ac.py" stamps --root "$REPO" --bugs 2>&1)"
  # Read the tool's OWN total, never a count of rows matching a shape. Counting `::` lines was the
  # first thing written here and it reported 3 for a corpus of 5: two of the dead selectors are a
  # `-k` pattern and a bare file target, neither of which carries `::`. A lane that miscounts is
  # worse than no lane, because the number it prints is the one nobody re-derives.
  n="$(echo "$out" | sed -n 's/^verify-stamps: \([0-9]*\) stamped AC(s).*/\1/p' | head -1)"
  if [ -z "$n" ]; then
    # No total line: either it found none (the clean path prints its own wording) or it broke.
    if echo "$out" | grep -qi "no stale\|0 stamped\|clean"; then n=0; else
      echo "$out" >&2
      fail "the stamp sweep printed no total - it did not complete, and 0 is not the same fact"
    fi
  fi
  compare "dead-stamps" "$n"
}

rehearse_red() {
  echo "red criteria: criteria that FAIL when executed (~28 minutes)"
  local out n
  out="$($PY "$SCRIPTS/gate.py" --root "$REPO" --release 2>&1)"
  # Read the count out of whichever clause carries it, never by position. The lane's detail is a
  # `; `-joined list and the unspecified-AC clause comes FIRST and contains colons of its own, so
  # an anchored `[^:]*` walk from the lane name cannot reach the red clause on a run that has both
  # - it returned empty against the live shape and the lane then refused as "did not complete"
  # while a real red count sat in the output it had just printed.
  n="$(printf '%s\n' "$out" | grep -E '\[(FAIL|warn)\] verify' \
       | grep -oE '[0-9]+ red AC' | head -1 | grep -oE '^[0-9]+')"
  if [ -z "$n" ]; then
    # The lane did not report a red count at all: either it passed outright, or it died before
    # reporting. Those are different facts and must not be collapsed into "0".
    # The PASS marker is `[PASS]`, the string gate.py actually renders. This read `[ OK ]`, which
    # occurs nowhere in the tree, so the green path was unreachable: once the corpus is repaired
    # and this baseline reaches 0 - the end state the lane exists to force - it could never have
    # gone green, and it would have said something false about why.
    if printf '%s\n' "$out" | grep -qE '\[PASS\] verify'; then n=0; else
      echo "$out" >&2
      fail "the verify lane reported no red count and did not pass - it did not complete"
    fi
  fi
  compare "red-criteria" "$n"
}

case "${1:-full}" in
  stamps) rehearse_stamps ;;
  full)   rehearse_stamps && rehearse_red ;;
  *)      echo "usage: verify-corpus.sh [stamps|full]" >&2; exit 2 ;;
esac
echo "corpus-verify: OK"
