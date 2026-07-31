"""The lockfile carries the patched transitives, and the linter still LINTS (BG0468).

Three high-severity advisories reached this tree through `markdownlint-cli`, the only
devDependency. A lockfile is easy to regress by accident - a stray `npm install` on an old
cache, a merge that takes the wrong side - and the regression is silent, so it is pinned here
rather than trusted to `npm audit` being run by someone.

The second test is the one that matters more. `js-yaml` crossed a MAJOR version to clear its
advisory, and markdownlint drives the gate's markdown lane. A dependency bump that leaves the
linter running but no longer detecting anything passes every gate it is in, which is the exact
shape of defect this repo keeps filing against itself.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOCK = REPO / "package-lock.json"
MDL = REPO / "node_modules" / ".bin" / "markdownlint"

#: (package, minimum patched version) from the advisories: GHSA-v245-v573-v5vm,
#: GHSA-52cp-r559-cp3m, GHSA-3jxr-9vmj-r5cp.
PATCHED = {"linkify-it": (5, 0, 2), "js-yaml": (4, 3, 0), "brace-expansion": (5, 0, 7)}


def _version(name: str) -> tuple[int, ...] | None:
    data = json.loads(LOCK.read_text(encoding="utf-8"))
    for path, meta in (data.get("packages") or {}).items():
        if path.endswith("/" + name):
            raw = (meta.get("version") or "").split("-")[0]
            return tuple(int(p) for p in raw.split(".") if p.isdigit())
    return None


class LockfileTests(unittest.TestCase):
    def test_the_patched_transitives_are_at_or_above_their_fixed_versions(self) -> None:
        self.assertTrue(LOCK.is_file(), f"{LOCK} is missing")
        for name, floor in PATCHED.items():
            got = _version(name)
            self.assertIsNotNone(got, f"{name} is not in the lockfile at all")
            self.assertGreaterEqual(got, floor,
                                    f"{name} {got} is below the patched {floor} - a high-severity "
                                    f"advisory has been reintroduced")

    def test_package_json_was_not_widened_to_clear_the_advisory(self) -> None:
        """The cheap wrong fix is to loosen a range until the resolver picks something clean.
        The declared range is unchanged; only the lockfile moved."""
        pkg = json.loads((REPO / "package.json").read_text(encoding="utf-8"))
        self.assertEqual("^0.49.0", (pkg.get("devDependencies") or {}).get("markdownlint-cli"))


class TheLinterStillLintsTests(unittest.TestCase):
    def test_a_file_with_known_violations_is_REFUSED(self) -> None:
        """Not that markdownlint RUNS - that it still FAILS on something it should fail on.
        `js-yaml` crossed a major version to clear its advisory, and a linter that exits 0 on
        everything is indistinguishable from a clean tree."""
        if not MDL.is_file():                     # pragma: no cover - npm install not run
            self.skipTest(f"{MDL} not installed; run npm install")
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "probe.md"
            bad.write_text("# T\n\ntrailing spaces   \n\n\n\nbare http://example.com\n",
                           encoding="utf-8")
            proc = subprocess.run([str(MDL), str(bad)], capture_output=True, text=True)
            self.assertNotEqual(0, proc.returncode,
                                "markdownlint accepted a file with trailing whitespace, "
                                "consecutive blanks and a bare URL - it runs but no longer lints")
            out = proc.stdout + proc.stderr
            for rule in ("MD009", "MD012", "MD034"):
                self.assertIn(rule, out, f"{rule} no longer fires")


if __name__ == "__main__":
    unittest.main()
