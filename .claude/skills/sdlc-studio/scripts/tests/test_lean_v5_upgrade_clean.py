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
import os
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


def _cutoff_project(root: Path, *ids: str) -> None:
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "schema_version: 3\nconformance:\n  adopt_after: BG-01KX95QP\n", encoding="utf-8")
    for sid in ids:
        _story(root, sid)


class UlidCutoffFailsClosedTests(unittest.TestCase):
    """US0974 round 1. A v3 suffix is six timestamp characters and two random ones, so ids in
    the cutoff's own ~17-minute bucket do not sort by when they were minted."""

    def test_a_ulid_cutoff_judges_every_other_id_in_its_own_bucket(self) -> None:
        """MUTANTS: (1) compare the whole suffix (`suffix <= cutoff`) - `US-01KX95AA`, minted in
        the cutoff's bucket and sorting below it by its random pair, is exempt; (2) exempt the
        whole bucket - `US-01KX95ZZ` is exempt; (3) drop the earlier-bucket exemption."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cutoff_project(root, "US-01KX94ZZ", "US-01KX95AA", "US-01KX95QP", "US-01KX95ZZ",
                            "US-01KX96AA")
            r = _cli(root, "conformance.py", "check", "--format", "json")
            exempt = {u["id"]: u["exempt"] for u in json.loads(r.stdout)["units"]}
        self.assertEqual({"US-01KX94ZZ": True,       # an earlier bucket
                          "US-01KX95AA": False,      # the cutoff's bucket, random pair below
                          "US-01KX95QP": True,       # the cutoff itself
                          "US-01KX95ZZ": False,      # the cutoff's bucket, random pair above
                          "US-01KX96AA": False},     # a later bucket
                         exempt)

    def test_a_sequential_id_under_a_ulid_cutoff_is_exempt(self) -> None:
        """The migration case: a project's sequential ids predate its v3 ids. MUTANT: return
        False for a sequential id under a v3 cutoff."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cutoff_project(root, "US0103", "US-01KZ00AA")
            r = _cli(root, "conformance.py", "check", "--format", "json")
            exempt = {u["id"]: u["exempt"] for u in json.loads(r.stdout)["units"]}
        self.assertEqual({"US0103": True, "US-01KZ00AA": False}, exempt)

    def test_only_a_dashed_id_is_read_as_a_v3_suffix(self) -> None:
        """MUTANT: make the dash optional in the v3 pattern - a dashless key (`US01KX94ZZ`) is
        read as a suffix and exempted, and a long sequential id could be too."""
        sys.path.insert(0, str(SCRIPTS))
        from lib import sdlc_md  # noqa: PLC0415
        cutoff = sdlc_md.parse_cutoff("BG-01KX95QP", allow_ulid=True)
        self.assertTrue(sdlc_md.cutoff_exempts("US-01KX94ZZ", cutoff), "premise: dashed, earlier")
        self.assertFalse(sdlc_md.cutoff_exempts("US01KX94ZZ", cutoff),
                         "a dashless key was read as a v3 suffix")
        self.assertTrue(sdlc_md.cutoff_exempts("US0123456", cutoff),
                        "a 7-digit sequential id is read as sequential, and exempt")

    def test_migrate_reads_a_ulid_cutoff_through_the_validate_lane(self) -> None:
        """The validate lane's no-AC exemption reads the same key. MUTANT: restore the strict
        `parse_cutoff` there - migrate then dies on `ValueError` over a story with no AC."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cutoff_project(root)
            st = root / "sdlc-studio" / "stories"
            st.mkdir(parents=True, exist_ok=True)
            (st / "US-01KX90AA-no-ac.md").write_text(
                "# US-01KX90AA: no ac\n\n> **Status:** Done\n> **Epic:** EP-01KX00AA\n",
                encoding="utf-8")
            r = _cli(root, "migrate.py", "--format", "json")
            self.assertNotIn("Traceback", r.stderr, r.stderr)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            json.loads(r.stdout)


class MigrateReadsOnlyWhatItReadsTests(unittest.TestCase):
    """US0974 round 1: the readability probe covers the config, the pipeline artefacts and their
    indexes, and a file no step reads is never one."""

    def test_a_bad_note_no_step_reads_does_not_stop_apply(self) -> None:
        """The reviewer's repro. MUTANT: probe every `*.md` under `sdlc-studio/` - a non-UTF-8
        `reviews/notes.md` stops `--apply`, and the missing config is never created."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _initialised(root)
            (root / "sdlc-studio" / ".config.yaml").unlink()
            (root / "sdlc-studio" / "reviews" / "notes.md").write_bytes(b"# notes\n\xff\xfe\n")
            (root / "sdlc-studio" / ".local").mkdir(exist_ok=True)
            (root / "sdlc-studio" / ".local" / "scratch.md").write_bytes(b"\xff\xfe\n")
            r = _cli(root, "migrate.py", "--apply", "--format", "json")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            report = json.loads(r.stdout)
            self.assertEqual([], [h for h in report["needs_human"] if h.get("kind") == "unreadable"])
            self.assertTrue((root / "sdlc-studio" / ".config.yaml").is_file(),
                            "--apply did not create the missing config")

    def test_an_unreadable_config_is_named(self) -> None:
        """MUTANT: leave `.config.yaml` out of the probe - it is not named."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _initialised(root)
            (root / "sdlc-studio" / ".config.yaml").write_bytes(b"schema_version: 3\n\xff\xfe\n")
            r = _cli(root, "migrate.py", "--format", "json")
            self.assertNotIn("Traceback", r.stderr, r.stderr)
            paths = [h.get("path") for h in json.loads(r.stdout)["needs_human"]
                     if h.get("kind") == "unreadable"]
            self.assertEqual(["sdlc-studio/.config.yaml"], paths)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root opens any file")
    def test_a_file_that_cannot_be_opened_is_named_with_its_own_remedy(self) -> None:
        """MUTANTS: (1) catch only `UnicodeDecodeError` - a `PermissionError` is a traceback;
        (2) tell it to re-save as UTF-8, a remedy that does not apply."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _initialised(root)
            story = root / "sdlc-studio" / "stories" / "US0001-locked.md"
            story.write_text("# US0001: locked\n\n> **Status:** Draft\n", encoding="utf-8")
            story.chmod(0)
            try:
                r = _cli(root, "migrate.py", "--format", "json")
            finally:
                story.chmod(0o644)       # before the directory is removed
            self.assertNotIn("Traceback", r.stderr, r.stderr)
            item = next(h for h in json.loads(r.stdout)["needs_human"]
                        if h.get("kind") == "unreadable")
            self.assertEqual("sdlc-studio/stories/US0001-locked.md", item["path"])
            self.assertIn("PermissionError", item["detail"])
            self.assertNotIn("re-save it as UTF-8", item["detail"])


#: Files a sweep step reads that the up-front probe does not cover: each stopped migrate with a
#: traceback (round 2's repros). Relative to the project root.
_STEP_READ_FILES = ("sdlc-studio/personas/maya.md", "AGENTS.md", "sdlc-studio/.version")


class MigrateStepFailureIsNamedTests(unittest.TestCase):
    """US0974 round 2: the probe covers only what AC3 names (pipeline artefacts, their indexes and
    `.config.yaml`); a step that meets an unreadable file is named as a failed step instead."""

    def test_a_step_reading_an_unreadable_file_is_named_not_a_traceback(self) -> None:
        """The reviewer's three repros. MUTANTS: (1) the guard removed - a traceback and exit 1;
        (2) the guard catching nothing - the same; (3) `--apply` writing after the failed step -
        the later sizing step gives the legacy-Effort CR a Size line."""
        for rel in _STEP_READ_FILES:
            with self.subTest(rel), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _initialised(root)
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"# x\n\xff\xfe\n")
                (root / "sdlc-studio" / ".config.yaml").unlink()
                cr = root / "sdlc-studio" / "change-requests" / "CR0001-x.md"
                cr.parent.mkdir(parents=True, exist_ok=True)
                cr.write_text("# CR0001: legacy\n\n> **Status:** Approved\n> **Effort:** M\n",
                              encoding="utf-8")
                r = _cli(root, "migrate.py", "--apply", "--format", "json")
                self.assertNotIn("Traceback", r.stderr, r.stderr)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                failed = [h for h in json.loads(r.stdout)["needs_human"]
                          if h.get("kind") == "step-failed"]
                self.assertTrue(failed, r.stdout)
                self.assertIn("UnicodeDecodeError", failed[0]["error"])
                self.assertIn(failed[0]["step"], failed[0]["detail"])
                self.assertIn(rel, failed[0]["files"], failed[0])
                self.assertIn(rel, failed[0]["detail"])
                self.assertFalse((root / "sdlc-studio" / ".config.yaml").exists(),
                                 "--apply wrote after a step failed")
                self.assertNotIn("Size", cr.read_text(encoding="utf-8"),
                                 "a later step wrote after a step failed")
                sized = [x for x in json.loads(r.stdout)["deterministic"]
                         if x.get("source") == "sizing"]
                self.assertEqual([False], [x["applied"] for x in sized], sized)

    def test_a_step_failing_after_it_wrote_says_so_and_names_the_file(self) -> None:
        """Round 3's repro: the conventions step writes the config and moves one amigo card
        before it reads the undecodable one. MUTANTS: (1) the detail claiming nothing was
        written; (2) no scan after the failure - `files` empty and the card unnamed; (3) the
        scan skipping `personas/` - the same."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _initialised(root)
            (root / "sdlc-studio" / ".config.yaml").unlink()
            amigos = root / "sdlc-studio" / "personas" / "amigos"
            amigos.mkdir(parents=True)
            (amigos / "a-eng.md").write_text("# Engineering\n\n> **Role:** engineering\n",
                                             encoding="utf-8")
            (amigos / "b-qa.md").write_bytes(b"# QA\n\xff\xfe\n")
            r = _cli(root, "migrate.py", "--apply", "--format", "json")
            self.assertNotIn("Traceback", r.stderr, r.stderr)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            item = next(h for h in json.loads(r.stdout)["needs_human"]
                        if h.get("kind") == "step-failed")
            wrote = (root / "sdlc-studio" / ".config.yaml").exists()
        self.assertTrue(wrote, "premise: the step wrote the config before it failed")
        self.assertEqual(["sdlc-studio/personas/amigos/b-qa.md"], item["files"])
        self.assertNotIn("nothing was written", item["detail"])
        self.assertIn("stays written", item["detail"])

    def test_a_corrupt_meta_file_does_not_stop_apply(self) -> None:
        """Round 2's MOVED finding: no step reads a review or retro file. MUTANT: the meta types
        put back into the probe - both are named unreadable and the config is not created."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _initialised(root)
            (root / "sdlc-studio" / ".config.yaml").unlink()
            (root / "sdlc-studio" / "reviews" / "RV0001-x.md").write_bytes(b"# RV0001\n\xff\n")
            (root / "sdlc-studio" / "retros" / "RETRO0001-x.md").write_bytes(b"\xff\xfe\n")
            r = _cli(root, "migrate.py", "--apply", "--format", "json")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            kinds = [h.get("kind") for h in json.loads(r.stdout)["needs_human"]]
            self.assertNotIn("unreadable", kinds)
            self.assertNotIn("step-failed", kinds)
            self.assertTrue((root / "sdlc-studio" / ".config.yaml").is_file(),
                            "--apply did not create the missing config")


if __name__ == "__main__":
    unittest.main()
