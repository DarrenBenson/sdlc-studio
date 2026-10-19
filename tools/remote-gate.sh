#!/usr/bin/env bash
# Run the push boundary gate on the gate host this clone configures (US1075, CR0635).
#
#   remote-gate.sh push --commit <sha> [--boundary push|release]
#       The local side, run by .githooks/pre-push when `git config sdlc.gateHost` names a host.
#       Sends exactly <sha>, with this clone's remote-tracking refs and tags, to a bare repository
#       on the host kept for this clone alone, then judges it there. Exits:
#         0  the host's gate passed          1  the host's gate refused
#         3  the connection failed            4  the host did not reach the gate (its setup, or
#         2  this script could not start         the preflight on its interpreter, refused)
#       Only 0 and 1 are a gate run whose duration the pre-push hook records.
#
#   remote-gate.sh remote --clone <id> --commit <sha> --boundary <b> --run <token>
#       The host side. Never installed on the host: `push` streams it from the PUSHED COMMIT's own
#       copy of this file, so the host always runs the version being judged.
#
# The host needs git on the PATH an ssh command sees, because the commit is received and checked
# out before anything else runs. Configuration, all in this clone's git config:
#   sdlc.gateHost     the host, as ssh names it (unset: the gate runs locally)
#   sdlc.gateSsh      the transport (default: ssh with BatchMode and a keepalive)
#   sdlc.gateCloneId  this clone's key on the host, written on first use
# A host may hold `~/sdlc-gate/gate-env.sh`, sourced before the gate runs, to put the Python and
# Node the gate needs on PATH. `SDLC_GATE_LOCAL=1` makes the pre-push hook run the gate locally instead.
#
# Runs on one host are serialised by a lock there, each in a directory of its own (US1076). The
# connection's stdin is held open for the whole run, so a push that goes away - interrupted,
# terminated, or its connection dropped - reaches the host as end-of-file, and the host stops the
# run's gate and removes its tree.
#
# The local side is written against bash builtins, git and python3 only: the hook's test fixtures
# run it on a PATH that holds nothing else.
set -uo pipefail

GATE_DIR="sdlc-gate"
DEFAULT_SSH="ssh -o BatchMode=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=10"
TRANSPORT_FAILED=3
HOST_SETUP_FAILED=4
SCRIPT_END="__REMOTE_GATE_SCRIPT_END__"

die() { echo "remote-gate: $1" >&2; exit "${2:-2}"; }

parse() {
  commit="" boundary="push" clone="" run=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --commit) commit="${2:-}"; shift 2 ;;
      --boundary) boundary="${2:-}"; shift 2 ;;
      --clone) clone="${2:-}"; shift 2 ;;
      --run) run="${2:-}"; shift 2 ;;
      *) die "unknown argument: $1" ;;
    esac
  done
  case "$boundary" in push|release) ;; *) die "--boundary must be push or release, not '$boundary'" ;; esac
  [[ $commit =~ ^[0-9a-f]{7,64}$ ]] || die "--commit needs a commit id, not '$commit'"
}

transport_failed() {
  echo "remote-gate: the gate host $host could not judge commit $commit: $1." >&2
  echo "  nothing ran locally in its place. Check that this clone reaches it: ssh $host true" >&2
  echo "  or run the gate on this machine for one push: SDLC_GATE_LOCAL=1 git push" >&2
  exit "$TRANSPORT_FAILED"
}

cmd_push() {
  parse "$@"
  host="$(git config --get sdlc.gateHost || true)"
  [ -n "$host" ] || die "no gate host is configured: git config sdlc.gateHost <host>"
  [[ $host == -* ]] && die "sdlc.gateHost may not start with '-': '$host'"
  ssh_cmd="$(git config --get sdlc.gateSsh || true)"
  [ -n "$ssh_cmd" ] || ssh_cmd="$DEFAULT_SSH"
  commit="$(git rev-parse --verify -q "$commit^{commit}")" || die "no such commit in this clone: $commit"
  id="$(git config --get sdlc.gateCloneId || true)"
  if [ -z "$id" ]; then
    id="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:16])')" || die "could not mint a clone id"
    git config sdlc.gateCloneId "$id" || die "could not record sdlc.gateCloneId"
  fi
  [[ $id =~ ^[A-Za-z0-9_-]+$ ]] || die "sdlc.gateCloneId may hold only letters, digits, '-' and '_': '$id'"
  run="$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')" || die "could not mint a run id"
  local repo="$GATE_DIR/clones/$id.git"

  # One bare repository per clone, so one clone's mirrored refs never narrow another's range,
  # prepared and listed in one call. The listing is what lets the send below DROP a tag or a
  # remote-tracking branch this clone has since deleted: without it the host's range and latest
  # tag follow everything this clone ever sent, not what it holds now.
  local host_refs rc
  host_refs="$($ssh_cmd -- "$host" "mkdir -p $GATE_DIR/clones && git init -q --bare $repo && git -C $repo for-each-ref --format='%(refname)' refs/remotes refs/tags" </dev/null)"
  rc=$?
  [ "$rc" -eq 255 ] && transport_failed "it could not be reached (the connection failed before the gate started)"
  if [ "$rc" -ne 0 ]; then
    echo "remote-gate: $host could not prepare this clone's repository (exit $rc): git must be on the PATH an ssh command sees there" >&2
    exit "$HOST_SETUP_FAILED"
  fi

  # Exactly the pushed commit, never HEAD or the working tree, under a ref of its own run so two
  # runs never fight over one, and with it this clone's remote-tracking refs and tags: without
  # them the host's pushed range widens to all of history and its latest-tag lookup fails.
  # `send-pack`, never `git push`, which would run this hook again.
  local refs=("$commit:refs/gate-runs/$run") ref
  local -A held=()
  while read -r ref; do
    [[ $ref == */HEAD ]] && continue
    refs+=("$ref:$ref")
    held[$ref]=1
  done < <(git for-each-ref --format='%(refname)' refs/remotes refs/tags)
  while read -r ref; do
    [ -n "$ref" ] && [ -z "${held[$ref]:-}" ] && refs+=(":$ref")
  done <<< "$host_refs"
  GIT_SSH_COMMAND="$ssh_cmd" git send-pack --force "$host:$repo" "${refs[@]}" >/dev/null 2>&1 \
    || transport_failed "the commit could not be sent (the connection failed before the gate started)"

  # The host side comes from the pushed commit's own copy of this file, and the connection's stdin
  # then stays open for the life of the run: a feeder writes the script and its end marker, then
  # waits for as long as this process lives. When this push goes away for any reason, the feeder
  # goes with it, the host reads end-of-file, and it stops the run.
  local script
  script="$(git show "$commit:tools/remote-gate.sh")" \
    || die "commit $commit carries no tools/remote-gate.sh, so its host side cannot run"
  local feed_fd feeder_pid ssh_pid=""
  exec {feed_fd}< <(REMOTE_GATE_SCRIPT="$script" REMOTE_GATE_END="$SCRIPT_END" exec python3 -c '
import os, sys, time
sys.stdout.write(os.environ["REMOTE_GATE_SCRIPT"] + "\n" + os.environ["REMOTE_GATE_END"] + "\n")
sys.stdout.flush()
parent = os.getppid()
while os.getppid() == parent:
    time.sleep(1)
')
  feeder_pid=$!
  trap 'kill "$feeder_pid" ${ssh_pid:+"$ssh_pid"} 2>/dev/null; exit 130' INT TERM HUP
  $ssh_cmd -- "$host" \
    "t=\$(mktemp) || exit 2; while IFS= read -r l; do [ \"\$l\" = $SCRIPT_END ] && break; printf '%s\n' \"\$l\"; done > \"\$t\"; bash \"\$t\" remote --clone '$id' --commit '$commit' --boundary '$boundary' --run '$run'; rc=\$?; rm -f \"\$t\"; exit \$rc" \
    <&"$feed_fd" 1>&2 &
  ssh_pid=$!
  exec {feed_fd}<&-
  wait "$ssh_pid"
  rc=$?
  kill "$feeder_pid" 2>/dev/null
  trap - INT TERM HUP
  [ "$rc" -eq 255 ] && transport_failed "the connection failed while it ran"
  if [ "$rc" -eq "$HOST_SETUP_FAILED" ]; then
    echo "remote-gate: $host did not run the gate for commit $commit - see the host's output above." >&2
  elif [ "$rc" -ne 0 ]; then
    echo "remote-gate: $host refused commit $commit at the $boundary boundary - see the host's output above." >&2
    echo "  re-run it on the host: bash tools/remote-gate.sh push --commit $commit --boundary $boundary" >&2
  fi
  return "$rc"
}

cmd_remote() {
  die() { echo "remote gate: $1" >&2; exit "$HOST_SETUP_FAILED"; }
  parse "$@"
  [[ $clone =~ ^[A-Za-z0-9_-]+$ ]] || die "--clone needs this clone's id, not '$clone'"
  [[ $run =~ ^[A-Za-z0-9]+$ ]] || die "--run needs this run's id, not '$run'"
  local base="$HOME/$GATE_DIR" here
  here="$(uname -n)"
  local repo="$base/clones/$clone.git" state="$base/local/$clone"
  # shellcheck disable=SC1091 # the host's own environment file, when it keeps one
  [ -f "$base/gate-env.sh" ] && . "$base/gate-env.sh"
  mkdir -p "$state" "$base/runs" "$base/node" || die "cannot create $base on $here"

  # This run's own directory, made before anything waits, so a second run of the same commit
  # never shares or removes the first one's tree.
  run_dir="$base/runs/$run"
  mkdir "$run_dir" || die "run $run already has a directory on $here"
  wt="$run_dir/tree" gate_pid="" lock_pid="" watch_pid=""
  cleanup() {
    [ -n "$watch_pid" ] && kill "$watch_pid" 2>/dev/null
    [ -n "$lock_pid" ] && kill "$lock_pid" 2>/dev/null
    if [ -n "$gate_pid" ] && kill -0 "$gate_pid" 2>/dev/null; then
      kill -TERM -- "-$gate_pid" 2>/dev/null
      wait "$gate_pid" 2>/dev/null
    fi
    cd "$base" || return
    [ -L "$wt/node_modules" ] && unlink "$wt/node_modules"
    [ -L "$wt/sdlc-studio/.local" ] && unlink "$wt/sdlc-studio/.local"
    rm -rf "$run_dir"
    git -C "$repo" worktree prune
    git -C "$repo" update-ref -d "refs/gate-runs/$run" 2>/dev/null
  }
  trap cleanup EXIT
  trap 'exit 130' INT TERM HUP

  # The pusher holds this connection's stdin open for the life of the run. End-of-file means it
  # has gone - interrupted, terminated or disconnected - so the run stops rather than finishing
  # for nobody. Its stdin is named explicitly, because a background job's is /dev/null otherwise,
  # and its stdout and stderr go nowhere, so it never holds the session open.
  python3 -c 'import os, signal, sys
sys.stdin.buffer.read()
os.kill(int(sys.argv[1]), signal.SIGTERM)' "$$" <&0 >/dev/null 2>&1 &
  watch_pid=$!

  # One run at a time on this host. A waiting run says so, and names the run it waits for.
  exec 9>"$base/run.lock"
  if ! flock -n 9; then
    echo "remote gate: waiting for the run holding $here's gate lock: $(cat "$base/run.holder" 2>/dev/null || echo unknown)"
    flock 9 &
    lock_pid=$!
    wait "$lock_pid" || die "could not take $here's gate lock"
    lock_pid=""
  fi
  echo "run $run, commit $commit, clone $clone, since $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$base/run.holder"

  # node_modules, cached per package-lock: two suite modules refuse to collect without markdownlint.
  local node_dir=""
  if lock_json="$(git -C "$repo" show "$commit:package-lock.json" 2>/dev/null)" && [ -n "$lock_json" ]; then
    local lock_sum
    lock_sum="$(printf '%s' "$lock_json" | sha256sum | cut -c1-16)"
    node_dir="$base/node/$lock_sum"
    if [ ! -d "$node_dir/node_modules" ]; then
      mkdir -p "$node_dir" && git -C "$repo" show "$commit:package.json" > "$node_dir/package.json" \
        && printf '%s' "$lock_json" > "$node_dir/package-lock.json" \
        && (cd "$node_dir" && npm ci --silent --no-audit --no-fund) \
        || { rm -rf "$node_dir"; die "npm ci failed on $here for package-lock $lock_sum"; }
    fi
  fi

  git -C "$repo" -c core.hooksPath=/dev/null worktree add -q --detach "$wt" "$commit" \
    || die "cannot check out $commit on $here"
  [ -n "$node_dir" ] && ln -s "$node_dir/node_modules" "$wt/node_modules"
  mkdir -p "$wt/sdlc-studio" && ln -s "$state" "$wt/sdlc-studio/.local"
  cd "$wt" || die "cannot enter $wt"
  echo "remote gate: $here judging $commit at --boundary $boundary with $(python3 --version 2>&1), load $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null || echo unknown)"

  # US1005's preflight, on THIS host's interpreter: the one that will run the suite.
  if [ -f tools/gate_prereqs.py ]; then
    if ! python3 tools/gate_prereqs.py check --refusing; then
      echo "remote gate: refused before the $boundary boundary gate runs: $here's interpreter lacks a prerequisite marked REFUSES above"
      exit "$HOST_SETUP_FAILED"
    fi
  fi

  # The gate in a session of its own, waited on rather than run in the foreground: a signal then
  # reaches this script at once, and the cleanup stops the gate's whole process group. A
  # background job in a non-interactive shell starts with SIGINT and SIGQUIT IGNORED, and every
  # process it starts inherits that, so a suite test that interrupts a hook it runs could not; the
  # gate is execed with both back at their defaults.
  local t0=$SECONDS rc
  SDLC_STUDIO_BOUNDARY_SUITE=1 setsid python3 -c 'import os, signal, sys
for sig in (signal.SIGINT, signal.SIGQUIT):
    signal.signal(sig, signal.SIG_DFL)
os.execvp(sys.argv[1], sys.argv[1:])' python3 .claude/skills/sdlc-studio/scripts/gate.py --boundary "$boundary" &
  gate_pid=$!
  wait "$gate_pid"
  rc=$?
  gate_pid=""
  echo "remote gate: exit $rc after $((SECONDS - t0))s"
  [ "$rc" -ne 0 ] && echo "remote gate: the full log is on $here at $state/boundary-suite-last.log"
  exit "$rc"
}

case "${1:-}" in
  push) shift; cmd_push "$@" ;;
  remote) shift; cmd_remote "$@" ;;
  *) echo "usage: remote-gate.sh push --commit <sha> [--boundary push|release]" >&2; exit 2 ;;
esac
