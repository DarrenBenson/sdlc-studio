"""Doc-claim invariants for doctrine a driving agent is expected to APPLY.

Every claim locked here was paid for by an incident, and each one is doctrine rather
than code: nothing executes it, so nothing but a test stops it being deleted, softened,
or left behind when the code beside it moves.

Among the incidents covered:

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

**The Fixed gate's public account.** The evaluation page said a bug reaches Fixed only when
its criteria pass. Of a bug's criteria, the gate in `transition.py` asks only that something
speak for the fix (a criterion ticked or one carrying a `Verify:` line) and that no recorded run
of them be red, so a `Verify:` line that was never run, or that names a file that does not
exist, lets a bug through. The page is held to what the gate enforces, and the bug record
that stood at Fixed on such a line is held to a test that exists and a recorded run of it.
"""
# test-selection: sweep 0.6s
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
SPRINT = SKILL / "scripts" / "sprint.py"
SPRINT_REF = SKILL / "reference-sprint.md"
STORY_TEMPLATE = SKILL / "templates" / "core" / "story.md"
WHY_PAGE = REPO / "docs" / "why-sdlc-studio.md"
BUGS = REPO / "sdlc-studio" / "bugs"


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


class CallerNamedTests(unittest.TestCase):
    """US0512: the story template asks for the consuming caller where the criterion is written.

    A lesson the author has to recall is a lesson the author skips: four mechanisms shipped
    reaching nothing in one sprint, each with green tests. The prompt has to arrive at the point
    the criterion is typed, and the field it asks for has to be the field the checker reads -
    a template and a checker disagreeing by one word is a field that looks answered and is never
    checked.
    """

    def test_the_template_asks_for_the_caller(self) -> None:
        mod = _load(CRITIC, "critic_docclaims")
        template = STORY_TEMPLATE.read_text(encoding="utf-8")
        field = mod.CALLER_FIELD
        # DERIVED from the template's own AC blocks: an AC4 added later without the field
        # fails here, rather than being silently exempt from a list written today
        blocks = re.split(r"^### AC(\d+)", template, flags=re.M)[1:]
        ac_ids = blocks[0::2]
        bodies = blocks[1::2]
        self.assertTrue(ac_ids, "the template has no AC blocks to check")
        for ac, body in zip(ac_ids, bodies):
            self.assertRegex(body, rf"(?m)^- \*\*{field}:\*\*",
                             f"AC{ac} in the story template never asks for the {field} field")
        # the field the template writes is the field the checker reads, proven by running the
        # checker's own parser over the shipped template rather than by reading both
        declared = {d["ac"] for d in mod.caller_declarations(template)}
        self.assertEqual(declared, {f"AC{ac}" for ac in ac_ids},
                         "the caller check does not read the field the template asks for")
        body = _norm(template)
        # the reason travels with the prompt: a field whose point is unstated gets a placeholder
        self.assertRegex(body, r"(?i)mechanism[^.]*(nothing calls|calls nothing|reaches no)",
                         "the template must say WHY the consumer is asked for")
        # and how to check it, so the author is not left to run the review in their head
        self.assertIn("caller-check", body,
                      "the template must name the command that checks the field")


class LaneObligationDocsTests(unittest.TestCase):
    """US0511: what a delivery lane is held to is carried by the dispatch, and stated where
    somebody building their own harness will meet it.

    The shipped dispatch already attaches the obligations to every brief, so a lane run through
    this project's own tooling inherits them. A project writing its own dispatch reads the
    reference instead, and an obligation that lives only in code is one such a project
    rediscovers by repeating the incident that bought it.
    """

    def test_the_obligations_are_documented(self) -> None:
        mod = _load(SPRINT, "sprint_docclaims")
        obligations = list(mod.LANE_OBLIGATIONS)
        self.assertTrue(obligations,
                        "an empty obligation set would make every assertion below vacuous")
        body = _section(PROMPT, "lane-obligations")
        for text in obligations:
            self.assertIn(_norm(text), body,
                          "the reference must carry the SHIPPED obligation text, so the doc and "
                          f"the dispatch cannot drift apart: {text!r}")
        # why the section exists: they travel with the dispatch rather than with whoever wrote
        # that sprint's prompt - the claim the whole arrangement rests on
        self.assertRegex(body, r"(?i)dispatch",
                         "the reference must say the obligations ride the dispatch")
        self.assertRegex(body, r"(?i)who(?:ever|m)?\s+(?:wrote|writes)",
                         "the reference must say they do not depend on who wrote the brief")
        # one home per rule: the sprint reference points here rather than restating them
        self.assertIn("reference-agent-prompt-template.md#lane-obligations", _doc(SPRINT_REF),
                      "reference-sprint.md must point at the obligations, not restate them")


#: The over-claim: a sentence saying a bug reaches Fixed only when its criteria pass. A story
#: named between Fixed and the condition makes the condition the story's.
_BUG_PASS_CLAIM = re.compile(r"\bFixed\b(?:(?!\bstor(?:y|ies)\b)[^.;])*?\bonly (?:when|if)\b"
                             r"[^.;]*?\bcriteria\b[^.;]*?\bpass")
#: What the account of the closing gates says instead, each in a paragraph that names Fixed.
_GATE_CLAIMS = {
    "a story reaches Done only when its executable criteria have passed": re.compile(
        r"\ba story reaches Done only when its executable criteria have passed\b"),
    "a bug is refused Fixed when nothing speaks for the fix": re.compile(
        r"\ba bug is refused Fixed when nothing speaks for the fix\b"),
    "or when a recorded run of its criteria is red": re.compile(
        r"\bor when a recorded run of its criteria is red\b"),
}
#: The statuses at which a bug record claims its fix.
_BUG_FIX_CLAIMED = {"Fixed", "Verified", "Closed"}


def fixed_gate_problems(text: str) -> list[str]:
    """Each sentence of a page saying a bug reaches Fixed only when its criteria pass, which
    `transition.py` does not enforce, and each true claim its account of the closing gates
    leaves out of every paragraph that names Fixed."""
    paragraphs = [_norm(p) for p in re.split(r"\n\s*\n", text)]
    problems = [f"claims a bug's criteria must pass: {m.group(0)[:70]}"
                for p in paragraphs for m in _BUG_PASS_CLAIM.finditer(p)]
    gate = [p for p in paragraphs if re.search(r"\bFixed\b", p)]
    problems += [f"the closing gates do not say {name!r}" for name, pattern in _GATE_CLAIMS.items()
                 if not any(pattern.search(p) for p in gate)]
    return problems


def bug_record_problems(text: str, repo: Path = REPO) -> list[str]:
    """Why a bug record is not spoken for by what it names. At a status claiming the fix: no
    criteria at all, a criterion with no `pytest` Verify line, a Verify line naming a file, class
    or function that does not exist, or a criterion with no `**Verified:** yes` marker from a
    recorded run. At any other status: no Revision History row that mentions a reopening."""
    m = re.search(r"^> \*\*Status:\*\* (\S+)", text, re.M)
    status = m.group(1) if m else ""
    if status not in _BUG_FIX_CLAIMED:
        history = text.partition("## Revision History")[2]
        if re.search(r"(?im)^\|.*\breopen", history):
            return []
        return [f"stands at {status or 'no status'} with no Revision History row saying why "
                f"it was reopened"]
    m = re.search(r"^## Acceptance Criteria\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    blocks = re.split(r"(?m)^- \[[ xX]\] ", m.group(1) if m else "")[1:]
    if not blocks:
        return ["claims its fix with no acceptance criteria"]
    problems = []
    for block in blocks:
        ac = block.split()[0].strip("*")
        selectors = re.findall(r"\*\*Verify:\*\* pytest (\S+)", block)
        if not selectors:
            problems.append(f"{ac} carries no pytest Verify line")
        for selector in selectors:
            path, _, names = selector.partition("::")
            if not (repo / path).is_file():
                problems.append(f"{ac} names {path}, which does not exist")
                continue
            source = (repo / path).read_text(encoding="utf-8")
            problems += [f"{ac} names {name}, which {path} does not define"
                         for name in names.split("::") if not re.search(
                             rf"^\s*(?:class|def) {re.escape(name)}\b", source, re.M)]
        if not re.search(r"\*\*Verified:\*\* yes\b", block):
            problems.append(f"{ac} records no passing run")
    return problems


class FixedGateClaimTests(unittest.TestCase):
    """The public account of the Fixed gate, and the record it let through, say what is true."""

    def test_the_why_page_claims_only_what_the_fixed_gate_enforces(self) -> None:
        self.assertEqual(fixed_gate_problems(WHY_PAGE.read_text(encoding="utf-8")), [])
        # Planted failures beside a positive control.
        good = ("Closing gates for Done and Fixed (a story reaches Done only when its executable "
                "criteria have passed; a bug is refused Fixed when nothing speaks for the fix, "
                "or when a recorded run of its criteria is red).")
        self.assertEqual(fixed_gate_problems(good), [])
        for over in ("a story reaches Done, and a bug Fixed, only when its criteria pass",
                     "A bug reaches Fixed only when its criteria pass.",
                     "A story reaches Done or Fixed only if its acceptance criteria passed."):
            with self.subTest(over=over):
                found = fixed_gate_problems(good + "\n\n" + over)
                self.assertEqual(len(found), 1, found)
                self.assertTrue(found[0].startswith("claims a bug's criteria must pass"), found)
        # A sentence or clause break, or a story named before the condition, takes it off Fixed.
        for story in ("A bug is Fixed. A story reaches Done only when its criteria pass.",
                      "A bug can be Fixed; Done comes only when its criteria pass.",
                      "Done and Fixed: stories reach Done only when their criteria pass."):
            with self.subTest(story=story):
                self.assertEqual(fixed_gate_problems(good + "\n\n" + story), [])
        for name in _GATE_CLAIMS:
            with self.subTest(dropped=name):
                cut = good.replace(name.removeprefix("or when "), "something else")
                self.assertEqual(fixed_gate_problems(cut),
                                 [f"the closing gates do not say {name!r}"])
        # Said only in a paragraph that does not name the Fixed gate, a claim does not count.
        story = "a story reaches Done only when its executable criteria have passed"
        self.assertEqual(fixed_gate_problems(f"Here {story}.\n\n" + good.replace(story, "x")),
                         [f"the closing gates do not say {story!r}"])

    def test_bg1039_names_tests_that_exist_and_records_their_run(self) -> None:
        record = next(BUGS.glob("BG1039-*.md"))
        self.assertEqual(bug_record_problems(record.read_text(encoding="utf-8")), [])
        # Planted failures beside a positive control.
        test = "tools/tests/test_prereq_list_is_ci_list.py::OneListTests"
        good = ("> **Status:** Fixed\n\n## Acceptance Criteria\n\n"
                f"- [ ] **AC1** Given a\n  - **Verify:** pytest {test}"
                "::test_the_corpus_verify_job_installs_a_declared_subset\n"
                "  - **Verified:** yes (2026-11-23)\n\n## Revision History\n\n| a | b | Filed |\n")
        self.assertEqual(bug_record_problems(good), [])
        stood = good.replace("test_prereq_list_is_ci_list.py", "test_prereq_list_is_ci_list_strict"
                             ".py").replace("  - **Verified:** yes (2026-11-23)\n", "")
        self.assertEqual(bug_record_problems(stood), [
            "AC1 names tools/tests/test_prereq_list_is_ci_list_strict.py, which does not exist",
            "AC1 records no passing run"])
        self.assertEqual(bug_record_problems(good.replace("installs_a", "installs_no")),
                         ["AC1 names test_the_corpus_verify_job_installs_no_declared_subset, "
                          "which tools/tests/test_prereq_list_is_ci_list.py does not define"])
        for missing in ("NoSuchTests", "OneListTest"):
            with self.subTest(missing=missing):
                self.assertEqual(bug_record_problems(good.replace("OneListTests", missing)),
                                 [f"AC1 names {missing}, which "
                                  "tools/tests/test_prereq_list_is_ci_list.py does not define"])
        self.assertEqual(bug_record_problems(good.replace(f" {test}::test_the_corpus_verify_job"
                                                          "_installs_a_declared_subset",
                                                          f" {test.partition('::')[0]}")), [])
        # A marker outside the criteria is not a recorded run of them.
        unrun = good.replace("  - **Verified:** yes (2026-11-23)\n", "")
        self.assertEqual(bug_record_problems(unrun + "\n## Notes\n\n- **Verified:** yes (x)\n"),
                         ["AC1 records no passing run"])
        self.assertEqual(bug_record_problems(good.replace("> **Status:** Fixed\n", "")), [
            "stands at no status with no Revision History row saying why it was reopened"])
        self.assertEqual(bug_record_problems(good.replace("**Verified:** yes", "**Verified:** no")),
                         ["AC1 records no passing run"])
        self.assertEqual(bug_record_problems(good.replace("**Verify:** pytest", "**Verify:** see")),
                         ["AC1 carries no pytest Verify line"])
        for claimed in ("Verified", "Closed"):
            with self.subTest(status=claimed):
                self.assertEqual(bug_record_problems(good.replace("Fixed", claimed).replace(
                    "- [ ] **AC1**", "- [x] **AC1**")), [])
                self.assertEqual(bug_record_problems(stood.replace("Fixed", claimed)),
                                 bug_record_problems(stood))
        self.assertEqual(bug_record_problems(good.split("## Acceptance")[0]),
                         ["claims its fix with no acceptance criteria"])
        reopened = good.replace("**Status:** Fixed", "**Status:** Open")
        self.assertEqual(bug_record_problems(reopened), [
            "stands at Open with no Revision History row saying why it was reopened"])
        self.assertEqual(bug_record_problems(reopened.replace(
            "| Filed |", "| Reopened: the test it names never existed |")), [])


if __name__ == "__main__":
    unittest.main()
