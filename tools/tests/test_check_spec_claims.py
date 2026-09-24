"""Guards over what the repo's own documents claim: the AGENTS.md lane roster, SKILL.md's
sections, and the doctrine's repair-evidence rule.

The module is named for `tools/check_spec_claims.py`, which US0879 deleted with its commit lane:
it checked the specs' countable and timing claims against a census, caught nothing, and its
timing claims deadlocked every fresh worktree (BG0746). The tests of the checker itself went
with it, and the criteria that named them are retired.
"""
# test-census-subject: AGENTS.md
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class GateLaneTests(unittest.TestCase):
    """The AGENTS.md roster rows for the lanes the hook-derived sweep cannot see: the boundary
    lanes, and the gate lanes whose blocking status is the thing a reader needs. The per-commit
    roster itself is pinned in both directions by `test_lean_commit_lanes.py`."""

    def test_the_lane_roster_names_the_revert_check_and_calls_it_advisory(self) -> None:
        """US0674. The second boundary-bound lane, and the same argument as the rehearsal above:
        the hook-derived sweep reads the pre-commit hook, so a lane that deliberately does not
        run per commit is invisible to it (LL0013).

        Its BLOCKING STATUS is pinned as well as its name, which the rehearsal's row does not
        need. This one ships advisory while its yield is measured, and a roster that named the
        lane without saying so would leave nobody able to check whether it had quietly started
        blocking - or quietly stopped."""
        repo = Path(__file__).resolve().parents[2]
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("revert-check", agents,
                      "AGENTS.md's roster does not name the revert-check lane")
        # Bounded by DISTANCE rather than by "up to the next full stop": the row names
        # `gate.py --boundary`, so a sentence-terminator rule stops at the dot in the filename
        # and the word it is looking for is always just past it.
        self.assertRegex(agents, r"(?s)revert-check.{0,120}boundar",
                         "the roster does not say the lane binds at a boundary rather than per "
                         "commit")
        # Read the lane's OWN paragraph, not a window around its name. A 900-character window
        # reached the `claim-drift` row, which also says ADVISORY, so the assertion passed with
        # the word deleted from this lane's row - a guard satisfied by a neighbouring sentence.
        para = next((b for b in agents.split("\n\n") if "revert-check" in b), "")
        self.assertTrue(para, "no paragraph in AGENTS.md mentions revert-check")
        self.assertIn("ADVISORY", para,
                      "the roster names the lane but not that it is ADVISORY - a reader cannot "
                      "tell whether it blocks, which is the one thing they need to know")
        gate = (repo / ".claude" / "skills" / "sdlc-studio" / "scripts"
                / "gate.py").read_text(encoding="utf-8")
        self.assertIn('"revert-check"', gate,
                      "AGENTS.md names a lane the gate does not register")
        self.assertIn('"derived-depth"', gate,
                      "AGENTS.md's gate block names derived-depth and the gate does not "
                      "register it")
        self.assertIn("derived-depth", agents,
                      "the gate blocks on derived-depth and the roster does not name it")
        # TIE THE WORD TO THE FLAG. Everything above pins the roster's PROSE and the lane's
        # NAME, and an independent review pointed out that neither reaches the lane's actual
        # `blocking` value: flip the lane to blocking and the roster's "ADVISORY" becomes a
        # lie with this test still green. So the flag itself is read here, on both of the
        # lane's return paths - the one that found nothing and the one that found something -
        # because a lane that is advisory only while it is silent is not an advisory lane.
        import sys as _sys  # noqa: PLC0415 - local: only this assertion loads the gate
        scripts = repo / ".claude" / "skills" / "sdlc-studio" / "scripts"
        if str(scripts) not in _sys.path:
            _sys.path.insert(0, str(scripts))
        import gate as gate_mod  # noqa: PLC0415
        from unittest import mock as _mock  # noqa: PLC0415
        for found, label in ((0, "found nothing"), (2, "found two units")):
            with self.subTest(path=label):
                import verify_ac as _va  # noqa: PLC0415 - the lane imports both deferred
                from lib import run_state as _rs  # noqa: PLC0415
                with _mock.patch.object(gate_mod, "_record_revert_yield"), \
                        _mock.patch.object(_rs, "base_ref", return_value="deadbeef"), \
                        _mock.patch.object(_rs, "read", return_value={
                            "batch": [f"US{9000 + i}" for i in range(2)]}), \
                        _mock.patch.object(_va, "revert_check", return_value={
                            "status": "refused" if found else "pass", "green": ["AC1"]}):
                    res = gate_mod._revert_check(str(repo))
                self.assertIs(False, res["blocking"],
                              f"the lane returned blocking=True when it {label}, while "
                              f"AGENTS.md's roster calls it ADVISORY")

    def test_the_lane_roster_names_evidence_drift_and_its_blocking_status(self) -> None:
        """BG0651. The lane that refuses a commit drifting a delivered unit's mutation evidence
        is named in the roster with its status, the way the revert-check row is. MUTANT: leave
        the roster without the lane."""
        repo = Path(__file__).resolve().parents[2]
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("evidence-drift", agents, "AGENTS.md's roster does not name the evidence-drift lane")
        para = next((b for b in agents.split("\n\n") if "`evidence-drift`" in b), "")
        self.assertTrue(para, "no paragraph in AGENTS.md names `evidence-drift`")
        self.assertIn("BLOCKING", para, "the roster names the lane but not that it BLOCKS")
        self.assertIn("mutation", para.lower(), "the roster does not say what the lane guards")

    def test_the_lane_roster_names_module_alone_as_boundary_bound(self) -> None:
        """BG0649. A third boundary-bound lane, invisible to the hook-derived sweep for the same
        reason as the two above (LL0013). MUTANTS: leave the roster without the lane; name it
        without saying it binds at the boundaries only."""
        repo = Path(__file__).resolve().parents[2]
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("module-alone", agents, "AGENTS.md's roster does not name the module-alone lane")
        para = next((b for b in agents.split("\n\n") if "`module-alone`" in b), "")
        self.assertTrue(para, "no paragraph in AGENTS.md names `module-alone`")
        # US0881 moved the lane to the tag: a push pays the full suite once instead
        self.assertIn("release boundary only", para,
                      "the roster does not say the lane binds at the release boundary and nowhere else")
        self.assertIn("never per push", para, "the roster does not say the lane is off the push path")
        # the COST, not only the decision it is stated beside: a false figure shipped once
        # because this pin read "D0180" alone, and deleting the whole cost sentence passed it
        # the figure is stated IN MINUTES immediately, so a false "about 45 s" cannot borrow
        # the word from a later clause of the same sentence
        self.assertRegex(para, r"(?s)Its cost is the lane's wall clock, (?:\w+ to \w+|about \w+)\s+minutes.{0,200}D0180",
                         "the roster does not state the lane's wall-clock cost in minutes beside D0180's")
        self.assertIn("test_gate", para, "the roster does not name the slowest module the cost is made of")
        gate = (repo / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py").read_text(encoding="utf-8")
        self.assertIn('"module-alone"', gate, "AGENTS.md names a lane the gate does not register")

    def test_the_lane_roster_names_the_release_rehearsal(self) -> None:
        """US0666: a lane bound at a BOUNDARY is invisible to the hook-derived sweep above, which
        reads the pre-commit hook - so the one lane that deliberately does not run per commit is
        the one that roster cannot see. It is pinned here by name, with the boundary it binds at,
        because a lane nobody has written down is one nobody notices losing (LL0013)."""
        repo = Path(__file__).resolve().parents[2]
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("release-rehearsal", agents,
                      "AGENTS.md's roster does not name the release-rehearsal lane")
        self.assertIn("rehearse-release.sh", agents,
                      "the roster names the lane but not the harness it runs")
        self.assertRegex(agents, r"release-rehearsal[^.]*boundar",
                         "the roster does not say the lane binds at a boundary rather than per "
                         "commit, which is the only thing a reader needs to know about it")
        gate = (repo / ".claude" / "skills" / "sdlc-studio" / "scripts"
                / "gate.py").read_text(encoding="utf-8")
        self.assertIn('"release-rehearsal"', gate,
                      "AGENTS.md names a lane the gate does not register")


class LintAggregateTests(unittest.TestCase):
    """US0655 AC2: the `lint` CHAIN calls `lint:disclosure`, which it did not."""

    def test_the_lint_chain_calls_disclosure(self) -> None:
        """`lint:disclosure` has existed as a script KEY all along; only the aggregate omitted
        it, so a checker with 28 advisory findings was one line from being read and was not.
        Asserting the key exists is green today with nothing changed, which is a criterion that
        cannot fail.

        Mutant: leave `lint:disclosure` defined as a key but absent from the `lint` chain.
        """
        import json
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertIn("lint:disclosure", pkg, "the disclosure lane is not defined at all")
        self.assertIn("lint:disclosure", pkg["lint"],
                      "the `lint` chain does not call `lint:disclosure`, so the checker runs "
                      "nowhere and reports nothing however good it is")




class SkillSectionTests(unittest.TestCase):
    """US0659 AC1/AC2: SKILL.md carries the sections its own checklist requires."""

    def test_skill_md_carries_the_sections_its_own_checklist_requires(self) -> None:
        """`best-practices/claude-skill.md` requires a "See Also" section and gives a single
        vague sentence as its BAD trigger example - labelled "Too vague, no trigger keywords",
        so the fault it names is VAGUENESS. The assertion is on trigger phrases being present,
        which is the rule, rather than on the shape of a list, which is a proxy that would
        outlive the reason for it.

        Mutant: remove the `## See Also` section.
        Mutant: revert `When to Use` to a single vague sentence with no trigger phrases.
        """
        skill = (ROOT / ".claude/skills/sdlc-studio/SKILL.md").read_text(encoding="utf-8")
        checklist = (ROOT / ".claude/skills/sdlc-studio/best-practices/claude-skill.md"
                     ).read_text(encoding="utf-8")
        self.assertIn("See Also", checklist, "the checklist no longer requires this section")
        self.assertIn("## See Also", skill,
                      "SKILL.md fails the checklist it ships - the cheapest possible finding "
                      "and the most embarrassing to leave")
        when = skill[skill.index("## When to Use"):]
        when = when[:when.index("\n## ", 5)]
        phrases = [ln for ln in when.splitlines() if ln.strip().startswith("- ")]
        self.assertGreaterEqual(len(phrases), 5,
                                "`When to Use` names no trigger phrases, which is the shape "
                                "the skill's own guidance gives as its bad example")

    def test_the_four_top_level_documents_are_in_the_loading_guide(self) -> None:
        """The doctrine calls the PRD, TRD, TSD and story the top-level human levers, and an
        agent following the Progressive Loading Guide was told about none of them.

        Mutant: drop one of the four rows.
        """
        skill = (ROOT / ".claude/skills/sdlc-studio/SKILL.md").read_text(encoding="utf-8")
        guide = skill[skill.index("## Progressive Loading Guide"):]
        guide = guide[:guide.index("\n## ", 5)]
        for ref in ("reference-prd.md", "reference-trd.md", "reference-tsd.md",
                    "reference-story.md"):
            with self.subTest(reference=ref):
                self.assertIn(ref, guide,
                              f"{ref} is a top-level document the loading guide never names")


# --- US0567: the doctrine's repair-evidence rule -------------------------------------------
# Lifted here rather than shipped as its own file: `tools/tests/test_doctrine_repair_evidence.py`
# could never be attributed by the test census, whose sibling-module rule only sees `tools/*.py`,
# and the census baseline is explicit that it is lowered when a file gains a home and NEVER
# raised to accommodate a new one. A guard that a shipped document's claim is true is a
# spec-claim check, so this is where it belongs.

DOCTRINE = ROOT / ".claude/skills/sdlc-studio/reference-doctrine.md"
DOD = ROOT / ".claude/skills/sdlc-studio/templates/core/definition-of-done.md"
LESSONS = ROOT / ".claude/skills/sdlc-studio/reference-agentic-lessons.md"


def _states_the_rule(text: str) -> bool:
    """Does THIS text state rule 21 and name its enforcing mechanism?

    Takes the text rather than reading the file, so the discrimination below can put a
    doctored corpus through the identical predicate. Asserting a length comparison instead
    proved too weak: a mutant that pointed the rule test at the whole file survived it,
    because the length check computed its own slice and never saw the sibling stop
    discriminating. The property has to be exercised, not inferred.
    """
    passage = _slice_rule(text)
    if not passage:
        return False
    low = passage.lower()
    return "author" in low and "mutant" in low and "transition.py" in passage


def _slice_rule(text: str) -> str:
    """Rule 21's own text, from its numbered heading to the next top-level heading or rule.

    Sliced rather than searched, so the assertions below cannot be satisfied by any other
    part of the file - a Revision History row included.
    """
    m = re.search(r"^21\. \*\*(.+?)\*\*.*?$", text, re.M)
    if not m:
        return ""
    rest = text[m.start():]
    end = re.search(r"^(?:## |\d+\. \*\*)", rest[len(m.group(0)):], re.M)
    return rest[: len(m.group(0)) + end.start()] if end else rest


def _defined_functions(source: str) -> set:
    """Every function `source` DEFINES, by AST."""
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    return {n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _doctrine_lane_names(doctrine: str, source: str) -> set:
    """The mechanisms rule 21 NAMES that `source` actually DEFINES.

    Two independent sources, and neither is the property under test. The doctrine supplies the
    claim; the module supplies which of the backticked tokens in it are functions rather than
    mode values (`report`, `block`, `off`), config keys or filenames. What the guard then asks
    is whether each is REACHED - and defining a function and reaching it are different
    properties, which is the entire content of BG0541: `repair_mutation_gate` was defined,
    tested and called by nothing while the doctrine said it refused.

    So this is not the circularity round 2 rejected. That was a set derived from the predicate's
    own reachability walk, which narrows exactly when the predicate narrows. This one does not
    move when the ladder changes; it moves only when the doctrine stops naming a mechanism or
    the module stops defining one, and the cardinality floor beside it catches both.
    """
    passage = _slice_rule(doctrine)
    named = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", passage))
    return named & _defined_functions(source)


def _calls_within(source: str, func: str) -> set:
    """Every name called inside `func`'s body, by AST rather than by substring.

    A substring search over a function's text cannot tell a call from a mention in a docstring,
    and every one of these names appears in prose somewhere in the module.
    """
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func:
            out = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    fn = sub.func
                    if isinstance(fn, ast.Name):
                        out.add(fn.id)
                    elif isinstance(fn, ast.Attribute):
                        out.add(fn.attr)
            return out
    return set()


def _lanes_are_reachable(source: str, lanes: set) -> bool:
    """Is every named lane reached from `_pre_write_gates`, directly or through one hop?

    One hop, because the composition is the design: `_pre_write_gates` calls
    `mutation_evidence_lane`, which calls the gates beneath it. A predicate demanding a direct
    call would force the ladder to inline the composition to stay green, which is the guard
    dictating the shape rather than checking the claim.
    """
    entry = _calls_within(source, "_pre_write_gates")
    reached = set(entry)
    for name in entry:
        reached |= _calls_within(source, name)
    return lanes <= reached


def _drop_call(source: str, name: str) -> str:
    """`source` with every statement calling `name` removed, for the doctored corpus.

    Line-wise and deliberately crude: it only has to produce a source in which the call is
    absent, and it asserts nothing about what else survives - the predicate re-parses it.
    """
    kept = [ln for ln in source.splitlines(keepends=True)
            if f"{name}(" not in ln or ln.lstrip().startswith(("#", '"', "'", "def "))]
    return "".join(kept)


class DoctrineTests(unittest.TestCase):
    def test_doctrine_states_the_rule_and_names_the_enforcing_gate(self) -> None:
        """A reader must arrive at a MECHANISM, not at advice.

        Mutant: delete the passage and leave every other line intact, Revision History
        included - this reddens. Mutant: state the rule and drop the sentence naming
        `transition.py` - a rule with no mechanism behind it is one this doctrine is
        explicit about distrusting, and the enforcement assertion catches it alone.
        """
        text = DOCTRINE.read_text(encoding="utf-8")
        self.assertTrue(_states_the_rule(text), "rule 21 is absent, or states no mechanism")
        passage = _slice_rule(text)
        low = passage.lower()
        self.assertIn("author", low, "the rule does not name whose evidence is insufficient")
        self.assertIn("mutant", low, "the rule does not name the evidence it demands")
        self.assertIn("transition.py", passage,
                      "the rule states no enforcing mechanism, so it is advice")

    def test_deleting_the_stating_passage_reddens_the_guard(self) -> None:
        """THE DISCRIMINATION, exercised rather than inferred.

        The predicate is run over a doctored corpus: rule 21 removed, and a Revision History
        row describing the change that added it left in place. That row contains every word
        the assertions look for. A guard anchored on the whole file passes it; one anchored on
        the rule's own passage does not. BG0457 records exactly this defect - four guards
        comparing a document against a projection of itself - and a guard shipped in the same
        change as the prose it checks is the easiest place to repeat it.

        Mutant: point `_states_the_rule` at the whole text instead of the slice - this reddens,
        and the earlier length-comparison version did not.
        """
        real = DOCTRINE.read_text(encoding="utf-8")
        self.assertTrue(_states_the_rule(real), "the positive control does not hold")
        doctored = real.replace(_slice_rule(real), "") + (
            "\n| 2026-08-06 | sdlc | Added the repair-evidence rule: a fix's author is not "
            "sufficient evidence, held by a mutant and enforced by transition.py |\n")
        self.assertFalse(_states_the_rule(doctored),
                         "the guard is satisfied by a Revision History row describing the "
                         "rule rather than by the rule itself")

    def test_the_definition_of_done_carries_a_consistent_clause(self) -> None:
        """A consuming project copies this file as its own Done contract.

        Mutant: drop the clause from the template - the doctrine states a rule the shipped
        contract does not carry, and a consuming project inherits the prose without the bar.

        Second mutant: write the clause with an internal provenance tag (`(US0567)`) or an
        em dash. The style guard would catch either, but only while somebody runs it over
        this file; asserting it HERE is what makes the criterion's own selector answer for
        the whole criterion rather than for half of it. This criterion previously pointed at
        `bash tools/lint-style.sh`, a whole-repo selector it shared with US0111 AC3 - two
        criteria that a regression in either would fail together, neither saying which.
        """
        dod = DOD.read_text(encoding="utf-8")
        story = dod[dod.index("## Story"): dod.index("## Delivery batch")]
        # Anchored on the CLAUSE, not on the section: `repair` and `mutant` both appear
        # elsewhere in the Story contract, so a whole-section substring check survived a mutant
        # that gutted the clause itself. Found by applying that mutant rather than by reading.
        clause = next((ln for ln in story.splitlines() if "REPAIR" in ln), "")
        self.assertTrue(clause, "the Story contract carries no repair clause")
        tail = story[story.index(clause):] if clause else ""
        tail = tail[:tail.index("- [ ]", len(clause))] if "- [ ]" in tail[len(clause):] else tail
        self.assertIn("mutant was applied", tail,
                      "the clause does not demand the evidence the gate reads - it names the "
                      "repair class and asks for nothing")
        self.assertIn("changed lines", tail,
                      "the clause does not scope the evidence to the repair's own change")
        self.assertIn("block", tail,
                      "the clause states a bar without naming the setting that makes it one, "
                      "so a project cannot tell what it is being held to")
        # Tool-neutral and untagged: a consuming project copies this file, so an id that means
        # something only in THIS repo is noise there, and the house style refuses it.
        tags = re.findall(r"\((?:US|CR|BG|RFC|EP|RV)\d{3,4}[^)]*\)", story)
        self.assertEqual([], tags, f"the clause carries an internal provenance tag: {tags}")
        self.assertNotIn("—", story, "the clause carries an em dash")


    def test_the_named_gate_actually_exists(self) -> None:
        """The doctrine names `transition.py` as what enforces this rule. If that file does not
        carry a repair-evidence gate, the doctrine names a mechanism that is not there - which
        is the failure this repo files as INERT, and the one thing worse than advice is advice
        wearing a mechanism's name.

        This also gives the guard a HOME in the test census: it now references the module it
        checks rather than only markdown, so the attribution convention can place it. Raising
        the unattributed baseline to accommodate a new file is explicitly forbidden, and the
        first remedy the ratchet offers is the right one - give the new file a home.

        Mutant: point the doctrine at a verb that carries no such gate - this reddens.
        """
        transition = (ROOT / ".claude/skills/sdlc-studio/scripts/transition.py").read_text(
            encoding="utf-8")
        self.assertIn("_plan_gate_active", transition,
                      "transition.py carries no repair/test-plan gate, so the doctrine names a "
                      "mechanism that does not exist")
        self.assertIn("review.test_plan_after", transition,
                      "the gate the doctrine names is not the one transition.py reads")

    def test_removing_any_lane_the_doctrine_names_reddens_the_guard(self) -> None:
        """Every mechanism rule 21 NAMES must be reachable from the gate ladder, not merely
        defined. The whole of BG0541 is that `repair_mutation_gate` was defined, tested, and
        called by nothing, while the doctrine told consuming projects it refused.

        Three properties, and the second is the one that took three review rounds to get right:

          1. the real source is wired - the positive control;
          2. removing ANY ONE named lane's call reddens the predicate. The removal set comes
             from the DOCTRINE, never from the predicate's own derived set: a set the predicate
             computes narrows when the predicate narrows, so the mutant `pin this to one lane`
             would leave the loop still red and survive. The doctrine is the text making the
             claim, so checking the claim against the code is what this guard is for;
          3. a floor of THREE lanes, so a doctrine passage edited down to one mechanism cannot
             quietly satisfy the loop either. Both ends have to be pinned or the pair can be
             satisfied by shrinking whichever end is not.

        Mutant: narrow `_wired_lanes` to a single hard-coded name - this reddens on the floor.
        Mutant: delete the `mutation_evidence_lane` call from `_pre_write_gates` - this reddens
        on the loop, and it is the state of the tree BG0541 was filed against.
        """
        transition = (ROOT / ".claude/skills/sdlc-studio/scripts/transition.py").read_text(
            encoding="utf-8")
        lanes = _doctrine_lane_names(DOCTRINE.read_text(encoding="utf-8"), transition)
        self.assertGreaterEqual(
            len(lanes), 3,
            f"rule 21 names {len(lanes)} mechanism(s) - {sorted(lanes)}. The floor is three: a "
            f"passage edited down to one satisfies the reachability loop below without any "
            f"mechanism being reached")
        self.assertTrue(_lanes_are_reachable(transition, lanes),
                        f"the positive control fails: {sorted(lanes)} are named by rule 21 and "
                        f"not all reachable from _pre_write_gates")
        for lane in sorted(lanes):
            doctored = _drop_call(transition, lane)
            self.assertNotEqual(doctored, transition,
                                f"no call to {lane} was found to remove, so the mutant cannot "
                                f"be applied and the loop proves nothing about it")
            self.assertFalse(
                _lanes_are_reachable(doctored, lanes),
                f"removing every call to {lane} leaves the guard green - a mechanism the "
                f"doctrine names can be unreached without this test noticing, which is "
                f"precisely the state BG0541 was filed against")

    def test_the_doctrine_names_the_mode_that_restores_refusal(self) -> None:
        """US0567 AC5: a project that read this rule as a refusal is owed the sentence saying
        the default changed.

        A documented block quietly becoming a documented report lowers a bar on somebody else's
        project without their knowing. The passage therefore has to state which of the three
        modes an unset project gets, and name the one that restores what it used to promise.

        Mutant: state the three modes without marking which is the default - a reader then has
        to guess whether their existing project still refuses.
        Mutant: drop `review.mutation_evidence` from the passage - the rule changes direction
        with no way to change it back.
        """
        passage = _slice_rule(DOCTRINE.read_text(encoding="utf-8"))
        self.assertIn("review.mutation_evidence", passage,
                      "the rule states no setting, so a project cannot choose its consequence")
        for mode in ("report", "block", "off"):
            with self.subTest(mode=mode):
                self.assertIn(f"`{mode}`", passage, f"the rule does not name the {mode} mode")
        self.assertRegex(passage, r"`report`[^\n]*default|default[^\n]*`report`",
                         "the rule names three modes without saying which one a project that "
                         "sets nothing gets, so an existing reader cannot tell whether their "
                         "bar moved")
        # The upgrade sentence itself, not an ordering accident: a reader who installed an
        # earlier version must be told, in one place, that the default moved and what to set to
        # move it back. Asserted on the two things that sentence has to carry.
        upgrade = next((ln for ln in passage.splitlines()
                        if "no longer" in ln or "earlier version" in ln), "")
        self.assertTrue(upgrade,
                        "the rule states three modes but never tells a project that installed "
                        "an earlier version that the default changed under it")
        after = passage[passage.index(upgrade):]
        self.assertIn("`review.mutation_evidence: block`", after,
                      "the upgrade note does not name the setting that restores the refusal "
                      "this rule used to describe")

    def test_the_carried_lesson_cites_the_gate(self) -> None:
        """The lesson must POINT at the doctrine and the enforcing verb, not restate their terms.

        Two documents stating the same rule in their own words drift, and the second is edited
        by whoever did not know the first existed. Citing is what makes them one rule.

        Mutant: restate the rule in the lesson without the `reference-doctrine.md#repair-evidence`
        anchor or the `transition.py` reference - this reddens, and a reader is left with advice
        that has no destination.
        """
        lessons = LESSONS.read_text(encoding="utf-8")
        self.assertIn("repair-evidence", lessons,
                      "the lesson does not cite the doctrine passage")
        self.assertIn("transition.py", lessons,
                      "the lesson does not name the verb that enforces it")


class StampsStagedRosterTests(unittest.TestCase):
    """BG0653 AC4: the roster and the hook name the `stamps-staged` lane by LITERAL. The derived
    sweep in `GateLaneTests` captures a `$skill`-quoted lane with its trailing quote and skips
    it (a Low under CR0511), so this pin does not rely on it."""

    def test_the_lane_roster_names_stamps_staged(self) -> None:
        """MUTANT: remove `stamps-staged` from AGENTS.md's pre-commit lane roster paragraph."""
        repo = Path(__file__).resolve().parents[2]
        agents = (repo / "AGENTS.md").read_text(encoding="utf-8")
        start = agents.index("The pre-commit lanes, recorded here")
        paragraph = agents[start:start + 2500]
        self.assertIn("`stamps-staged`", paragraph, "the roster must name the lane")
        self.assertIn("stamps --staged", paragraph, "and the command that runs it")
        hook = (repo / ".githooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn('run "stamps-staged"', hook, "the hook must wire the lane by that name")
        self.assertIn("stamps --staged", hook)


if __name__ == "__main__":
    unittest.main()
