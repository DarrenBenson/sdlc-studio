"""EP0146 / US0393: on the FLAG path a prose-taking writer reports a detected shell hazard on
stderr (non-blocking); on the --fields-file path it raises none, because that prose crossed no
shell. Verified against every converted writer, not one representative."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))

HAZARD = "run `git status` and $(whoami) - a swallowed command on the flag path"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _critic_repo(d):
    (d / "sdlc-studio" / "reviews").mkdir(parents=True)


def _close_owed_repo(d):
    (d / "sdlc-studio").mkdir(parents=True)


def _sprint_repo(d):
    (d / "sdlc-studio" / ".local").mkdir(parents=True)
    (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
        {"schema": 1, "run_id": "RUN-X", "sprint_goal": "g", "outcome": "running", "batch": []}))


#: (module name, repo setup, argv builder given root and a note-value) for every converted writer.
WRITERS = [
    ("critic", _critic_repo, lambda d, note: ["signoff", "--unit", "US0001", "--principal",
     "operator", "--author", "builder", "--note", note, "--root", str(d)]),
    ("close_owed", _close_owed_repo, lambda d, note: ["--root", str(d), "baseline", "--note", note]),
    ("sprint", _sprint_repo, lambda d, note: ["goal-verdict", "--verdict", "achieved",
     "--note", note, "--root", str(d)]),
]


class FlagPathHazardTests(unittest.TestCase):

    def _run(self, name, setup, argv):
        mod = _load(name)
        d = Path(tempfile.mkdtemp(prefix=f"hazard_{name}_"))
        setup(d)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = mod.main(argv(d) if callable(argv) else argv)
        return rc, buf.getvalue(), d

    def test_each_writer_reports_a_hazard_on_stderr(self) -> None:
        for name, setup, build in WRITERS:
            rc, out, _ = self._run(name, setup, lambda d, b=build: b(d, HAZARD))
            self.assertIn("metacharacters", out, f"{name} did not report the flag-path hazard")

    def test_the_warning_is_emitted_yet_does_not_block_the_flag_path(self) -> None:
        for name, setup, build in WRITERS:
            rc, out, _ = self._run(name, setup, lambda d, b=build: b(d, HAZARD))
            self.assertEqual(rc, 0, f"{name} blocked the flag path over a hazard - it must warn only")
            self.assertIn("metacharacters", out)

    def test_fields_file_prose_raises_no_hazard_warning(self) -> None:
        for name, setup, _build in WRITERS:
            mod = _load(name)
            d = Path(tempfile.mkdtemp(prefix=f"hazard_ff_{name}_"))
            setup(d)
            fields = {"verdict": "achieved", "note": HAZARD} if name == "sprint" else {"note": HAZARD}
            (d / "f.json").write_text(json.dumps(fields))
            if name == "critic":
                argv = ["signoff", "--unit", "US0001", "--principal", "operator", "--author",
                        "builder", "--fields-file", str(d / "f.json"), "--root", str(d)]
            elif name == "close_owed":
                argv = ["--root", str(d), "baseline", "--fields-file", str(d / "f.json")]
            else:
                argv = ["goal-verdict", "--fields-file", str(d / "f.json"), "--root", str(d)]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = mod.main(argv)
            self.assertEqual(rc, 0, f"{name} refused the fields-file path")
            self.assertNotIn("metacharacters", buf.getvalue(),
                             f"{name} warned on the fields-file path, which crossed no shell")


if __name__ == "__main__":
    unittest.main()
