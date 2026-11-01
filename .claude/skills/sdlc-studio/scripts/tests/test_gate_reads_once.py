"""BG1109: one gate run reads the verdict ledger and the decisions log once each.

The conformance and engagement-floor lanes ask for a ledger once per unit, and each ask used to
read and parse the whole file again: 2255 parses of the decisions log in one engagement-floor
pass over this repository. `decisions.read_once` memoises a value derived from a file on that
file's identity, and a file changed within `decisions.SETTLED_NS` is read on every call, so a
fixture written a moment ago is read exactly as it was before the memo existed.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_gate_reads_once.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/decisions.py
from __future__ import annotations

import builtins
import collections
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

gate = loader.load_script("gate")
critic = loader.load_script("critic")
decisions = loader.load_script("decisions")
# Loaded so sys.modules holds both lanes; the tests read them from there, as the gate does.
loader.load_script("conformance")
loader.load_script("engagement_floor")

#: Never settled: every read is a fresh one, which is what every reader did before the memo.
NEVER = 10 ** 30
LANES = ["conformance", "engagement-floor"]


def _decisions_modules() -> list:
    """Every live copy of decisions.py. Another test module may re-execute it, and each lane
    module holds the copy it imported, so a patch must reach all of them."""
    mods = [sys.modules.get("decisions"), decisions,
            getattr(sys.modules.get("conformance"), "decisions", None),
            getattr(sys.modules.get("engagement_floor"), "decisions", None)]
    out: list = []
    for m in mods:
        if m is not None and all(m is not o for o in out):
            out.append(m)
    return out


@contextlib.contextmanager
def _settled_after(ns: int):
    """Run with `SETTLED_NS` at `ns` on every copy of decisions.py, from an empty memo."""
    with contextlib.ExitStack() as stack:
        for m in _decisions_modules():
            m._READS.clear()
            stack.enter_context(mock.patch.object(m, "SETTLED_NS", ns))
        try:
            yield
        finally:
            for m in _decisions_modules():
                m._READS.clear()


@contextlib.contextmanager
def _one_decisions_module():
    """Point the lane modules the gate imports at the one decisions.py in sys.modules. A gate
    run imports each module once, so it holds one memo; a test process that re-executed
    decisions.py holds several copies, each with a memo of its own, and would count a read
    per copy."""
    one = sys.modules["decisions"]
    with contextlib.ExitStack() as stack:
        for name in ("conformance", "engagement_floor"):
            stack.enter_context(mock.patch.object(sys.modules[name], "decisions", one))
        yield


@contextlib.contextmanager
def _counting_opens(paths: dict):
    """Count every open of each watched file, `{label: Path}`, through `open` or `Path.open`."""
    watched = {str(p.resolve()): label for label, p in paths.items()}
    counts: collections.Counter = collections.Counter()
    real_open = io.open

    def counted(file, *args, **kwargs):
        if isinstance(file, (str, Path)):
            label = watched.get(str(Path(file).resolve()))
            if label:
                counts[label] += 1
        return real_open(file, *args, **kwargs)

    with mock.patch.object(io, "open", counted), mock.patch.object(builtins, "open", counted):
        yield counts


def _story(root: Path, num: int, *, ac: bool, affects: str = "") -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# US{num:04d}: sample", "", "> **Status:** Done",
             "> **Epic:** [EP0001: x](../epics/EP0001-x.md)"]
    if affects:
        lines.append(f"> **Affects:** {affects}")
    lines.append("")
    if ac:
        lines += ["## Acceptance Criteria", "", "### AC1: works", "- **Given** a thing",
                  "- **Verify:** shell echo ok", "- **Verified:** yes (2026-01-01)"]
    (d / f"US{num:04d}-sample.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _verdict(root: Path, unit: str, verdict: str) -> None:
    with mock.patch.object(critic.sdlc_md, "now_date", return_value=critic.REPAIR_VERB_RETIRED):
        critic.record_verdict(root, unit, verdict, reviewer="independent-critic", author="builder")


def _fixture(root: Path) -> None:
    """Six Done stories whose lane verdicts turn on both ledgers: US0001 approved, US0002
    rejected and waived from the critiqued stage, US0003 rejected then approved, and three
    multi-file stories with no plan, of which US0004 and US0005 are waived from the engagement
    floor and US0006 is not."""
    _story(root, 1, ac=True)
    _story(root, 2, ac=True)
    _story(root, 3, ac=True)
    _story(root, 4, ac=False, affects="src/a.py, src/b.py")
    _story(root, 5, ac=False, affects="src/c.py, src/d.py")
    _story(root, 6, ac=False, affects="src/e.py, src/f.py")
    _verdict(root, "US0001", "approve")
    _verdict(root, "US0002", "reject")
    _verdict(root, "US0003", "reject")
    _verdict(root, "US0003", "approve")
    decisions.record_waiver(root, "rule:conformance:critiqued:US0002", "inherited debt")
    decisions.record_waiver(root, "rule:engagement-floor:US0004", "legacy carve-out")
    decisions.record_waiver(root, "rule:engagement-floor:US0005", "legacy carve-out")


def _ledgers(root: Path) -> dict:
    return {"verdicts": critic.verdicts_path(root), "decisions": decisions._log_path(root)}


def _lane_outputs(root: Path) -> dict:
    """What each lane reports, through the gate and through its own detector, minus the lane
    timings and the detectors' `generated_at` clock readings. The detectors are the modules
    the gate imports, which `_one_decisions_module` points at one decisions.py."""
    res = gate.run_gate(str(root), only=LANES)
    lanes = [{k: v for k, v in c.items() if k != "seconds"} for c in res["checks"]]
    floor = sys.modules["engagement_floor"].detect(root)
    conf = sys.modules["conformance"].detect_conformance(root)
    for detected in (floor, conf):
        detected.pop("generated_at")
    return {"ok": res["ok"], "lanes": lanes, "floor": floor, "conformance": conf}


class GateReadsOnceTests(unittest.TestCase):

    def test_each_ledger_is_read_once_and_the_lanes_agree(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            with _one_decisions_module():
                with _settled_after(NEVER), _counting_opens(_ledgers(root)) as per_unit:
                    before = _lane_outputs(root)
                with _settled_after(0), _counting_opens(_ledgers(root)) as once:
                    after = _lane_outputs(root)
        # The control: without the memo the lanes ask for each ledger many times over, so
        # "once" below is a saving and not a fixture that only ever asked once.
        self.assertGreater(per_unit["verdicts"], 1, per_unit)
        self.assertGreater(per_unit["decisions"], 1, per_unit)
        self.assertEqual(once["verdicts"], 1, once)
        self.assertEqual(once["decisions"], 1, once)
        self.assertEqual(after, before)
        # And the outputs carry what the ledgers say, so agreeing is not agreeing on nothing.
        floor = {u["id"]: u for u in after["floor"]["units"]}
        self.assertTrue(floor["US0004"]["waived"] and floor["US0005"]["waived"])
        self.assertTrue(floor["US0006"]["violation"])
        units = {u["id"]: u for u in after["conformance"]["units"]}
        self.assertEqual([w["stage"] for w in units["US0002"]["waived"]], ["critiqued"])
        self.assertFalse(after["ok"])

    def test_the_verdict_ledger_is_parsed_once(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            mod = sys.modules["conformance"].critic
            with _one_decisions_module(), _settled_after(0), mock.patch.object(
                    mod, "_parse_verdicts", wraps=mod._parse_verdicts) as parse:
                gate.run_gate(str(root), only=LANES)
                gate.run_gate(str(root), only=LANES)
        self.assertEqual(parse.call_count, 1)


class ReadOnceTests(unittest.TestCase):

    def test_a_changed_file_is_read_again(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.record_waiver(root, "rule:engagement-floor:US0001", "first")
            with _settled_after(0):
                self.assertEqual(len(decisions.list_decisions(root)), 1)
                decisions.record_waiver(root, "rule:engagement-floor:US0002", "second")
                self.assertEqual(len(decisions.list_decisions(root)), 2)
                _verdict(root, "US0001", "approve")
                self.assertEqual(len(critic.read_verdicts(root)), 1)
                _verdict(root, "US0001", "reject")
                self.assertEqual([r["verdict"] for r in critic.read_verdicts(root)],
                                 ["APPROVE", "REJECT"])

    def test_a_file_changed_within_the_window_is_read_on_every_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.record_waiver(root, "rule:engagement-floor:US0001", "first")
            _verdict(root, "US0001", "approve")
            with _settled_after(NEVER), _counting_opens(_ledgers(root)) as reads:
                decisions.list_decisions(root)
                decisions.list_decisions(root)
                critic.read_verdicts(root)
                critic.read_verdicts(root)
        self.assertEqual(reads["decisions"], 2, reads)
        self.assertGreaterEqual(reads["verdicts"], 2, reads)
        # The window outlasts a whole-second timestamp tick, so a file on a filesystem that
        # records seconds is never trusted on its identity inside the second it changed.
        self.assertGreater(decisions.SETTLED_NS, 1_000_000_000)

    def test_each_reader_of_the_ledger_gets_its_own_value(self) -> None:
        """The parsed rows and the raw text are two values memoised on one file, so neither may
        answer for the other."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _verdict(root, "US0001", "approve")
            _verdict(root, "US0001", "reject")
            date = critic.read_verdicts(root)[0]["date"]
            critic.record_supersession(root, "US0001", date=date, reason="the row is retired",
                                       authorised_by="Darren Benson (operator)",
                                       boundary="operator console", verdict="APPROVE")

            def readers() -> tuple:
                return (critic.read_verdicts(root), critic.read_supersessions(root),
                        critic.read_round_rulings(root), critic.read_verdicts(root))

            with _settled_after(NEVER):
                fresh = readers()
            with _settled_after(0):
                memoised = readers()
        self.assertEqual(memoised, fresh)
        self.assertTrue(fresh[0][0]["superseded"])
        self.assertEqual(len(fresh[1]), 1)

    def test_each_caller_gets_its_own_rows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.record_waiver(root, "rule:engagement-floor:US0001", "first")
            _verdict(root, "US0001", "approve")
            with _settled_after(0):
                decisions.list_decisions(root)[0]["status"] = "revisited"
                critic.read_verdicts(root)[0]["verdict"] = "REJECT"
                decisions.list_decisions(root).clear()
                self.assertEqual(decisions.list_decisions(root)[0]["status"], "accepted")
                self.assertEqual(critic.read_verdicts(root)[0]["verdict"], "APPROVE")

    def test_a_status_filter_reads_from_the_same_parse(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            decisions.record_waiver(root, "rule:engagement-floor:US0001", "first")
            decisions.add(root, "a ruling", "because", "revisited")
            with _settled_after(0), _counting_opens(_ledgers(root)) as reads:
                self.assertEqual(len(decisions.list_decisions(root)), 2)
                self.assertEqual([r["status"] for r in decisions.list_decisions(root, "revisited")],
                                 ["revisited"])
        self.assertEqual(reads["decisions"], 1, reads)


if __name__ == "__main__":
    unittest.main()
