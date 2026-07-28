"""Doc-claim invariants for doctrine a driving agent is expected to APPLY.

Every claim locked here was paid for by an incident, and each one is doctrine rather
than code: nothing executes it, so nothing but a test stops it being deleted, softened,
or left behind when the code beside it moves.

Two classes are covered.

**The silent stall (US0502/US0503).** Two delegated review agents stopped without
returning and without erroring, at 841KB and 405KB of transcript, costing about 35
minutes each while the driver read the silence as work in progress. The doctrine must
name the mode, state that an absent result is never a pending one, and give a detection
rule a driver can actually run - transcript growth plus a result marker, not the clock.
It is the same class as the audit reference's dead-vote quorum rule one layer down, so
the two must point at each other or a reader meets only half of it.

**Mutating the author's tree (US0504/US0505).** A delegated reviewer mutation-tested by
editing the live working tree and silently reverted a shipped repair; the suite stayed
green over the reverted code. The doctrine must say where a reviewer mutates, and the
author-side rule that follows must be the one the tool actually enforces - so the code
is read here too, not just the prose that describes it.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
LESSONS = SKILL / "reference-agentic-lessons.md"
AUDIT = SKILL / "reference-audit.md"
PROMPT = SKILL / "reference-agent-prompt-template.md"
REVIEW = SKILL / "reference-review.md"
MUTATION = SKILL / "scripts" / "mutation.py"
CRITIC = SKILL / "scripts" / "critic.py"


def _norm(text: str) -> str:
    """Collapse whitespace so a claim wrapped across doc lines still matches."""
    return " ".join(text.split())


def _doc(path: Path) -> str:
    return _norm(path.read_text(encoding="utf-8"))


def _section(path: Path, anchor: str) -> str:
    """The body of the heading carrying `{#anchor}`, up to the next heading of the same
    or a shallower depth. Raises when the anchor is absent, so a moved anchor is a test
    failure rather than a silently empty search space."""
    text = path.read_text(encoding="utf-8")
    m = re.search(rf"^(#+) .*\{{#{re.escape(anchor)}\}}\s*$", text, re.M)
    if not m:
        raise AssertionError(f"{path.name} has no heading anchored {{#{anchor}}}")
    depth = len(m.group(1))
    rest = text[m.end():]
    nxt = re.search(rf"^#{{1,{depth}}} ", rest, re.M)
    return _norm(rest[: nxt.start()] if nxt else rest)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class StallDoctrineTests(unittest.TestCase):
    """US0502/US0503: the silent stall is named, detectable, and reported as unfinished."""

    def test_the_stall_mode_and_detection_are_documented(self) -> None:
        body = _section(LESSONS, "silent-stall")
        # 1. the mode: a delegate can stop without erroring
        self.assertRegex(body, r"(?i)stop[s]?\b[^.]*without[^.]*error",
                         "the doctrine must say a delegate can stop WITHOUT erroring")
        # 2. an absent result is never read as pending
        self.assertRegex(body, r"(?i)absent result is not a pending result",
                         "the doctrine must state that an absent result is not a pending one")
        # 3. how a driver tells one from the other, with signals it can actually read
        for signal in ("size", "mtime", "result marker"):
            self.assertIn(signal, body.lower(),
                          f"the detection rule must name the {signal} signal")
        self.assertRegex(body, r"(?i)stalled", "the detection rule must name the stalled verdict")
        self.assertRegex(body, r"(?i)running", "the detection rule must name the running verdict")
        # 4. and rule OUT the detector that does not work - elapsed time alone
        self.assertRegex(body, r"(?i)(elapsed time|the clock)[^.]*(alone|not the detector)",
                         "the doctrine must say elapsed time alone does not distinguish them")
        # the evidence that bought it, so a later editor cannot read it as speculation
        self.assertIn("841KB", body)
        self.assertIn("405KB", body)

    def test_an_unfinished_delegate_is_reported_as_unfinished(self) -> None:
        body = _section(PROMPT, "unfinished-delegate")
        self.assertRegex(body, r"(?i)returns no result is \*\*unfinished\*\*",
                         "a delegate returning no result must be called unfinished")
        self.assertRegex(body, r"(?i)report[^.]*names it",
                         "the report must NAME the unfinished delegate, not just count it")
        self.assertRegex(body, r"(?i)never (be )?folded into a pending count",
                         "an unfinished delegate must never be folded into a pending count")
        self.assertRegex(body, r"(?i)pending count says[^.]*may still come",
                         "the reason must be stated: pending implies an answer may still arrive")
        # the detection rule is not restated here, it is pointed at - one home per rule
        self.assertIn("reference-agentic-lessons.md#silent-stall", body)

    def test_the_quorum_rule_cross_references_the_stall_rule(self) -> None:
        quorum = _section(AUDIT, "audit-refute-quorum")
        self.assertIn("reference-agentic-lessons.md#silent-stall", quorum,
                      "the dead-vote quorum rule must point at the stall rule")
        self.assertRegex(quorum, r"(?i)dead agent",
                         "the quorum rule must name the agent-level half of its own class")
        # and back the other way, so a reader arriving at either half reaches the other
        stall = _section(LESSONS, "silent-stall")
        self.assertIn("reference-audit.md#audit-refute-quorum", stall,
                      "the stall rule must point back at the dead-vote quorum rule")
        # both anchors resolve
        self.assertTrue(_section(AUDIT, "audit-refute-quorum"))
        self.assertTrue(_section(LESSONS, "silent-stall"))


class MutationIsolationTests(unittest.TestCase):
    """US0504: where a delegated reviewer mutates, and the author-side rule that follows."""

    def test_the_isolation_rule_is_documented(self) -> None:
        body = _section(REVIEW, "mutation-isolation")
        self.assertRegex(body, r"(?i)isolated checkout",
                         "the doctrine must say a delegated reviewer mutates an isolated checkout")
        self.assertRegex(body, r"(?i)never the author'?s (working )?tree",
                         "the doctrine must forbid mutating the author's tree")
        self.assertRegex(body, r"(?i)silently reverted",
                         "the incident that bought the rule must be stated, not implied")
        # the author-side rule that follows, named as the tool that enforces it
        self.assertRegex(body, r"(?i)mutation\.py[^.]*refus",
                         "the author-side rule must name mutation.py refusing")
        self.assertRegex(body, r"(?i)uncommitted changes",
                         "the author-side rule must say WHICH files are refused")
        # and the prose is checked against the code, so the doc cannot claim a guard
        # the tool does not have (the failure mode this whole file exists for)
        mut = _load(MUTATION, "mutation_docclaims")
        self.assertTrue(hasattr(mut, "dirty_targets"),
                        "reference-review.md claims mutation.py refuses uncommitted targets, "
                        "so mutation.py must expose the check that does it")


class RepairCoverageTests(unittest.TestCase):
    """US0505: a behaviour-changing repair carries a test asserting that behaviour, and a
    repair with none is reported as a finding rather than trusted."""

    def _brief(self, mod, root: Path) -> str:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / "US0001-x.md").write_text(
            "# US0001: the thing\n\n> **Status:** In Progress\n"
            "> **Affects:** src/a.py\n> **Points:** 3\n\n"
            "## Acceptance Criteria\n\n### AC1: works\n\n- **Given** x\n- **When** y\n"
            "- **Then** z\n- **Verify:** shell true\n", encoding="utf-8")
        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True, exist_ok=True)
        (seats / "qa.md").write_text("# Sam - QA seat\n\ncharter text\n", encoding="utf-8")
        return mod.brief(root, "US0001", "qa")

    def test_an_unpinned_repair_is_reported(self) -> None:
        mod = _load(CRITIC, "critic_docclaims")
        names = [n for n, _i, _r in mod._BRIEF_PRACTICES]
        self.assertIn("regression cover for a repair", names,
                      "the standing practices must carry the repair-cover practice")
        with tempfile.TemporaryDirectory() as d:
            text = self._brief(mod, Path(d))
            body = _norm(text)
            # the shipped brief instructs it, with its reason
            self.assertEqual(mod.missing_practices(text), [], body)
            self.assertRegex(body, r"(?i)changes behaviour carries a test",
                             "the brief must demand a test asserting the changed behaviour")
            self.assertRegex(body, r"(?i)report[^.]*as a finding",
                             "a repair with no cover must be REPORTED, not merely noted")
            self.assertRegex(body, r"(?i)revert[^.]*suite still green|still green[^.]*revert",
                             "the reason must be stated: an unpinned repair reverts green")
            # removing the instruction makes the guard name it and refuse - so the
            # practice is load-bearing rather than decorative prose
            instruction = dict((n, i) for n, i, _r in mod._BRIEF_PRACTICES)[
                "regression cover for a repair"]
            gutted = re.sub(instruction, "REDACTED", body, flags=re.I)
            self.assertIn("regression cover for a repair", mod.missing_practices(gutted))
            with self.assertRaises(ValueError):
                mod.assert_brief_practices(gutted)
        # and the shipped doc states the same practice, so brief and doctrine agree
        doc = _doc(REVIEW)
        self.assertRegex(doc, r"(?i)regression cover",
                         "reference-review.md must document the repair-cover practice")


if __name__ == "__main__":
    unittest.main()
