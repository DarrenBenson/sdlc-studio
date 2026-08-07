#!/usr/bin/env python3
"""The shipped command surface, enumerated once for every reader that needs it.

Promoted out of `tests/test_cli_grammar.py`, whose `_all_parsers()` swallowed every import
failure and every `build_parser()` failure with a bare `continue` while its docstring claimed to
sweep the whole family. A sweep that silently drops what it cannot load reports a count of what
happened to work, and the two are indistinguishable to anybody reading the number.

So this enumerates and NAMES. A module that will not import appears in the result carrying its
exception; a `build_parser` that raises appears carrying its own. Nothing is dropped, and a
caller that wants only the working ones filters them out itself, visibly.

Two shapes of verb exist and both are walked:

  * a SUBPARSER choice - `sprint.py plan`, the common case;
  * a positional argument's `choices` - which is how `verify_ac.py testplan derive` exists. A
    subparser-only walk misses it, and a verb the enumeration cannot see is a verb no coverage
    number can count as missing, which is the direction that flatters the total.

Pure stdlib, and it imports nothing from the skill's own modules at import time, because it is
the thing those modules' tests measure.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

#: Scripts that are NOT command-line entry points and are exempt from carrying `build_parser`.
#: One entry, and it earns it structurally: `carry_forward.py` has no `main`, no `__main__`
#: guard and no `ArgumentParser` anywhere in it - it is a policy library that other modules
#: import. Writing a parser for it to satisfy a blanket rule would be inventing a surface, which
#: is the opposite of enumerating one.
#:
#: `autosprint.py` is deliberately ABSENT from this list. It is a deprecated alias that
#: re-exports `sprint`'s `build_parser` by name, so `getattr` finds one and it is not an
#: exception at all - listing it here would make the exemption set wrong on the day it was
#: written.
NON_CLI = ("carry_forward.py",)


@dataclass
class ScriptSurface:
    """One script's contribution to the surface, including the ways it can fail to have one."""

    name: str
    verbs: list[str] = field(default_factory=list)
    flags: set[str] = field(default_factory=set)
    error: str | None = None          # why this script contributed nothing, or None
    has_build_parser: bool = False

    @property
    def readable(self) -> bool:
        return self.error is None


def _load(path: Path):
    """Import `path` under its OWN module name, registered before execution.

    The name matters. A module registered under a fabricated one (`sweep_foo`) is a different
    module to anything that resolves itself by name, and `sys.modules[name] = mod` before
    `exec_module` is what lets a module import its own siblings during execution.
    """
    name = path.stem
    cached = sys.modules.get(name)
    if cached is not None:
        # ...but only if it is THIS file. Two directories can hold the same stem - a fixture and
        # the real script - and returning the cached one would report the fixture's surface as
        # the real script's, or the other way round. The name is the key argparse needs; the
        # PATH is the identity.
        if getattr(cached, "__file__", None) and Path(cached.__file__) == path:
            return cached
        sys.modules.pop(name, None)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        sys.modules.pop(name, None)   # a half-executed module must not be left importable
        raise
    return mod


def verbs_of(parser: argparse.ArgumentParser, prefix: str = "") -> list[str]:
    """Every verb reachable from `parser`, subcommands and positional choices alike."""
    found: list[str] = []
    for action in getattr(parser, "_actions", []):
        if isinstance(action, argparse._SubParsersAction):        # noqa: SLF001 - argparse's API
            for name, sub in action.choices.items():
                found.append(prefix + name)
                found.extend(verbs_of(sub, f"{prefix}{name} "))
        elif not action.option_strings and getattr(action, "choices", None):
            # A POSITIONAL with `choices` is a verb by any reading a user would give it:
            # `verify_ac.py testplan derive` is typed exactly like a subcommand.
            found.extend(prefix + c for c in action.choices if isinstance(c, str))
    return found


def flags_of(parser: argparse.ArgumentParser) -> set[str]:
    """Every option string in the tree, `--help` included."""
    out: set[str] = set()
    stack = [parser]
    while stack:
        p = stack.pop()
        for action in getattr(p, "_actions", []):
            out.update(action.option_strings)
            if isinstance(action, argparse._SubParsersAction):    # noqa: SLF001
                stack.extend(action.choices.values())
    return out


def enumerate_scripts(scripts_dir: Path | str | None = None) -> list[ScriptSurface]:
    """Every script under `scripts_dir`, with its verbs, its flags, or the reason it has neither.

    NOTHING IS SKIPPED. A module that raises on import comes back with `error` set and
    `readable` False, which is the whole point: `_all_parsers()` returned a shorter list and
    said nothing, so the count it produced was of the scripts that happened to load.
    """
    root = Path(scripts_dir or SCRIPTS)
    out: list[ScriptSurface] = []
    for path in sorted(root.glob("*.py")):
        if path.name.startswith("_"):
            continue
        rec = ScriptSurface(name=path.name)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                mod = _load(path)
        except BaseException as exc:  # noqa: BLE001 - REPORTED, never swallowed
            rec.error = f"{type(exc).__name__}: {exc}"
            out.append(rec)
            continue
        build = getattr(mod, "build_parser", None)
        rec.has_build_parser = callable(build)
        if not rec.has_build_parser:
            rec.error = "no build_parser"
            out.append(rec)
            continue
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                parser = build()
        except BaseException as exc:  # noqa: BLE001 - a parser needing runtime state is a finding
            rec.error = f"build_parser raised {type(exc).__name__}: {exc}"
            out.append(rec)
            continue
        rec.verbs = verbs_of(parser)
        rec.flags = flags_of(parser)
        out.append(rec)
    return out


def verbs(scripts_dir: Path | str | None = None) -> dict[str, list[str]]:
    """`{script name: [verb, ...]}` for every script that has any. The readers' usual entry."""
    return {s.name: s.verbs for s in enumerate_scripts(scripts_dir) if s.verbs}


def all_flags(scripts_dir: Path | str | None = None) -> set[str]:
    """Every option string across the whole surface."""
    out: set[str] = set()
    for s in enumerate_scripts(scripts_dir):
        out |= s.flags
    return out


def unreadable(scripts_dir: Path | str | None = None) -> dict[str, str]:
    """`{script name: why}` for everything the sweep could not read. Empty is the good state,
    and it is a STATED empty rather than an absence somebody has to infer."""
    return {s.name: s.error for s in enumerate_scripts(scripts_dir)
            if s.error and s.error != "no build_parser"}


def missing_build_parser(scripts_dir: Path | str | None = None) -> list[str]:
    """CLI scripts with no `build_parser`, with the declared non-CLIs removed."""
    return [s.name for s in enumerate_scripts(scripts_dir)
            if not s.has_build_parser and s.name not in NON_CLI]
