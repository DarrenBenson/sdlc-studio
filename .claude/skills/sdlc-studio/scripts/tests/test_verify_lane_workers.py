"""US1113: the release verify lane runs the criteria its batch leaves on a bounded worker pool.

After the pytest batch (US1112) the lane ran every story one after another, so each Verify line
the batch cannot answer (the 631 that are not a bare `pytest <node>`, and each bare one naming a
file the batch did not collect) paid its subprocess in series: 1,524 s on this workspace on
2026-11-03, against 741 s on eight workers.

Each fixture verifier appends `<name> start <time>` and `<name> end <time>` to a log, so how
many ran at once, and in what order, is observed rather than patched (LL0014).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import errno
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

gate = loader.load_script("gate")

GATE = Path(__file__).resolve().parent.parent / "gate.py"

#: A verifier that logs its start and end around a sleep, then exits with the code it is given.
PROBE = '''import sys, time
name, sleep, code = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
with open("ran.log", "a", encoding="utf-8") as fh:
    fh.write(f"{name} start {time.time()}\\n")
time.sleep(sleep)
with open("ran.log", "a", encoding="utf-8") as fh:
    fh.write(f"{name} end {time.time()}\\n")
sys.exit(code)
'''
#: A test module carrying the marker, whose tests log the same way.
MARKED = '''import time
import unittest
from pathlib import Path

import pytest

LOG = Path(__file__).resolve().parent.parent / "ran.log"


def _probe(name):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"{name} start {time.time()}\\n")
    time.sleep(0.5)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"{name} end {time.time()}\\n")


@pytest.mark.serial_only
def test_s1():
    _probe("s1")


@pytest.mark.serial_only
def test_s2():
    _probe("s2")


class MarkedCase(unittest.TestCase):
    def test_s3(self):
        _probe("s3")
'''
#: A test module carrying the marker whose one test fails.
RED_MARKED = "import pytest\n\n\n@pytest.mark.serial_only\ndef test_red():\n    assert False\n"
PYTEST_INI = ("[pytest]\naddopts = -p no:cacheprovider\nmarkers =\n"
              "    serial_only: runs in the serial phase\n")


def probe(name: str, sleep: float, code: int = 0) -> str:
    """The Verify line that runs the probe."""
    return f'shell "{sys.executable}" probe.py {name} {sleep} {code}'


def _workspace(root: Path, stories: list[tuple]) -> None:
    """Write the probe and one story per (status, Verify line or None, extra lines) row,
    numbered US9101 upwards so path order is row order."""
    (root / "probe.py").write_text(PROBE, encoding="utf-8")
    (root / "pytest.ini").write_text(PYTEST_INI, encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_marked.py").write_text(MARKED, encoding="utf-8")
    folder = root / "sdlc-studio" / "stories"
    folder.mkdir(parents=True)
    for i, (status, verify, extra) in enumerate(stories, 1):
        body = (f"# US{9100 + i}: s\n\n> **Status:** {status}\n{extra}\n"
                f"## Acceptance Criteria\n\n### AC1: it holds\n\n- **Then** it holds\n")
        if verify:
            body += f"- **Verify:** {verify}\n"
        (folder / f"US{9100 + i}-s.md").write_text(body, encoding="utf-8")


def _intervals(root: Path) -> dict[str, list[tuple[float, float]]]:
    """Each probe's runs as (start, end), in the order they started. A run killed at its
    ceiling has no end, so it is closed at infinity."""
    log = root / "ran.log"
    runs: dict[str, list] = {}
    for line in (log.read_text(encoding="utf-8") if log.is_file() else "").splitlines():
        name, edge, stamp = line.split()
        if edge == "start":
            runs.setdefault(name, []).append([float(stamp), float("inf")])
        else:
            runs[name][-1][1] = float(stamp)
    return {name: [tuple(r) for r in rs] for name, rs in runs.items()}


def _most_at_once(intervals: list[tuple[float, float]]) -> int:
    """The largest number of intervals open at one instant; an end at the instant another
    starts is not an overlap."""
    events = sorted([(s, 1) for s, _ in intervals] + [(e, -1) for _, e in intervals],
                    key=lambda ev: (ev[0], ev[1]))
    most = now = 0
    for _, step in events:
        now += step
        most = max(most, now)
    return most


def _env(**extra: str) -> dict:
    """This process's environment for the lane, without an outer pytest's `PYTEST_XDIST_*`,
    `PYTEST_ADDOPTS` and `PYTEST_CURRENT_TEST`, so a nested pytest a verifier spawns does not
    inherit them."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("PYTEST_XDIST_") and k not in ("PYTEST_ADDOPTS",
                                                               "PYTEST_CURRENT_TEST")}
    env.update(extra)
    return env


def _lane(root: Path, workers: str, timeout: int = 60) -> dict:
    """The release verify lane in-process under `SDLC_VERIFY_WORKERS=workers`."""
    with mock.patch.dict(os.environ, _env(**{gate.VERIFY_WORKERS_ENV: workers}), clear=True):
        return gate._verify_acs(str(root), timeout=timeout, batch=True)


class VerifyLaneWorkersTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_the_pool_is_bounded_by_the_worker_setting(self) -> None:
        """AC1. MUTANTS: a pool built with no `max_workers` (twelve threads on eight cores, so
        all six probes overlap); the setting read and named while the loop stays serial (none
        overlap at 3); the clause dropped from the detail. Through `gate.py --release`, the
        command an operator runs, so the variable is read where the registered lane reads it:
        the two settings run at once, each on its own workspace."""
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        roots = {"3": self.root, "1": Path(other.name)}
        for root in roots.values():
            _workspace(root, [("Done", probe(f"p{i}", 1.0), "") for i in range(6)])
        argv = [sys.executable, "-B", str(GATE), "--release",
                "--only", "verify,review-legs,versions,changelog-fragments"]
        procs = {k: subprocess.Popen(argv + ["--root", str(root)], text=True,
                                     env=_env(**{gate.VERIFY_WORKERS_ENV: k,
                                                 "PYTHONDONTWRITEBYTECODE": "1"}),
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                 for k, root in roots.items()}
        pages = {k: p.communicate(timeout=120)[0] for k, p in procs.items()}
        for k, root in roots.items():
            lane = [ln for ln in pages[k].splitlines() if "] verify [" in ln]
            self.assertEqual(1, len(lane), pages[k])
            self.assertTrue(lane[0].lstrip().startswith("[PASS] verify"), lane[0])
            self.assertIn(f", stories on {k} worker(s) ({gate.VERIFY_WORKERS_ENV}, default ",
                          lane[0])
            runs = _intervals(root)
            self.assertEqual({f"p{i}" for i in range(6)}, set(runs), pages[k])
            self.assertTrue(all(len(r) == 1 for r in runs.values()), runs)
            most = _most_at_once([r[0] for r in runs.values()])
            if k == "3":
                self.assertGreaterEqual(most, 2, "three workers: some verifiers overlap")
                self.assertLessEqual(most, 3, "three workers: never more than three at once")
            else:
                self.assertEqual(1, most, "one worker: no two verifiers overlap")
        out = subprocess.run([sys.executable, "-B", str(GATE), "--help"], capture_output=True,
                             text=True, check=False, timeout=60).stdout
        self.assertIn(gate.VERIFY_WORKERS_ENV, re.sub(r"\s+", " ", out))

    def test_a_timeout_on_the_pool_still_reads_red(self) -> None:
        """AC2. MUTANTS: the worker catching the slow story's overrun and dropping its report
        (the lane reads green); the red stories re-run alone after the pool, keeping the second
        verdict (the slow probe starts twice). A 6 s probe under a 2 s ceiling, three 0.3 s
        probes beside it; the same workspace with one worker is the serial run compared."""
        _workspace(self.root, [("Done", probe("slow", 6), "")]
                   + [("Done", probe(f"f{i}", 0.3), "") for i in range(3)])
        pooled = _lane(self.root, "3", timeout=2)
        runs = _intervals(self.root)
        (self.root / "ran.log").unlink()
        serial = _lane(self.root, "1", timeout=2)
        self.assertEqual(1, pooled["count"], pooled["detail"])
        self.assertIn("[ids: US9101::AC1]", pooled["detail"])
        self.assertEqual(1, len(runs["slow"]), f"the slow verifier ran once: {runs}")
        self.assertTrue(any(r[0][0] < runs["slow"][0][0] + 2
                            for name, r in runs.items() if name != "slow"),
                        f"the others ran while the slow one did: {runs}")
        self.assertEqual(1, len(_intervals(self.root)["slow"]))
        self.assertEqual((serial["count"], re.findall(r"\[ids: [^]]*\]", serial["detail"])),
                         (pooled["count"], re.findall(r"\[ids: [^]]*\]", pooled["detail"])))

    def test_serial_only_verifiers_run_after_the_pool(self) -> None:
        """AC3. MUTANT: every story sent to the pool (the three marked stories, first in path
        order, start beside the probes). They name the marked module in a flagged pytest line, a
        shell line, and a `cd tests && python3 -m unittest` dotted name; four 0.8 s probes on
        three workers are the pool, whose own overlap is the positive control."""
        _workspace(self.root, [("Done", "pytest tests/test_marked.py::test_s1 -q", ""),
                               ("Done", f'shell "{sys.executable}" -m pytest -q '
                                        "tests/test_marked.py::test_s2", ""),
                               ("Done", f'shell cd tests && "{sys.executable}" -m unittest '
                                        "test_marked.MarkedCase.test_s3", "")]
                   + [("Done", probe(f"p{i}", 0.8), "") for i in range(4)])
        res = _lane(self.root, "3")
        runs = {n: r[0] for n, r in _intervals(self.root).items()}
        self.assertEqual(0, res["count"], res["detail"])
        marked = ("s1", "s2", "s3")
        self.assertEqual({*marked, "p0", "p1", "p2", "p3"}, set(runs), res["detail"])
        pool = [runs[f"p{i}"] for i in range(4)]
        self.assertGreaterEqual(_most_at_once(pool), 2, "the probes ran on the pool")
        drained = max(end for _, end in pool)
        for name in marked:
            self.assertGreaterEqual(runs[name][0], drained, f"{name} started beside the pool")
        self.assertEqual(1, _most_at_once([runs[n] for n in marked]), "and one at a time")
        self.assertIn("then 3 naming a serial_only test module, one at a time", res["detail"])

    def test_the_pool_reports_in_story_order_and_writes_nothing(self) -> None:
        """AC4. MUTANTS: reports collected with `as_completed` (the red clause lists the fastest
        first); the `serial_only` story reported after the pooled ones, as it ran (US9101 moves
        to the end of the red clause, and one worker runs it last too, so only the ids named
        here see it); `verify_story(dry_run=False)` (the green criterion gains `Verified: yes`,
        and the stamped red one is downgraded). The red criteria finish in the reverse of path
        order here, and every clause is compared with the one-worker run's."""
        _workspace(self.root, [
            ("Done", f'shell "{sys.executable}" -m pytest -q tests/test_red_marked.py', ""),
            ("Done", probe("r1", 1.2, 1) + "\n- **Verified:** yes", ""),
            ("Done", probe("r2", 0.8, 1), ""),
            ("Done", probe("g1", 0.1), ""),
            ("Ready", probe("u1", 1.0, 1), ""),
            ("Done", probe("r3", 0.4, 1), ""),
            ("Ready", probe("u2", 0.2, 1), ""),
            ("Done", None, ""),
            ("Done", probe("b1", 0), "> **Provenance:** external\n"),
            ("Done", None, "")])
        (self.root / "tests" / "test_red_marked.py").write_text(RED_MARKED, encoding="utf-8")
        stories = sorted((self.root / "sdlc-studio" / "stories").glob("*.md"))
        before = {p.name: p.read_bytes() for p in stories}
        pooled = _lane(self.root, "4")
        serial = _lane(self.root, "1")
        self.assertEqual(before, {p.name: p.read_bytes() for p in stories})
        detail = pooled["detail"]
        self.assertIn("then 1 naming a serial_only test module, one at a time", detail)
        self.assertIn("[ids: US9101::AC1 US9102::AC1 US9103::AC1 US9106::AC1]", detail)
        self.assertLess(detail.index("US9105::AC1"), detail.index("US9107::AC1"), detail)
        self.assertLess(detail.index("US9108"), detail.index("US9110"), detail)

        def without_cost(text: str) -> str:
            return re.sub(r" \[\d+ story/stories, [^]]*\]", "", text)

        self.assertNotEqual(without_cost(detail), detail, "the cost clause was cut")
        self.assertEqual(without_cost(serial["detail"]), without_cost(detail))
        self.assertEqual(serial["count"], pooled["count"])


class PoolEdgeTests(unittest.TestCase):
    """The pool's edges the criteria do not reach."""

    def test_each_named_py_file_is_read_once_for_the_marker(self) -> None:
        """MUTANTS: the `::node` not cut (a node's file is never read); quotes kept on a shell
        token; a dotted name, or a file read against a directory the line names, never read; a
        script that is not a test module, a `.pyc` or an absent file read as marked; the memo
        ignored (the emptied file is read again)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "t").mkdir()
            (root / "t" / "test_m.py").write_text("@pytest.mark.serial_only\n",
                                                  encoding="utf-8")
            (root / "t" / "test_c.py").write_text("def test_a(): pass\n", encoding="utf-8")
            (root / "t" / "test_m.pyc").write_text("serial_only", encoding="utf-8")
            (root / "t" / "tool.py").write_text("# serial_only\n", encoding="utf-8")
            memo: dict = {}
            names = gate._names_serial_only
            self.assertTrue(names(["pytest t/test_m.py::C::test_a"], root, memo))
            for line in ("shell python3 -m pytest 't/test_m.py'",
                         "shell python3 -m unittest t.test_m.C.test_a",
                         "shell cd t && python3 -m unittest test_m.C",
                         "shell python3 -m unittest discover -s t -p test_m.py"):
                self.assertTrue(names([line], root, {}), line)
            self.assertFalse(names(["pytest t/test_c.py::test_a", "grep x t/test_m.pyc",
                                    "pytest t/test_gone.py::test_a", "shell python3 t/tool.py",
                                    "shell cd t && python3 -m unittest test_c.C"], root, {}))
            (root / "t" / "test_m.py").write_text("", encoding="utf-8")
            self.assertTrue(names(["pytest t/test_m.py"], root, memo), "read once, from the memo")

    def test_a_verify_token_too_long_to_stat_is_judged_not_raised(self) -> None:
        """REGRESSION. The directory test stats every word of a Verify line, and on Python 3.10
        and 3.12 `Path.is_dir` raises on the stat's ENAMETOOLONG, as for a 300-character grep
        pattern: the lane raised `OSError: [Errno 36] File name too long` and judged nothing.
        Python 3.14 answers False, so `Path.is_dir` is made to raise as 3.10 does, and the test
        fails on the old line under 3.14 as well as 3.10. MUTANT: the directory test back on
        `Path.is_dir`."""
        real_is_dir = Path.is_dir

        def is_dir_as_on_3_10(path, *args, **kwargs):
            if any(len(part) > 255 for part in path.parts):
                raise OSError(errno.ENAMETOOLONG, "File name too long", str(path))
            return real_is_dir(path, *args, **kwargs)

        line = "grep -q " + "a" * 300 + " README.md"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, [("Done", line, "")])
            (root / "README.md").write_text("x\n", encoding="utf-8")
            with mock.patch.object(Path, "is_dir", is_dir_as_on_3_10):
                self.assertFalse(gate._names_serial_only([line], root, {}))
                res = _lane(root, "2")
        self.assertEqual(1, res["count"], res["detail"])
        self.assertIn("[ids: US9101::AC1]", res["detail"])

    def test_the_worker_setting_is_read_from_its_variable(self) -> None:
        """MUTANT: the override ignored, a nonsense value honoured, or the default not capped."""
        with mock.patch.object(gate.os, "cpu_count", return_value=32):
            for raw, want in (("3", 3), ("", 8), ("0", 8), ("-2", 8), ("2.5", 8), ("x", 8)):
                with mock.patch.dict(os.environ, {gate.VERIFY_WORKERS_ENV: raw}):
                    self.assertEqual((want, 8), gate._verify_workers(), raw)
        with mock.patch.object(gate.os, "cpu_count", return_value=None), \
                mock.patch.dict(os.environ, {gate.VERIFY_WORKERS_ENV: ""}):
            self.assertEqual((1, 1), gate._verify_workers())

    def test_the_batch_count_survives_the_pool(self) -> None:
        """The seam with US1112. MUTANT: the answers each story's view of the batch counted never
        added back to the shared cache, so the cost clause reads `batch resolved 0 of 3` for a
        batch that answered all three. Three bare pytest verifiers on three workers."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, [("Done", f"pytest tests/test_plain.py::test_{i}", "")
                              for i in range(3)])
            (root / "tests" / "test_plain.py").write_text(
                "".join(f"def test_{i}():\n    pass\n\n\n" for i in range(3)), encoding="utf-8")
            with mock.patch.dict(os.environ, _env(**{gate.VERIFY_WORKERS_ENV: "3",
                                                     "PYTEST_XDIST_AUTO_NUM_WORKERS": "2"}),
                                 clear=True):
                res = gate._verify_acs(str(root), timeout=60, batch=True)
        self.assertEqual(0, res["count"], res["detail"])
        self.assertIn("batch resolved 3 of 3 pytest verifier(s)", res["detail"])

    def test_an_interrupt_cancels_the_stories_still_queued(self) -> None:
        """MUTANT: the queued stories left in the pool when the lane is interrupted, so the
        interpreter's exit runs all nine. SIGINT goes to the lane's process group, as a
        terminal sends Ctrl-C, once three of nine 3 s probes have started on three workers."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, [("Done", probe(f"p{i}", 3), "") for i in range(9)])
            proc = subprocess.Popen(
                [sys.executable, "-B", str(GATE), "--release", "--root", str(root),
                 "--only", "verify,review-legs,versions,changelog-fragments"],
                env=_env(**{gate.VERIFY_WORKERS_ENV: "3"}), stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, start_new_session=True)
            deadline = time.monotonic() + 60
            while len(_intervals(root)) < 3 and time.monotonic() < deadline:
                time.sleep(0.05)
            os.killpg(proc.pid, signal.SIGINT)
            self.assertNotEqual(0, proc.wait(timeout=60))
            time.sleep(0.5)
            self.assertEqual(3, len(_intervals(root)), "only the three running ever started")


if __name__ == "__main__":
    unittest.main()
