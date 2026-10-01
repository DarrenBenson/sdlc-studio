"""BG0866: the lockfile resolves a js-yaml outside Dependabot alert 19's range.

markdownlint-cli 0.49.1, the latest release and the only devDependency, pins `js-yaml ~5.2.1`,
so a plain install resolves 5.2.2 - inside GHSA-r3ph-w7gj-g6xm (vulnerable >= 5.0.0, <= 5.4.0,
patched 5.4.1). No markdownlint-cli release admits a patched js-yaml, so package.json holds it
with an npm `overrides` entry, and this test pins both the resolved version and the override:
a lockfile regenerated without the override drops straight back to 5.2.2.

The compare is numeric on the (major, minor, patch) tuple, never on the string, so 5.10.0 reads
above 5.4.1 and 5.4.10 above 5.4.9.
"""
from __future__ import annotations

# test-census-subject: package-lock.json
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOCK = REPO / "package-lock.json"
PACKAGE = REPO / "package.json"
#: First patched release for GHSA-r3ph-w7gj-g6xm (Dependabot alert 19).
PATCHED = (5, 4, 1)


def semver(raw: str) -> tuple[int, int, int]:
    """(major, minor, patch) of a plain or range-prefixed version: '5.4.1', '^5.4.1', '5.4.1-rc.1'."""
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", raw or "")
    if not m:
        raise ValueError(f"no semver in {raw!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


class SemverTests(unittest.TestCase):
    def test_the_compare_is_numeric_not_lexical(self) -> None:
        self.assertGreater(semver("5.10.0"), PATCHED)
        self.assertLess(semver("5.4.0"), PATCHED)
        self.assertGreater(semver("^5.4.10"), semver("5.4.9"))


class JsYamlPatchedTests(unittest.TestCase):
    def test_the_lockfile_resolves_a_patched_js_yaml(self) -> None:
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        entry = (lock.get("packages") or {}).get("node_modules/js-yaml")
        self.assertIsNotNone(entry, "node_modules/js-yaml is not in package-lock.json")
        got = semver(entry.get("version", ""))
        self.assertGreaterEqual(got, PATCHED,
                                f"package-lock.json resolves js-yaml {entry.get('version')}, inside "
                                f"GHSA-r3ph-w7gj-g6xm (patched 5.4.1)")
        nested = [k for k in lock["packages"] if k.endswith("/node_modules/js-yaml")]
        self.assertEqual([], nested, f"a second, unpatched js-yaml may resolve at {nested}")

        pkg = json.loads(PACKAGE.read_text(encoding="utf-8"))
        override = (pkg.get("overrides") or {}).get("js-yaml")
        self.assertIsNotNone(override, "package.json carries no js-yaml override, so the next "
                                       "install resolves markdownlint-cli's ~5.2.1 again")
        self.assertGreaterEqual(semver(override), PATCHED,
                                f"the js-yaml override {override!r} admits a vulnerable release")


if __name__ == "__main__":
    unittest.main()
