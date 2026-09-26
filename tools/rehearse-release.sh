#!/usr/bin/env bash
# Drive the paths every adopter arrives on, through the shipped CLI, on fixtures built from
# nothing.
#
# Every other check in this repository runs against this repository. The situations a user is
# actually in - a project that has just been created, and a project being upgraded from v4 or
# v5.1 - are the ones this repository cannot occupy, and the first two were found broken the
# first time anybody walked them. Twenty minutes of walking them by hand turned up three
# consumer-facing defects that a 6000-test suite, twenty gate lanes and a 250-point backlog had
# all missed.
#
#   rehearse-release.sh greenfield   init a project from nothing, reach a written sprint plan
#   rehearse-release.sh upgrade      build a v4-era workspace, migrate it, gate it
#   rehearse-release.sh upgrade-v5   build a v5.1 workspace, migrate it, gate it
#   rehearse-release.sh all          all three, in that order
#
# Exit 0 only when the path completes. Every command is invoked as the shipped CLI and its exit
# status is read directly - never through a pipe, because a pipe reports the last stage's status
# and this repository has read a red suite as green that way twice in one session.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$REPO/.claude/skills/sdlc-studio/scripts"
BASELINE="$REPO/tools/release-rehearsal-baseline.txt"
PY="${PYTHON:-python3}"
# The harness runs the repository's own scripts, and CPython writes `__pycache__` beside them -
# INSIDE the repository, which is what US0664 AC3 says must not happen. It was invisible until
# round 3 taught `_git_status` to report ignored files, and then the criterion's own verifier
# passed only because a sibling test warmed the cache first. Set at the harness, so a caller
# overriding PYTHON cannot lose it.
export PYTHONDONTWRITEBYTECODE=1

# Fixtures are built under a temporary root and NOTHING is written inside the repository. A
# caller-supplied root that defaulted to `.` once destroyed 23 mutation registrations in this
# working tree, so the root here is never taken from an argument.
WORK="$(mktemp -d)"
# REFUSE a work root inside the repository, before the cleanup trap is armed. The trap is
# `rm -rf "$WORK"`, so a work root pointed at the repository deletes the working tree - a
# reviewer applying this file's own declared mutant lost a git worktree that way. The guard
# costs one comparison and removes the whole class.
case "$WORK" in
  "$REPO"|"$REPO"/*) echo "rehearsal REFUSED: the work root must not be inside the repository ($WORK)" >&2; exit 2 ;;
esac
trap 'rm -rf "$WORK"' EXIT

fail() { echo "rehearsal FAILED: $*" >&2; exit 1; }
step() { echo "  - $*"; }

# ---------------------------------------------------------------- greenfield

rehearse_greenfield() {
  echo "greenfield: a project that has just been created reaches a written sprint plan"
  local root="$WORK/greenfield"
  mkdir -p "$root"

  step "init run"
  $PY "$SCRIPTS/init.py" --root "$root" run >/dev/null 2>&1 \
    || fail "greenfield: \`init run\` did not complete"

  # An ordinary first story: it describes code nobody has written, so NONE of its declared paths
  # exists. That is the whole point of the fixture - it is the shape every greenfield story has.
  cat > "$root/sdlc-studio/stories/US0001-signup.md" <<'STORY'
# US0001: a visitor can sign up with an email address

> **Status:** Ready
> **Epic:** EP0001
> **Priority:** High
> **Affects:** src/auth/signup.py, tests/test_signup.py
> **Points:** 3

## Acceptance Criteria

### AC1: an account is created

- **Given** a valid email address
- **When** the signup form is submitted
- **Then** an account exists
- **Verify:** shell true
STORY

  echo "US0001" > "$root/worklist.txt"

  step "sprint plan --write"
  $PY "$SCRIPTS/sprint.py" --root "$root" plan --worklist "$root/worklist.txt" --write \
        --sprint-goal "a visitor can sign up" >/dev/null 2>&1 \
    || fail "greenfield: \`sprint plan --write\` refused a first sprint (exit $?)"

  [ -f "$root/sdlc-studio/.local/run-state.json" ] \
    || fail "greenfield: sprint plan exited 0 but wrote no run"
  grep -q "US0001" "$root/sdlc-studio/.local/run-state.json" \
    || fail "greenfield: a run was written but the story is not in its batch"

  echo "greenfield: OK"
}

# ------------------------------------------------------------------- upgrade

# The upgrade does NOT reach a green gate today: conformance fails on a freshly migrated project,
# and the remedy is the grandfathering work in a later charter. (Its stale indexes still show,
# reported rather than refused, as mechanical drift the reconcile and index-derived lanes name.)
# Claiming green here would be exactly the false claim this rehearsal exists to prevent, so the
# failing lanes are compared against a recorded baseline and the comparison reddens in BOTH
# directions - a new failure blocks, and a baselined lane that starts passing blocks too, because
# a baseline that only ever tolerates is one that never empties.
rehearse_upgrade() {
  echo "upgrade: a v4-era project migrates, and its gate matches the recorded baseline"
  local root="$WORK/upgrade"
  mkdir -p "$root"

  step "init run, then age the workspace back to v4"
  $PY "$SCRIPTS/init.py" --root "$root" run >/dev/null 2>&1 \
    || fail "upgrade: \`init run\` did not complete"
  $PY - "$root" <<'AGE'
import pathlib, sys
root = pathlib.Path(sys.argv[1])
cfg = root / "sdlc-studio" / ".config.yaml"
cfg.write_text(cfg.read_text(encoding="utf-8").replace("schema_version: 3", "schema_version: 2"),
               encoding="utf-8")
(root / "sdlc-studio" / "stories" / "US0001-legacy.md").write_text(
    "# US0001: legacy login\n\n> **Status:** Done\n> **Epic:** EP0001\n> **Priority:** High\n\n"
    "## Acceptance Criteria\n\n- [x] **AC1** a valid password logs the user in\n", encoding="utf-8")
(root / "sdlc-studio" / "stories" / "US0002-legacy.md").write_text(
    "# US0002: legacy reset\n\n> **Status:** Ready\n> **Epic:** EP0001\n> **Priority:** Medium\n\n"
    "## Acceptance Criteria\n\n- [ ] **AC1** a reset link sets a new password\n", encoding="utf-8")
(root / "sdlc-studio" / "change-requests" / "CR0001-legacy.md").write_text(
    "# CR-0001: legacy request\n\n> **Status:** Approved\n> **Priority:** Medium\n"
    "> **Effort:** M\n\n## Summary\n\nAdd SSO.\n", encoding="utf-8")
AGE

  step "migrate --apply"
  echo "    order: migrate" 
  $PY "$SCRIPTS/migrate.py" --root "$root" --apply >/dev/null 2>&1 \
    || fail "upgrade: \`migrate --apply\` did not complete"

  # ASSERT THE MIGRATE HAPPENED, on its real deterministic outputs. Dropping `--apply` above
  # left every test of this path green: the failing lane set is identical on a migrated and an
  # unmigrated fixture, so nothing downstream could tell them apart. A seat proved it by deleting
  # the flag. These are what `migrate --apply` actually writes - it does NOT bump schema_version.
  [ -f "$root/sdlc-studio/.version" ] \
    || fail "upgrade: migrate --apply wrote no sdlc-studio/.version - the migration did not run"
  grep -q '^> \*\*Size:\*\* M' "$root/sdlc-studio/change-requests/CR0001-legacy.md" \
    || fail "upgrade: the legacy CR's Effort was not converted to a Size"
  # NOT "and no Effort": measured on the real tool, `migrate --apply` ADDS the derived `Size` and
  # LEAVES the legacy `Effort` in place. Asserting its removal would fail on correct behaviour -
  # the review suggested it, and running the command decided it.
  echo "    migrated: .version written, CR0001 carries a derived Size"

  gate_against_baseline upgrade "$root"
}

# Gate a migrated fixture and compare its failing lanes with the baseline rows for this path
# (the first column). Reddens in both directions; see the note above `rehearse_upgrade`.
gate_against_baseline() {
  local path="$1" root="$2"
  step "gate"
  echo "    order: gate"
  local out; out="$($PY "$SCRIPTS/gate.py" --root "$root" 2>&1)"
  local failing; failing="$(echo "$out" | sed -n 's/^  \[FAIL\] \([a-z-]*\) .*/\1/p' | sort -u)"
  local baselined; baselined="$(sed -n "s/^$path|\([a-z-]*\)|.*/\1/p" "$BASELINE" | sort -u)"

  local new_failures; new_failures="$(comm -23 <(echo "$failing") <(echo "$baselined"))"
  local now_passing; now_passing="$(comm -13 <(echo "$failing") <(echo "$baselined"))"

  if [ -n "$new_failures" ]; then
    echo "$out" >&2
    fail "$path: lane(s) failing that the baseline does not record: $(echo "$new_failures" | tr '\n' ' ')"
  fi
  if [ -n "$now_passing" ]; then
    fail "$path: baselined lane(s) now PASS and must be removed from $BASELINE: $(echo "$now_passing" | tr '\n' ' ')"
  fi

  while IFS='|' read -r rowpath lane artefact _rest; do
    [ "$rowpath" = "$path" ] || continue
    [ -n "$artefact" ] || fail "$path: baseline row for '$lane' names no clearing artefact"
    echo "    known gap: $lane -> $artefact"
  done < "$BASELINE"
  echo "$path: OK ($(echo "$baselined" | wc -w) known gap(s), none new)"
}

# ---------------------------------------------------------------- upgrade-v5

# A project on v5.1 carries what v6 retired: DoD criteria tagged with the retired review and
# repair gates, and instructions naming the retired `review.two_role_after` key. `migrate --apply`
# must strip the tags (keeping each criterion as human-judged) and REPORT the instructions line,
# which is the project's own prose and never rewritten. The DoD lines below are v5.1.0's template,
# verbatim; the rest of the workspace is this tree's `init`, which v5.1.0's matches at schema 3.
rehearse_upgrade_v5() {
  echo "upgrade-v5: a v5.1 project migrates, and its gate matches the recorded baseline"
  local root="$WORK/upgrade-v5"
  mkdir -p "$root"

  step "init run, then give the workspace v5.1's retired review surfaces"
  $PY "$SCRIPTS/init.py" --root "$root" run >/dev/null 2>&1 \
    || fail "upgrade-v5: \`init run\` did not complete"
  $PY - "$root" <<'AGE' || fail "upgrade-v5: the fixture could not be given its v5.1 shape"
import pathlib, sys
root = pathlib.Path(sys.argv[1])
cfg = root / "sdlc-studio" / ".config.yaml"
if "schema_version: 3" not in cfg.read_text(encoding="utf-8"):
    sys.exit("init no longer writes schema 3, so this fixture is not v5.1's shape")
dod = root / "sdlc-studio" / "definition-of-done.md"
lines = dod.read_text(encoding="utf-8").splitlines(keepends=True)
at = [i for i, ln in enumerate(lines) if "[check: review.critic-approve]" in ln]
if len(at) != 1:
    sys.exit(f"the DoD names review.critic-approve {len(at)} times, so the v5.1 lines have no anchor")
lines[at[0] + 1:at[0] + 1] = [
    "- [ ] The adversarial pass is recorded as evidence and the reviewer of record has signed off"
    " [check: review.two-role]\n",
    "- [ ] If it is a REPAIR: a mutant was applied to its own changed lines and its test was seen\n",
    "      to fail on that mutant. A fix's author is not sufficient evidence for that fix - the\n",
    "      test is written after the answer is known, so it must be shown capable of failing.\n",
    "      By default a survivor is FILED as a severity-rated bug and the unit still closes, so\n",
    "      this box is about the evidence existing, not about the count being zero. Set\n",
    "      `review.mutation_evidence: block` to make a survivor refuse instead\n",
    "      [check: repair.mutation-evidence]\n",
]
dod.write_text("".join(lines), encoding="utf-8")
agents = root / "AGENTS.md"
agents.write_text(agents.read_text(encoding="utf-8") + (
    "\n**Review is independent of the author.** With\n"
    "`review.two_role_after` set in `.config.yaml`, a unit holds at Review until that\n"
    "sign-off lands.\n"), encoding="utf-8")
AGE
  local agents_line; agents_line="$(grep -n 'review\.two_role_after' "$root/AGENTS.md" | cut -d: -f1)"

  step "migrate --apply"
  echo "    order: migrate"
  local report; report="$($PY "$SCRIPTS/migrate.py" --root "$root" --apply 2>&1)" \
    || fail "upgrade-v5: \`migrate --apply\` did not complete"

  # What `migrate --apply` writes, and what it must only report. Dropping `--apply` leaves both
  # tags, so the first check is what catches a rehearsal that never migrated.
  if grep -qE '\[check: *(review\.two-role|repair\.mutation-evidence) *\]' \
       "$root/sdlc-studio/definition-of-done.md"; then
    fail "upgrade-v5: the DoD still carries a retired [check:] tag after migrate --apply"
  fi
  case "$report" in
    *"AGENTS.md:$agents_line names the retired \`review.two_role_after\`"*) ;;
    *) echo "$report" >&2
       fail "upgrade-v5: migrate's report does not name AGENTS.md:$agents_line, the line naming review.two_role_after" ;;
  esac
  echo "    migrated: the DoD carries no retired tag, AGENTS.md:$agents_line reported"

  gate_against_baseline upgrade-v5 "$root"
}

case "${1:-all}" in
  greenfield) rehearse_greenfield ;;
  upgrade)    rehearse_upgrade ;;
  upgrade-v5) rehearse_upgrade_v5 ;;
  all)        rehearse_greenfield && rehearse_upgrade && rehearse_upgrade_v5 ;;
  *)          echo "usage: rehearse-release.sh [greenfield|upgrade|upgrade-v5|all]" >&2; exit 2 ;;
esac
