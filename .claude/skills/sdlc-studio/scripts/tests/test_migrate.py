"""Tests for the migrate orchestrator (migrate.py) - RFC0041, US0154-US0156.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_SCRIPTS / "tests"))
import gitutil  # noqa: E402 - confined, hermetic git for fixtures
migrate = _load("migrate")


def _w(root: Path, rel: str, text: str) -> None:
    p = root / "sdlc-studio" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _mixed(root: Path) -> None:
    """A project with one of each: a legacy-Effort container (deterministic Size), an accepted
    childless request (needs refine), a childless Triaging Issue (needs triage), a legacy-Effort
    delivery unit (needs resize)."""
    _w(root, "change-requests/CR0001-x.md", "# CR-0001: legacy\n\n> **Status:** Approved\n> **Effort:** M\n")
    _w(root, "change-requests/CR0002-y.md", "# CR-0002: accepted\n\n> **Status:** Approved\n> **Size:** M\n")
    _w(root, "issues/IS0001-z.md", "# IS0001: untriaged\n\n> **Status:** Triaging\n> **Severity:** High\n> **Size:** M\n")
    _w(root, "bugs/BG0001-b.md", "# BG0001: bug\n\n> **Status:** Open\n> **Effort:** S\n> **Severity:** Low\n")


class MigrateTests(unittest.TestCase):
    def test_non_skill_repo_is_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            res = migrate.migrate(Path(d))
            self.assertFalse(res["applicable"])

    def test_dry_run_aggregates_deterministic_and_needs_human_and_writes_nothing(self) -> None:
        from lib import sdlc_md
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root)   # dry-run
            self.assertTrue(res["applicable"])
            self.assertFalse(res["applied"])
            # deterministic includes the container's sizing conversion + the conventions gaps
            det = {x.get("id") or x.get("kind") for x in res["deterministic"]}
            self.assertIn("CR0001", det)
            # nothing written
            self.assertFalse((root / "sdlc-studio" / ".version").exists())
            self.assertIsNone(sdlc_md.read_size(
                (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text()))

    def test_the_artefact_sweep_names_each_ceremony_with_a_command(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root)
            kinds = {h["kind"]: h for h in res["needs_human"] if h.get("id")}
            self.assertIn("needs-refine", kinds)          # CR0002 (and CR0001) accepted, childless
            self.assertIn("needs-triage", kinds)          # IS0001
            self.assertIn("needs-resize", kinds)          # BG0001 legacy Effort
            # each carries the exact command to resolve it
            refine = next(h for h in res["needs_human"] if h["kind"] == "needs-refine")
            self.assertIn("refine apply --request", refine["command"])
            triage = next(h for h in res["needs_human"] if h["kind"] == "needs-triage")
            self.assertIn("triage apply --issue IS0001", triage["command"])

    def test_apply_writes_only_the_deterministic_set(self) -> None:
        from lib import sdlc_md
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root, apply=True)
            self.assertTrue(res["applied"])
            # deterministic set written: a real version (BG0150 - never "unknown"), config, Size
            ver = (root / "sdlc-studio" / ".version").read_text()
            self.assertIn("skill_version:", ver)
            self.assertNotIn("unknown", ver)
            self.assertEqual(sdlc_md.read_size(
                (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text()), "M")
            # the needs-human items are NEVER auto-applied, checked at the FILE level:
            # the accepted CR is still childless, the Issue still untriaged, the bug still no Points
            self.assertEqual(sdlc_md.decomposed_ids(
                (root / "sdlc-studio" / "change-requests" / "CR0002-y.md").read_text()), [])
            issue = (root / "sdlc-studio" / "issues" / "IS0001-z.md").read_text()
            self.assertEqual(sdlc_md.decomposed_ids(issue), [])
            self.assertEqual(sdlc_md.extract_field(issue, "Status"), "Triaging")   # not triaged
            self.assertIsNone(sdlc_md.read_points(
                (root / "sdlc-studio" / "bugs" / "BG0001-b.md").read_text()))

    def test_apply_deterministic_list_has_no_advisories_or_warnings(self) -> None:
        # the honest split: an advisory (team-offer) or a warning (BG0150 not-stamped) must NEVER be
        # reported as an applied deterministic upgrade - only real changes are.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root, apply=True)
            for det in res["deterministic"]:
                self.assertNotIn("WARNING", det["detail"])
                self.assertNotIn("run persona", det["detail"])
                self.assertNotIn("uncovered", det["detail"])
                self.assertNotIn("SKIPPED", det["detail"])

    def test_dry_run_and_apply_agree_on_the_deterministic_count(self) -> None:
        # dry-run is a faithful preview: applying the same tree reports the same deterministic set,
        # classified from the same source (audit), not from apply's free-text actions.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            preview = migrate.migrate(root)["summary"]["deterministic"]
            applied = migrate.migrate(root, apply=True)["summary"]["deterministic"]
            self.assertEqual(preview, applied)

    def test_unreadable_install_version_is_needs_human_not_deterministic(self) -> None:
        # BG0150 through the orchestrator: when the install version cannot be read, the version is a
        # needs-human blocker in the report - never a promised/applied deterministic upgrade.
        vc = migrate.project_upgrade.version_check
        orig = vc.installed_version
        vc.installed_version = lambda *a, **k: None
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _mixed(root)
                res = migrate.migrate(root)   # dry-run
                det_kinds = {x.get("kind") for x in res["deterministic"]}
                self.assertNotIn("missing-version", det_kinds)   # not promised
                hk = {h["kind"] for h in res["needs_human"]}
                self.assertIn("version-unresolvable", hk)        # reported as a blocker
        finally:
            vc.installed_version = orig

    def _deterministic_section(self, res: dict) -> str:
        """The rendered report's deterministic half, up to the needs-human heading."""
        return migrate.render(res).split("## Needs a human")[0]

    def test_apply_seeds_a_missing_agents_md(self) -> None:
        # US0293 AC1: seeding a file that does not exist is deterministic, so the command whose
        # purpose is bringing a project up to date writes it instead of handing back a task.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root, apply=True)
            agents = root / "AGENTS.md"
            self.assertTrue(agents.exists(), "AGENTS.md was not seeded")
            text = agents.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# "), "the guidance comment was not stripped")
            self.assertIn(root.resolve().name, text)      # the derivable placeholder is filled
            self.assertNotRegex(text, r"(?i)\{\{\s*project_name\s*\}\}")
            self.assertIn("{{", text)                     # judgement fields stay visibly unfilled
            self.assertIn("AGENTS.md", self._deterministic_section(res))

    def test_dry_run_names_the_seed_and_writes_nothing(self) -> None:
        # US0293 AC2: seeding is visible before it happens.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root)                   # no --apply
            section = self._deterministic_section(res)
            self.assertIn("AGENTS.md", section)
            self.assertIn("CLAUDE.md", section)
            self.assertFalse((root / "AGENTS.md").exists())
            self.assertFalse((root / "CLAUDE.md").exists())

    def test_claude_md_seeded_when_absent_and_reported_when_duplicating(self) -> None:
        # US0293 AC4: absent -> the thin pointer is written; duplicating -> untouched, reported
        # with the one-line pointer that would replace it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            migrate.migrate(root, apply=True)
            self.assertIn("@AGENTS.md", (root / "CLAUDE.md").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            (root / "AGENTS.md").write_text("# Proj\n\nour own instructions\n", encoding="utf-8")
            dup = root / "CLAUDE.md"
            dup.write_text("# Proj\n\nthe whole instructions restated inline\n", encoding="utf-8")
            before = dup.read_bytes()
            res = migrate.migrate(root, apply=True)
            self.assertEqual(dup.read_bytes(), before, "a CLAUDE.md that exists was rewritten")
            human = " ".join(h["detail"] for h in res["needs_human"])
            self.assertIn("claude-not-pointer", human)
            self.assertIn("@AGENTS.md", human)

    def test_render_has_both_sections(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            text = migrate.render(migrate.migrate(root))
            self.assertIn("Deterministic", text)
            self.assertIn("Needs a human", text)
            self.assertIn("refine apply --request", text)


def _v4_era(root: Path, config_tail: str = "") -> None:
    """`tools/rehearse-release.sh upgrade`'s fixture: an `init`ed workspace aged to schema 2,
    US0001 Done and US0002 Ready (neither with a Verify line) and an Effort-sized CR."""
    import subprocess  # noqa: PLC0415
    subprocess.run([sys.executable, str(_SCRIPTS / "init.py"), "--root", str(root), "run"],
                   check=True, capture_output=True, text=True)
    cfg = root / "sdlc-studio" / ".config.yaml"
    cfg.write_text(cfg.read_text(encoding="utf-8").replace("schema_version: 3", "schema_version: 2")
                   + config_tail, encoding="utf-8")
    _w(root, "stories/US0001-legacy.md",
       "# US0001: legacy login\n\n> **Status:** Done\n> **Epic:** EP0001\n> **Priority:** High\n\n"
       "## Acceptance Criteria\n\n- [x] **AC1** a valid password logs the user in\n")
    _w(root, "stories/US0002-legacy.md",
       "# US0002: legacy reset\n\n> **Status:** Ready\n> **Epic:** EP0001\n"
       "> **Priority:** Medium\n\n"
       "## Acceptance Criteria\n\n- [ ] **AC1** a reset link sets a new password\n")
    _w(root, "change-requests/CR0001-legacy.md",
       "# CR-0001: legacy request\n\n> **Status:** Approved\n> **Priority:** Medium\n"
       "> **Effort:** M\n\n## Summary\n\nAdd SSO.\n")


class ConformanceCutoffTests(unittest.TestCase):
    """BG0785: the conformance lane fails a v4-era project's pre-adoption units, and migrate names
    the `conformance.adopt_after` cutoff that grandfathers them without ever writing it."""

    @staticmethod
    def _cutoffs(res: dict) -> list[dict]:
        return [h for h in res["needs_human"] if h["kind"] == "conformance-cutoff"]

    def test_migrate_names_the_cutoff_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v4_era(root)
            cfg = root / "sdlc-studio" / ".config.yaml"
            before = cfg.read_bytes()
            for apply in (False, True):
                res = migrate.migrate(root, apply=apply)
                items = self._cutoffs(res)
                self.assertEqual(1, len(items), f"apply={apply}: {res['needs_human']}")
                detail = items[0]["detail"]
                # The units the lane fails, and the HIGHEST of them as the cutoff: a lower one
                # leaves US0002 failing.
                self.assertIn("US0001", detail)
                self.assertIn("US0002", detail)
                self.assertIn("`conformance.adopt_after: US0002`", detail)
                # each unit with what it misses, so history reads apart from a breakage
                self.assertIn("US0002 (verifiable)", detail)
                self.assertIn("conformance.adopt_after: US0002", migrate.render(res))
                self.assertEqual(before, cfg.read_bytes(),
                                 f"apply={apply}: migrate wrote the cutoff itself")

    def test_an_existing_covering_cutoff_is_left_alone(self) -> None:
        # A real v4.1 project already carries `adopt_after: 179`, a bare number above every unit.
        # Proposing a cutoff anyway - or one computed without the existing exemption, which
        # would LOWER it to US0002 - is the failure.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v4_era(root, "\nconformance:\n  adopt_after: 179\n")
            for apply in (False, True):
                res = migrate.migrate(root, apply=apply)
                self.assertEqual([], self._cutoffs(res), f"apply={apply}")

    def test_a_dry_run_leaves_a_stamped_tree_byte_identical(self) -> None:
        # The lane resolves a STAMPED pytest selector by running the project's
        # `pytest --collect-only`, which writes into the project unless told not to: bytecode for
        # the conftest it loads, and `.pytest_cache/v/cache/lastfailed` when collection fails, as
        # the stamped file's missing import makes it. Both halves of migrate's guard are needed
        # for a dry run to leave every byte where it was. The caller's own cache and bytecode
        # settings are cleared so only migrate's guard can pass this.
        import os  # noqa: PLC0415
        import shutil  # noqa: PLC0415
        from unittest import mock  # noqa: PLC0415
        if shutil.which("pytest") is None:
            self.skipTest("no pytest on PATH, so the lane collects nothing and writes nothing")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v4_era(root)
            (root / "tests").mkdir()
            (root / "tests" / "conftest.py").write_text("import os\n", encoding="utf-8")
            (root / "tests" / "test_login.py").write_text(
                "import nosuchmod  # noqa: F401\n\n\ndef test_ok():\n    assert True\n",
                encoding="utf-8")
            _w(root, "stories/US0003-stamped.md",
               "# US0003: stamped\n\n> **Status:** Done\n> **Epic:** EP0001\n\n"
               "## Acceptance Criteria\n\n- [x] **AC1** given x, when y, then z\n"
               "  - **Verify:** pytest tests/test_login.py::test_ok\n"
               "  - **Verified:** yes (2026-09-02)\n")

            def tree() -> dict:
                return {str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None)
                        for p in sorted(root.rglob("*"))}
            before = tree()
            env = {k: v for k, v in os.environ.items()
                   if k not in ("PYTEST_ADDOPTS", "PYTHONDONTWRITEBYTECODE")}
            with mock.patch.dict(os.environ, env, clear=True):
                self.assertEqual(1, len(self._cutoffs(migrate.migrate(root))))
                self.assertNotIn("PYTEST_ADDOPTS", os.environ, "the guard leaked past the call")
            after = tree()
            self.assertEqual(sorted(before), sorted(after), "a dry run created or removed paths")
            self.assertEqual(before, after, "a dry run changed a file's bytes")

    def test_an_unreadable_cutoff_is_reported_not_raised(self) -> None:
        # The lane refuses a malformed cutoff; migrate names it rather than dying on it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v4_era(root, "\nconformance:\n  adopt_after: soon\n")
            items = self._cutoffs(migrate.migrate(root))
            self.assertEqual(1, len(items))
            self.assertIn("soon", items[0]["detail"])
            # BG0854: the error item still names the lane it speaks for, with no ids to name.
            self.assertEqual(("conformance", []), (items[0]["lane"], items[0]["ids"]))


#: A stand-in `pytest` for `CollectionPrimerTests`: it logs each `--collect-only` it is asked for,
#: with when it ran, the environment it ran under and whether CR0001 was sized when it started,
#: holds for a moment so that collections run together overlap, and lists one node.
_FAKE_PYTEST = """#!{python}
import json, os, sys, time
start = time.time()
cr = os.path.join("sdlc-studio", "change-requests", "CR0001-legacy.md")
with open(cr, encoding="utf-8") as f:
    sized = "**Size:**" in f.read()
time.sleep(1)
row = {{"file": sys.argv[-1], "start": start, "end": time.time(), "sized": sized,
        "addopts": os.environ.get("PYTEST_ADDOPTS", ""),
        "prefix": os.environ.get("PYTHONPYCACHEPREFIX"),
        "dontwrite": os.environ.get("PYTHONDONTWRITEBYTECODE"), "parent": os.getppid()}}
with open(os.environ["FAKE_PYTEST_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps(row) + "\\n")
print(sys.argv[-1] + "::test_ok")
"""


class CollectionPrimerTests(unittest.TestCase):
    """BG1183 AC2: the conformance step's test-file collections run side by side, each once,
    under the guard, and under --apply only once the steps that write have run."""

    FILES = [f"tests/test_{n}.py" for n in (1, 2, 3, 4)]

    def _run(self, apply: bool, between=None) -> tuple[list[dict], Path]:
        """The fixture through `migrate.migrate`, with `conformance` and `verify_ac` imported
        afresh for the call and dropped after it, so what an earlier test left in `sys.modules`
        cannot decide which module the primer and the lane collect with. `between` runs at the
        signed-records step, after a dry run's collections start and before the lane."""
        import json  # noqa: PLC0415
        import os  # noqa: PLC0415
        import shutil  # noqa: PLC0415
        from unittest import mock  # noqa: PLC0415
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        root, fake_bin, log = d / "repo", d / "bin", d / "collect.log"
        root.mkdir()
        fake_bin.mkdir()
        _v4_era(root)
        (root / "tests").mkdir()
        for n, rel in enumerate(self.FILES, 3):
            (root / rel).write_text("def test_ok():\n    assert True\n", encoding="utf-8")
            _w(root, f"stories/US000{n}-stamped.md",
               f"# US000{n}: stamped\n\n> **Status:** Done\n> **Epic:** EP0001\n\n"
               f"## Acceptance Criteria\n\n- [x] **AC1** given x, when y, then z\n"
               f"  - **Verify:** pytest {rel}::test_ok\n  - **Verified:** yes (2026-11-03)\n")
        # Two the lane never collects, so the primer must not: a Done story's unstamped line and
        # a Ready story's stamped one.
        for sid, status, stamp in (("US0007", "Done", ""),
                                   ("US0008", "Ready", "  - **Verified:** yes (2026-11-03)\n")):
            (root / f"tests/test_{sid}.py").write_text("def test_ok():\n    pass\n", "utf-8")
            _w(root, f"stories/{sid}-other.md",
               f"# {sid}: other\n\n> **Status:** {status}\n> **Epic:** EP0001\n\n"
               f"## Acceptance Criteria\n\n- [ ] **AC1** given x, when y, then z\n"
               f"  - **Verify:** pytest tests/test_{sid}.py::test_ok\n{stamp}")
        fake = fake_bin / "pytest"
        fake.write_text(_FAKE_PYTEST.format(python=sys.executable), encoding="utf-8")
        fake.chmod(0o755)
        env = {k: v for k, v in os.environ.items()
               if k not in ("PYTEST_ADDOPTS", "PYTHONPYCACHEPREFIX")}
        env.update(PATH=f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
                   FAKE_PYTEST_LOG=str(log))
        records = migrate._signed_records

        def recorded(*args, **kwargs):
            if between is not None:
                between()
            return records(*args, **kwargs)

        with mock.patch.dict(os.environ, env, clear=True), mock.patch.dict(sys.modules), \
                mock.patch.object(migrate, "_signed_records", recorded):
            for name in ("conformance", "verify_ac"):
                sys.modules.pop(name, None)
            migrate.migrate(root, apply=apply)
            self.assertNotIn("PYTEST_ADDOPTS", os.environ, "the guard leaked past the call")
            self.assertNotIn("PYTHONPYCACHEPREFIX", os.environ, "the guard leaked past the call")
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()], root

    def test_a_dry_run_collects_each_file_once_side_by_side_under_the_guard(self) -> None:
        """Fails on: no priming, or one worker (no two collections overlap); collections run
        as processes of migrate's own rather than by a `CollectionServer`; a primer whose
        cache key the lane does not read, or a lane that does not wait for a collection in
        flight (a file collected twice); a primer that collects a file the lane does not (an
        unstamped line, a story not Done); a guard that keeps `PYTHONDONTWRITEBYTECODE`, sets
        no bytecode prefix, leaves it behind, or is turned on again inside the lane."""
        import itertools  # noqa: PLC0415
        import os  # noqa: PLC0415
        rows, root = self._run(apply=False)
        self.assertEqual(self.FILES, sorted(r["file"] for r in rows))
        if (os.cpu_count() or 1) > 1:
            self.assertTrue(any(a["start"] < b["end"] and b["start"] < a["end"]
                                for a, b in itertools.combinations(rows, 2)),
                            "the collections ran one after another")
        for row in rows:
            self.assertNotEqual(os.getpid(), row["parent"], "collected without a server")
            self.assertEqual("-p no:cacheprovider", row["addopts"], "one guard, not two")
            self.assertIsNone(row["dontwrite"], "bytecode writes off: nothing is shared")
            self.assertTrue(row["prefix"], "no private bytecode directory")
            self.assertNotIn(str(root), row["prefix"], "the bytecode went into the project")
            self.assertFalse(Path(row["prefix"]).exists(), "the bytecode directory was left")

    def test_a_lane_on_another_verify_ac_module_reads_the_primed_answers(self) -> None:
        """A process can hold two `verify_ac` modules, as a test runner that loads it again under
        its name does, and the lane's can change after the collections start. Here the lane's
        module is swapped between the primer's start and the lane. Fails on a `serving` bound
        only to the module `start` collected with: the lane reads a cache nothing filled, and
        collects every file a second time."""
        import importlib.util  # noqa: PLC0415
        from unittest import mock  # noqa: PLC0415
        spec = importlib.util.spec_from_file_location("verify_ac", _SCRIPTS / "verify_ac.py")
        other = importlib.util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, {"verify_ac": other}):   # a dataclass looks it up
            spec.loader.exec_module(other)
        swaps = []

        def swap():
            patcher = mock.patch.object(sys.modules["conformance"], "verify_ac", other)
            patcher.start()
            swaps.append(patcher)

        try:
            rows, _root = self._run(apply=False, between=swap)
        finally:
            for patcher in swaps:
                patcher.stop()
        self.assertEqual(1, len(swaps))
        self.assertEqual(self.FILES, sorted(r["file"] for r in rows))

    def test_a_guard_turned_on_inside_another_changes_nothing(self) -> None:
        """The lane turns its guard on while the primer's collections may still be starting.
        Fails on an inner guard that sets its own bytecode directory and a second
        `-p no:cacheprovider`, or whose `off` restores the outer one's values and removes the
        directory the running collections write to."""
        import os  # noqa: PLC0415
        keys = ("PYTEST_ADDOPTS", "PYTHONDONTWRITEBYTECODE", "PYTHONPYCACHEPREFIX")
        outer = migrate._QuietCollection()
        outer.on()
        try:
            before = {k: os.environ.get(k) for k in keys}
            with migrate._QuietCollection():
                self.assertEqual(before, {k: os.environ.get(k) for k in keys})
            self.assertEqual(before, {k: os.environ.get(k) for k in keys})
            self.assertTrue(Path(before["PYTHONPYCACHEPREFIX"]).is_dir())
        finally:
            outer.off()
        self.assertFalse(Path(before["PYTHONPYCACHEPREFIX"]).exists())

    def test_seed_puts_beside_source_bytecode_where_the_guard_reads_it(self) -> None:
        """Fails on a seed that copies nothing, or copies to a place other than where Python
        looks under `PYTHONPYCACHEPREFIX` (`importlib.util.cache_from_source`), which keeps an
        earlier run's bytecode from being read."""
        import importlib.util  # noqa: PLC0415
        import os  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "tests"
            (src / "__pycache__").mkdir(parents=True)
            (src / "test_a.py").write_text("x = 1\n", encoding="utf-8")
            tag = sys.implementation.cache_tag
            (src / "__pycache__" / f"test_a.{tag}.pyc").write_bytes(b"compiled")
            guard = migrate._QuietCollection()
            guard.on()
            try:
                guard.seed([src])
                prefix, saved = os.environ["PYTHONPYCACHEPREFIX"], sys.pycache_prefix
                sys.pycache_prefix = prefix
                try:
                    where = Path(importlib.util.cache_from_source(str(src / "test_a.py")))
                finally:
                    sys.pycache_prefix = saved
                self.assertEqual(b"compiled", where.read_bytes())
            finally:
                guard.off()
            self.assertFalse(Path(prefix).exists())

    def test_a_relative_root_reads_the_cached_corpus(self) -> None:
        """A dry run reads the corpus through `sdlc_md.corpus_cache`, which hands every caller
        the paths its first walk built. Fails on a root left relative: the conventions step
        reaches `reconcile` with the root made absolute, is handed relative paths, and
        `Path.relative_to` refuses them."""
        import os  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v4_era(root)
            self.assertEqual(migrate.migrate(root),
                             migrate.migrate(Path(os.path.relpath(root))))

    def test_a_terminated_run_removes_its_bytecode_directory(self) -> None:
        """Fails on a CLI run that keeps Python's default SIGTERM: `timeout` stops it mid-way,
        no `finally` runs, and the guard's bytecode directory is left in the temporary
        directory, about 25 MB of it on this repository."""
        import os  # noqa: PLC0415
        import shutil  # noqa: PLC0415
        import signal  # noqa: PLC0415
        import subprocess  # noqa: PLC0415
        import time  # noqa: PLC0415
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        root, fake_bin, tmp = d / "repo", d / "bin", d / "tmp"
        for path in (root, fake_bin, tmp):
            path.mkdir()
        _v4_era(root)
        (root / "tests").mkdir()
        (root / "tests" / "test_1.py").write_text("def test_ok():\n    pass\n", "utf-8")
        _w(root, "stories/US0003-stamped.md",
           "# US0003: stamped\n\n> **Status:** Done\n> **Epic:** EP0001\n\n"
           "## Acceptance Criteria\n\n- [x] **AC1** given x, when y, then z\n"
           "  - **Verify:** pytest tests/test_1.py::test_ok\n  - **Verified:** yes (2026-11-03)\n")
        started = d / "started"
        fake = fake_bin / "pytest"
        fake.write_text(f"#!{sys.executable}\nimport pathlib, time\n"
                        f"pathlib.Path({str(started)!r}).touch()\ntime.sleep(3)\n"
                        f"print('tests/test_1.py::test_ok')\n", encoding="utf-8")
        fake.chmod(0o755)
        env = dict(os.environ, TMPDIR=str(tmp),
                   PATH=f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}")
        proc = subprocess.Popen([sys.executable, str(_SCRIPTS / "migrate.py"), "--root", str(root)],
                                env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 60
        while not started.exists() and proc.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(started.exists(), "the run never reached a collection")
        self.assertTrue(any(tmp.glob("sdlc-migrate-pyc-*")), "no bytecode directory to remove")
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(128 + signal.SIGTERM, proc.wait(timeout=60))
        self.assertEqual([], [p.name for p in tmp.glob("sdlc-migrate-pyc-*")])

    def test_apply_collects_only_after_the_steps_that_write(self) -> None:
        """Fails on a primer started before the steps under --apply. The order is read from the
        calls themselves, the last writing step's (`_signed_records`) before the primer's
        `start`, because a collection server's start-up can outlast this fixture's writes; and
        every collection then reads CR0001 sized."""
        from unittest import mock  # noqa: PLC0415
        events: list[str] = []
        start, records = migrate._CollectionPrimer.start, migrate._signed_records

        def started(primer):
            events.append("start")
            return start(primer)

        def recorded(*args, **kwargs):
            events.append("records")
            return records(*args, **kwargs)

        with mock.patch.object(migrate._CollectionPrimer, "start", started), \
                mock.patch.object(migrate, "_signed_records", recorded):
            rows, _root = self._run(apply=True)
        self.assertEqual("records", events[0], events)
        self.assertIn("start", events)
        self.assertEqual(self.FILES, sorted(r["file"] for r in rows))
        self.assertTrue(all(r["sized"] for r in rows), rows)


#: The test files `CollectionServerTests` collects both ways: a pass, a parametrised class, an
#: empty file (pytest exits 5), a syntax error and a missing import (both exit 2), a test named
#: outside ASCII, and one whose test is named from `sys.path` as it is imported. The conftest writes a node-shaped line to standard error
#: once pytest has stopped capturing it.
_COLLECT_FIXTURES = {
    "test_ok.py": "def test_a():\n    pass\n\n\ndef test_b():\n    pass\n",
    "test_param.py": ("import pytest\n\n\nclass TestP:\n    @pytest.mark.parametrize('n', [1, 2])\n"
                      "    def test_n(self, n):\n        pass\n"),
    "test_empty.py": "",
    "test_syntax.py": "def broken(:\n",
    "test_import.py": "import nosuchmodule_bg1183  # noqa: F401\n",
    "test_unicode.py": "def test_caf\u00e9():\n    pass\n",
    "test_path.py": ("import hashlib, sys\n\n"
                     "globals()['test_' + hashlib.md5(repr(sys.path).encode()).hexdigest()[:8]] = "
                     "lambda: None\n"),
    "conftest.py": ("import sys\n\n\ndef pytest_unconfigure(config):\n"
                    "    sys.stderr.write('tests/test_ok.py::stderr\\n')\n"),
}


class CollectionServerTests(unittest.TestCase):
    """BG1183 AC2: a `verify_ac.CollectionServer` answers each file as `_collect_fresh`, a fresh
    `pytest --collect-only -q` of its own, answers it."""

    def setUp(self) -> None:
        import os  # noqa: PLC0415
        import verify_ac  # noqa: PLC0415
        self.va = verify_ac
        if not hasattr(os, "fork") or verify_ac.pytest_launcher() is None:
            self.skipTest("no fork, or a pytest no CollectionServer can run")

    def _project(self) -> Path:
        import shutil  # noqa: PLC0415
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        (root / "tests").mkdir()
        for name, text in _COLLECT_FIXTURES.items():
            (root / "tests" / name).write_text(text, encoding="utf-8")
        return root

    def test_a_server_answers_each_file_as_a_fresh_collection_does(self) -> None:
        """Fails on a server that reads its children's standard error as output, reports every
        exit as a pass, leaves `sys.path[0]` as `-c` sets it (`test_path.py` then names its test
        from another `sys.path`), drops a parametrised id, or decodes
        its children's output other than as `subprocess.run(text=True)` does."""
        root = self._project()
        files = [f"tests/{name}" for name in _COLLECT_FIXTURES
                 if name != "conftest.py"] + ["tests/test_absent.py"]
        server = self.va.CollectionServer.start(root)
        self.addCleanup(server.close)
        served = {f: server.collect(f) for f in files}
        fresh = {f: self.va._collect_fresh(f, root) for f in files}
        self.assertEqual(fresh, served)
        self.assertIsNone(served["tests/test_syntax.py"])
        self.assertEqual([], served["tests/test_empty.py"])
        self.assertIn("tests/test_param.py::TestP::test_n[2]", served["tests/test_param.py"])
        self.assertNotIn("tests/test_ok.py::stderr", served["tests/test_ok.py"])
        self.assertEqual(1, len(served["tests/test_path.py"]))
        self.assertEqual(["tests/test_unicode.py::test_caf\u00e9"], served["tests/test_unicode.py"])
        self.assertEqual(served["tests/test_ok.py"],
                         self.va._COLLECT_CACHE[("tests/test_ok.py", str(root))])

    def test_a_project_that_turns_warnings_into_errors_reads_as_a_fresh_run_does(self) -> None:
        """Fails on a server that imports an installed `pytest11` plugin before it forks: each
        child then draws PytestAssertRewriteWarning, the project's error filter fails its
        collection, and the file reads as not collecting where a fresh run lists its nodes. A
        machine with no such plugin cannot draw the warning, so the case only passes there."""
        for config in ("[pytest]\nfilterwarnings =\n    error\n", "[pytest]\naddopts = -W error\n"):
            with self.subTest(config=config):
                root = self._project()
                (root / "pytest.ini").write_text(config, encoding="utf-8")
                server = self.va.CollectionServer.start(root)
                self.addCleanup(server.close)
                expected = ["tests/test_ok.py::test_a", "tests/test_ok.py::test_b"]
                self.assertEqual(expected, self.va._collect_fresh("tests/test_ok.py", root))
                self.assertEqual(expected, server.collect("tests/test_ok.py"))

    def test_stamps_on_a_project_that_turns_warnings_into_errors_reads_live_selectors_live(
            self) -> None:
        """The same fix pinned on `verify_ac.py stamps --bugs`, which collects its files through
        these servers. Fails on a server that imports an installed `pytest11` plugin before it
        forks: under `filterwarnings = error` both live selectors then read STALE and the
        command exits 1, where fresh collections find both."""
        import os  # noqa: PLC0415
        import shutil  # noqa: PLC0415
        import subprocess  # noqa: PLC0415
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        (root / "t").mkdir()
        (root / "t" / "test_one.py").write_text("def test_alpha():\n    pass\n", "utf-8")
        (root / "t" / "test_two.py").write_text("def test_gamma():\n    pass\n", "utf-8")
        (root / "pytest.ini").write_text("[pytest]\nfilterwarnings =\n    error\n", "utf-8")
        _w(root, "stories/US0001-x.md",
           "# US0001: x\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
           "### AC1: a\n\n- **Verify:** pytest t/test_one.py::test_alpha\n- **Verified:** yes\n\n"
           "### AC2: b\n\n- **Verify:** pytest t/test_two.py::test_gamma\n- **Verified:** yes\n")
        env = {k: v for k, v in os.environ.items() if k != "PYTEST_DISABLE_PLUGIN_AUTOLOAD"}
        cp = subprocess.run([sys.executable, str(_SCRIPTS / "verify_ac.py"), "stamps", "--bugs",
                             "--root", str(root)], capture_output=True, text=True, env=env,
                            cwd=str(root), timeout=300)
        self.assertEqual(0, cp.returncode, cp.stdout + cp.stderr)
        self.assertNotIn("STALE", cp.stdout + cp.stderr)

    def test_a_collection_past_the_timeout_reads_as_not_collecting(self) -> None:
        """Fails on a server that waits past `COLLECT_TIMEOUT`, or that cannot answer the next
        file after it killed a child. No clock is read: a server that waits lets the file's
        30 s import finish, and the file, which holds no test, then reads as collecting
        nothing (`[]`) rather than as not collecting (None)."""
        from unittest import mock  # noqa: PLC0415
        root = self._project()
        (root / "tests" / "test_slow.py").write_text("import time\ntime.sleep(30)\n", "utf-8")
        server = self.va.CollectionServer.start(root)
        self.addCleanup(server.close)
        with mock.patch.object(self.va, "COLLECT_TIMEOUT", 2):
            self.assertIsNone(server.collect("tests/test_slow.py"))
        self.assertEqual(["tests/test_ok.py::test_a", "tests/test_ok.py::test_b"],
                         server.collect("tests/test_ok.py"))

    def test_a_server_that_stops_answering_hands_the_file_to_a_fresh_collection(self) -> None:
        """Fails on a dead server's file read as not collecting, or asked again."""
        root = self._project()
        server = self.va.CollectionServer.start(root)
        self.addCleanup(server.close)
        server._proc.kill()
        server._proc.wait()
        self.assertEqual(self.va._collect_fresh("tests/test_ok.py", root),
                         server.collect("tests/test_ok.py"))
        self.assertIsNone(server._proc)

    def test_the_launcher_runs_only_a_pytest_whose_first_line_names_python(self) -> None:
        """Fails on a launcher that runs a shell shim, a binary or an `env -S` line as Python,
        or that drops the one argument a shebang may carry."""
        import os  # noqa: PLC0415
        import shutil  # noqa: PLC0415
        from unittest import mock  # noqa: PLC0415
        python = shutil.which("python3") or sys.executable
        cases = {
            f"#!{python}\n": [python],
            f"#!{python} -s\n": [python, "-s"],
            "#!/usr/bin/env python3\n": [shutil.which("python3")],
            "#!/bin/sh\n": None,
            "#!/usr/bin/env -S python3 -X dev\n": None,
            "\x7fELF\x02": None,
        }
        for first, argv in cases.items():
            with self.subTest(first=first), tempfile.TemporaryDirectory() as d:
                script = Path(d) / "pytest"
                script.write_text(first + "import sys\n", encoding="utf-8")
                script.chmod(0o755)
                with mock.patch.dict(os.environ, {"PATH": f"{d}{os.pathsep}{os.path.dirname(python)}"}):
                    got = self.va.pytest_launcher()
                self.assertEqual(argv, got and got[0])
                if argv:
                    self.assertEqual(str(script), got[1])


class EngagementFloorCutoffTests(unittest.TestCase):
    """BG0843: a v4.1 project's engagement-floor lane failed 349 shipped units before and after
    `migrate --apply`, and migrate never mentioned the floor. It now asks the lane which units it
    fails and names the `engagement_floor.adopt_after` line that grandfathers them, never writing
    it. Read through `migrate.py --format json` and `gate.py`, the commands an upgrader runs."""

    KIND = "engagement-floor-cutoff"

    @staticmethod
    def _fixture(root: Path, config_tail: str = "") -> None:
        """BG0001 and BG0002 shipped with no plan and no Affects (the lane fails both); BG0003
        and US0001 carry a criterion (it passes them), so the highest id is 3."""
        _v4_era(root, config_tail)
        for n in (1, 2):
            _w(root, f"bugs/BG000{n}-b.md",
               f"# BG000{n}: b\n\n> **Status:** Fixed\n> **Severity:** Low\n")
        _w(root, "bugs/BG0003-p.md",
           "# BG0003: p\n\n> **Status:** Fixed\n> **Severity:** Low\n\n"
           "## Acceptance Criteria\n\n- [x] **AC1** given x, then y\n")

    @staticmethod
    def _cli_json(main, argv: list[str]) -> tuple[int, dict]:
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415
        import json  # noqa: PLC0415
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = main(argv)
        return rc, json.loads(buf.getvalue())

    def _items(self, root: Path, *extra: str) -> list[dict]:
        rc, out = self._cli_json(migrate.main, ["--root", str(root), "--format", "json", *extra])
        self.assertEqual(0, rc, out)
        return [h for h in out["needs_human"] if h["kind"] == self.KIND]

    def _lane(self, root: Path) -> dict:
        import gate  # noqa: PLC0415
        _rc, out = self._cli_json(gate.main, ["--root", str(root), "--only", "engagement-floor",
                                              "--format", "json"])
        lanes = [c for c in out["checks"] if c["check"] == "engagement-floor"]
        self.assertEqual(1, len(lanes), out)
        return lanes[0]

    def test_migrate_names_the_engagement_floor_cutoff(self) -> None:
        # Mutants: silence (today), a cutoff below a failing unit (the lowest id), naming units
        # the lane passes, and writing the line into .config.yaml.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            lane = self._lane(root)
            self.assertEqual((lane["status"], lane["count"]), ("fail", 2), lane)
            cfg = root / "sdlc-studio" / ".config.yaml"
            before = cfg.read_bytes()
            for extra in ((), ("--apply",)):
                items = self._items(root, *extra)
                self.assertEqual(1, len(items), extra)
                item = items[0]
                self.assertEqual(["BG0001", "BG0002"], item["ids"], extra)
                self.assertEqual(lane["count"], len(item["ids"]))
                self.assertEqual(lane["count"], item["count"])      # BG0854: the gate's number
                self.assertEqual("engagement_floor.adopt_after: BG0002", item["line"])
                self.assertEqual("engagement-floor", item["lane"])
                self.assertIn("`engagement_floor.adopt_after: BG0002`", item["detail"])
                self.assertIn("BG0001", item["detail"])
                self.assertNotIn("BG0003", item["detail"])
                self.assertEqual(before, cfg.read_bytes(), f"{extra}: migrate wrote the cutoff")

    def test_a_cutoff_already_covering_every_unit_names_nothing(self) -> None:
        # Mutant: judging the lane's would-violate kind rather than its live violation, which
        # proposes a cutoff for units the existing one already exempts. Both cutoffs are at or
        # above every failing id and at or below the highest id, so the lane passes on each.
        for cutoff in ("BG0002", "3"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._fixture(root, f"\nengagement_floor:\n  adopt_after: {cutoff}\n")
                lane = self._lane(root)
                self.assertEqual((lane["status"], lane["count"]), ("pass", 0), lane)
                self.assertIn("2 exempt unit(s) would violate", lane["detail"],
                              "the over-proposing mutant needs exempt failures to reach")
                for extra in ((), ("--apply",)):
                    self.assertEqual([], self._items(root, *extra), (cutoff, extra))

    def test_a_cutoff_below_a_failing_unit_is_named_as_a_raise(self) -> None:
        # An existing cutoff that stops short: only the units above it are named, and the line
        # reads as raising the value already set, not as adding a second key.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, "\nengagement_floor:\n  adopt_after: 1\n")
            items = self._items(root)
        self.assertEqual(1, len(items), items)
        self.assertEqual(["BG0002"], items[0]["ids"])
        self.assertEqual("engagement_floor.adopt_after: BG0002", items[0]["line"])
        self.assertIn("raise `engagement_floor.adopt_after` from 1", items[0]["detail"])

    def test_a_forward_cutoff_is_named_with_the_lanes_own_words(self) -> None:
        # A cutoff above the highest id fails the lane as a config error; migrate must not read
        # its zero violations as "nothing to say", nor propose a line on top of it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, "\nengagement_floor:\n  adopt_after: 9\n")
            lane = self._lane(root)
            self.assertEqual("fail", lane["status"])
            items = self._items(root)
        self.assertEqual(1, len(items), items)
        self.assertIsNone(items[0]["line"])
        self.assertEqual(lane["count"], items[0]["count"])            # BG0854: the gate's number
        self.assertIn("exceeds the highest existing id 3", items[0]["detail"])

    def test_a_ulid_unit_is_named_without_a_line_it_could_not_parse(self) -> None:
        # A v3 id has no number for `adopt_after` to reach, so no cutoff can cover it: it is
        # named with the per-unit remedies, and the line covers only the numbered units.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            _w(root, "bugs/BG-01JQK3F8-u.md",
               "# BG-01JQK3F8: u\n\n> **Status:** Fixed\n> **Severity:** Low\n")
            items = self._items(root)
        self.assertEqual(1, len(items), items)
        self.assertEqual(["BG-01JQK3F8", "BG0001", "BG0002"], items[0]["ids"])
        self.assertEqual("engagement_floor.adopt_after: BG0002", items[0]["line"])
        self.assertIn("BG-01JQK3F8", items[0]["detail"])
        self.assertIn("no cutoff can reach", items[0]["detail"])

    def test_judgement_mode_and_an_unreadable_cutoff(self) -> None:
        # `judgement` makes the lane advisory: nothing blocks, so nothing is proposed. A cutoff
        # the lane refuses to parse is named rather than raised.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, "\nengagement_floor: judgement\n")
            self.assertEqual([], self._items(root))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root, "\nengagement_floor:\n  adopt_after: soon\n")
            items = self._items(root)
        self.assertEqual(1, len(items), items)
        self.assertIn("soon", items[0]["detail"])
        self.assertIsNone(items[0]["line"])


#: The per-clone CI cache a pre-6.0 close read, and the shape `gh run list --json` answers.
CI_CACHE = Path("sdlc-studio") / ".local" / "ci-runs.json"


def _ci_run(rid: int, at: str, event: str = "push", conclusion: str = "success") -> dict:
    return {"databaseId": rid, "event": event, "conclusion": conclusion, "headBranch": "main",
            "headSha": f"{rid:07d}", "workflowName": "Lint", "createdAt": at, "updatedAt": at}


#: The fixture run's window is 2026-09-20T08:00Z to 18:00Z.
INSIDE = _ci_run(4242, "2026-09-20T09:00:00Z")
BEFORE = _ci_run(1111, "2026-09-17T07:58:50Z")
#: A run the cache gains later that moves no figure: DORA counts push-triggered runs alone.
DISPATCHED = _ci_run(4343, "2026-09-20T10:00:00Z", event="workflow_dispatch")
#: What the forge answers once the page is signed: a red push and a green one, both in the window.
MOVED = [_ci_run(5151, "2026-09-20T11:00:00Z", conclusion="failure"),
         _ci_run(5252, "2026-09-20T12:00:00Z")]
#: A session outside the repository that wrote one meter reading and no closing one.
UNCOVERED = {"tokens": 700, "source": "/home/someone/.claude/projects/-repo/9a8b7c6d.jsonl",
             "at": "2026-09-20T09:00:00Z", "kind": "open", "model": "lean-model-7"}


class SignedRecordMigrationTests(unittest.TestCase):
    """US0960: `migrate --apply` files the tracked run record of a report signed before records
    were tracked, frozen as the page read its inputs, so the report checks in any clone.

    The fixture is a report as a pre-6.0 close filed it: derived with no `record_paths` mark,
    its DORA read from the per-clone CI cache, signed through the seal's own signature writer
    and committed, and its run record archived in `.local` once the next run opened. `gh` is a
    stub whose answer each test sets."""

    def setUp(self) -> None:
        import os  # noqa: PLC0415
        from unittest import mock  # noqa: PLC0415
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.bin = base / "bin"
        self.bin.mkdir()
        (base / "transcripts").mkdir()
        self._forge([])
        env = gitutil.git_env(PATH=f"{self.bin}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(base / "transcripts"))
        patch = mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.root = base / "signer"
        self.root.mkdir()

    # --- the fixture ------------------------------------------------------------------------

    @staticmethod
    def _sr():
        import importlib  # noqa: PLC0415 - bound at call time, as the suite loads it
        return importlib.import_module("sprint_report")

    def _forge(self, rows: list[dict]) -> None:
        """What the stub `gh run list` answers from now on. Every call is logged in `gh.log`."""
        import json  # noqa: PLC0415
        gh = self.bin / "gh"
        gh.write_text(f"#!/bin/sh\necho \"$*\" >> '{self.bin / 'gh.log'}'\n"
                      f"cat <<'EOF'\n{json.dumps(rows)}\nEOF\n", encoding="utf-8")
        gh.chmod(0o755)

    def _git(self, *argv: str, cwd: Path | None = None):
        return gitutil.git(list(argv), cwd or self.root, text=True)

    def _commit(self, message: str) -> None:
        self._git("add", "-A")
        self._git("-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", message)

    def _cache(self, rows: list[dict]) -> None:
        import json  # noqa: PLC0415
        (self.root / CI_CACHE).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    def _signed_before_records_were_tracked(self, cache: list[dict] | None,
                                            stamps: list[dict] = ()) -> str:
        """A report filed, signed and committed the way a pre-6.0 close left it, and its run
        archived when the next run opened. `cache` is the per-clone CI cache the close read,
        or None for a clone that held none. Returns the report id."""
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415
        import json  # noqa: PLC0415
        from unittest import mock  # noqa: PLC0415
        import sprint  # noqa: PLC0415 - the seal's own signature writer
        import test_lean_report as leanrep  # noqa: PLC0415 - the one-page report's fixture
        sr = self._sr()
        leanrep.lean_run(self.root)
        live = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(live.read_text(encoding="utf-8"))
        state["session_token_stamps"] += list(stamps)
        live.write_text(json.dumps(state, indent=2), encoding="utf-8")
        (self.root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        if cache is not None:
            self._cache(cache)
        self._git("init", "-q", ".")
        self._commit("the delivered batch")
        # The DORA reader a pre-6.0 close ran: the per-clone cache whenever it exists.
        read = (cache, CI_CACHE.as_posix()) if cache is not None else ([], "gh run list")
        with mock.patch.object(sr, "_ci_runs", lambda *a, **k: read):
            page = sr.build_report(self.root, leanrep.RETRO, portable=False)
        rid = sr.file_report(self.root, page)
        with contextlib.redirect_stdout(io.StringIO()):
            sprint._write_the_signature(self.root, rid, "Maya Okafor")
        self._commit("sign the report")
        sr.run_state.archive(self.root)
        sr.run_state.write(self.root, {"schema": 1, "run_id": "RUN-01LATERRUN",
                                       "started_at": "2026-09-27T00:00:00Z",
                                       "outcome": "running", "batch": ["US0005"]})
        self.assertFalse(self._tracked().exists())
        return rid

    def _tracked(self, root: Path | None = None) -> Path:
        return (root or self.root) / "sdlc-studio" / "reports" / "runs" / "RUN-01LEANREP.json"

    def _check(self, root: Path, rid: str) -> tuple[int, str]:
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = self._sr().main(["--root", str(root), "check", "--report", rid])
        return rc, out.getvalue() + err.getvalue()

    @staticmethod
    def _records(res: dict) -> list[dict]:
        return [d for d in res["deterministic"] if d.get("source") == "run-record"]

    @staticmethod
    def _named(res: dict) -> list[dict]:
        return [h for h in res["needs_human"] if h.get("kind") == "run-record"]

    # --- the criteria -----------------------------------------------------------------------

    def test_migrate_files_the_record_of_a_signed_report(self) -> None:
        """AC1. Mutants: write in a dry run; read only the live record, which names the next
        run, so the archived run of the signed report is never found."""
        import json  # noqa: PLC0415
        rid = self._signed_before_records_were_tracked([INSIDE, BEFORE])
        res = migrate.migrate(self.root)
        self.assertEqual([(rid, "RUN-01LEANREP", False)],
                         [(d["id"], d["run"], d["applied"]) for d in self._records(res)],
                         res["deterministic"])
        self.assertIn("sdlc-studio/reports/runs/RUN-01LEANREP.json", migrate.render(res))
        self.assertFalse(self._tracked().exists(), "a dry run filed the record")
        res = migrate.migrate(self.root, apply=True)
        self.assertEqual([(rid, True)], [(d["id"], d["applied"]) for d in self._records(res)])
        self.assertEqual([], self._named(res), res["needs_human"])
        record = json.loads(self._tracked().read_text(encoding="utf-8"))
        archived = self._sr().run_state.read_archived(self.root, "RUN-01LEANREP")
        self.assertEqual(archived["signature"], record["signature"])
        self.assertEqual(archived["ended_at"], record["ended_at"])
        # Through the projection `sprint sign` files through: no absolute path is committed.
        self.assertNotIn("/t/s1.jsonl", self._tracked().read_text(encoding="utf-8"))

    def test_a_migrated_record_checks_in_a_clean_clone(self) -> None:
        """AC2. Mutant: file the record without freezing the CI runs the page read, so the clone
        re-derives DORA from no runs (RPT0010 read INVALIDATED that way: `dora_value[0]` signed
        72, now 7). The forge answers other runs in the window by then; `check` must not read
        it."""
        import json  # noqa: PLC0415
        rid = self._signed_before_records_were_tracked([INSIDE, BEFORE])
        # The premise: a record that froze nothing re-derives DORA from no runs.
        rc, out = self._check(self.root, rid)
        self.assertEqual(1, rc, out)
        self.assertIn("dora_value", out)
        migrate.migrate(self.root, apply=True)
        record = json.loads(self._tracked().read_text(encoding="utf-8"))
        self.assertEqual({"source": CI_CACHE.as_posix(), "runs": [INSIDE]}, record["ci_runs"])
        self.assertEqual({"US0001": 2, "US0002": 1, "US0003": 0, "US0004": 0, "US0005": 0},
                         {u: len(ids) for u, ids in record["review_rows"].items()})
        self._commit("migrate the signed history")
        self._forge(MOVED)
        rc, out = self._check(self.root, rid)
        self.assertEqual(0, rc, out)
        clone = Path(self.tmp.name) / "clean"
        self._git("clone", "-q", f"file://{self.root}", str(clone), cwd=Path(self.tmp.name))
        self.assertFalse((clone / "sdlc-studio" / ".local").exists())
        rc, out = self._check(clone, rid)
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {rid}", out)

    def test_migrate_never_rewrites_a_filed_record(self) -> None:
        """AC3. Mutant: re-freeze from today's cache and ledger on every run - the cache has
        gained a dispatched run inside the window since, which moves no figure, so the record
        still verifies and would be rewritten."""
        rid = self._signed_before_records_were_tracked([INSIDE, BEFORE])
        migrate.migrate(self.root, apply=True)
        filed = self._tracked().read_bytes()
        self._cache([INSIDE, DISPATCHED, BEFORE])
        self._forge(MOVED)
        ledger = self.root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
        ledger.write_text(ledger.read_text(encoding="utf-8")
                          + "| US0005 | APPROVE | a seat | author | 2026-09-27 | - | - | - |\n",
                          encoding="utf-8")
        res = migrate.migrate(self.root, apply=True)
        self.assertEqual(filed, self._tracked().read_bytes(), "a filed record was rewritten")
        self.assertEqual([], self._records(res))
        self.assertEqual([], self._named(res))
        rc, out = self._check(self.root, rid)
        self.assertEqual(0, rc, out)

    def test_a_report_that_would_not_rederive_is_named_not_filed(self) -> None:
        """AC4. Mutant: file the frozen record without re-deriving the page from it - the
        counted REJECT superseded since is no round by today's rule, so the filed record reads
        US0001's rounds as 1, not the 2 signed, in every clone."""
        import subprocess  # noqa: PLC0415
        rid = self._signed_before_records_were_tracked([INSIDE, BEFORE])
        proc = subprocess.run(
            [sys.executable, str(_SCRIPTS / "critic.py"), "supersede", "--unit", "US0001",
             "--date", "2026-09-20", "--verdict", "REJECT", "--reviewer", "a seat",
             "--reason", "the reviewer mis-entered the verdict",
             "--authorised-by", "Maya Okafor", "--boundary", "operator console",
             "--root", str(self.root)],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stderr)
        for apply in (False, True):
            res = migrate.migrate(self.root, apply=apply)
            self.assertEqual([], self._records(res), f"apply={apply}")
            named = self._named(res)
            self.assertEqual([rid], [h["id"] for h in named], res["needs_human"])
            self.assertIn("unit_rounds", named[0]["detail"])
            self.assertIn("sprint_report.py check --report", named[0]["command"])
            self.assertIn(rid, migrate.render(res))
            self.assertFalse(self._tracked().exists(), f"apply={apply} filed the record")

    def test_migrate_reads_the_cache_once_and_never_writes_it_or_asks_the_forge(self) -> None:
        """BG0795 AC3 as it holds for migrate, the one script that names the per-clone cache.
        On a signed report, with a cache and without one, `migrate --apply` leaves the cache's
        bytes (or its absence) as they were and never calls `gh`. Mutants: write the cache when
        it is absent; rewrite it; read the forge (`fetch_ci_runs`) for the runs to freeze."""
        for label, cache in (("with a cache", [INSIDE, BEFORE]), ("without one", None)):
            with self.subTest(label):
                self.setUp()
                rid = self._signed_before_records_were_tracked(cache)
                before = (self.root / CI_CACHE).read_bytes() if cache is not None else None
                (self.bin / "gh.log").unlink(missing_ok=True)
                res = migrate.migrate(self.root, apply=True)
                self.assertEqual([rid], [d["id"] for d in self._records(res)],
                                 res["needs_human"])
                after = (self.root / CI_CACHE).read_bytes() if (
                    self.root / CI_CACHE).exists() else None
                self.assertEqual(before, after, "migrate wrote the per-clone cache")
                self.assertFalse((self.bin / "gh.log").exists(),
                                 "migrate asked the forge: "
                                 + ((self.bin / "gh.log").read_text(encoding="utf-8")
                                    if (self.bin / "gh.log").exists() else ""))

    def test_an_unmarked_page_naming_a_session_outside_the_repo_is_named_not_filed(
            self) -> None:
        """A page derived before records were tracked names an uncovered session by its path;
        the tracked record holds it only as a digest, so the page could not be judged from it
        in any clone. Mutant: file it projected anyway - the signing clone then reads the
        tracked record and stops judging a page it judged VALID."""
        rid = self._signed_before_records_were_tracked([BEFORE], stamps=[UNCOVERED])
        rc, out = self._check(self.root, rid)
        self.assertEqual(0, rc, f"the positive control: {out}")
        page = self._sr().read_report(self.root, rid)
        cost = next(s for s in page["sections"] if s["key"] == "cost")
        self.assertIn(UNCOVERED["source"], cost["figures"]["token_coverage"]["value"])
        res = migrate.migrate(self.root, apply=True)
        self.assertEqual([], self._records(res))
        named = self._named(res)
        self.assertEqual([rid], [h["id"] for h in named], res["needs_human"])
        self.assertIn("predates tracked records", named[0]["detail"])
        self.assertFalse(self._tracked().exists())
        rc, out = self._check(self.root, rid)
        self.assertEqual(0, rc, out)


if __name__ == "__main__":
    unittest.main()
