#!/usr/bin/env python3
"""What the gates need, checked on the interpreter the hooks run, with a way to get it here.

A fresh clone learned what its gates needed from a push that went red after the full suite, or
from an install command its system Python refused. This names each missing or too-old
prerequisite at setup (`tools/enable-hooks.sh` runs it), says what breaks without it, and gives
an install route read from the interpreter that lacks it: pip only where pip can install,
otherwise the OS package or a virtual environment placed first on PATH.

One list: the Python distributions come from `requirements-dev.txt`, the file CI installs the
suite's packages from; the Node tool and the executables are declared here.

Subcommands:
  check   print every gap with its consequence and route; exit 1 if any, 0 if none
          (`--refusing`: exit 1 only when a gap turns the push suite red, every other gap
          printed as a note - the pre-push hook's preflight)
"""
from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

#: The interpreter floor: what CI tests on and what `repo map build` needs.
PYTHON_FLOOR = (3, 10)

#: What breaks without each distribution, keyed by its normalised name. A declared distribution
#: with no class listed here refuses the push: an unknown gap is assumed to be the worst kind.
REFUSES = "the push suite goes red without it"
CONSEQUENCE = {
    "pytest": REFUSES,
    "coverage": REFUSES,
    "pyyaml": REFUSES,
    "pytest-xdist": "the push suite runs serially, so the gate takes several times as long",
}

#: Prerequisites outside Python: `(name, executable, consequence, route)`.
TOOLS = (
    ("markdownlint", "markdownlint",
     "the commit's markdown lanes skip it, and CI enforces them after the push", "npm ci"),
    ("rg", "rg", "the tests that need ripgrep skip", "the package `ripgrep`"),
    ("gh", "gh", "the red-CI read before a push reads UNREAD",
     "https://cli.github.com (the package `gh`)"),
)

#: One requirement line: a name, optional extras, a specifier set, an optional environment marker.
_REQ = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(\[[^\]]*\])?\s*([^;#]*?)\s*(;[^#]*)?(#.*)?$")
_SPEC = re.compile(r"^\s*(>=|==|~=|<=|<|>|!=|===)\s*([0-9][0-9A-Za-z.*+!-]*)\s*$")
_FLOOR_OPS = (">=", "==", "~=", "===")


def normalise(name: str) -> str:
    """A distribution name as the packaging index compares it."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", text)[:3])


def _below(found: tuple[int, ...], floor: tuple[int, ...]) -> bool:
    """Whether `found` is older than `floor`, comparing release parts padded to one length, so
    `8.3` meets a floor of `8.3.0` and `8.3.0` meets `8.3`."""
    width = max(len(found), len(floor))
    return found + (0,) * (width - len(found)) < floor + (0,) * (width - len(floor))


def requirements(root: Path) -> tuple[list[tuple[str, tuple[int, ...] | None]], list[str]]:
    """`(rows, not understood)`: `(distribution, floor or None)` for each requirement line of
    `requirements-dev.txt`, and each line the checker cannot read, which it names rather than
    drops. A floor is the lowest version a specifier admits (`>=`, `==`, `~=`); an upper bound
    sets none. A pip option line (`-r`, `--index-url`) is not a requirement and is skipped."""
    path = root / "requirements-dev.txt"
    if not path.is_file():
        return [], []
    rows, unread = [], []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith(("#", "-")):
            continue
        m = _REQ.match(line)
        specs = [s for s in (m.group(3).split(",") if m and m.group(3) else []) if s.strip()]
        parsed = [_SPEC.match(s) for s in specs]
        if not m or not all(parsed):
            unread.append(f"requirements-dev.txt line {n} ({line.strip()}) is not understood, so "
                          f"it is not checked")
            continue
        floors = [_version_tuple(p.group(2)) for p in parsed if p.group(1) in _FLOOR_OPS]
        rows.append((m.group(1), max(floors) if floors else None))
    return rows, unread


def installed_version(dist: str, python: str | None = None) -> str | None:
    """The installed version of `dist`, read by DISTRIBUTION name (an import name such as `yaml`
    or `xdist` is not a distribution name): on this interpreter, or, when `python` names one,
    on THAT interpreter in a subprocess, never this one (a virtual environment's `bin/python`
    resolves to its base interpreter, which holds different packages). Raises OSError when
    `python` cannot run."""
    if python:
        r = subprocess.run([python, "-c", "import importlib.metadata as m, sys\n"
                            "try: print(m.version(sys.argv[1]))\n"
                            "except m.PackageNotFoundError: pass", dist],
                           capture_output=True, text=True, timeout=60, check=False)
        return r.stdout.strip() or None
    try:
        return importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return None


def install_route() -> str:
    """How to install the Python prerequisites on THIS interpreter."""
    exe = sys.executable
    in_venv = sys.prefix != sys.base_prefix
    managed = (Path(sysconfig.get_path("stdlib")) / "EXTERNALLY-MANAGED").exists()
    has_pip = importlib.util.find_spec("pip") is not None
    if has_pip and (in_venv or not managed):
        return "python3 -m pip install -r requirements-dev.txt"
    if in_venv:
        return (f"{exe} is a virtual environment with no pip: add it with `{exe} -m ensurepip`, "
                f"or install with the tool that made the environment (for example "
                f"`uv pip install -r requirements-dev.txt`)")
    why = "is externally managed" if managed else "has no pip"
    return (f"{exe} {why}: install the OS packages (for example python3-pytest), or create a "
            f"virtual environment and put it first on PATH: python3 -m venv .venv && "
            f".venv/bin/python -m pip install -r requirements-dev.txt && "
            f"export PATH=\"$PWD/.venv/bin:$PATH\"")


def _other_route(python: str, dist: str, floor: tuple[int, ...] | None) -> str:
    """The route for a distribution checked on an interpreter other than this one."""
    spec = f"{dist}>={'.'.join(map(str, floor))}" if floor else dist
    return f"{python} -m pip install '{spec}' (the interpreter SDLC_COVERAGE_PYTHON names)"


def gaps(root: Path) -> list[str]:
    """One line per missing or too-old prerequisite, each with its consequence and route."""
    out = []
    if sys.version_info[:2] < PYTHON_FLOOR:
        out.append(f"python3 {sys.version.split()[0]} is older than "
                   f"{'.'.join(map(str, PYTHON_FLOOR))}: CI and `repo map build` need "
                   f"{'.'.join(map(str, PYTHON_FLOOR))} or later")
    rows, unread = requirements(root)
    out.extend(unread)
    route = None
    coverage_python = os.environ.get("SDLC_COVERAGE_PYTHON") or None
    for dist, floor in rows:
        on = coverage_python if normalise(dist) == "coverage" else None
        consequence = CONSEQUENCE.get(normalise(dist), REFUSES)
        try:
            found = installed_version(dist, on)
        except OSError as exc:
            out.append(f"SDLC_COVERAGE_PYTHON names {on}, which cannot run ({exc.strerror or exc})"
                       f" - {consequence}. Point it at an interpreter that has {dist}, or unset it")
            continue
        where = f" on {on}" if on else ""
        if found is None:
            problem = f"{dist} is missing{where}"
        elif floor and _below(_version_tuple(found), floor):
            problem = (f"{dist} {found} is too old{where}: "
                       f"{'.'.join(map(str, floor))} or later is needed")
        else:
            continue
        if on:
            how = _other_route(on, dist, floor)
        else:
            route = route or install_route()
            how = route
        out.append(f"{problem} - {consequence}. Install: {how}")
    for name, exe, consequence, how in TOOLS:
        local = root / "node_modules" / ".bin" / exe
        if shutil.which(exe) or (name == "markdownlint" and os.access(local, os.X_OK)):
            continue
        out.append(f"{name} is not found - {consequence}. Install: {how}")
    return out


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    found = gaps(root)
    if not found:
        print("gate prerequisites: every one present")
        return 0
    if getattr(args, "refusing", False):
        refusing = [g for g in found if REFUSES in g]
        for line in found:
            print(f"  {'REFUSES' if line in refusing else 'note'}: {line}")
        return 1 if refusing else 0
    print(f"gate prerequisites: {len(found)} gap(s) on {sys.executable}")
    for line in found:
        print(f"  {line}")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the clone's root (default: .)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("check", help="name every missing prerequisite; exit 1 if any")
    check.add_argument("--refusing", action="store_true",
                       help="exit 1 only for a gap that turns the push suite red; name the "
                            "rest as notes")
    args = ap.parse_args(argv)
    return cmd_check(args)


if __name__ == "__main__":
    sys.exit(main())
