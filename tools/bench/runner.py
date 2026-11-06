#!/usr/bin/env python3
"""RFC0025 / CR0178 benchmark harness runner (repo-only, not shipped in the skill payload).

Drives the sdlc-studio-vs-plain-Claude-Code comparison over the fixtures in
`tools/bench/fixtures/`: setting up a workspace for one (fixture, arm) run, running it headless
in one harness's CLI, scoring a finished workspace against the fixture's held-back suite, and
recording/summarising results. There is no API call inside this file: `run` launches the
harness's own CLI, and an operator may still drive a session by hand and `record` it.

Subcommands:
  prepare   Set up a workspace for one (fixture, arm) run; with `--harness` and `--skill-ref`,
            the skill comes from that commit into the harness's local skill directory.
  run       Prepare a workspace, run the arm's prompt headless in the harness's CLI, score it
            and record the usage the CLI printed, normalised by `lib/harness_usage.py`.
  score     Run the held-back suite against a finished workspace.
  record    Append one run's metrics to the results log.
  summary   Aggregate results per fixture x arm, and per harness where a row names one, with
            the estimated US dollar cost from `lib/prices.py` where the model is priced.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parent
FIXTURES_DIR = BENCH_ROOT / "fixtures"
ARMS_DIR = BENCH_ROOT / "arms"
RESULTS_PATH = BENCH_ROOT / "results" / "runs.jsonl"
SKILL_REL = ".claude/skills/sdlc-studio"
SKILL_DIR = BENCH_ROOT.parent.parent / SKILL_REL
#: The repository a `--skill-ref` is read from; resolved at call time so a test can point it at
#: a fixture repository.
REPO_ROOT = BENCH_ROOT.parent.parent
#: The installer whose `--list-targets` names each harness's workspace-local skill directory.
INSTALL_SH = BENCH_ROOT.parent.parent / "install.sh"

sys.path.insert(0, str(SKILL_DIR / "scripts" / "lib"))
import harness_usage  # noqa: E402  (each CLI's printed usage, normalised to one basis)
import prices as model_prices  # noqa: E402  (the dated per-model US dollar table)

ARM_CLAUDE_MD = {"A": ARMS_DIR / "pipeline_CLAUDE.md",
                 "B": ARMS_DIR / "baseline_CLAUDE.md",
                 "R": ARMS_DIR / "pipeline_routed_CLAUDE.md"}
# Arms whose workspace gets the skill copied IN (environmental isolation: arm B's
# workspace simply does not contain the skill, rather than being told not to use it).
SKILL_ARMS = ("A", "R")
# Arm R's workspace .config.yaml: routing enabled with the operator's model map,
# written at prepare time from arms/routed_config.yaml.
ROUTED_CONFIG = ARMS_DIR / "routed_config.yaml"


def list_fixtures(fixtures_dir: Path = FIXTURES_DIR) -> list[str]:
    """Fixture names, sorted, i.e. directories with both a visible/ and hidden/ subdir."""
    if not fixtures_dir.is_dir():
        return []
    return sorted(p.name for p in fixtures_dir.iterdir()
                  if p.is_dir() and (p / "visible").is_dir() and (p / "hidden").is_dir())


def prepare_workspace(fixture: str, arm: str, dest: Path,
                       fixtures_dir: Path = FIXTURES_DIR,
                       skill_dir: Path = SKILL_DIR) -> Path:
    """Copy the fixture's visible/ files plus the arm's CLAUDE.md into `dest`. Never touches
    the fixture's hidden/ (or audit/, reference/) content - that is the whole point of
    "held-back". Arms A/R additionally get the skill copied INTO the workspace
    (.claude/skills/sdlc-studio) so arm B's isolation is environmental - the skill is absent
    from B's world, not merely forbidden by instruction. Arm R also gets a .config.yaml
    enabling routing (from arms/routed_config.yaml). This copies the working tree's skill;
    `prepare_harness_workspace` installs a pinned commit's instead."""
    _check_fixture_arm(fixture, arm, fixtures_dir)
    _lay_out(fixture, arm, dest, fixtures_dir)
    if arm in SKILL_ARMS:
        shutil.copytree(skill_dir, dest / SKILL_REL, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", ".local"))
    return dest


def _check_fixture_arm(fixture: str, arm: str, fixtures_dir: Path) -> None:
    if arm not in ARM_CLAUDE_MD:
        raise ValueError(f"unknown arm {arm!r} - expected one of {sorted(ARM_CLAUDE_MD)}")
    if not (fixtures_dir / fixture / "visible").is_dir():
        raise ValueError(f"unknown fixture {fixture!r} (no visible/ dir under {fixtures_dir})")


def _lay_out(fixture: str, arm: str, dest: Path, fixtures_dir: Path) -> None:
    """The fixture's visible/ files, the arm's CLAUDE.md and arm R's routing config."""
    dest.mkdir(parents=True, exist_ok=True)
    for item in (fixtures_dir / fixture / "visible").iterdir():
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)
    shutil.copy2(ARM_CLAUDE_MD[arm], dest / "CLAUDE.md")
    if arm == "R":
        cfg_dir = dest / "sdlc-studio"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROUTED_CONFIG, cfg_dir / ".config.yaml")


class Refused(ValueError):
    """A request the runner will not carry out; the message names what was refused and why."""


#: Git variables a hook exports, pointing at whatever repository invoked it. Dropped from the
#: git, installer and harness CLI subprocesses here, so `git -C <repo>` reads that repository
#: and an agent's git calls inside a workspace never reach the one the hook is committing to.
_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)


def _clean_env(*drop: str) -> dict:
    return {k: v for k, v in os.environ.items() if k not in _GIT_ENV_VARS and k not in drop}


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          env=_clean_env(), check=False)


def skill_targets(install_sh: Path | None = None) -> dict[str, str | None]:
    """Each install target and its workspace-local skill directory, read from the LOCAL DIR
    column of `install.sh --list-targets`, so the benchmark installs where the installer would.
    A target whose local directory is absent, absolute or climbs out of the workspace maps to
    None."""
    install_sh = install_sh if install_sh is not None else INSTALL_SH
    proc = subprocess.run(["bash", str(install_sh), "--list-targets"], capture_output=True,
                          text=True, timeout=60, env=_clean_env(), check=False)
    if proc.returncode != 0:
        raise Refused(f"{install_sh} --list-targets exited {proc.returncode}: "
                      f"{proc.stderr.strip()[-300:]}")
    targets: dict[str, str | None] = {}
    in_table = False
    for line in re.sub(r"\x1b\[[0-9;]*m", "", proc.stdout).splitlines():
        cols = line.split()
        if cols[:1] == ["TARGET"]:
            in_table = True
        elif in_table and cols:
            # TARGET, GLOBAL DIR, LOCAL DIR, DETECTED: read the local column from the right, so
            # a global directory holding a space cannot shift it.
            local = cols[-2] if len(cols) >= 4 else None
            if local and (local.startswith(("/", "~")) or ".." in Path(local).parts):
                local = None
            targets[cols[0]] = local
    if not targets:
        raise Refused(f"{install_sh} --list-targets printed no target table")
    return targets


def skill_dir_for(harness: str, targets: dict[str, str | None] | None = None) -> str:
    """The harness's workspace-local skill directory; a harness install.sh names none for is
    refused by name."""
    targets = targets if targets is not None else skill_targets()
    local = targets.get(harness)
    if not local:
        named = ", ".join(sorted(t for t, d in targets.items() if d))
        raise Refused(f"harness {harness!r} has no skill directory in install.sh --list-targets "
                      f"(it names one for {named})")
    return local


def resolve_skill_ref(ref: str, repo: Path | None = None) -> str:
    """The full commit id `ref` names in `repo` (default REPO_ROOT)."""
    repo = repo if repo is not None else REPO_ROOT
    proc = _git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    sha = proc.stdout.decode().strip()
    if proc.returncode != 0 or not sha:
        raise Refused(f"--skill-ref {ref!r} names no commit in {repo}")
    return sha


def _skill_archive(sha: str, repo: Path) -> bytes:
    """The skill as commit `sha` holds it, as a tar from git's object store - never the working
    tree, whose edits and untracked files are not that commit's."""
    proc = _git(repo, "archive", "--format=tar", sha, SKILL_REL)
    if proc.returncode != 0:
        raise Refused(f"commit {sha} carries no skill at {SKILL_REL}: "
                      f"{proc.stderr.decode().strip()}")
    return proc.stdout


def _unpack_skill(archive: bytes, dest_skill: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp, tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        if hasattr(tarfile, "data_filter"):
            tar.extractall(tmp, filter="data")
        else:  # an interpreter older than the extraction filters
            tar.extractall(tmp)  # noqa: S202 - our own repository's archive
        shutil.copytree(Path(tmp) / SKILL_REL, dest_skill, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", ".local"))


def prepare_harness_workspace(fixture: str, arm: str, dest: Path, harness: str, skill_ref: str,
                              fixtures_dir: Path = FIXTURES_DIR,
                              targets: dict[str, str | None] | None = None,
                              repo: Path | None = None) -> str:
    """`prepare_workspace` for one harness against a pinned skill: arms A and R get the skill as
    commit `skill_ref` holds it, at `<harness local dir>/sdlc-studio` as `install.sh
    --list-targets` names it; arm B gets none. Everything is checked before the first write, so
    a refused harness, ref or fixture leaves no workspace. Returns the full commit id."""
    repo = repo if repo is not None else REPO_ROOT
    local = skill_dir_for(harness, targets)
    _check_fixture_arm(fixture, arm, fixtures_dir)
    sha = resolve_skill_ref(skill_ref, repo)
    archive = _skill_archive(sha, repo)
    _lay_out(fixture, arm, dest, fixtures_dir)
    if arm in SKILL_ARMS:
        _unpack_skill(archive, dest / local / "sdlc-studio")
    return sha


#: The prompt every arm runs. The arm's instructions are its CLAUDE.md; the prompt names that
#: file, so a harness that does not load CLAUDE.md unasked still reads it.
ARM_PROMPT = ("Complete the ticket in TICKET.md, following the instructions in CLAUDE.md. "
              "Work only in this directory, and run the tests before you finish.")


def _flag(name: str, value: str | None) -> list[str]:
    return [name, value] if value else []


#: Each harness's headless command for one prompt, printing its usage as JSON, with the
#: permission flag that lets the session edit the workspace unattended. Cursor CLI is absent:
#: install.sh names no skill directory for it, so it is refused before a command is needed.
HEADLESS = {
    "claude": lambda prompt, model: ["claude", "-p", prompt, "--output-format", "json",
                                     "--permission-mode", "bypassPermissions",
                                     *_flag("--model", model)],
    "codex": lambda prompt, model: ["codex", "exec", "--json", "--skip-git-repo-check",
                                    "--sandbox", "workspace-write", *_flag("-m", model), prompt],
    "copilot": lambda prompt, model: ["copilot", "-p", prompt, "--output-format", "json", "-s",
                                      "--allow-all-tools", *_flag("--model", model)],
    "opencode": lambda prompt, model: ["opencode", "run", "--format", "json", "--auto",
                                       *_flag("-m", model), prompt],
}
#: Each harness's variable for its own configuration directory, which holds the personal skill
#: directory it scans (`<dir>/skills`), as Copilot CLI's help, Codex CLI's bundled docs and
#: tools/eval_run.py's worker setup name it. A run points
#: it at a private empty directory, so a personal copy of the skill there, or wherever the
#: operator's own value points, never reaches the session. OpenCode is absent: its
#: OPENCODE_CONFIG_DIR adds a directory to the ones it reads rather than replacing its global one.
CONFIG_DIR_VAR = {"claude": "CLAUDE_CONFIG_DIR", "codex": "CODEX_HOME",
                  "copilot": "COPILOT_HOME"}
#: Switches a CLI documents for turning its scans of other tools' personal skill directories off.
SKILL_SCAN_OFF = {"opencode": {"OPENCODE_DISABLE_EXTERNAL_SKILLS": "1",
                               "OPENCODE_DISABLE_CLAUDE_CODE_SKILLS": "1"}}
SKILL_NAME = "sdlc-studio"


def fixed_skill_dirs(harness: str, env: dict) -> list[Path]:
    """The personal skill directories `harness` scans that no variable of its own relocates:
    `~/.agents/skills` for Codex CLI and Copilot CLI, and OpenCode's global
    `${XDG_CONFIG_HOME:-~/.config}/opencode/skill(s)`."""
    home = Path(env.get("HOME") or os.path.expanduser("~"))
    if harness in ("codex", "copilot"):
        return [home / ".agents" / "skills"]
    if harness == "opencode":
        xdg = Path(env["XDG_CONFIG_HOME"]) if env.get("XDG_CONFIG_HOME") else home / ".config"
        return [xdg / "opencode" / "skills", xdg / "opencode" / "skill"]
    return []


def isolate_skills(harness: str, env: dict, private: Path | None) -> dict:
    """The CLI's environment with the operator's personal skill copies out of the session's
    reach, so it loads only the skill `prepare` installed, and none for arm B. A harness whose
    personal copy sits where no variable reaches is refused, naming the copy, because a row
    from that session could not say which skill ran. `private` is the empty directory the
    harness's configuration variable is pointed at; None checks the refusal alone."""
    for root in fixed_skill_dirs(harness, env):
        copy = root / SKILL_NAME
        if copy.exists():
            raise Refused(f"harness {harness!r}: a personal copy of the skill at {copy} would "
                          f"load into the session beside the pinned one, and {harness} offers "
                          f"no variable to move it; remove it to run {harness}")
    env = dict(env)
    if private is not None and harness in CONFIG_DIR_VAR:
        env[CONFIG_DIR_VAR[harness]] = str(private)
    env.update(SKILL_SCAN_OFF.get(harness, {}))
    return env


#: The normalised counts a row records, from `harness_usage.Usage`.
USAGE_COUNTS = ("input", "cache_read", "cache_write", "cache_write_1h", "output", "reasoning")


def _json_events(text: str) -> list[dict]:
    try:
        whole = json.loads(text)
    except ValueError:
        whole = None
    if isinstance(whole, dict):
        return [whole]
    events = []
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def usage_by_model(harness: str, text: str) -> dict[str, dict] | None:
    """Each model's own normalised counts, where the output splits a session's usage by model
    (Claude Code's `modelUsage`, Copilot's `modelMetrics`) and names more than one. Each model's
    record goes through `harness_usage.parse` alone, so it is read exactly as the session's sum
    is, and a session that delegated to a cheaper model is priced at each model's own rate. None
    for a single-model session or an output without the split."""
    events = _json_events(text)
    if harness == "claude":
        result = next((e for e in reversed(events) if e.get("type") == "result"),
                      events[-1] if events else {})
        split = result.get("modelUsage")
        one = lambda name, rec: {"type": "result", "modelUsage": {name: rec}}  # noqa: E731
    elif harness == "copilot":
        result = next((e for e in reversed(events) if e.get("type") in
                       ("session.usage_checkpoint", "session.shutdown")), {})
        split = ((result.get("data") or {}).get("accountingSnapshot") or {}).get("modelMetrics")
        one = lambda name, rec: {"type": result["type"], "data": {  # noqa: E731
            "accountingSnapshot": {"modelMetrics": {name: rec}}}}
    else:
        return None
    if not isinstance(split, dict) or len(split) < 2:
        return None
    out = {}
    for name, rec in split.items():
        u = harness_usage.parse(harness, json.dumps(one(name, rec)))
        if not u.metered:
            return None
        out[name] = {k: getattr(u, k) for k in USAGE_COUNTS}
    return out


def run_headless(fixture: str, arm: str, harness: str, skill_ref: str, run_id: str, dest: Path,
                 *, model: str | None = None, timeout: int = 3600, score_timeout: int = 120,
                 phase: str = "measured", prompt: str = ARM_PROMPT,
                 results_path: Path | None = None, fixtures_dir: Path = FIXTURES_DIR) -> dict:
    """One measured run: prepare `dest` for the harness against the pinned skill, run `prompt`
    headless in the harness's CLI there, score the workspace against the held-back suite and
    record a row. The row's tokens are the usage the CLI printed, normalised by
    `harness_usage.parse`; `wall_time_s` is the CLI session's own duration, scoring excluded;
    `metrics_source` is `measured`. A CLI that exits non-zero, times out or prints no usage
    writes no row: the run is refused with the normaliser's reason. The session gets the
    operator's HOME but, where its harness has a variable for one, a private, empty
    configuration directory, removed when it ends, so it loads no personal copy of the skill
    (`isolate_skills`); that directory holds no credential, so the CLI authenticates from what
    the operator's environment exports."""
    dest = Path(dest)
    targets = skill_targets()
    skill_dir_for(harness, targets)
    if harness not in HEADLESS:
        raise Refused(f"harness {harness!r} has no headless command in the runner "
                      f"(it runs {', '.join(sorted(HEADLESS))})")
    if dest.exists() and any(dest.iterdir()):
        raise Refused(f"--dest {dest} is not empty: a run starts from a fresh workspace")
    cmd = HEADLESS[harness](prompt, model)
    env = _clean_env("CLAUDECODE")  # a nested Claude Code session refuses to start under it
    exe = shutil.which(cmd[0], path=env.get("PATH"))
    if not exe:
        raise Refused(f"harness {harness!r}: {cmd[0]} is not on PATH")
    isolate_skills(harness, env, None)  # refuse before the workspace is written
    sha = prepare_harness_workspace(fixture, arm, dest, harness, skill_ref, fixtures_dir,
                                    targets=targets)
    with tempfile.TemporaryDirectory(prefix=f"bench-{harness}-config-") as private:
        session_env = isolate_skills(harness, env, Path(private))
        start = time.monotonic()
        try:
            proc = subprocess.run([exe, *cmd[1:]], cwd=dest, capture_output=True, text=True,
                                  timeout=timeout, env=session_env, stdin=subprocess.DEVNULL,
                                  check=False)
        except subprocess.TimeoutExpired:
            raise Refused(f"no row written: {cmd[0]} ran past --timeout {timeout}s") from None
        wall = round(time.monotonic() - start, 2)
    usage = harness_usage.parse(harness, proc.stdout, exit_code=proc.returncode, model=model)
    if not usage.metered:
        raise Refused(f"no row written: {harness} {usage.reason}")
    scored = score(fixture, dest, fixtures_dir=fixtures_dir, timeout=score_timeout)
    entry = {"fixture": fixture, "arm": arm, "harness": harness, "run_id": run_id,
             "skill_ref": sha, "model": usage.model, "model_source": usage.model_source,
             "session_id": usage.session_id, "tokens": usage.prompt + usage.output,
             "usage": {k: getattr(usage, k) for k in USAGE_COUNTS},
             "wall_time_s": wall, "defect_escape": scored["defect_escape"],
             "metrics_source": "measured", "phase": phase}
    split = usage_by_model(harness, proc.stdout)
    if split:
        entry["usage_by_model"] = split
    if usage.unreported:
        entry["unreported"] = list(usage.unreported)
    if usage.disagreements:
        entry["usage_disagreements"] = list(usage.disagreements)
    return record(entry, results_path)


def score(fixture: str, workspace: Path, fixtures_dir: Path = FIXTURES_DIR,
          timeout: int = 120) -> dict:
    """Run the fixture's held-back suite against `workspace`. Returns {"passed": bool,
    "defect_escape": bool, "output": str}. `defect_escape` is the inverse of `passed` - named
    per the protocol's metric, so callers don't have to remember to invert it. The hidden
    tree is copied whole (subdirectories included) into a scoring tempdir - pytest never
    runs from the fixture directory itself."""
    hidden = fixtures_dir / fixture / "hidden"
    if not hidden.is_dir():
        raise ValueError(f"unknown fixture {fixture!r} (no hidden/ dir under {fixtures_dir})")
    with tempfile.TemporaryDirectory() as scoring_dir:
        scoring_dir = Path(scoring_dir)
        for item in hidden.iterdir():
            target = scoring_dir / item.name
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(scoring_dir), "--workspace", str(workspace), "-q"],
            capture_output=True, text=True, timeout=timeout,
        )
        passed = result.returncode == 0
        return {"passed": passed, "defect_escape": not passed,
                "output": (result.stdout + result.stderr)[-4000:]}


# Protocol v2 forbids pooling calibration rows with measured rows. `phase` makes that
# rule live in the data, not the operator's memory. `v2n1` was the protocol-v2 calibration
# spike; every other run id is a measured run. Classification is only used to backfill rows
# recorded before the field existed - new rows carry their own phase.
_CALIBRATION_RUN_IDS = {"v2n1"}


def classify_phase(entry: dict) -> str:
    """The phase a legacy (pre-field) row should carry, from its run id."""
    return "calibration" if entry.get("run_id") in _CALIBRATION_RUN_IDS else "measured"


def record(entry: dict, results_path: Path | None = None) -> dict:
    """Append one run's metrics. Required keys: fixture, arm, run_id. Optional: tokens,
    wall_time_s, iterations, defect_escape, rework, phase. Unknown extra keys are kept
    as-is - this is a benchmark log, not a fixed schema like the skill's own telemetry.py.
    A row is stamped `phase: "measured"` unless the caller sets it (the operator passes
    `--phase calibration` for a calibration run); the default keeps the majority case honest.
    `results_path` resolves at CALL time (module attribute, not a def-time default) so
    tests can redirect it - a def-time default silently wrote test rows into the real log."""
    results_path = results_path if results_path is not None else RESULTS_PATH
    for k in ("fixture", "arm", "run_id"):
        if k not in entry:
            raise ValueError(f"record: missing required key {k!r}")
    entry = dict(entry)                       # never mutate the caller's dict
    entry.setdefault("phase", "measured")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with results_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def backfill_phases(results_path: Path | None = None) -> int:
    """One-time migration: stamp a `phase` on every existing row that lacks one
    (`classify_phase`), leaving already-stamped rows untouched. Returns the number stamped;
    idempotent (a second run stamps nothing). Rewrites the file in place."""
    results_path = results_path if results_path is not None else RESULTS_PATH
    rows = read_all(results_path)
    stamped = 0
    for r in rows:
        if "phase" not in r:
            r["phase"] = classify_phase(r)
            stamped += 1
    if stamped:
        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return stamped


def read_all(results_path: Path | None = None) -> list[dict]:
    results_path = results_path if results_path is not None else RESULTS_PATH
    if not results_path.exists():
        return []
    out = []
    for line in results_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def _mean(vals: list) -> float | None:
    return round(sum(vals) / len(vals), 2) if vals else None


def _min_max(vals: list):
    return (round(min(vals), 2), round(max(vals), 2)) if vals else (None, None)


def parse_price_map(spec: str | None) -> dict:
    """`tiny=0.25,small=1,large=5` -> {tier: relative price}. Pricing is operator-supplied
    at invocation, never stored in the repo or the skill payload."""
    if not spec:
        return {}
    out = {}
    for part in spec.split(","):
        name, _, val = part.partition("=")
        if not name.strip() or not val.strip():
            raise ValueError(f"bad --price entry {part!r} - expected tier=number")
        out[name.strip()] = float(val)
    return out


def parse_model_mix(spec: str | None) -> dict:
    """`tiny:2,medium:1` -> {tier: unit count} - which tiers delivered how many units."""
    if not spec:
        return {}
    out = {}
    for part in spec.split(","):
        name, _, val = part.partition(":")
        if not name.strip() or not val.strip():
            raise ValueError(f"bad --model-mix entry {part!r} - expected tier:count")
        out[name.strip()] = int(val)
    return out


def cost_index(model_mix: dict, prices: dict) -> float | None:
    """Sum of units x relative tier price. None (never a fabricated 0) when the mix or
    any needed price is missing."""
    if not model_mix or not prices:
        return None
    if any(t not in prices for t in model_mix):
        return None
    return round(sum(n * prices[t] for t, n in model_mix.items()), 3)


def _components(counts: dict) -> dict:
    """Normalised counts as `prices.cost` components: the one-hour writes apart from the rest,
    which are priced at the five-minute rate, as an unsplit write is."""
    one_hour = counts.get("cache_write_1h") or 0
    return {"input": counts["input"], "output": counts["output"],
            "cache_read": counts["cache_read"],
            "cache_write_5m": counts["cache_write"] - one_hour, "cache_write_1h": one_hour}


def row_cost(row: dict, table) -> tuple[float | None, str | None]:
    """A measured row's estimated US dollar cost and, when it cannot be priced, why. Each model
    in `usage_by_model` is priced at its own rate; a row without the split is priced at its one
    model. A row with any unpriced model has no dollar figure, never a partial one."""
    per_model = row.get("usage_by_model") or {row.get("model"): row["usage"]}
    usd, unpriced = 0.0, []
    for model, counts in per_model.items():
        c = model_prices.cost(model, _components(counts), table)
        if c.usd is None:
            unpriced.append(c.unpriced)
        else:
            usd += c.usd
    return (None, "; ".join(unpriced)) if unpriced else (usd, None)


def _price_table():
    """The shipped price table with this repository's `pricing.models` laid over it."""
    scripts = str(SKILL_DIR / "scripts")
    if scripts not in sys.path:
        sys.path.append(scripts)  # prices.load reads the project's pricing through config.py
    return model_prices.load(REPO_ROOT)


def summarize(entries: list[dict], prices: dict | None = None,
              include_phases: set | None = None, table=None) -> dict:
    """Per (fixture, arm, harness) aggregates: n, defect_escape_rate, rework_rate, mean/min/max
    tokens and wall_time_s, mean audit score, and (when the operator supplies --price and
    runs carry a model mix) a mean cost index. A field absent from every entry in a group
    is None, not a fabricated 0.

    A row naming a harness is grouped under `fixture::arm::harness`, so two harnesses' runs are
    never pooled; a legacy row naming none keeps its `fixture::arm` key. A group holding measured
    usage rows also carries `mean_usd` over the rows `table` (a `prices.PriceTable`, loaded when
    None) can price, `priced_n` and `unpriced`, the reasons the rest could not be.

    Calibration rows are excluded by default (protocol v2's no-pooling rule, enforced by
    the tool). `include_phases` selects which phases count; None means measured-only. A row
    with no `phase` counts as measured, so a legacy log not yet backfilled still aggregates."""
    prices = prices or {}
    include = include_phases or {"measured"}
    entries = [e for e in entries if e.get("phase", "measured") in include]
    groups: dict[tuple, list[dict]] = {}
    for e in entries:
        groups.setdefault((e.get("fixture"), e.get("arm"), e.get("harness")), []).append(e)
    out = {}
    for (fixture, arm, harness), rows in sorted(
            groups.items(), key=lambda kv: tuple(str(k or "") for k in kv[0])):
        tokens = [r["tokens"] for r in rows if isinstance(r.get("tokens"), (int, float))]
        wall = [r["wall_time_s"] for r in rows if isinstance(r.get("wall_time_s"), (int, float))]
        escapes = [r["defect_escape"] for r in rows if r.get("defect_escape") is not None]
        rework = [r["rework"] for r in rows if r.get("rework") is not None]
        audit = [r["audit_score"] for r in rows if isinstance(r.get("audit_score"), (int, float))]
        costs = [c for r in rows
                 if (c := cost_index(r.get("model_mix") or {}, prices)) is not None]
        g = {
            "n": len(rows),
            "mean_tokens": _mean(tokens),
            "mean_wall_time_s": _mean(wall),
            "defect_escape_rate": _mean([1 if v else 0 for v in escapes]),
            "rework_rate": _mean([1 if v else 0 for v in rework]),
        }
        g["min_tokens"], g["max_tokens"] = _min_max(tokens)
        g["min_wall_time_s"], g["max_wall_time_s"] = _min_max(wall)
        if audit:
            g["mean_audit_score"] = _mean(audit)
        if costs:
            g["mean_cost_index"] = _mean(costs)
        metered = [r for r in rows if isinstance(r.get("usage"), dict)]
        if metered:
            table = table if table is not None else _price_table()
            priced = [row_cost(r, table) for r in metered]
            usd = [c for c, _ in priced if c is not None]
            g["mean_usd"] = round(sum(usd) / len(usd), 8) if usd else None
            g["priced_n"] = len(usd)
            g["unpriced"] = sorted({why for c, why in priced if c is None})
        if harness:
            g["harness"] = harness
        out[f"{fixture}::{arm}::{harness}" if harness else f"{fixture}::{arm}"] = g
    return out


def cmd_prepare(args: argparse.Namespace) -> int:
    dest = Path(args.dest)
    if bool(args.harness) != bool(args.skill_ref):
        raise Refused("prepare: --harness and --skill-ref go together - a harness workspace "
                      "carries a pinned commit's skill, never the working tree's")
    if args.harness:
        sha = prepare_harness_workspace(args.fixture, args.arm, dest, args.harness,
                                        args.skill_ref)
        print(f"prepared {dest} ({args.fixture}, arm {args.arm}, harness {args.harness}, "
              f"skill {sha})")
        return 0
    prepare_workspace(args.fixture, args.arm, dest)
    print(f"prepared {dest} ({args.fixture}, arm {args.arm})")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    row = run_headless(args.fixture, args.arm, args.harness, args.skill_ref, args.run_id,
                       Path(args.dest), model=args.model, timeout=args.timeout,
                       score_timeout=args.score_timeout, phase=args.phase,
                       results_path=Path(args.results) if args.results else None)
    print(f"recorded {row['fixture']}/{row['arm']}/{row['harness']}/{row['run_id']}: "
          f"{row['tokens']} tokens, {row['wall_time_s']}s, "
          f"{'defect escape' if row['defect_escape'] else 'held-back suite passed'}")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    r = score(args.fixture, Path(args.workspace), timeout=args.timeout)
    print(json.dumps(r) if args.format == "json" else
          ("PASS" if r["passed"] else "FAIL (defect escape)"))
    return 0 if r["passed"] else 1


def cmd_record(args: argparse.Namespace) -> int:
    entry = {"fixture": args.fixture, "arm": args.arm, "run_id": args.run_id}
    if args.metrics_json:
        # automatic capture: tokens/wall-time parsed from the orchestrator's per-run
        # usage JSON (transcript_metrics.py output) - the preferred, disclosed-by-default path
        m = json.loads(Path(args.metrics_json).read_text(encoding="utf-8"))
        if m.get("tokens") is not None:
            entry["tokens"] = m["tokens"]
        if m.get("wall_time_s") is not None:
            entry["wall_time_s"] = m["wall_time_s"]
        entry["metrics_source"] = "parsed"
    if args.tokens is not None:
        entry["tokens"] = args.tokens
        entry["metrics_source"] = "manual"
    if args.wall_time_s is not None:
        entry["wall_time_s"] = args.wall_time_s
        entry["metrics_source"] = "manual"
    if args.iterations is not None:
        entry["iterations"] = args.iterations
    if args.defect_escape is not None:
        entry["defect_escape"] = args.defect_escape.lower() in ("true", "yes", "1")
    if args.rework is not None:
        entry["rework"] = args.rework.lower() in ("true", "yes", "1")
    if args.audit_score is not None:
        entry["audit_score"] = args.audit_score
    if args.model_mix:
        entry["model_mix"] = parse_model_mix(args.model_mix)
    entry["phase"] = args.phase
    record(entry)
    print(f"recorded {entry['fixture']}/{entry['arm']}/{entry['run_id']} (phase {args.phase})")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    rows = read_all(Path(args.results) if args.results else None)
    include = None
    if args.include_phase:
        vals = set(args.include_phase)
        unknown = vals - {"measured", "calibration", "all"}
        if unknown:
            raise ValueError(f"--include-phase: unknown phase(s) {sorted(unknown)} - "
                             "expected measured, calibration, or all")
        include = ({r.get("phase", "measured") for r in rows} or {"measured"}) \
            if "all" in vals else {"measured"} | vals
    table = None
    if any(isinstance(r.get("usage"), dict) for r in rows):
        table = _price_table()
        if (warning := model_prices.stale(table)):
            print(f"warning: {warning}", file=sys.stderr)
    s = summarize(rows, prices=parse_price_map(args.price), include_phases=include, table=table)
    print(json.dumps(s, indent=2))
    return 0


def cmd_backfill(args: argparse.Namespace) -> int:
    n = backfill_phases()
    print(f"backfilled phase on {n} row(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Benchmark harness runner (repo-only).")
    sub = p.add_subparsers(dest="cmd", required=True)
    arms = tuple(sorted(ARM_CLAUDE_MD))

    pr = sub.add_parser("prepare", help="Set up a workspace for one (fixture, arm) run.")
    pr.add_argument("--fixture", required=True)
    pr.add_argument("--arm", required=True, choices=arms)
    pr.add_argument("--dest", required=True)
    pr.add_argument("--harness", help="install the skill into this harness's local skill "
                                      "directory, as install.sh --list-targets names it")
    pr.add_argument("--skill-ref", dest="skill_ref",
                    help="the commit whose skill is installed (with --harness)")
    pr.set_defaults(func=cmd_prepare)

    rn = sub.add_parser("run", help="Prepare, run the arm's prompt headless in a harness's CLI, "
                                    "score and record the usage it printed.")
    rn.add_argument("--fixture", required=True)
    rn.add_argument("--arm", required=True, choices=arms)
    rn.add_argument("--harness", required=True, help=f"one of {', '.join(sorted(HEADLESS))}")
    rn.add_argument("--skill-ref", dest="skill_ref", required=True,
                    help="the commit whose skill the workspace carries")
    rn.add_argument("--run-id", dest="run_id", required=True)
    rn.add_argument("--dest", required=True, help="the workspace; absent or empty")
    rn.add_argument("--model", help="passed to the CLI, and the row's model where its output "
                                    "names none")
    rn.add_argument("--timeout", type=int, default=3600, help="seconds the CLI may run")
    rn.add_argument("--score-timeout", dest="score_timeout", type=int, default=120)
    rn.add_argument("--phase", choices=("measured", "calibration"), default="measured")
    rn.add_argument("--results", help="the results log (default tools/bench/results/runs.jsonl)")
    rn.set_defaults(func=cmd_run)

    sc = sub.add_parser("score", help="Run the held-back suite against a finished workspace.")
    sc.add_argument("--fixture", required=True)
    sc.add_argument("--workspace", required=True)
    sc.add_argument("--timeout", type=int, default=120)
    sc.add_argument("--format", choices=("text", "json"), default="text")
    sc.set_defaults(func=cmd_score)

    rc = sub.add_parser("record", help="Append one run's metrics to the results log.")
    rc.add_argument("--fixture", required=True)
    rc.add_argument("--arm", required=True, choices=arms)
    rc.add_argument("--run-id", dest="run_id", required=True)
    rc.add_argument("--metrics-json", dest="metrics_json",
                    help="path to a transcript_metrics.py output file (automatic capture)")
    rc.add_argument("--tokens", type=int, help="manual fallback; stamps metrics_source=manual")
    rc.add_argument("--wall-time-s", dest="wall_time_s", type=float,
                    help="manual fallback; stamps metrics_source=manual")
    rc.add_argument("--iterations", type=int)
    rc.add_argument("--defect-escape", dest="defect_escape")
    rc.add_argument("--rework", dest="rework")
    rc.add_argument("--audit-score", dest="audit_score", type=float,
                    help="0-1 Auditability score from audit_quiz.py")
    rc.add_argument("--model-mix", dest="model_mix",
                    help="tiers that delivered the run, e.g. tiny:2,medium:1 (arm R)")
    rc.add_argument("--phase", choices=("measured", "calibration"), default="measured",
                    help="measured (default) or calibration; calibration rows are excluded "
                         "from summary aggregates unless --include-phase asks for them")
    rc.set_defaults(func=cmd_record)

    sm = sub.add_parser("summary", help="Aggregate results per fixture x arm x harness.")
    sm.add_argument("--price", help="relative tier prices, e.g. tiny=0.25,small=1,large=5 "
                                      "(operator-supplied; enables the cost index)")
    sm.add_argument("--include-phase", dest="include_phase", action="append",
                    help="add a phase to the default measured-only aggregate (repeatable); "
                         "e.g. --include-phase calibration, or --include-phase all. Calibration "
                         "rows are excluded by default (protocol v2 no-pooling rule).")
    sm.add_argument("--results", help="the results log (default tools/bench/results/runs.jsonl)")
    sm.set_defaults(func=cmd_summary)

    bf = sub.add_parser("backfill", help="One-time: stamp phase on legacy rows lacking it.")
    bf.set_defaults(func=cmd_backfill)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
