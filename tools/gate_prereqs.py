#!/usr/bin/env python3
"""What the gates need, checked on the interpreter the hooks run, with a way to get it here.

A fresh clone learned what its gates needed from a push that went red after the full suite, or
from an install command its system Python refused. This names each missing or too-old
prerequisite at setup (`tools/enable-hooks.sh` runs it), says what breaks without it, and gives
an install route read from THIS interpreter: pip only where pip can install, otherwise the OS
package or a virtual environment placed first on PATH.

One list: the Python distributions come from `requirements-dev.txt`, the file CI installs from,
so the checker and CI cannot drift; the Node tool and the executables are declared here.

Subcommands:
  check   print every gap with its consequence and route; exit 1 if any, 0 if none
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

#: Prerequisites outside Python: `(name, how it is found, consequence, route)`.
TOOLS = (
    ("markdownlint", "markdownlint",
     "the commit's markdown lanes skip it, and CI enforces them after the push", "npm ci"),
    ("rg", "rg", "the tests that need ripgrep skip", "the package `ripgrep`"),
    ("gh", "gh", "the red-CI read before a push reads UNREAD",
     "https://cli.github.com (the package `gh`)"),
)

_REQ = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:>=\s*([0-9][0-9.]*))?\s*(?:#.*)?$")


def normalise(name: str) -> str:
    """A distribution name as the packaging index compares it."""
    return re.sub(r"[-_.]+", "-", name).lower()


def requirements(root: Path) -> list[tuple[str, tuple[int, ...] | None]]:
    """`(distribution, floor or None)` for each line of `requirements-dev.txt`."""
    path = root / "requirements-dev.txt"
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = _REQ.match(line)
        if m:
            out.append((m.group(1), _version_tuple(m.group(2)) if m.group(2) else None))
    return out


def _version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", text)[:3])


def installed_version(dist: str, python: str | None = None) -> str | None:
    """The installed version of `dist` on this interpreter, or on `python` when given, read by
    DISTRIBUTION name: an import name (`yaml`, `xdist`) is not a distribution name."""
    if python and Path(python).resolve() != Path(sys.executable).resolve():
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
    if in_venv or (has_pip and not managed):
        return "python3 -m pip install -r requirements-dev.txt"
    why = "is externally managed" if managed else "has no pip"
    return (f"{exe} {why}: install the OS packages (for example python3-pytest), or create a "
            f"virtual environment and put it first on PATH: python3 -m venv .venv && "
            f".venv/bin/python -m pip install -r requirements-dev.txt && "
            f"export PATH=\"$PWD/.venv/bin:$PATH\"")


def gaps(root: Path) -> list[str]:
    """One line per missing or too-old prerequisite, each with its consequence and route."""
    out = []
    if sys.version_info[:2] < PYTHON_FLOOR:
        out.append(f"python3 {sys.version.split()[0]} is older than "
                   f"{'.'.join(map(str, PYTHON_FLOOR))}: CI and `repo map build` need "
                   f"{'.'.join(map(str, PYTHON_FLOOR))} or later")
    route = None
    coverage_python = os.environ.get("SDLC_COVERAGE_PYTHON") or None
    for dist, floor in requirements(root):
        on = coverage_python if normalise(dist) == "coverage" else None
        found = installed_version(dist, on)
        consequence = CONSEQUENCE.get(normalise(dist), REFUSES)
        where = f" on {on}" if on else ""
        if found is None:
            problem = f"{dist} is missing{where}"
        elif floor and _version_tuple(found) < floor:
            problem = (f"{dist} {found} is too old{where}: "
                       f"{'.'.join(map(str, floor))} or later is needed")
        else:
            continue
        route = route or install_route()
        out.append(f"{problem} - {consequence}. Install: {route}")
    for name, exe, consequence, how in TOOLS:
        local = root / "node_modules" / ".bin" / exe
        if shutil.which(exe) or (name == "markdownlint" and local.exists()):
            continue
        out.append(f"{name} is not found - {consequence}. Install: {how}")
    return out


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    found = gaps(root)
    if not found:
        print("gate prerequisites: every one present")
        return 0
    print(f"gate prerequisites: {len(found)} gap(s) on {sys.executable}")
    for line in found:
        print(f"  {line}")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="the clone's root (default: .)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="name every missing prerequisite; exit 1 if any")
    args = ap.parse_args(argv)
    return cmd_check(args)


if __name__ == "__main__":
    sys.exit(main())
