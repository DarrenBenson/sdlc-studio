"""US0889: the close forward-ports the skill where the repository ships the tool, and a re-run
close refreshes its own handover rather than filing another.

Driven through `sprint.main`, the shipped entry point, in throwaway project trees built by the
US0876 fixtures. The forward-port tool is a FAKE written into the temp repository: the real one
mirrors into `~/.claude`, which no test may touch.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402  (the US0876 fixtures, functions only)

#: A stand-in for `tools/forward-port.sh` honouring its contract: `--check` exits 1 naming a
#: count while a `drift` marker sits beside it, else 0; `--yes` clears the marker. Every call is
#: appended to `calls.log` so the test reads what the close asked for, in order.
_FAKE_TOOL = """#!/usr/bin/env bash
here="$(cd "$(dirname "$0")" && pwd)"
echo "$1" >> "$here/calls.log"
case "$1" in
  --check)
    if [[ -e "$here/drift" ]]; then
      echo "forward-port check: 2 file(s) differ between src and copy - run --yes to mirror"
      exit 1
    fi
    echo "forward-port check: in sync - copy matches src"; exit 0 ;;
  --yes)
    if [[ -e "$here/refuse" ]]; then echo "rsync: copy is read-only" >&2; exit 23; fi
    rm -f "$here/drift"; echo "forward-port applied -> copy"; exit 0 ;;
esac
exit 2
"""


def _tool(root: Path, *, drift: bool, refuse: bool = False) -> Path:
    tools = root / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    (tools / "forward-port.sh").write_text(_FAKE_TOOL, encoding="utf-8")
    for name, on in (("drift", drift), ("refuse", refuse)):
        if on:
            (tools / name).write_text("", encoding="utf-8")
    return tools


def _calls(tools: Path) -> list[str]:
    log = tools / "calls.log"
    return log.read_text(encoding="utf-8").split() if log.exists() else []


def _handovers(root: Path) -> list[str]:
    return sorted(p.name for p in (root / "sdlc-studio" / "handoffs").glob("HO*.md"))


class CloseHousekeepingTests(unittest.TestCase):

    def test_the_close_forward_ports_where_the_tool_exists(self) -> None:
        """Mutants: report the drift without applying it; apply without re-checking; refuse the
        close on a failed port; run the port over a copy the check found in sync (a pinned or
        absent copy answers in sync, and must never be written)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root)
            tools = _tool(root, drift=True)
            rc, out, err = lean._close(root)
            self.assertEqual(0, rc, err)
            # the pre-flight's check found the drift; the close applied it, then re-checked
            self.assertEqual(["--check", "--yes", "--check"], _calls(tools))
            self.assertIn("installed copy forward-ported - in sync", out)
            self.assertFalse(lean._read(root)["close_known_issues"])

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root)
            tools = _tool(root, drift=True, refuse=True)
            rc, _out, err = lean._close(root)
            self.assertEqual(0, rc, err)       # a failed port is a known issue, never a refusal
            self.assertEqual(["--check", "--yes"], _calls(tools))
            issues = [i for i in lean._read(root)["close_known_issues"]
                      if i["source"] == "installed-copy"]
            self.assertEqual(1, len(issues), issues)
            self.assertIn("--yes", issues[0]["detail"])
            self.assertIn("read-only", issues[0]["detail"])

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root)
            tools = _tool(root, drift=False)
            rc, out, err = lean._close(root)
            self.assertEqual(0, rc, err)
            self.assertEqual(["--check"], _calls(tools))       # in sync: nothing written
            self.assertNotIn("forward-ported", out)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean._fixture(root)                                 # a consuming project: no tool
            rc, out, err = lean._close(root)
            self.assertEqual(0, rc, err)
            self.assertFalse(lean._read(root)["close_known_issues"])
            self.assertNotIn("forward-port", out + err)

    def test_a_rerun_close_refreshes_its_own_handover(self) -> None:
        """Mutants: `generate` always mints through `meta_new`; the refresh keeps the stale body
        or the stale title; a new run reuses the previous run's handover."""
        # The close's tail re-renders the handover as well, so it is held still here: the body
        # this test reads is the one the handoff STEP wrote, or a stale-body mutant hides.
        tail = unittest.mock.patch.object(lean._live("sprint"), "_apply_signoff_tail",
                                          lambda *a, **k: 0)
        with tempfile.TemporaryDirectory() as d, tail:
            root = Path(d)
            lean._fixture(root)
            rc, _out, err = lean._close(root, real=("handoff",))
            self.assertEqual(0, rc, err)
            first = lean._read(root)["handoff"]
            self.assertTrue(first, "the first close filed no handover")
            [name] = _handovers(root)
            doc = root / "sdlc-studio" / "handoffs" / name
            doc.write_text(doc.read_text(encoding="utf-8").replace(
                "## Where to pick up", "## Where to pick up\n\nSTALE-SENTINEL"), encoding="utf-8")

            rc, _out, err = lean._close(root, real=("handoff",))
            self.assertEqual(0, rc, err)
            self.assertEqual([name], _handovers(root), "the re-run filed a second HO file")
            self.assertEqual(first, lean._read(root)["handoff"])
            text = doc.read_text(encoding="utf-8")
            self.assertNotIn("STALE-SENTINEL", text, "the handover was not refreshed")
            self.assertIn("RUN-LEAN0001", text)
            index = (root / "sdlc-studio" / "handoffs" / "_index.md").read_text(encoding="utf-8")
            self.assertEqual(1, index.count(name), index)

            # the verdict moved between closes, so the refreshed title follows it
            state_file = root / "sdlc-studio" / ".local" / "run-state.json"
            state = json.loads(state_file.read_text(encoding="utf-8"))
            state["sprint_goal_verdict"] = {"verdict": "partial", "note": "not all of it"}
            state_file.write_text(json.dumps(state), encoding="utf-8")
            rc, _out, err = lean._close(root, real=("handoff",))
            self.assertEqual(0, rc, err)
            [renamed] = _handovers(root)
            self.assertEqual(first, lean._read(root)["handoff"])
            h1 = (root / "sdlc-studio" / "handoffs" / renamed).read_text(
                encoding="utf-8").splitlines()[0]
            self.assertIn("RUN-LEAN0001 closed partial", h1)

            # a NEW run still gets a new handover
            lean._state(root, run_id="RUN-LEAN0002")
            rc, _out, err = lean._close(root, real=("handoff",))
            self.assertEqual(0, rc, err)
            self.assertEqual(2, len(_handovers(root)))
            self.assertNotEqual(first, lean._read(root)["handoff"])

    def test_only_the_open_runs_own_handover_is_refreshed(self) -> None:
        """Mutants: `_open_handoff` refreshes a handover the state names although the run has
        ended (a sealed run's handover is a record), or although the document records a
        different run."""
        tail = unittest.mock.patch.object(lean._live("sprint"), "_apply_signoff_tail",
                                          lambda *a, **k: 0)
        for label, over in (("sealed", {"outcome": "goal-reached"}),
                            ("another run's", {"run_id": "RUN-LEAN0002"})):
            with self.subTest(label), tempfile.TemporaryDirectory() as d, tail:
                root = Path(d)
                lean._fixture(root)
                rc, _out, err = lean._close(root, real=("handoff",))
                self.assertEqual(0, rc, err)
                first = lean._read(root)["handoff"]
                [name] = _handovers(root)
                before = (root / "sdlc-studio" / "handoffs" / name).read_text(encoding="utf-8")
                lean._state(root, handoff=first, **over)
                res = lean._live("handoff").generate(root, "next")
                self.assertNotEqual(first, res["id"], f"{label} handover was reused")
                self.assertEqual(2, len(_handovers(root)))
                self.assertEqual(before, (root / "sdlc-studio" / "handoffs" / name).read_text(
                    encoding="utf-8"), f"{label} handover was rewritten")


if __name__ == "__main__":
    unittest.main()
