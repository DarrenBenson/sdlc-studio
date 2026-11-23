"""BG1417: CI's lint.yml set up Node 20 while markdownlint-cli and markdownlint declare
`node >=22`, and `npm ci` only warns on an engines mismatch, so the gap stayed invisible until a
dependency used an API Node 20 lacks.

The check reads every `node-version` lint.yml's setup-node steps ask for and every
`engines.node` range package-lock.json records, and holds each requested version to each range.
A `node-version` of `22` lets setup-node install any 22.x, the runner's cached one included, so
both the lowest and the highest version it admits must satisfy every range.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

# test-census-subject: .github/workflows/lint.yml

REPO = Path(__file__).resolve().parents[5]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
LOCK = REPO / "package-lock.json"
#: Stands in for "any later minor or patch" in the highest version a partial version admits.
_ANY = 10 ** 9
_VERSION = re.compile(r"^v?(\d+)(?:\.(\d+|[xX*]))?(?:\.(\d+|[xX*]))?$")


def _parts(text: str) -> list[int | None]:
    """`22.12` -> [22, 12, None]: the parts a version names, None for each it leaves open."""
    m = _VERSION.match(text.strip())
    if not m:
        raise ValueError(f"not a version this check reads: {text!r}")
    return [int(p) if p and p.isdigit() else None for p in m.groups()]


def _low(parts: list[int | None]) -> tuple[int, int, int]:
    return tuple(p if p is not None else 0 for p in parts)  # type: ignore[return-value]


def _high(parts: list[int | None]) -> tuple[int, int, int]:
    return tuple(p if p is not None else _ANY for p in parts)  # type: ignore[return-value]


def _bump(parts: list[int | None], at: int) -> tuple[int, int, int]:
    """The first version past `parts` at position `at`: `^22.22.2` ends below `_bump(.., 0)`."""
    out = [p or 0 for p in parts]
    out[at] += 1
    return tuple(out[:at + 1] + [0] * (2 - at))  # type: ignore[return-value]


def _comparators(alternative: str) -> list[tuple[str, tuple[int, int, int]]]:
    """One `||` alternative of an npm range as (operator, version) pairs ANDed together."""
    out: list[tuple[str, tuple[int, int, int]]] = []
    for tok in re.sub(r"(>=|<=|>|<|=)\s+", r"\1", alternative).split():
        op, ver = re.match(r"^(>=|<=|>|<|=|\^|~)?(.*)$", tok).groups()
        if ver in ("*", "x", "X", ""):
            continue
        parts = _parts(ver)
        filled = sum(p is not None for p in parts)
        if op in (">=", ">", "<", "<="):
            out.append((op, _high(parts) if op in (">", "<=") else _low(parts)))
        elif op == "^":
            first = next((i for i, p in enumerate(parts) if p), filled - 1)
            out += [(">=", _low(parts)), ("<", _bump(parts, min(first, filled - 1)))]
        elif op == "~":
            out += [(">=", _low(parts)), ("<", _bump(parts, min(1, filled - 1)))]
        else:  # an exact or partial version: `20` is any 20.x
            out += [(">=", _low(parts)), ("<=", _high(parts))]
    return out


def satisfies(version: tuple[int, int, int], spec: str) -> bool:
    """Whether `version` meets the npm range `spec` (`>=22`, `18 || 20 || >=22`, `^22.22.2`)."""
    ops = {">=": lambda a, b: a >= b, ">": lambda a, b: a > b, "<": lambda a, b: a < b,
           "<=": lambda a, b: a <= b, "=": lambda a, b: a == b}
    return any(all(ops[op](version, bound) for op, bound in _comparators(alt))
               for alt in spec.split("||"))


def ci_node_versions(workflow: dict) -> list[str]:
    """The `node-version` of every setup-node step in every job."""
    found = []
    for job in workflow.get("jobs", {}).values():
        for step in job.get("steps", []):
            if str(step.get("uses", "")).startswith("actions/setup-node@"):
                found.append(str(step.get("with", {}).get("node-version", "")))
    return found


def engine_ranges(lock: dict) -> dict[str, str]:
    """`engines.node` of every package the lockfile installs, by its path in the lock."""
    return {name or "(root)": pkg["engines"]["node"]
            for name, pkg in lock.get("packages", {}).items()
            if isinstance(pkg.get("engines"), dict) and pkg["engines"].get("node")}


def problems(workflow: dict, lock: dict) -> list[str]:
    """Each CI Node version that an engines range refuses, at either end of what it admits."""
    out = []
    for requested in ci_node_versions(workflow):
        parts = _parts(requested)
        for name, spec in sorted(engine_ranges(lock).items()):
            for end in sorted({_low(parts), _high(parts)}):
                if not satisfies(end, spec):
                    shown = ".".join("x" if p == _ANY else str(p) for p in end)
                    out.append(f"node-version {requested!r} admits {shown}, which {name} "
                               f"refuses (engines.node {spec!r})")
    return out


class CiNodeVersionTests(unittest.TestCase):
    """BG1417 AC1: the Node CI sets up meets every engines requirement in the lockfile."""

    def setUp(self) -> None:
        self.workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        self.lock = json.loads(LOCK.read_text(encoding="utf-8"))

    def test_every_ci_node_version_meets_every_engines_range(self) -> None:
        versions = ci_node_versions(self.workflow)
        self.assertEqual(3, len(versions), versions)
        self.assertGreater(len(engine_ranges(self.lock)), 10)
        self.assertEqual([], problems(self.workflow, self.lock))

    def test_node_20_against_a_node_22_engine_is_refused(self) -> None:
        """The case the bug names, and the near misses either side of it."""
        def lint(version: str, spec: str, package: str = "node_modules/markdownlint-cli"):
            workflow = {"jobs": {"ci": {"steps": [
                {"uses": "actions/setup-node@abc", "with": {"node-version": version}}]}}}
            return problems(workflow, {"packages": {package: {"engines": {"node": spec}}}})

        refused = lint("20", ">=22")
        self.assertEqual(["node-version '20' admits 20.0.0, which node_modules/markdownlint-cli "
                          "refuses (engines.node '>=22')",
                          "node-version '20' admits 20.x.x, which node_modules/markdownlint-cli "
                          "refuses (engines.node '>=22')"], refused)
        self.assertEqual([], lint("22", ">=22"))
        self.assertEqual([], lint("26", ">=22"))
        # a major alone admits its .0 release: a minor floor inside the line is not met
        self.assertEqual(1, len(lint("22", ">=22.12.0")))
        self.assertEqual([], lint("22.12.0", ">=22.12.0"))
        # an upper bound holds too: the highest 24.x is outside `^22.22.2 || <24.5`
        self.assertEqual(1, len(lint("24", "^22.22.2 || <24.5")))
        # the project's own engines field, the lockfile's "" package, is held too
        self.assertIn("which (root) refuses", lint("20", ">=22", package="")[0])

    def test_the_range_reader_follows_npm(self) -> None:
        """Each npm range form the lockfile uses, at and across its edges."""
        cases = [
            ((20, 0, 0), "18 || 20 || >=22", True), ((21, 9, 0), "18 || 20 || >=22", False),
            ((22, 22, 2), "^22.22.2 || ^24.15.0 || >=26.0.0", True),
            ((22, 22, 1), "^22.22.2 || ^24.15.0 || >=26.0.0", False),
            ((23, 0, 0), "^22.22.2 || ^24.15.0 || >=26.0.0", False),
            ((24, 14, 9), "^22.22.2 || ^24.15.0 || >=26.0.0", False),
            ((26, 0, 0), "^22.22.2 || ^24.15.0 || >=26.0.0", True),
            ((18, 0, 0), ">= 18", True), ((17, 9, 9), ">= 18", False),
            ((6, 0, 0), ">=6.0", True), ((5, 9, 0), ">=6.0", False),
            ((0, 10, 0), ">=0.10.0", True), ((0, 9, 9), ">=0.10.0", False),
            ((0, 2, 5), "^0.2.3", True), ((0, 3, 0), "^0.2.3", False),
            ((0, 0, 3), "^0.0.3", True), ((0, 0, 4), "^0.0.3", False),
            ((1, 2, 9), "~1.2.3", True), ((1, 3, 0), "~1.2.3", False),
            ((1, 9, 0), "~1", True), ((2, 0, 0), "~1", False),
            ((4, 9, 0), ">4", False), ((5, 0, 0), ">4", True), ((4, 0, 0), ">4.0.0", False),
            ((4, 0, 1), ">4.0.0", True), ((3, 9, 9), "<4", True),
            ((4, 0, 0), "<4", False), ((4, 5, 0), "<=4", True), ((5, 0, 0), "<=4", False),
            ((4, 0, 0), "=4.0.0", True), ((4, 0, 1), "=4.0.0", False),
            ((9, 9, 9), "*", True), ((20, 1, 0), "20.x", True), ((21, 0, 0), "20.x", False),
            ((12, 0, 0), ">=12 <13", True), ((13, 0, 0), ">=12 <13", False),
        ]
        for version, spec, want in cases:
            with self.subTest(version=version, spec=spec):
                self.assertEqual(want, satisfies(version, spec))
        for unreadable in ("lts/*", "node", "22.1.2.3"):
            with self.subTest(unreadable=unreadable), self.assertRaises(ValueError):
                _parts(unreadable)


if __name__ == "__main__":
    unittest.main()
