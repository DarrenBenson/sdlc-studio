"""US1089: `critic.py brief` refuses a unit whose author has recorded no self-check of its diff.

`review.author_self_check` decides what a brief does when the unit has no current self-check row
(its digest matching the content of its Affects as it stands, or the commit view BG1117 adds,
pinned in test_self_check_survives_a_later_unit.py): `block` refuses it, before anything
reaches stdout and before the brief's fingerprint is noted, and still prints the author
self-check section so the author is told what to record; `report`, the shipped default, prints
the brief and names the missing or stale record on stderr; `off` says nothing of it. The check
binds a first-round brief and a `--rejoinder` one, at either tier.

Every criterion drives `critic.py` through its entry point in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")

HEADING = "AUTHOR SELF-CHECK"
RECORD = "critic.py self-check record"
MISSING = "no author self-check recorded"
STALE = "is stale"
AFFECTS = "src/widget.py, tests/test_widget.py, changelog.d/US0101.md"
TIERS = ("full", "light")


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, setting: str | None) -> None:
    """US0101 with a code file, a test file and a fragment in its Affects, a QA seat card, and
    `review.author_self_check` set to `setting` (left unset when None)."""
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "tests/test_widget.py", "def test_w():\n    assert True\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
    _write(root, "sdlc-studio/stories/US0101-widget.md",
           "# US0101: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Affects:** {AFFECTS}\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")
    if setting is not None:
        _write(root, "sdlc-studio/.config.yaml", f"review:\n  author_self_check: {setting}\n")


def _record(root: Path) -> None:
    """A self-check of US0101 as its Affects stand now, through the shipped command."""
    claims = [{"surface": "commit message", "claim": "w returns 1", "ruling": "TRUE"},
              {"surface": "changelog.d/US0101.md", "claim": "w is new", "ruling": "TRUE"}]
    mutants = [{"mutant": "w returns 2", "test": "tests/test_widget.py::test_w",
                "result": "killed"}]
    (root / "claims.json").write_text(json.dumps(claims), encoding="utf-8")
    (root / "mutants.json").write_text(json.dumps(mutants), encoding="utf-8")
    r = subprocess.run([sys.executable, "-B", str(CRITIC), "self-check", "record", "--unit",
                        "US0101", "--claims", str(root / "claims.json"), "--mutants",
                        str(root / "mutants.json"), "--author", "builder", "--root", str(root)],
                       capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                       check=False)
    assert r.returncode == 0, r.stderr


def _brief(root: Path, tier: str, rejoinder: bool = False) -> subprocess.CompletedProcess:
    extra = []
    if rejoinder:
        prior = root / "verdict.txt"
        prior.write_text("VERDICT: REJECT\nISSUES: [new] blocking: w returns 1 (src/widget.py:2)\n",
                         encoding="utf-8")
        extra = ["--rejoinder", str(prior)]
    return subprocess.run([sys.executable, "-B", str(CRITIC), "brief", "--unit", "US0101",
                           "--seat", "qa", "--tier", tier, *extra, "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


class SelfCheckRefusalTests(unittest.TestCase):

    def _refused(self, root: Path, r: subprocess.CompletedProcess, *names: str) -> None:
        """Exit 2 naming the record command and `names`, nothing on stdout, no fingerprint
        noted, and the author self-check section on stderr ahead of the refusal."""
        self.assertEqual(2, r.returncode, f"not refused:\n{r.stderr}")
        self.assertEqual("", r.stdout, "a refused brief still reached stdout")
        self.assertNotIn("brief fingerprint:", r.stderr, "a refused brief printed a fingerprint")
        self.assertIsNone(critic.noted_brief(root, "US0101"),
                          "a refused brief still noted its fingerprint")
        refusal = r.stderr[r.stderr.find("brief refused:"):]
        self.assertTrue(refusal.startswith("brief refused:"), r.stderr)
        for name in (RECORD, "review.author_self_check: block", *names):
            self.assertIn(name, refusal, "the refusal does not name what to do")
        self.assertIn(HEADING, r.stderr, "the steps to record were withheld on a refusal")
        self.assertLess(r.stderr.find(HEADING), r.stderr.find("brief refused:"),
                        "the steps come after the refusal rather than before it")

    def _admitted(self, root: Path, r: subprocess.CompletedProcess) -> str:
        """Exit 0 with the brief on stdout and its fingerprint on stderr and noted; returns it."""
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertTrue(r.stdout.strip(), "no brief on stdout")
        found = re.search(r"brief fingerprint: (\S+)", r.stderr)
        self.assertIsNotNone(found, f"no fingerprint on stderr:\n{r.stderr}")
        self.assertEqual(found.group(1), critic.noted_brief(root, "US0101"),
                         "the printed fingerprint was not noted")
        return found.group(1)

    def test_no_record_is_refused_with_the_steps(self) -> None:
        """AC1. Mutants: the refusal printed after the brief (stdout carries it) or after
        `note_brief` (the fingerprint is noted); the steps withheld on a refusal; the light tier
        skipping the check."""
        for tier in TIERS:
            with self.subTest(tier=tier), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, "block")
                self._refused(root, _brief(root, tier), MISSING)

    def test_a_stale_record_is_refused(self) -> None:
        """AC2. Mutants: the `--rejoinder` path or the light tier skipping the check; the latest
        row admitted on its unit alone, whatever its digest; the refusal naming no staleness."""
        for tier in TIERS:
            for rejoinder in (False, True):
                with self.subTest(tier=tier, rejoinder=rejoinder), \
                        tempfile.TemporaryDirectory() as d:
                    root = Path(d)
                    _project(root, "block")
                    _record(root)
                    _write(root, "src/widget.py", "def w():\n    return 2\n")
                    self._refused(root, _brief(root, tier, rejoinder), STALE)

    def test_a_current_record_admits_the_brief(self) -> None:
        """AC3, the positive control. Mutants: a matching record still refused; the brief or its
        fingerprint changed by the gate; a record of an earlier diff, re-recorded, not admitted."""
        for tier in TIERS:
            for rejoinder in (False, True):
                with self.subTest(tier=tier, rejoinder=rejoinder), \
                        tempfile.TemporaryDirectory() as d:
                    root = Path(d)
                    _project(root, "block")
                    _record(root)
                    _write(root, "src/widget.py", "def w():\n    return 2\n")
                    _record(root)
                    r = _brief(root, tier, rejoinder)
                    fp = self._admitted(root, r)
                    for said in (MISSING, STALE, "brief refused"):
                        self.assertNotIn(said, r.stderr)
                    if not rejoinder:
                        self.assertEqual(critic.brief_fingerprint(
                            critic.brief(root, "US0101", "qa", tier)), fp,
                            "the admitted brief is not the brief critic.brief() renders")

    def test_the_setting_decides_refuse_report_or_silence(self) -> None:
        """AC4. Mutants: the shipped default set to `block`, which only a run leaving the key
        unset can see; `report` naming neither a missing nor a stale record; `off` still
        printing it; the default declared as anything but `report` in config-defaults.yaml or
        reference-config.md."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, None)
            r = _brief(root, "full")
            self._admitted(root, r)
            self.assertIn(MISSING, r.stderr, "an unset key did not name the missing record")
            self.assertIn(RECORD, r.stderr[r.stderr.find(MISSING):])
            _record(root)
            self.assertNotIn(MISSING, _brief(root, "full").stderr)
            _write(root, "src/widget.py", "def w():\n    return 2\n")
            r = _brief(root, "light", rejoinder=True)
            self._admitted(root, r)
            self.assertIn(STALE, r.stderr, "an unset key did not name the stale record")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "off")
            r = _brief(root, "full")
            self._admitted(root, r)
            self.assertIn(HEADING, r.stderr, "`off` withheld the author self-check section")
            for said in (MISSING, STALE):
                self.assertNotIn(said, r.stderr, "`off` still spoke of the record")
        import yaml  # noqa: PLC0415 - the shipped defaults are YAML
        defaults = yaml.safe_load((SKILL / "templates" / "config-defaults.yaml")
                                  .read_text(encoding="utf-8"))
        self.assertEqual("report", defaults["review"]["author_self_check"])
        self.assertEqual("report", critic.AUTHOR_SELF_CHECK_DEFAULT)
        doc = (SKILL / "reference-config.md").read_text(encoding="utf-8")
        self.assertRegex(doc, r"\n\| `review\.author_self_check` \| `report` \|",
                         "reference-config.md gives no row for the key with default `report`")

    def test_an_unknown_setting_is_refused_by_name(self) -> None:
        """Mutant: a mistyped setting read as `off` (or as the default), so a typo switches the
        gate off silently."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "blokc")
            _record(root)
            r = _brief(root, "full")
            self.assertEqual(2, r.returncode, r.stderr)
            self.assertEqual("", r.stdout)
            self.assertIn("review.author_self_check is `blokc`", r.stderr)


if __name__ == "__main__":
    unittest.main()
