#!/usr/bin/env python3
"""SDLC Studio config loader.

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

DEFAULTS_PATH = Path(__file__).resolve().parent.parent / "templates" / "config-defaults.yaml"


def _yaml():
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - exercised only without PyYAML
        raise RuntimeError("config loading needs PyYAML (pip install pyyaml)") from exc
    return yaml


def _load_errors() -> tuple[type[BaseException], ...]:
    """The exception types `get` degrades on. BG0160: a malformed `.config.yaml` makes
    `yaml.safe_load` raise `yaml.YAMLError` (Parser/Scanner errors) - a subclass of Exception,
    NOT ValueError - so it slipped past the old `(RuntimeError, OSError, ValueError)` catch and
    tracebacked through every consumer. `yaml.YAMLError` is added when PyYAML is importable (the
    import is guarded: its absence is already covered by the RuntimeError from `_yaml`)."""
    errors: tuple[type[BaseException], ...] = (RuntimeError, OSError, ValueError)
    try:
        import yaml
        errors += (yaml.YAMLError,)
    except ImportError:  # pragma: no cover - PyYAML absence is the RuntimeError path
        pass
    return errors


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


_DEGRADE_WARNED = False


def get(repo_root: Path | str, dotted: str, default=None):
    """Resolve a dotted key (e.g. `coverage.unit`) from the config, or `default`.

    BG0093: if the config cannot be loaded at all (PyYAML absent, or an unreadable/malformed
    override), degrade to `default` with a one-line stderr warning instead of raising - so a
    stdlib-only machine gets the built-in default, not a traceback. This unifies the former
    three regimes (warn-degrade / silent-default / hard-crash) into warn-and-default."""
    global _DEGRADE_WARNED
    try:
        cur = load_config(repo_root)
    except _load_errors() as exc:
        if not _DEGRADE_WARNED:
            _DEGRADE_WARNED = True
            print(f"warning: could not load .config.yaml ({exc}); using built-in defaults "
                  "(config-driven behaviour needs PyYAML: pip install pyyaml)", file=sys.stderr)
        return default
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def feature_enabled(repo_root: Path | str, feature: str) -> bool:
    """Is `<feature>.enabled` in force? THE one resolution of knob-then-schema, shared.

    `<feature>.enabled` when the project states one, and the schema version otherwise. Two
    reasons for a knob rather than the schema gate alone, both learned rather than designed.

    The v3 gate BUNDLES. A project wanting one control had to adopt plan-review, spec-guard, the
    inbox status and the v3 id format in a single act across every artefact it holds, so the
    controls stayed unreachable in practice: the project that BUILT the triage session cap filed
    801 findings in a month with that cap sitting unused, and hand-rolled the consolidation the
    fold does automatically. And the schema version describes the shape of artefacts, which is
    not what any of these features is about.

    ONE definition, called by both adopters. Two copies of this resolution are two answers to the
    question "is this on", and they drift the moment either is touched - which is the class of
    defect this repository files against itself most often.

    An unset knob keeps the previous behaviour exactly, so no consuming project changes.
    """
    try:
        stated = get(repo_root, f"{feature}.enabled", None)
    except Exception:  # noqa: BLE001 - config must never break a feature check
        stated = None
    if stated is None:
        from lib import sdlc_md  # noqa: PLC0415 - deferred; avoids a config->sdlc_md import cycle
        return sdlc_md.is_schema_v3(repo_root)
    return bool(stated)


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
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
