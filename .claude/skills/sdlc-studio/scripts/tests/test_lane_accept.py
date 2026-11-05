"""US1119: `sprint lane accept` records a reviewer's verdict and, on APPROVE, finishes the unit.

Every case drives `sprint.py lane accept` through `sprint.main` against a throwaway repository
holding a story whose criterion passes (`shell true`), one whose criterion fails (`shell false`)
and a bug, each with the QA brief `lane land` saves and the note `critic.py brief` makes of it.
The note carries the `full` tier, which the fixture's risk band would never derive, and a later
decoy note for the same unit carries another fingerprint and tier, so a verdict recorded at
`full` was matched by the brief's own fingerprint. `critic.py record`, `verify_ac.py run`,
`transition.py set` and `sprint.py lane return` run for real through their entry points; a spy
on `lanes._script` names the calls made. One case stubs the record, for a REJECT at the review
cap: carrying a unit needs an open run whose batch holds it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import lanes  # noqa: E402

critic = loader.load_script("critic")
sprint = loader.load_script("sprint")

GREEN, RED, BUG = "US0101", "US0102", "BG0001"
AUTHOR = "builder-agent"
APPROVE = "VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"
REJECT = ("VERDICT: REJECT\n"
          "ISSUES: [new] the gate lets a red unit through; [new] a docstring overstates the "
          "refusal; [pre-existing] BG0900 the lane is slow\n"
          "BLOCKING: [new] the gate lets a red unit through\n")


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _unit(root: Path, uid: str, verify: str) -> None:
    kind, status = ("bugs", "In Progress") if uid.startswith("BG") else ("stories", "Review")
    _write(root, f"sdlc-studio/{kind}/{uid}-lane.md",
           f"# {uid}: lane\n\n> **Status:** {status}\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Severity:** Medium\n> **Affects:** src/a.py, tests/test_a.py, "
           f"changelog.d/{uid}.md\n\n## Acceptance Criteria\n\n### AC1: works\n"
           f"- **Verify:** shell {verify}\n")


def _status(root: Path, uid: str) -> str:
    path = next((root / "sdlc-studio").glob(f"*/{uid}-lane.md"))
    line = next(ln for ln in path.read_text(encoding="utf-8").splitlines() if "Status:" in ln)
    return line.split("**Status:**", 1)[1].strip()


class LaneAcceptTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = root = Path(self._tmp.name).resolve()
        _write(root, ".gitignore", "sdlc-studio/.local/\n")
        _write(root, "src/a.py", "A = 1\n")
        _write(root, "tests/test_a.py", "def test_a():\n    assert True\n")
        _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam\n\ncharter\n")
        _unit(root, GREEN, "true")
        _unit(root, RED, "false")
        _unit(root, BUG, "true")
        gitutil.git(["init", "-q", "-b", "main"], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "-m", "chore: the fixture"], root)
        self.fp = {}
        notes = []
        for uid in (GREEN, RED, BUG):
            text = f"QA brief for {uid}\nreview the diff of {uid}\n"
            _write(root, f"sdlc-studio/.local/briefs/{uid}-qa.txt", text)
            self.fp[uid] = critic.brief_fingerprint(text)
            notes.append({"fp": self.fp[uid], "unit": uid, "seat": "qa", "tier": "full"})
            notes.append({"fp": "0123456789ab", "unit": uid, "seat": "qa", "tier": "light"})
        _write(root, "sdlc-studio/.local/briefs.jsonl", "".join(json.dumps(n) + "\n"
                                                              for n in notes))
        claims = [{"surface": "commit message", "claim": "a", "ruling": "TRUE"},
                  {"surface": f"changelog.d/{GREEN}.md", "claim": "a", "ruling": "TRUE"}]
        mutants = [{"mutant": "a stays one", "test": "tests/test_a.py::test_a",
                    "result": "killed"}]
        files = [_write(root, f"sc/{n}.json", json.dumps(v))
                 for n, v in (("claims", claims), ("mutants", mutants))]
        done = subprocess.run(
            [sys.executable, str(SCRIPTS / "critic.py"), "self-check", "record", "--unit", GREEN,
             "--claims", str(files[0]), "--mutants", str(files[1]), "--author", AUTHOR,
             "--root", str(root)], capture_output=True, text=True, timeout=300, check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _accept(self, uid: str, verdict: str, *extra: str, stub=None) -> tuple[int, str, str]:
        path = _write(self.root, f"verdicts/{uid}.txt", verdict)
        real = lanes._script

        def spy(root, script, *args, **kw):
            self.calls.append((script, args))
            return (stub or real)(root, script, *args, **kw)

        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.object(lanes, "_script", spy), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["lane", "accept", "--unit", uid, "--verdict", str(path),
                              "--reviewer", "qa-seat", *extra, "--root", str(self.root)])
        return rc, out.getvalue(), err.getvalue()

    def _rows(self, uid: str) -> list[list[str]]:
        text = critic.verdicts_path(self.root).read_text(encoding="utf-8")
        return [[c.strip() for c in ln.strip().strip("|").split("|")]
                for ln in text.splitlines() if ln.startswith(f"| {uid} |")]

    def _scripts(self) -> list[str]:
        return [f"{script} {args[0]}" for script, args in self.calls]

    def test_an_approve_records_verifies_transitions_and_returns(self) -> None:
        rc, out, err = self._accept(GREEN, APPROVE, "--agent", "agent-x",
                                    "--proof", "unit=pinned")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self._scripts(), ["critic.py record", "verify_ac.py run",
                                           "transition.py set", "sprint.py lane"])
        row = self._rows(GREEN)[-1]
        # verdict, reviewer, author (the self-check's), date, brief fingerprint, tier
        self.assertEqual([row[1], row[2], row[3], row[5], row[6]],
                         ["APPROVE", "qa-seat", AUTHOR, self.fp[GREEN], "full"])
        self.assertEqual(_status(self.root, GREEN), "Done")
        back = self.calls[-1][1]
        self.assertEqual(back[:3], ("lane", "return", "--units"))
        self.assertIn(("--agent", "agent-x"), list(zip(back, back[1:])))
        self.assertIn(("--proof", "unit=pinned"), list(zip(back, back[1:])))
        self.assertIn("AC1: passed", out)
        # a bug moves to Fixed, not Done; its author is named when no self-check names one
        self.calls.clear()
        rc, out, err = self._accept(BUG, APPROVE, "--author", "bug-builder", "--tokens", "1200",
                                    "--minutes", "3", "--gap", "unit=none owed")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(_status(self.root, BUG), "Fixed")
        self.assertEqual(self._rows(BUG)[-1][3], "bug-builder")
        back = self.calls[-1][1]
        for pair in (("--tokens", "1200"), ("--minutes", "3.0"), ("--gap", "unit=none owed")):
            self.assertIn(pair, list(zip(back, back[1:])))
        self.assertNotIn("--agent", back)

    def test_a_reject_records_and_prints_only_the_blocking_findings(self) -> None:
        rc, out, err = self._accept(GREEN, REJECT)
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(self._scripts(), ["critic.py record"])
        self.assertEqual(self._rows(GREEN)[-1][1], "REJECT")
        self.assertEqual(_status(self.root, GREEN), "Review")
        self.assertIn("round 1", out)
        self.assertIn("BLOCKING: [new] the gate lets a red unit through", out)
        for unblocking in ("docstring overstates", "BG0900", "lane is slow"):
            self.assertNotIn(unblocking, out + err)
        # at the review cap the record carries the unit as a bug, and its id is printed
        self.calls.clear()

        def capped(root, script, *args, **kw):
            said = (f"recorded {GREEN} REJECT [delivery] round 2 -> verdicts.md\n"
                    f"{critic.carried_notice(GREEN, 'BG0042')}\n")
            return subprocess.CompletedProcess([script, *args], 0, said, "")

        rc, out, err = self._accept(GREEN, REJECT, stub=capped)
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(self._scripts(), ["critic.py record"])
        self.assertIn("round 2", out)
        self.assertIn(f"{critic.CARRIED_REASON}: BG0042", out)
        self.assertEqual(_status(self.root, GREEN), "Review")

    def test_a_red_criterion_stops_the_transition(self) -> None:
        rc, out, err = self._accept(RED, APPROVE, "--author", "red-builder",
                                    "--agent", "agent-x")
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(self._scripts(), ["critic.py record", "verify_ac.py run"])
        self.assertEqual(_status(self.root, RED), "Review")
        self.assertIn("FAIL AC1: shell false", err)
        self.assertIn("NOT moved to Done", err)

    def test_a_refusal_records_nothing(self) -> None:
        cases = {"no brief": (RED, ("--author", "x"), "no QA brief"),
                 "no author": (RED, (), "name --author"),
                 "no unit": ("US0999", ("--author", "x"), "no artefact with id US0999"),
                 "no noted tier": (RED, ("--author", "x"), "records the review tier")}
        (self.root / "sdlc-studio/.local/briefs" / f"{RED}-qa.txt").unlink()
        for name, (uid, extra, said) in cases.items():
            with self.subTest(name):
                if name == "no author":
                    _write(self.root, f"sdlc-studio/.local/briefs/{RED}-qa.txt",
                           f"QA brief for {RED}\nreview the diff of {RED}\n")
                if name == "no noted tier":
                    (self.root / "sdlc-studio/.local/briefs.jsonl").unlink()
                rc, out, err = self._accept(uid, APPROVE, *extra)
                self.assertEqual(rc, 2, out + err)
                self.assertIn(said, err)
        self.assertEqual(self.calls, [])
        self.assertFalse(critic.verdicts_path(self.root).exists())


if __name__ == "__main__":
    unittest.main()
