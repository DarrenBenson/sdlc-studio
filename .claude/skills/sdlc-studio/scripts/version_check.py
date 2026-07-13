#!/usr/bin/env python3
"""SDLC Studio skill version check + self-update signal.

Compares the installed skill version (its own SKILL.md) against the latest published
GitHub release, so `status`/`hint` can surface a one-line "update available" notice on
the first use of a session - without nagging. Deterministic and fully degrading: any
network failure / rate-limit / disabled config yields a quiet status (never errors,
never blocks). The remote tag is TTL-cached and a declined version is snoozed until a
newer release appears. The `skill-update` action consumes `scope` to run the installer.

Subcommands:
  check   Report {installed, latest, status, scope}; status drives the notice.
  snooze  Record the current latest as dismissed (no notice until a newer release).
  scope   Print the detected install scope (user / project / agents).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

REPO = "DarrenBenson/sdlc-studio"
DEFAULT_TTL_HOURS = 24
_SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def skill_root() -> Path:
    """The installed skill directory (this script lives in <skill>/scripts/)."""
    return Path(__file__).resolve().parent.parent


def installed_version(skill_dir: Path | str) -> str | None:
    sk = Path(skill_dir) / "SKILL.md"
    if not sk.exists():
        return None
    m = re.search(r'^\s*version:\s*"?(\d+\.\d+\.\d+)"?', sk.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def _semver(v: str | None):
    m = _SEMVER.search(v or "")
    return tuple(int(x) for x in m.groups()) if m else None


def _gt(a: str | None, b: str | None) -> bool:
    """True when version a is strictly newer than b (both must parse)."""
    sa, sb = _semver(a), _semver(b)
    return sa is not None and sb is not None and sa > sb


def latest_release(repo: str = REPO, timeout: int = 5) -> str | None:
    """The latest published release tag (without a leading 'v'), or None on any failure
    (offline, rate-limited, 404) - the check then degrades silently."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers={"User-Agent": "sdlc-studio-version-check",  # GitHub API 403s without a UA
                 "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310  # nosec B310 - https GitHub API only
            tag = (json.loads(r.read().decode("utf-8")).get("tag_name") or "").lstrip("v")
        return tag or None
    except Exception:  # noqa: BLE001 - any failure is "offline"; never surface it
        return None


def _cache_path(skill_dir: Path) -> Path:
    return Path(skill_dir) / ".local" / "version-check.json"


def _read_cache(skill_dir: Path) -> dict:
    try:
        return json.loads(_cache_path(skill_dir).read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - missing/corrupt cache starts fresh
        return {}


def _write_cache(skill_dir: Path, data: dict) -> None:
    try:
        p = _cache_path(skill_dir)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:  # noqa: BLE001 - the cache is best-effort; a write failure is silent
        pass


def scope(skill_dir: Path | str | None = None) -> str:
    """Install scope from the skill's path: agents / user / project. User-scope means the
    tool dir (.claude/.codex/...) sits directly in $HOME; otherwise it is a project."""
    sd = Path(skill_dir or skill_root()).resolve()
    if ".agents" in sd.parts:
        return "agents"
    toolroot = sd.parent.parent  # <toolroot>/skills/<name>
    try:
        return "user" if str(toolroot.parent) == str(Path.home().resolve()) else "project"
    except Exception:  # noqa: BLE001
        return "project"


def check(skill_dir: Path | str | None = None, repo: str = REPO,
          ttl_hours: float = DEFAULT_TTL_HOURS, enabled: bool = True,
          _fetch=None, now: float | None = None) -> dict:
    """The version status. status is one of: disabled / offline / up-to-date / snoozed /
    update-available. The remote tag is TTL-cached; a network call happens only when the
    cache is stale (and never when disabled)."""
    sd = Path(skill_dir or skill_root())
    now = time.time() if now is None else now
    result = {"installed": installed_version(sd), "latest": None,
              "status": "up-to-date", "scope": scope(sd)}
    if not enabled:
        result["status"] = "disabled"
        return result
    cache = _read_cache(sd)
    cached = cache.get("latest")
    fresh = bool(cached) and (now - cache.get("fetched_at", 0)) < ttl_hours * 3600
    # A cached latest OLDER than what's installed is provably stale - a release shipped since the
    # cache was written (you cannot install newer-than-latest), so re-fetch instead of trusting it
    # (post-release the TTL window otherwise reports the old latest until it expires).
    if fresh and not _gt(result["installed"] or "0.0.0", cached):
        latest = cached  # fresh cache - no network call
    else:
        try:
            latest = (_fetch or (lambda: latest_release(repo)))()
        except Exception:  # noqa: BLE001 - any fetch failure is "offline", never raised
            latest = None
        if latest:  # a None (offline) result never poisons the cached latest
            cache.update(latest=latest, fetched_at=now)
            _write_cache(sd, cache)
    result["latest"] = latest
    if latest is None:
        result["status"] = "offline"
    elif not _gt(latest, result["installed"] or "0.0.0"):
        result["status"] = "up-to-date"
    elif cache.get("snoozed") == latest:
        result["status"] = "snoozed"
    else:
        result["status"] = "update-available"
    return result


def snooze(skill_dir: Path | str | None = None) -> str | None:
    """Dismiss the current latest version - no notice until a newer release appears."""
    sd = Path(skill_dir or skill_root())
    cache = _read_cache(sd)
    if cache.get("latest"):
        cache["snoozed"] = cache["latest"]
        _write_cache(sd, cache)
    return cache.get("snoozed")


def notice(result: dict) -> str | None:
    """The one-line notice for `status`/`hint`, or None when there is nothing to say."""
    if result.get("status") != "update-available":
        return None
    return (f"SDLC Studio {result['latest']} is available (installed {result['installed']}) "
            f"- run /sdlc-studio skill-update, or it stays quiet until the next release.")


def _config(args):
    enabled = sdlc_md.project_override(args.root, "version_check.enabled", True)
    ttl = sdlc_md.project_override(args.root, "version_check.ttl_hours", DEFAULT_TTL_HOURS)
    try:
        ttl = float(ttl)
    except (TypeError, ValueError):
        ttl = DEFAULT_TTL_HOURS
    return bool(enabled), ttl


def cmd_check(args: argparse.Namespace) -> int:
    enabled, ttl = _config(args)
    res = check(args.skill_dir, ttl_hours=ttl, enabled=enabled)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        print(notice(res) or f"version: {res['status']} (installed {res['installed']}, "
              f"latest {res['latest'] or '?'})")
    return 0


def cmd_snooze(args: argparse.Namespace) -> int:
    print(f"snoozed at {snooze(args.skill_dir) or '(nothing to snooze)'}")
    return 0


def cmd_scope(args: argparse.Namespace) -> int:
    print(scope(args.skill_dir))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Skill version check + self-update signal.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Report the version status.")
    c.add_argument("--root", default=".", help="Project root for config (default: .)")
    c.add_argument("--skill-dir", default=None, help="Override the skill dir (default: this install)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    s = sub.add_parser("snooze", help="Dismiss the current latest version.")
    s.add_argument("--skill-dir", default=None)
    s.set_defaults(func=cmd_snooze)
    sc = sub.add_parser("scope", help="Print the detected install scope.")
    sc.add_argument("--skill-dir", default=None)
    sc.set_defaults(func=cmd_scope)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
