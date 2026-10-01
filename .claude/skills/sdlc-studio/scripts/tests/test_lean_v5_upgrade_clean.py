"""US0974: a v5 upgrade reads clean.

Three things kept an up-to-date project's `migrate` from reading clean or from naming its own
trouble: a schema v3 adoption cutoff (`conformance.adopt_after: BG-01KX95QP`) raised
`ValueError`, so the remedy the conformance lane names could not be written; a standard
directory not yet created was listed under needs-a-human although it is created on first use;
and a story holding non-UTF-8 bytes stopped `migrate --format json` with a traceback that named
no file.

Every test drives the shipped CLI in a throwaway tree and reads nothing of this repository.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/migrate.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402


def _cli(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *args, "--root", str(root)],
                          cwd=root, env=gitutil.git_env(), capture_output=True, text=True,
                          timeout=300, check=False)


def _story(root: Path, sid: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{sid}-a-story.md").write_text(
        f"# {sid}: a story\n\n> **Status:** Done\n> **Epic:** EP-01KX00AA\n\n"
        "## Acceptance Criteria\n\n### AC1: works\n\n- **Verify:** shell true\n", encoding="utf-8")


def _initialised(root: Path) -> None:
    """A fresh `init run` project: up to date with the shipped skill, schema v3."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], env=gitutil.git_env(),
                   check=True, capture_output=True)
    r = _cli(root, "init.py", "run")
    if r.returncode != 0:
        raise AssertionError(f"init run failed:\n{r.stdout}\n{r.stderr}")


class V5UpgradeCleanTests(unittest.TestCase):
    """AC1-AC3."""

    def test_a_ulid_cutoff_is_accepted(self) -> None:
        """AC1. MUTANTS: (1) HEAD's `parse_cutoff` - the ULID raises `ValueError`; (2) compare a
        ULID by `id_number` alone - nothing is exempt; (3) compare the suffix the wrong way -
        the later unit is exempt and the earlier one judged."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "schema_version: 3\nconformance:\n  adopt_after: BG-01KX95QP\n", encoding="utf-8")
            _story(root, "US-01KX90AA")     # minted before the cutoff
            _story(root, "US-01KX95QP")     # minted at it: "at or before" includes it
            _story(root, "US-01KZ00AA")     # minted after it
            r = _cli(root, "conformance.py", "check", "--format", "json")
            self.assertNotIn("ValueError", r.stderr, r.stderr)
            self.assertNotIn("Traceback", r.stderr, r.stderr)
            exempt = {u["id"]: u["exempt"] for u in json.loads(r.stdout)["units"]}
            self.assertEqual({"US-01KX90AA": True, "US-01KX95QP": True, "US-01KZ00AA": False},
                             exempt, "the ULID cutoff did not exempt exactly the units at or "
                                     "before it")

    def test_an_unused_standard_dir_needs_no_human(self) -> None:
        """AC2. MUTANT: keep the `missing-dirs` report - `no retros dir(s) - created when you
        first use them` is listed under needs-a-human."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _initialised(root)
            retros = root / "sdlc-studio" / "retros"
            for p in sorted(retros.rglob("*"), reverse=True):
                p.unlink() if p.is_file() else p.rmdir()
            retros.rmdir()
            r = _cli(root, "migrate.py", "--format", "json")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            human = json.loads(r.stdout)["needs_human"]
            self.assertTrue(isinstance(human, list), "premise: the report carries needs_human")
            self.assertEqual([], [h for h in human if "retros" in h["detail"]
                                  or h.get("kind") == "missing-dirs"],
                             f"an unused standard directory needs a human:\n{human}")

    def test_an_unreadable_story_is_named_in_the_json(self) -> None:
        """AC3. MUTANTS: (1) drop the readability probe - `validate` raises `UnicodeDecodeError`
        mid-sweep and stdout is empty; (2) name no file - the item does not carry the path."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _initialised(root)
            bad = root / "sdlc-studio" / "stories" / "US0001-x.md"
            bad.write_bytes(b"# US0001: x\n\n> **Status:** Draft\n\xff\xfe\n")
            r = _cli(root, "migrate.py", "--format", "json")
            self.assertNotIn("Traceback", r.stderr, r.stderr)
            report = json.loads(r.stdout)
            unreadable = [h for h in report["needs_human"] if h.get("kind") == "unreadable"]
            self.assertEqual(["sdlc-studio/stories/US0001-x.md"],
                             [h.get("path") for h in unreadable], report["needs_human"])
            self.assertIn("sdlc-studio/stories/US0001-x.md", unreadable[0]["detail"])
            self.assertEqual(b"# US0001: x\n\n> **Status:** Draft\n\xff\xfe\n", bad.read_bytes(),
                             "migrate rewrote the file it could not read")


if __name__ == "__main__":
    unittest.main()
