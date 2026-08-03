#!/bin/bash
# Run a test suite and write its verdict where it can be READ, not interpreted.
# Usage: tools/run-suite.sh scripts|tools|all
#
# `npm test 2>&1 | tail -15` reports TAIL's exit status, not the suite's. The runners set
# `set -uo pipefail`; the ad-hoc shell that invokes them does not. That cost two false claims
# in one session - a commit reported as landed when the hook had refused it, and a suite
# reported green with a real failure in it.
#
# Telling people to be careful does not fix it: the pipe is there because a six-minute suite's
# output does not fit in one read, so the incentive comes back every run. This prints ONE line
# and writes the verdict to sdlc-studio/.local/suite-verdict.json, so the question "was it
# green" is answered by reading a field instead of interpreting a stream.
#
# The verdict is written on FAILURE as well as success, and deliberately overwrites: a wrapper
# that skipped the write on a red run would leave the previous GREEN verdict in place, which is
# worse than none because it is stale and looks current.

set -uo pipefail

# The root is resolved from where the script was INVOKED, not from where it lives. Anchoring
# to the script's own directory means a run inside another checkout - a worktree, a fixture -
# writes its verdict into the source tree instead, so the file would describe a suite that was
# never run there. Caught by this script's own tests writing into the real repo.
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
VERDICT_REL="sdlc-studio/.local/suite-verdict.json"

usage() {
    cat <<'EOF'
Usage: tools/run-suite.sh scripts|tools|all
       tools/run-suite.sh --check [scripts|tools|all]

Runs a suite, prints one verdict line, and writes the full verdict to
sdlc-studio/.local/suite-verdict.json:

  {suite, exit_code, passed, failed, duration, head_sha, tree_hash}

Exits with the SUITE's status, so a caller that checks $? is still correct.
Read the file rather than the output - that is the point.

--check confirms a verdict is current and covers the suite asked about. With no
suite named it requires `all`, because an unqualified claim of greenness is a
claim about the whole tree and only `all` establishes that. `--check scripts`
asserts the narrower thing; an `all` verdict satisfies it, having run that suite.

Options:
  --help, -h    Show this help
EOF
}

# The hasher, chosen once. coreutils on Linux, BSD `shasum` elsewhere; absent on neither is
# treated as a reason to refuse rather than to skip - see `tree_state`.
_hash_cmd() {
    if command -v sha256sum >/dev/null 2>&1; then printf 'sha256sum'
    elif command -v shasum >/dev/null 2>&1; then printf 'shasum -a 256'
    else printf ''; fi
}

# A digest of the TRACKED WORKING TREE, not of the commit (BG0492).
#
# A verdict is necessarily taken at its parent commit, so `head_sha` alone authorises every
# edit made after the suite ran - and an uncommitted working tree is the normal state
# mid-session. With a green verdict at HEAD, staging a syntactically broken file and claiming
# "Both suites green." passed.
#
# Three inputs, each for a case the others miss: the commit, so a new commit invalidates;
# `git diff HEAD`, which covers staged AND unstaged edits to tracked files (BG0492's own
# reproduction stages the file, so reading the unstaged diff alone would see nothing); and the
# CONTENT of untracked files, because a new module is the commonest mid-session change and is
# untracked until somebody adds it.
#
# `--exclude-standard` keeps ignored files out, and the verdict's own directory is excluded
# explicitly on top of that: the verdict is written INTO the tree it describes, so counting it
# would make every verdict differ from its own tree the instant it was recorded, and a guard
# that refuses always is a guard that gets switched off. In this repo `.local/` is gitignored
# and the exclusion is redundant; in a fixture that has not written a .gitignore yet it is not.
tree_state() {
    local h; h="$(_hash_cmd)"
    [[ -z "$h" ]] && return 1
    {
        git rev-parse HEAD 2>/dev/null || echo nohead
        git diff HEAD --binary 2>/dev/null
        git ls-files --others --exclude-standard -z 2>/dev/null \
            | { grep -zv '^sdlc-studio/\.local/' || true; } \
            | xargs -0 -r $h 2>/dev/null | sort
    } | $h | cut -d' ' -f1
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage; exit 0
fi

# --check is the half that makes the verdict load-bearing. Writing a verdict nobody reads
# changes nothing; this turns "I ran the suite" from a claim into a fact a gate can refuse.
if [[ "${1:-}" == "--check" ]]; then
    cd "$PROJECT_ROOT" || exit 2
    if [[ ! -f "$VERDICT_REL" ]]; then
        # ABSENT never reads as green. That is the fail-open shape, and it is exactly the
        # state - a suite that was never run - the check exists to catch.
        echo "run-suite --check: no suite verdict at $VERDICT_REL - run 'tools/run-suite.sh all' " \
             "before claiming the suite is green" >&2
        exit 1
    fi
    V_RC="$(grep -oE '"exit_code":[[:space:]]*-?[0-9]+' "$VERDICT_REL" | grep -oE '\-?[0-9]+' || echo missing)"
    V_SHA="$(grep -oE '"head_sha":[[:space:]]*"[^"]*"' "$VERDICT_REL" | sed 's/.*"\([^"]*\)"$/\1/' || echo missing)"
    V_SUITE="$(grep -oE '"suite":[[:space:]]*"[^"]*"' "$VERDICT_REL" | sed 's/.*"\([^"]*\)"$/\1/' || echo missing)"
    V_TREE="$(grep -oE '"tree_hash":[[:space:]]*"[^"]*"' "$VERDICT_REL" | sed 's/.*"\([^"]*\)"$/\1/' || echo "")"
    HEAD_NOW="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
    # Which suite the caller is entitled to claim. Unqualified means the WHOLE tree, because
    # that is what an unqualified claim of greenness asserts - the commit-msg lane matches
    # "Both suites green." and called a bare --check, which never read this field at all.
    WANT="${2:-all}"
    if [[ "$V_SHA" != "$HEAD_NOW" ]]; then
        echo "run-suite --check: the suite verdict is STALE - taken at ${V_SHA:0:12}, HEAD is " \
             "${HEAD_NOW:0:12}. A verdict from an earlier commit exists and looks current, " \
             "which is worse than none. Re-run the suite." >&2
        exit 1
    fi
    # The TREE, checked after the commit and before the exit code: a verdict at the right sha
    # over a tree that has since moved is the same stale-but-current-looking shape, and it is
    # the commoner one - every uncommitted edit lands in it.
    TREE_NOW="$(tree_state || true)"
    if [[ -z "$TREE_NOW" ]]; then
        echo "run-suite --check: cannot hash the working tree - no sha256sum or shasum on PATH, " \
             "so whether the tree still matches the verdict is UNKNOWN. Refusing rather than " \
             "assuming, because an unverifiable green is the shape this check exists to remove." >&2
        exit 1
    fi
    if [[ -z "$V_TREE" ]]; then
        echo "run-suite --check: the verdict records no tree_hash - it predates the tree binding " \
             "and cannot say whether the working tree has moved since. Re-run the suite." >&2
        exit 1
    fi
    if [[ "$V_TREE" != "$TREE_NOW" ]]; then
        echo "run-suite --check: the working TREE has changed since the verdict was taken " \
             "(recorded ${V_TREE:0:12}, now ${TREE_NOW:0:12}) - the verdict authorises the commit " \
             "it ran at, not the edits made after it. Re-run the suite." >&2
        exit 1
    fi
    # Coverage, not equality: `all` ran the scripts suite, so it answers a request for
    # `scripts`. Equality would refuse a verdict that genuinely covers the question asked.
    if [[ "$WANT" != "$V_SUITE" && "$V_SUITE" != "all" ]]; then
        echo "run-suite --check: the recorded verdict is from the '$V_SUITE' suite, which does " \
             "not cover a claim about '$WANT'. Run 'tools/run-suite.sh $WANT'." >&2
        exit 1
    fi
    if [[ "$V_RC" != "0" ]]; then
        echo "run-suite --check: the recorded verdict is RED (exit $V_RC) at this HEAD" >&2
        exit 1
    fi
    echo "suite verdict: GREEN ($V_SUITE) at ${HEAD_NOW:0:12}, tree ${TREE_NOW:0:12}"
    exit 0
fi

SUITE="${1:-}"
case "$SUITE" in
    scripts) CMD='python3 -B -m pytest .claude/skills/sdlc-studio/scripts/tests -q' ;;
    tools)   CMD='PYTHONPATH=tools/tests python3 -B -m unittest discover -s tools/tests' ;;
    all)     CMD='python3 -B -m pytest .claude/skills/sdlc-studio/scripts/tests -q && PYTHONPATH=tools/tests python3 -B -m unittest discover -s tools/tests' ;;
    *)
        # REFUSED, never defaulted. Running a different suite and reporting it under the
        # requested name is a false green of exactly the kind this script exists to remove,
        # and no verdict is written - an absent verdict is honest, a wrong one is not.
        echo "run-suite: unknown suite ${SUITE:-<none>} - expected scripts, tools or all" >&2
        usage >&2
        exit 2
        ;;
esac

# FOR THE TESTS. A test that shelled out to the real six-minute suite to check this script's
# bookkeeping could not run in a suite itself; one that mocked the script entirely would test
# nothing. Documented rather than hidden, because an undocumented env hook is a trapdoor.
CMD="${SUITE_CMD_OVERRIDE:-$CMD}"

cd "$PROJECT_ROOT" || exit 2
mkdir -p "$(dirname "$VERDICT_REL")"

OUT="$(mktemp)"
trap 'rm -f "$OUT"' EXIT

START="$(date +%s)"
# Bytecode is purged so a same-length mutant cannot be served from a cached .pyc - the false
# SURVIVED this repo has been bitten by before.
find . -name "__pycache__" -not -path "./node_modules/*" -not -path "./.claude/worktrees/*" \
    -exec rm -rf {} + 2>/dev/null
bash -c "$CMD" >"$OUT" 2>&1
RC=$?
DURATION=$(( $(date +%s) - START ))

# Counts are best-effort across two runners with different report lines; an unparseable count
# is recorded as null rather than 0, because "not stated" and "none" are different facts.
PASSED="$(grep -oE '([0-9]+) passed' "$OUT" | tail -1 | grep -oE '[0-9]+' || true)"
FAILED="$(grep -oE '([0-9]+) failed' "$OUT" | tail -1 | grep -oE '[0-9]+' || true)"
if [[ -z "$PASSED" ]]; then
    PASSED="$(grep -oE '^Ran ([0-9]+) tests' "$OUT" | tail -1 | grep -oE '[0-9]+' || true)"
fi
[[ -z "$PASSED" ]] && PASSED=null
[[ -z "$FAILED" ]] && FAILED=null

HEAD_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
# Taken AFTER the run, so it describes the tree the suite actually saw rather than the one it
# started against - a run that rewrites a fixture would otherwise record a hash for a state
# that no longer exists. Recorded empty when the tree cannot be hashed; `--check` refuses on
# an empty one rather than skipping the comparison.
TREE_HASH="$(tree_state || true)"

cat > "$VERDICT_REL" <<EOF
{
  "suite": "$SUITE",
  "exit_code": $RC,
  "passed": $PASSED,
  "failed": $FAILED,
  "duration": $DURATION,
  "head_sha": "$HEAD_SHA",
  "tree_hash": "$TREE_HASH"
}
EOF

if [[ $RC -eq 0 ]]; then
    echo "suite $SUITE: GREEN (${PASSED} passed, ${DURATION}s) -> $VERDICT_REL"
else
    # The tail of the output goes to STDERR on failure only: a red run is the one time the
    # detail is worth seeing, and stderr keeps stdout to the single verdict line.
    echo "suite $SUITE: RED (exit $RC, ${DURATION}s) -> $VERDICT_REL"
    tail -25 "$OUT" >&2
fi
exit $RC
