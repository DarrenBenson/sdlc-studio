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

  {suite, exit_code, passed, failed, duration, head_sha, tree_hash, log}

Exits with the SUITE's status, so a caller that checks $? is still correct.
Read the file rather than the output - that is the point.

`log` is this run's OWN full output, kept under sdlc-studio/.local/suite-logs/
rather than a rolling file a later run overwrites. A red run prints the failing
test NAMES to stderr before the tail, because a count without a name cannot be
acted on. The ten most recent logs are kept.

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

# A digest of the WORKING TREE's CONTENT, not of the commit (BG0492).
#
# A verdict is necessarily taken at its parent commit, so `head_sha` alone authorises every
# edit made after the suite ran - and an uncommitted working tree is the normal state
# mid-session. With a green verdict at HEAD, staging a syntactically broken file and claiming
# both suites green passed.
#
# Computed as a real git TREE OBJECT, built in a throwaway index: read HEAD, stage everything
# the working tree currently holds, write the tree. That is the whole point - a tree object is
# a function of CONTENT alone, so it cannot tell a staged change from an unstaged one, and
# `git add` on its own can never move the digest.
#
# The first shape of this hashed three things (HEAD, `git diff HEAD`, and untracked file
# hashes) and was REJECTED in review for exactly that: an untracked file contributed
# `sha256  path` while the same bytes staged contributed a new-file patch, so `git add -A`
# alone invalidated a byte-identical tree. On the shipped commit-msg lane that meant the
# ordinary sequence - write a module, run the suite, `git add -A`, commit - was refused and
# told to re-run a nine-minute suite for no information. A guard that refuses always is a
# guard that gets switched off.
#
# Ignored files are excluded by `git add` itself rather than by a flag this script passes, so
# there is no second ignore rule to drift from git's. The verdict's own directory is excluded
# by pathspec on top of that: the verdict is written INTO the tree it describes, so counting it
# would make every verdict differ from its own tree the instant it was recorded. That exclusion
# is by PATH, so it holds whether the file is untracked, staged or committed - the earlier
# version excluded it only while untracked, and a committed verdict could then never match.
tree_state() {
    local idx tree
    idx="$(mktemp "${TMPDIR:-/tmp}/sdlc-tree-index.XXXXXX")" || return 1
    rm -f "$idx"                 # git wants to CREATE the index file, not adopt an empty one
    # `read-tree` seeds from HEAD so an unmodified tree costs almost nothing to stage; on a
    # repo with no commits there is nothing to seed from and `add` builds the index alone.
    GIT_INDEX_FILE="$idx" git read-tree HEAD >/dev/null 2>&1 || true
    GIT_INDEX_FILE="$idx" git add -A -- . >/dev/null 2>&1 || { rm -f "$idx"; return 1; }
    # Dropped from the INDEX rather than excluded by pathspec. `git add -- ':(exclude)<p>'`
    # errors when <p> is also gitignored ("the following paths are ignored"), which is exactly
    # this repository's shape - so the pathspec form returned empty here while every fixture,
    # none of which ignores .local, passed. `rm --cached --ignore-unmatch` is silent whether the
    # path is tracked, untracked or ignored, so one form covers all three.
    GIT_INDEX_FILE="$idx" git rm --cached -r -q --ignore-unmatch \
        -- "sdlc-studio/.local" >/dev/null 2>&1 || true
    tree="$(GIT_INDEX_FILE="$idx" git write-tree 2>/dev/null)"
    rm -f "$idx"
    [[ -n "$tree" ]] || return 1
    printf '%s' "$tree"
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
    # REFUSED, never defaulted - the same rule the run path applies to an unknown suite. Without
    # this, `--check nonsense`, `--check ALL` and `--check --help` all printed GREEN against an
    # `all` verdict, because the coverage test short-circuits on `"$V_SUITE" = all`. A typo in a
    # future hook lane would read as a checked assertion and be none.
    case "$WANT" in
        scripts|tools|all) ;;
        *) echo "run-suite --check: unknown suite ${WANT} - expected scripts, tools or all. " \
                "A verdict cannot be checked against a suite that does not exist." >&2
           exit 2 ;;
    esac
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

# THE BOUNDARY MARKER. This script IS the boundary runner - it is what push, release, close and
# CI invoke - so the tests deferred out of the per-commit gate run here, in full, every time.
# Exported unconditionally rather than per-suite: a marked test that ran under `all` and not
# under `scripts` would make the coverage depend on which word the caller typed.
# See scripts/tests/boundary.py for what may be marked and why (BG0579).
export SDLC_STUDIO_BOUNDARY_SUITE=1

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

# The failing test's NAME is what a red run must leave behind, and until BG0513 this script
# destroyed it: the full output went to a `mktemp` file removed by an EXIT trap, and only
# `tail -25` reached stderr. unittest prints its `FAIL:` headers well above the closing
# `FAILED (failures=1)` line, so the tail carried the COUNT and never the NAME. That is why an
# intermittent red in the full runner went unnamed across five invocations - the evidence was
# captured and then deleted, every time.
#
# The log is per-RUN, not one rolling file. A rolling log belongs to whichever run wrote last,
# so the log a verdict points at stops describing that verdict the moment another run starts -
# and the moment you read it is precisely when a later run has already happened. The verdict
# records its own log path, so "the output behind THIS verdict" stays answerable.
#
# It lives under .local/, which `tree_state` drops from its index, so preserving it cannot move
# the tree hash the verdict binds itself to.
LOG_DIR_REL="sdlc-studio/.local/suite-logs"
mkdir -p "$LOG_DIR_REL"
LOG_REL="$LOG_DIR_REL/${SUITE}-$(date +%s)-$$.log"
OUT="$PROJECT_ROOT/$LOG_REL"

# Bounded, or a directory of full-suite logs grows without limit. Newest kept, by mtime, and
# only within this directory - the names are generated here and hold no spaces or newlines.
prune_suite_logs() {
    local keep=10
    # shellcheck disable=SC2012 # our own generated filenames; no unsafe characters
    ls -1t "$LOG_DIR_REL"/*.log 2>/dev/null | tail -n "+$((keep + 1))" | while read -r old; do
        rm -f "$old"
    done
}

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
  "tree_hash": "$TREE_HASH",
  "log": "$LOG_REL"
}
EOF

prune_suite_logs

if [[ $RC -eq 0 ]]; then
    echo "suite $SUITE: GREEN (${PASSED} passed, ${DURATION}s) -> $VERDICT_REL"
else
    # The detail goes to STDERR on failure only: a red run is the one time it is worth seeing,
    # and stderr keeps stdout to the single verdict line.
    echo "suite $SUITE: RED (exit $RC, ${DURATION}s) -> $VERDICT_REL"
    # NAMES first, then the tail. Both runners are matched because the batch runs both and a
    # red can come from either: unittest emits `FAIL: test_x (mod.Class)`, pytest's short
    # summary emits `FAILED path::Class::test_x - AssertionError`. Reporting the count without
    # the name is the whole of BG0513.
    NAMED="$(grep -E '^(FAIL|ERROR): |^FAILED ' "$OUT" || true)"
    if [[ -n "$NAMED" ]]; then
        printf '  failing test(s):\n%s\n' "$NAMED" >&2
    else
        # Stated rather than left blank. "No header matched" and "no failure" are different
        # facts, and a silent absence here reads as the second.
        printf '  no FAIL:/ERROR: header matched - the full log is the only record\n' >&2
    fi
    printf '  full output: %s\n' "$LOG_REL" >&2
    tail -25 "$OUT" >&2
fi
exit $RC
