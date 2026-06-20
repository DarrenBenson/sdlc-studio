#!/usr/bin/env python3
"""SDLC Studio config loader (CR0008).

`templates/config-defaults.yaml` is the single source of truth for skill defaults.
This loader reads it (merged with an optional project `sdlc-studio/.config.yaml`
override) so scripts read the value instead of re-deriving it from a markdown
table. Before this, every default lived in three places - the YAML, a duplicate
fenced block in reference-config.md, and a prose table - and drifted.

PyYAML is a soft dependency, imported lazily, so the pure-stdlib core scripts are
unaffected and only this helper needs it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULTS_PATH = Path(__file__).resolve().parent.parent / "templates" / "config-defaults.yaml"


def _yaml():
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - exercised only without PyYAML
        raise RuntimeError("config loading needs PyYAML (pip install pyyaml)") from exc
    return yaml


def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for key, val in over.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def load_config(repo_root: Path | str = ".", defaults_path: Path | str = DEFAULTS_PATH) -> dict:
    """Skill defaults merged with the project's `.config.yaml` override, if present."""
    yaml = _yaml()
    cfg = yaml.safe_load(Path(defaults_path).read_text(encoding="utf-8")) or {}
    override = Path(repo_root) / "sdlc-studio" / ".config.yaml"
    if override.exists():
        cfg = _deep_merge(cfg, yaml.safe_load(override.read_text(encoding="utf-8")) or {})
    return cfg


def get(repo_root: Path | str, dotted: str, default=None):
    """Resolve a dotted key (e.g. `coverage.unit`) from the config, or `default`."""
    cur = load_config(repo_root)
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def cmd_show(args: argparse.Namespace) -> int:
    """Print the resolved config, or a single dotted key."""
    if args.key:
        print(json.dumps(get(args.root, args.key)))
    else:
        print(json.dumps(load_config(args.root), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio config loader.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show", help="Print resolved config (or a single --key).")
    s.add_argument("--key", help="Dotted key, e.g. coverage.unit")
    s.add_argument("--root", default=".", help="Repo root (default: .)")
    s.set_defaults(func=cmd_show)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
