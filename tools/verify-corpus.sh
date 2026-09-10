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
# The corpus the run is taken over, and the one the identity existence check reads. Overridable
# for the same reason BASELINE is, and it is what lets the lane's whole logic - including the
# check that a baseline identity still EXISTS - be driven against a small fixture corpus.
ROOT="${VERIFY_CORPUS_ROOT:-$REPO}"
PY="${PYTHON:-python3}"
# The lane runs the repository's own scripts and CPython writes `__pycache__` beside them, inside
# the repository. Set at the harness so a caller overriding PYTHON cannot lose it.
export PYTHONDONTWRITEBYTECODE=1

fail() { echo "corpus-verify FAILED: $*" >&2; exit 1; }

baseline_row() {
  local metric="$1" row
  row="$(grep -m1 "^${metric}|" "$BASELINE")"
  [ -n "$row" ] || fail "no baseline row for '$metric' in $BASELINE"
  printf '%s' "$row"
}

baseline_for() {
  local metric="$1" n
  n="$(sed -n "s/^${metric}|\([0-9]*\)|.*/\1/p" "$BASELINE" | head -1)"
  [ -n "$n" ] || fail "no baseline row for '$metric' in $BASELINE"
  echo "$n"
}

# The IDENTITIES behind a metric's count: field 4 of its row, whitespace-separated. Field 3 is
# free prose and is never read as ids, which is why the identities were appended after it rather
# than inserted before: an older three-field row then reads as "no identities recorded" and is
# refused by name, instead of parsing its prose into nonsense ids.
baseline_ids() {
  local metric="$1"
  # pipefail is on, so a missing row's refusal is the pipeline's status and the caller's
  # `|| exit 1` sees it: a `fail` inside a command substitution exits only that subshell.
  baseline_row "$metric" | cut -d'|' -f4
}

ids_count() {
  local n=0 x
  for x in $1; do n=$((n + 1)); done
  echo "$n"
}

# The ids in $1 that are not in $2. Membership is tested on the whole space-delimited token so
# `US0004::AC1` never counts as present because `US0004::AC10` is.
diff_ids() {
  local a="$1" b="$2" x out=""
  for x in $a; do
    case " $b " in *" $x "*) ;; *) out="$out $x" ;; esac
  done
  echo "${out# }"
}

or_none() { if [ -n "$1" ]; then echo "$1"; else echo "(none)"; fi; }

# Does this identity still EXIST in the corpus? A baseline id that no longer resolves is not a
# repair - the unit was deleted, or its criteria renumbered - and counting it as one lets the
# number fall for a reason nobody chose.
identity_exists() {
  local id="$1" rec ac f
  rec="${id%%::*}"
  ac="${id##*::}"
  for f in "$ROOT"/sdlc-studio/stories/"$rec"-*.md "$ROOT"/sdlc-studio/bugs/"$rec"-*.md; do
    [ -f "$f" ] || continue
    if grep -qE "(^|[^A-Za-z0-9])${ac}([^A-Za-z0-9]|\$)" "$f"; then return 0; fi
  done
  return 1
}

# Compare an observed run against its baseline: the COUNT in both directions, as before, and now
# the IDENTITIES behind it. The count alone cannot see an equal-sized swap - one criterion
# repaired and another introduced in the same window - and a swap is the case that matters most,
# because the number is right and the corpus is not.
compare() {
  local metric="$1" observed="$2" observed_ids="${3-}"
  local want base_ids base_n new gone repaired vanished report id
  want="$(baseline_for "$metric")" || exit 1
  base_ids="$(baseline_ids "$metric")" || exit 1
  base_n="$(ids_count "$base_ids")"
  # The baseline's OWN integrity, before it is used to judge anything. A row recording a count
  # its identity list does not support is a record of neither.
  if [ "$base_n" != "$want" ]; then
    fail "$metric: the baseline row records a count of $want and names $base_n identity/identities
  - a count its own list does not support is a record of neither. Fix the '$metric' row in
  $BASELINE so the two agree."
  fi
  new="$(diff_ids "$observed_ids" "$base_ids")"
  gone="$(diff_ids "$base_ids" "$observed_ids")"
  repaired=""
  vanished=""
  for id in $gone; do
    if identity_exists "$id"; then repaired="$repaired $id"; else vanished="$vanished $id"; fi
  done
  repaired="${repaired# }"
  vanished="${vanished# }"
  if [ -n "$new" ] || [ -n "$gone" ]; then
    report="$metric: $observed, baseline $want - the SET moved.
  NEW: $(or_none "$new")
  went green: $(or_none "$repaired")
  VANISHED from the corpus (deleted or renumbered, NOT repaired): $(or_none "$vanished")"
    if [ "$observed" -gt "$want" ]; then
      report="$report
  $((observed - want)) NEW one(s) against the baseline count. The write-time guard refuses a
  selector that resolves to nothing, so a rise means one was introduced by a hand-edit or a test
  rename. Find it, fix it; do not raise the baseline."
    elif [ "$observed" -lt "$want" ]; then
      report="$report
  $((want - observed)) fewer. Good news that must be BANKED: lower the '$metric' row in
  tools/verify-corpus-baseline.txt in this same commit, or the tolerance stays available to
  admit a different defect later."
    else
      report="$report
  The COUNTS MATCH, which is exactly why the identities are recorded: an equal-sized swap is
  silent to a bare number. Record the new set in the '$metric' row of
  tools/verify-corpus-baseline.txt in the same commit that explains it."
    fi
    fail "$report"
  fi
  # The sets agree. The counts can still disagree - the run reported a total its own identity
  # payload does not carry - and that is a defect in the reporting, not a clean lane.
  if [ "$observed" != "$want" ]; then
    fail "$metric: $observed, baseline $want, yet every identity matches - the run reported a
  count its own identity list does not support. Neither figure can be trusted; re-run it."
  fi
  echo "  $metric: $observed (baseline $want) OK - identities match"
}

rehearse_stamps() {
  echo "dead stamps: criteria stamped verified whose selector selects nothing"
  local out n ids
  out="$($PY "$SCRIPTS/verify_ac.py" stamps --root "$ROOT" --bugs 2>&1)"
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
  # The IDENTITIES, from the tool's own per-criterion rows. Read as `<record> <AC>:` and rewritten
  # into the `<record>::<AC>` address the baseline stores, so the two metrics record one shape.
  ids="$(printf '%s\n' "$out" \
         | sed -n 's/^\([A-Za-z][A-Za-z0-9]*\) \(AC[0-9][0-9]*\): stamped verified.*/\1::\2/p' \
         | tr '\n' ' ')"
  compare "dead-stamps" "$n" "${ids% }"
}

rehearse_red() {
  echo "red criteria: criteria that FAIL when executed (~28 minutes)"
  local out n ids
  out="$($PY "$SCRIPTS/gate.py" --root "$ROOT" --release 2>&1)"
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
  # The IDENTITIES, from the red clause's own machine-readable payload. `[^]]*` is the
  # DISCRIMINATOR and it is doing the same job the count parse already needed: the detail is a
  # `; `-joined list and the exclusion ledger prints AFTER the red clause with a per-AC list and
  # bracketed statuses of its own, so a capture that runs past the clause boundary swallows the
  # 67 criteria the metric deliberately excludes and calls them red.
  ids="$(printf '%s\n' "$out" | grep -E '\[(FAIL|warn)\] verify' \
         | grep -oE '\[ids: [^]]*\]' | head -1 | sed 's/^\[ids: //; s/\]$//')"
  compare "red-criteria" "$n" "$ids"
}

case "${1:-full}" in
  stamps) rehearse_stamps ;;
  full)   rehearse_stamps && rehearse_red ;;
  *)      echo "usage: verify-corpus.sh [stamps|full]" >&2; exit 2 ;;
esac
echo "corpus-verify: OK"
