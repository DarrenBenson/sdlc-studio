"""The applied-mutant guard: a skill entry point invoked while a mutation run has a
mutant on disk says so, and a write-path one refuses.

A mutation evidence run rewrites live files one at a time for minutes at a stretch. Any
script invoked in that window can execute a mutated sibling, misbehave, and hand its wrong
behaviour to whoever is reading the output as if it were the tool's real behaviour. The
in-flight sidecar already marks the exact window; nothing read it.
"""
from __future__ import annotations

import base64
import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


from lib import sdlc_md  # noqa: E402

artifact = _load("artifact")
mutation = _load("mutation")
status = _load("status")
transition = _load("transition")


def _sidecar(root: Path, mutated: Path, original: bytes = b"x = 1\n") -> Path:
    """The sidecar `mutation.py` writes while a mutant is applied: {path: base64-original}."""
    path = sdlc_md.inflight_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({str(mutated): base64.b64encode(original).decode("ascii")}),
                    encoding="utf-8")
    return path


def _story(root: Path, sid: str = "US0001", st: str = "Draft") -> Path:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{sid}-x.md"
    p.write_text(f"# {sid}: x\n\n> **Status:** {st}\n> **Points:** 2\n", encoding="utf-8")
    (d / "_index.md").write_text(
        "# Stories\n\n## All Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [{sid}]({p.name}) | x | {st} |\n", encoding="utf-8")
    return p


def _tree(root: Path) -> dict[str, bytes]:
    """Every file under `root/sdlc-studio` and its bytes, minus the sidecar itself - the
    census a refusal must leave byte-identical."""
    base = root / "sdlc-studio"
    sidecar = sdlc_md.inflight_path(root)
    return {str(p.relative_to(root)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file() and p != sidecar}


class InflightGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        # The exemption marker must not be inherited from an outer mutation run, or every
        # assertion below would pass for that reason instead of the one under test.
        self._marker = os.environ.pop(sdlc_md.MUTATION_RUN_ENV, None)

    def tearDown(self) -> None:
        if self._marker is not None:
            os.environ[sdlc_md.MUTATION_RUN_ENV] = self._marker
        else:
            os.environ.pop(sdlc_md.MUTATION_RUN_ENV, None)

    def test_read_path_warns_naming_the_mutated_file_and_still_exits_zero(self) -> None:
        """AC1: a read is degraded evidence, not blocked - so it warns and completes."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root)
            mutated = root / ".claude" / "skills" / "sdlc-studio" / "scripts" / "status.py"
            _sidecar(root, mutated)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = status.main(["hint", "--root", str(root)])
            self.assertEqual(rc, 0)                       # degraded, never blocked
            self.assertIn(str(mutated), err.getvalue())   # names the file that is mutated
            self.assertIn("single-writer", err.getvalue())
            # and the read it was asked for still happened
            self.assertIn("/sdlc-studio ", out.getvalue())

    def test_write_path_refuses_and_writes_nothing(self) -> None:
        """AC2: a write made against a mutated tool is one nobody can trust afterwards."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = _story(root)
            mutated = root / ".claude" / "skills" / "sdlc-studio" / "scripts" / "artifact.py"
            sidecar = _sidecar(root, mutated)
            before = _tree(root)
            for argv in (["new", "--type", "bug", "--title", "a new bug", "--severity", "Low",
                          "--points", "2", "--affects", "a.py", "--root", str(root)],
                         ["set", "--id", "US0001", "--status", "In Progress",
                          "--root", str(root)]):
                out, err = io.StringIO(), io.StringIO()
                entry = artifact if argv[0] == "new" else transition
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = entry.main(argv)
                self.assertEqual(rc, 2, f"{argv[0]}: {out.getvalue()}{err.getvalue()}")
                self.assertIn(str(mutated), err.getvalue())     # names the mutated file
                self.assertIn(str(sidecar), err.getvalue())     # and how to clear it
                # nothing written: no new artefact, no id burnt, no status moved
                self.assertEqual(_tree(root), before, f"{argv[0]} wrote to the tree")
            self.assertIn("> **Status:** Draft", story.read_text(encoding="utf-8"))

    def test_own_run_is_exempt_and_a_stale_sidecar_still_recovers(self) -> None:
        """AC3: the guard cannot block the one run whose job is to clean up after itself."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root)
            mutated = root / "victim.py"
            original = b"def f():\n    return 1\n"
            mutated.write_bytes(original)
            _sidecar(root, mutated, original)

            # (a) a process carrying the marker mutation.py sets on the environment it runs
            # its suites under is neither warned nor refused.
            suite_env = {k: v for k, v in mutation._suite_env().items()
                         if k == sdlc_md.MUTATION_RUN_ENV}
            self.assertTrue(suite_env, "mutation.py sets no exemption marker on its suite env")
            with unittest.mock.patch.dict(os.environ, suite_env):
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc_read = status.main(["hint", "--root", str(root)])
                self.assertEqual(rc_read, 0)
                self.assertNotIn(str(mutated), err.getvalue())
                out2, err2 = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
                    rc_write = transition.main(["set", "--id", "US0001", "--status",
                                                "In Progress", "--root", str(root)])
                self.assertEqual(rc_write, 0, err2.getvalue())
            # the write the exempt process asked for actually landed
            self.assertIn("> **Status:** In Progress",
                          (root / "sdlc-studio" / "stories" / "US0001-x.md").read_text(
                              encoding="utf-8"))

            # (b) a sidecar stranded by a killed predecessor still recovers, unchanged.
            mutated.write_bytes(b"def f():\n    return 2\n")
            recovered = mutation._recover_stranded(root)
            self.assertEqual(recovered, [str(mutated)])
            self.assertEqual(mutated.read_bytes(), original)
            self.assertFalse(sdlc_md.inflight_path(root).exists())


if __name__ == "__main__":
    unittest.main()
