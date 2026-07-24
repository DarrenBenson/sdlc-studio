"""The anchoring contract: a script that declares `--root` anchors it BEFORE it dispatches.

The census guard beside this one measures whether a script CALLS the shared resolver. That is
a lower bound and it says so: a call made for one purpose (a guard, an advisory) sits happily
beside verbs that still read a bare `--root .`, and the script measures "anchored" while every
path it touches is the cwd's. This suite measures the thing that actually matters instead - the
value the verbs receive.

The method is behavioural, not textual. Each script's `main()` is called with a namespace this
suite owns, carrying the family default `root="."` and a recorder in place of the dispatch
target. Because the namespace object is ours, whatever `main()` wrote onto it is readable
afterwards, whether the run dispatched, exited or raised. The assertion is that `root` is no
longer `"."` but the DISCOVERED root of a fixture project the cwd sits below - which is exactly
the failure the family had: a run from a subdirectory took the cwd as the project, read an
empty tree or wrote into a stray one, and exited 0.

The applicable set is MEASURED (every script whose parser or source declares `--root`), never
listed, so a script added to the family is held to the contract without anyone remembering to
add it, and a script that has no project-root surface is out of scope by measurement.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_root_census as census  # noqa: E402  (the measurement, reused rather than re-spelled)

SCRIPTS = census.SCRIPTS

#: What makes a script a WRITER for the purposes of the two slices this suite reports. Measured
#: off the source, so the split cannot drift from the code the way a hand-kept list would. It is
#: a coarse signal deliberately: a script that can mutate a tree is the fail-open case, because
#: its output lands in a stray tree and the exit code is still 0.
_WRITES = re.compile(
    r"\.write_text\(|\.mkdir\(|open\([^)]*[\"']w|\.unlink\(|shutil\.(?:copy|move|rmtree)")

#: A marker file that makes a directory an sdlc-studio workspace, so `discover_root` stops there.
_WORKSPACE = Path("sdlc-studio")


def _root_declaring_scripts() -> list[str]:
    return sorted(name for name, klass in census.measure().items() if klass != "non-root")


def _is_writer(name: str) -> bool:
    return bool(_WRITES.search((SCRIPTS / name).read_text(encoding="utf-8")))


class _Recorded(Exception):
    """Raised by the stand-in dispatch target so no real verb runs after the anchor is read."""


class RootAnchorContractTests(unittest.TestCase):
    """Every root-declaring script anchors `args.root` on the discovered root before dispatch."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.scripts = _root_declaring_scripts()
        if not cls.scripts:
            raise unittest.SkipTest("the measurement found no root-declaring scripts")

    def _anchored_root(self, name: str) -> tuple[str, str]:
        """Call `<script>.main()` from a subdirectory of a fixture project.

        Returns (what main left on args.root, the root it should have discovered).
        """
        mod = census._load(SCRIPTS / name)
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp).resolve() / "project"
            (project / _WORKSPACE / "stories").mkdir(parents=True)
            below = project / "deep" / "sub"
            below.mkdir(parents=True)

            ns = argparse.Namespace(root=".", cmd="", format="text")
            ns.func = lambda _args: (_ for _ in ()).throw(_Recorded())

            cwd = os.getcwd()
            os.chdir(below)
            try:
                with mock.patch.object(argparse.ArgumentParser, "parse_args",
                                       lambda self, *a, **k: ns), \
                        contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()):
                    try:
                        mod.main([])
                    except BaseException:  # noqa: BLE001 - the verb never gets to matter here
                        pass
            finally:
                os.chdir(cwd)
            return str(getattr(ns, "root", "")), str(project)

    def _assert_anchors(self, name: str) -> None:
        got, want = self._anchored_root(name)
        self.assertEqual(
            got, want,
            f"{name}: main() left root={got!r} - a run from a subdirectory of a project must "
            f"anchor on the project ({want!r}), not on the cwd")

    def test_every_writer_script_anchors_its_root_before_dispatch(self) -> None:
        writers = [n for n in self.scripts if _is_writer(n)]
        self.assertTrue(writers, "the measurement found no writer scripts")
        for name in writers:
            with self.subTest(script=name):
                self._assert_anchors(name)

    def test_every_reader_script_anchors_its_root_before_dispatch(self) -> None:
        readers = [n for n in self.scripts if not _is_writer(n)]
        self.assertTrue(readers, "the measurement found no reader scripts")
        for name in readers:
            with self.subTest(script=name):
                self._assert_anchors(name)

    def test_a_named_root_is_honoured_verbatim_and_never_discovered_over(self) -> None:
        """Anchoring must only ever widen the default: pointing a run at another project stands.

        Without this the fix could pass by hard-wiring discovery, which would silently retarget
        every `--root X` invocation in the family - a far worse failure than the one repaired.
        """
        for name in self.scripts:
            with self.subTest(script=name):
                mod = census._load(SCRIPTS / name)
                with tempfile.TemporaryDirectory() as tmp:
                    named = Path(tmp).resolve() / "elsewhere"
                    (named / _WORKSPACE).mkdir(parents=True)
                    ns = argparse.Namespace(root=str(named), cmd="", format="text")
                    ns.func = lambda _args: (_ for _ in ()).throw(_Recorded())
                    with mock.patch.object(argparse.ArgumentParser, "parse_args",
                                           lambda self, *a, **k: ns), \
                            contextlib.redirect_stdout(io.StringIO()), \
                            contextlib.redirect_stderr(io.StringIO()):
                        try:
                            mod.main([])
                        except BaseException:  # noqa: BLE001
                            pass
                    self.assertEqual(str(getattr(ns, "root", "")), str(named),
                                     f"{name}: a NAMED root must be honoured verbatim")


if __name__ == "__main__":
    unittest.main()
