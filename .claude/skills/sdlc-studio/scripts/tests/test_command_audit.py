"""Tests for the command-surface audit (command_audit.py) - CR0272 slice 1, US0149/US0150.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
_REPO = _SCRIPTS.parents[3]   # the real repo (has SKILL.md)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
command_audit = _load("command_audit")
doc_coverage = command_audit.doc_coverage   # the enumerators both tools share


def _skill(root: Path, *, type_ref: list[str], help_cmds: list[str],
           scripts: dict[str, str]) -> None:
    """Build a minimal skill fixture: a SKILL.md Type Reference, a help catalogue, and scripts."""
    sd = root / ".claude" / "skills" / "sdlc-studio"
    (sd / "scripts").mkdir(parents=True)
    tr = "\n".join(f"| `{c}` | desc |" for c in type_ref)
    (sd / "SKILL.md").write_text(
        f"# SKILL\n\n## Type Reference\n\n| Command | Description |\n| --- | --- |\n{tr}\n\n"
        f"## Full Reference\n\nx\n", encoding="utf-8")
    (sd / "help").mkdir()
    cat = "\n".join(f"| `/sdlc-studio {c}` | desc |" for c in help_cmds)
    (sd / "help" / "help.md").write_text(f"# help\n\n{cat}\n", encoding="utf-8")
    for name, body in scripts.items():
        (sd / "scripts" / f"{name}.py").write_text(body, encoding="utf-8")
    # a reference-scripts page documenting every fixture script (so `undocumented` is 0 unless a
    # test deliberately omits one)
    entries = "\n".join(f"### `{name}.py`\n\ndesc\n" for name in scripts)
    (sd / "reference-scripts.md").write_text(f"# scripts\n\n{entries}\n", encoding="utf-8")


_GOOD = "import argparse\np=argparse.ArgumentParser()\np.parse_args()\n"
_BROKEN = "import sys\nprint('boom', file=sys.stderr)\nsys.exit(1)\n"


class RealRepoAuditTests(unittest.TestCase):
    """The audit on this actual repo - the surface it will be run against."""

    def setUp(self) -> None:
        self.result = command_audit.audit(_REPO)

    def test_applicable_and_every_command_dispositioned(self) -> None:
        self.assertTrue(self.result["applicable"])
        self.assertTrue(self.result["commands"])
        for r in self.result["commands"]:
            self.assertIn(r["spine"], command_audit.SPINE_ORDER)
            self.assertIn(r["disposition"], ("keep", "review"))

    def test_spine_map_is_complete_no_unmapped(self) -> None:
        # every command in the live surface is placed on the spine; a new one would land `unmapped`
        # and this test would fail - the nudge to place it.
        unmapped = [r["command"] for r in self.result["commands"] if r["spine"] == "unmapped"]
        self.assertEqual(unmapped, [], f"unmapped commands: {unmapped}")

    def test_no_command_is_left_in_one_surface_only(self) -> None:
        # the five help-only commands (lessons, repo, retro, review, upgrade) were the standing
        # finding here; four are now promoted into the Type Reference and `upgrade` is folded
        # behind `migrate`, so the surface must carry no drift in either direction.
        drift = {r["command"]: r["drift"] for r in self.result["commands"] if r["drift"]}
        self.assertEqual(drift, {}, f"catalogue drift: {drift}")
        self.assertEqual(self.result["summary"]["drift"], 0)


class HelpOnlyPromotionTests(unittest.TestCase):
    """The spine-serving help-only commands are promoted into the SKILL Type Reference.

    `lessons` and `retro` are bound into the sprint close gate, `review` is one of the three
    support features, and `repo` map ranks files for a story - all four are working commands
    whose absence from the Type Reference was the drift, so they are promoted rather than cut.
    """

    PROMOTED = ("lessons", "repo", "retro", "review")

    def setUp(self) -> None:
        self.skill_dir = _REPO / ".claude" / "skills" / "sdlc-studio"
        self.result = command_audit.audit(_REPO)
        self.by = {r["command"]: r for r in self.result["commands"]}

    def test_each_promoted_command_is_present_in_both_surfaces(self) -> None:
        for cmd in self.PROMOTED:
            with self.subTest(command=cmd):
                self.assertIn(cmd, self.by, f"`{cmd}` is not in the command surface at all")
                row = self.by[cmd]
                self.assertTrue(row["in_type_ref"], f"`{cmd}` is missing from the Type Reference")
                self.assertTrue(row["in_help"], f"`{cmd}` is missing from the help catalogue")
                self.assertIsNone(row["drift"], f"`{cmd}` still drifts: {row['drift']}")

    def test_each_promoted_command_has_a_one_line_description(self) -> None:
        # a bare row satisfies "present" while telling a reader nothing; the AC asks for a
        # description, so an empty or stub cell fails here.
        import re
        text = (self.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        section = text.split("## Type Reference", 1)[1].split("## Full Reference")[0]
        rows = {m.group(1): m.group(2).strip()
                for m in re.finditer(r"^\| `([^`]+)` \| (.+?) \|\s*$", section, re.M)}
        for cmd in self.PROMOTED:
            with self.subTest(command=cmd):
                self.assertIn(cmd, rows, f"no Type Reference row for `{cmd}`")
                self.assertGreaterEqual(
                    len(rows[cmd]), 20,
                    f"`{cmd}` has no real description in the Type Reference: {rows[cmd]!r}")

    def test_promotion_closes_the_documented_coverage_gate(self) -> None:
        # a Type Reference row with no help catalogue entry fails doc_coverage repo-wide, for
        # every unit - so promotion is only complete when that gate is green.
        r = doc_coverage.check(_REPO)
        uncatalogued = [f["name"] for f in r["findings"] if f["kind"] == "command-uncatalogued"]
        self.assertEqual(uncatalogued, [], f"promoted but uncatalogued: {uncatalogued}")


class RetiredCommandAbsenceTests(unittest.TestCase):
    """A command taken out of the catalogue leaves a redirect, not a dead route.

    `upgrade` is FOLDED behind `migrate`: `reference-upgrade.md` names migrate the front door
    that orchestrates upgrade, so it is a working component of a catalogued command, not a dead
    one. The observable contract the AC asks for holds either way - the command is absent from
    both catalogue surfaces, and one redirect line names what replaces it.
    """

    FOLDED = "upgrade"
    TARGET = "migrate"

    def setUp(self) -> None:
        self.skill_dir = _REPO / ".claude" / "skills" / "sdlc-studio"
        self.result = command_audit.audit(_REPO)

    def test_folded_command_is_absent_from_both_surfaces(self) -> None:
        self.assertNotIn(self.FOLDED, doc_coverage._type_ref_commands(self.skill_dir),
                         f"`{self.FOLDED}` is still in the SKILL Type Reference")
        self.assertNotIn(self.FOLDED, command_audit._help_commands(self.skill_dir),
                         f"`{self.FOLDED}` is still catalogued in help/help.md")
        self.assertNotIn(self.FOLDED, {r["command"] for r in self.result["commands"]},
                         f"`{self.FOLDED}` still holds a command-surface row")

    def test_exactly_one_redirect_names_the_replacement(self) -> None:
        redirects = command_audit._redirects(self.skill_dir)
        self.assertEqual(redirects.get(self.FOLDED), self.TARGET,
                         f"no redirect from `{self.FOLDED}` to `{self.TARGET}`")
        text = (self.skill_dir / "help" / "help.md").read_text(encoding="utf-8")
        n = sum(1 for ln in text.splitlines() if command_audit._REDIRECT_RE.match(ln))
        self.assertEqual(n, 1, f"expected exactly one redirect line, found {n}")

    def test_the_folded_help_page_survives_and_names_the_front_door(self) -> None:
        # folding is not deletion: reference-upgrade.md links this page, and an operator
        # following an old habit must land on a page that redirects rather than a 404.
        p = self.skill_dir / "help" / self.FOLDED
        p = p.with_suffix(".md")
        self.assertTrue(p.is_file(), f"help/{self.FOLDED}.md was deleted")
        self.assertIn(f"/sdlc-studio {self.TARGET}", p.read_text(encoding="utf-8"),
                      f"help/{self.FOLDED}.md does not point at `{self.TARGET}`")

    def test_a_redirect_line_does_not_count_as_a_catalogue_entry(self) -> None:
        # the discriminating half: if the audit read a redirect as a catalogue entry, folding
        # would be indistinguishable from leaving the command in place, and drift would persist.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={})
            hp = root / ".claude" / "skills" / "sdlc-studio" / "help" / "help.md"
            hp.write_text(hp.read_text(encoding="utf-8") +
                          "\n- Folded: `/sdlc-studio upgrade` -> `/sdlc-studio migrate` - "
                          "migrate is the front door\n", encoding="utf-8")
            res = command_audit.audit(root)
            self.assertNotIn("upgrade", {r["command"] for r in res["commands"]})
            self.assertEqual(res["summary"]["drift"], 0)
            self.assertEqual(res["summary"]["redirects"], 1)
            self.assertEqual(res["redirects"], {"upgrade": "migrate"})

    def test_a_plain_catalogue_line_is_still_counted(self) -> None:
        # the guard on the guard: stripping redirects must not swallow ordinary entries.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug", "upgrade"], scripts={})
            res = command_audit.audit(root)
            by = {r["command"]: r for r in res["commands"]}
            self.assertIn("upgrade", by)
            self.assertEqual(by["upgrade"]["drift"], "in-help-not-in-type-ref")
            self.assertEqual(res["summary"]["redirects"], 0)


class FixtureAuditTests(unittest.TestCase):
    def test_drift_both_directions_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug", "onlytr"], help_cmds=["bug", "onlyhelp"], scripts={})
            res = command_audit.audit(root)
            by = {r["command"]: r for r in res["commands"]}
            self.assertIsNone(by["bug"]["drift"])                       # in both
            self.assertEqual(by["onlytr"]["drift"], "in-type-ref-not-in-help")
            self.assertEqual(by["onlyhelp"]["drift"], "in-help-not-in-type-ref")
            self.assertEqual(by["onlytr"]["disposition"], "review")    # drift -> review

    def test_unmapped_command_is_a_review_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["zzznovel"], help_cmds=["zzznovel"], scripts={})
            res = command_audit.audit(root)
            r = res["commands"][0]
            self.assertEqual(r["spine"], "unmapped")
            self.assertEqual(r["disposition"], "review")

    def test_broken_tool_detected_and_good_tool_alive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"],
                   scripts={"good": _GOOD, "broken": _BROKEN})
            res = command_audit.audit(root, check_tools=True)
            by = {r["script"]: r for r in res["scripts"]}
            self.assertTrue(by["good"]["alive"])
            self.assertFalse(by["broken"]["alive"])
            self.assertGreaterEqual(res["summary"]["broken_tools"], 1)

    def test_strict_exit_nonzero_on_broken_tool(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={"broken": _BROKEN})
            rc = command_audit.main(["--root", str(root), "--check-tools", "--strict"])
            self.assertEqual(rc, 1)

    def test_write_produces_the_audit_document(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug", "cr"], help_cmds=["bug", "cr"], scripts={})
            rc = command_audit.main(["--root", str(root), "--write"])
            self.assertEqual(rc, 0)
            doc = (root / "sdlc-studio" / "reviews" / "command-audit.md").read_text()
            self.assertIn("# Command-surface audit", doc)
            self.assertIn("## raise", doc)
            self.assertIn("`bug`", doc)

    def test_write_without_check_tools_does_not_certify_tooling(self) -> None:
        # the persisted doc must not claim "every tool runs" when --check-tools was not passed -
        # it would be an unverified claim on disk (a broken tool would be silently certified fine).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={"broken": _BROKEN})
            command_audit.main(["--root", str(root), "--write"])   # no --check-tools
            doc = (root / "sdlc-studio" / "reviews" / "command-audit.md").read_text()
            self.assertIn("tooling not checked", doc)
            self.assertNotIn("every tool runs", doc)

    def test_write_with_check_tools_certifies_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={"good": _GOOD})
            command_audit.main(["--root", str(root), "--write", "--check-tools"])
            doc = (root / "sdlc-studio" / "reviews" / "command-audit.md").read_text()
            self.assertIn("every tool runs", doc)

    def test_non_skill_repo_is_a_noop(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            res = command_audit.audit(Path(d))
            self.assertFalse(res["applicable"])
            self.assertEqual(command_audit.main(["--root", d]), 0)


#: gate.py's three `verify_batch` lines, verbatim at the revision before US0479 deleted them
#: (`git show d982e31a^:.claude/skills/sdlc-studio/scripts/gate.py`). Pinned as lines rather than
#: described as a past state, so this holds after the deletion - and quoted rather than
#: paraphrased, because a paraphrase would be a fixture of what I believed the bug looked like.
VERIFY_BATCH_DEFINITION = (
    '    p.add_argument("--verify-batch", dest="verify_batch", action="store_true",\n'
    '                   help="--release: run jest once and resolve jest verifiers from the '
    'cached "\n'
    '                        "result, instead of a cold start per AC")\n')
VERIFY_BATCH_FORWARD = '                      verify_batch=getattr(args, "verify_batch", False),\n'
VERIFY_BATCH_PARAMETER = '             allow_external: bool = False, verify_batch: bool = False,\n'

#: The three lines above, in a module shaped like the one they came from: a `run_gate` whose body
#: acts on other parameters and never on this one, a `cmd_gate` that forwards it, and a parser.
GATE_FIXTURE = (
    "import argparse\n"
    "\n"
    "\n"
    "def run_gate(root: str = '.', only=None,\n"
    + VERIFY_BATCH_PARAMETER +
    "             release: bool = False) -> dict:\n"
    "    checks = {'root': root, 'only': only, 'release': release, 'external': allow_external}\n"
    "    return checks\n"
    "\n"
    "\n"
    "def cmd_gate(args) -> int:\n"
    "    report = run_gate(args.root, only=args.only,\n"
    '                      allow_external=getattr(args, "allow_external", False),\n'
    + VERIFY_BATCH_FORWARD +
    '                      release=getattr(args, "release", False))\n'
    "    print(report)\n"
    "    return 0\n"
    "\n"
    "\n"
    "def build_parser():\n"
    "    p = argparse.ArgumentParser()\n"
    '    p.add_argument("--root", default=".")\n'
    '    p.add_argument("--only", default="")\n'
    '    p.add_argument("--release", action="store_true")\n'
    '    p.add_argument("--allow-external", dest="allow_external", action="store_true")\n'
    + VERIFY_BATCH_DEFINITION +
    "    p.set_defaults(func=cmd_gate)\n"
    "    return p\n"
    "\n"
    "\n"
    "def main(argv=None) -> int:\n"
    "    args = build_parser().parse_args(argv)\n"
    "    return args.func(args)\n")


class DeadFlagTests(unittest.TestCase):
    """A flag whose destination nothing acts on (US0485).

    The rule this replaces could not have found the bug it was written for. `--verify-batch` was
    MENTIONED three times, and one of those was a `getattr(args, ...)` read - so every rule that
    counts mentions, and every rule that treats a defaulted lookup as a read, called it live. So
    each test here is about where the value LANDS, not about how it is spelled.
    """

    def _dead(self, source: str) -> list[str]:
        return [d["dest"] for d in command_audit.dead_flags(source)["dead"]]

    def _unjudged(self, source: str) -> list[str]:
        return [u["dest"] for u in command_audit.dead_flags(source)["unjudged"]]

    def test_a_flag_whose_value_is_never_consumed_is_reported(self) -> None:
        """AC1. The parsed value is forwarded into a callee whose body never reads the parameter
        it arrives in, and the module is otherwise ordinary.

        MUTANT: stop following the value into the callee and treat a forward as a use. `spare` is
        then indistinguishable from `wanted`, which is the defect that shipped.
        """
        src = ("import argparse\n"
               "def work(wanted=False, spare=False):\n"
               "    if wanted:\n"
               "        print('working')\n"
               "    return 0\n"
               "def cmd(args):\n"
               "    return work(wanted=args.wanted, spare=args.spare)\n"
               "def main(argv=None):\n"
               "    p = argparse.ArgumentParser()\n"
               "    p.add_argument('--wanted', action='store_true')\n"
               "    p.add_argument('--spare', action='store_true')\n"
               "    p.set_defaults(func=cmd)\n"
               "    args = p.parse_args(argv)\n"
               "    return args.func(args)\n")
        result = command_audit.dead_flags(src)
        self.assertEqual(["spare"], [d["dest"] for d in result["dead"]],
                         "the unconsumed flag was not reported, or the consumed one was")
        self.assertEqual("--spare", result["dead"][0]["flag"],
                         "the report must name the switch an operator types")
        self.assertEqual([], result["unjudged"])

    def test_the_detector_catches_verify_batch_from_a_pinned_fixture(self) -> None:
        """AC2, on the three lines as gate.py carried them, quoted verbatim.

        Also run against the real module at the revision before US0479's deletion, where it
        reports `verify_batch` dead and nothing unjudged. That run is evidence, not a test: it
        needs git history, so the contract is pinned here instead.
        """
        result = command_audit.dead_flags(GATE_FIXTURE)
        self.assertEqual(["verify_batch"], [d["dest"] for d in result["dead"]])
        self.assertEqual([], result["unjudged"],
                         "a cannot-judge verdict on this shape would let the flag through")
        # All three quoted sites are in the fixture, so it cannot pass by having lost one - and
        # each is asserted against the constant, so an edit to a quote fails on its own line.
        for site, name in ((VERIFY_BATCH_DEFINITION, "the argparse definition"),
                           (VERIFY_BATCH_FORWARD, "the defaulted lookup that forwards it"),
                           (VERIFY_BATCH_PARAMETER, "the run_gate parameter")):
            with self.subTest(site=name):
                self.assertIn(site, GATE_FIXTURE, f"{name} is not in the pinned fixture")
                self.assertIn("verify_batch", site)

    def test_a_consumed_defaulted_lookup_is_not_reported(self) -> None:
        """AC3. Same access pattern as the dead flag - `getattr(args, name, default)` forwarded as
        a keyword argument - and here the receiving parameter is acted on.

        MUTANT: report a defaulted lookup as no read, which is what the first specification for
        this did. Both flags would then be reported, and the detector would be useless.
        """
        src = ("import argparse\n"
               "def work(quiet=False):\n"
               "    if quiet:\n"
               "        return 1\n"
               "    return 0\n"
               "def cmd(args):\n"
               "    return work(quiet=getattr(args, 'quiet', False))\n"
               "def main(argv=None):\n"
               "    p = argparse.ArgumentParser()\n"
               "    p.add_argument('--quiet', action='store_true')\n"
               "    p.set_defaults(func=cmd)\n"
               "    args = p.parse_args(argv)\n"
               "    return args.func(args)\n")
        self.assertEqual([], self._dead(src))
        self.assertEqual([], self._unjudged(src))

    def test_the_detector_is_wired_into_the_gate(self) -> None:
        """AC4. Present in the hook AND in the npm chain, invoking the verb that judges.

        MUTANT: drop `--dead-flags` from either invocation. `command_audit.py` without it audits
        the command surface and exits 0 having judged no flag at all - a lane that is present,
        green and inert, which is the failure mode the sibling ratchet lane demonstrated.
        """
        hook = (_REPO / ".githooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn('run "dead-flags"', hook, "no dead-flags lane in the pre-commit hook")
        i = hook.find('run "dead-flags"')
        command = next((ln for ln in hook[i:].splitlines() if ln.strip().startswith("--")), "")
        self.assertIn("command_audit.py", command, f"the lane runs something else: {command}")
        self.assertIn("--dead-flags", command,
                      "the lane does not pass --dead-flags, so it audits the command surface "
                      "and judges no flag")
        import json
        pkg = json.loads((_REPO / "package.json").read_text(encoding="utf-8"))
        self.assertIn("lint:dead-flags", pkg["scripts"], "no npm script for the lane")
        self.assertIn("--dead-flags", pkg["scripts"]["lint:dead-flags"])
        self.assertIn("lint:dead-flags", pkg["scripts"]["lint"],
                      "the lane exists but the `lint` chain does not run it")

    def test_the_verb_exits_non_zero_on_a_dead_flag_and_zero_when_clean(self) -> None:
        """A lane that reports a defect and exits 0 cannot stop it shipping."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={})
            with contextlib.redirect_stdout(io.StringIO()) as clean:
                self.assertEqual(0, command_audit.main(["--root", str(root), "--dead-flags"]))
            self.assertIn("0 dead flag(s)", clean.getvalue())
            (root / ".claude" / "skills" / "sdlc-studio" / "scripts" / "dead.py").write_text(
                GATE_FIXTURE, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as found:
                self.assertEqual(1, command_audit.main(["--root", str(root), "--dead-flags"]))
            self.assertIn("--verify-batch", found.getvalue())

    def test_a_positional_is_not_judged_as_a_flag(self) -> None:
        """`p.add_argument("cmd", choices=["build"])` - argparse makes the caller supply it
        whether or not a line reads the value, so "never consumed" is not a defect. Reported as
        dead, it also printed the positional as `--cmd`, a switch that does not exist."""
        src = ("import argparse\n"
               "def main(argv=None):\n"
               "    p = argparse.ArgumentParser()\n"
               "    p.add_argument('cmd', choices=['build'])\n"
               "    p.add_argument('--root', default='.')\n"
               "    args = p.parse_args(argv)\n"
               "    print(args.root)\n"
               "    return 0\n")
        self.assertNotIn("cmd", command_audit.argparse_dests(command_audit.ast.parse(src)))
        self.assertEqual([], self._dead(src))

    def test_a_namespace_read_straight_off_parse_args_counts(self) -> None:
        """`build(Path(ap.parse_args().out))` binds no name, and reading it as no namespace at all
        reported a live flag as dead."""
        src = ("import argparse\n"
               "def build(out):\n"
               "    print(out)\n"
               "def main():\n"
               "    ap = argparse.ArgumentParser()\n"
               "    ap.add_argument('--out', default='x')\n"
               "    build(ap.parse_args().out)\n"
               "    return 0\n")
        self.assertEqual([], self._dead(src))


class CannotJudgeTests(unittest.TestCase):
    """Three shapes where the value may be read somewhere this analysis cannot see.

    Each is reported as NOT JUDGED and named, never as dead and never silently dropped: a
    fabricated verdict is worse than an absent one, and an absent one that says nothing is
    indistinguishable from a flag that passed.
    """

    def _judge(self, source: str, path: Path | None = None) -> dict:
        return command_audit.dead_flags(source, path)

    def test_a_computed_getattr_makes_unread_destinations_unjudged(self) -> None:
        """The shared prose loader is `{k: getattr(args, k, None) for k in keys}`, so the
        destination read cannot be named. Reported dead, it named four live flags in two
        modules."""
        src = ("import argparse\n"
               "def load(fields):\n"
               "    return {k: v for k, v in fields.items() if v}\n"
               "def cmd(args):\n"
               "    return load({k: getattr(args, k, None) for k in ('decision', 'rationale')})\n"
               "def main(argv=None):\n"
               "    p = argparse.ArgumentParser()\n"
               "    p.add_argument('--decision')\n"
               "    p.add_argument('--rationale')\n"
               "    p.set_defaults(func=cmd)\n"
               "    args = p.parse_args(argv)\n"
               "    return args.func(args)\n")
        result = self._judge(src)
        self.assertEqual([], result["dead"])
        self.assertEqual(["decision", "rationale"], [u["dest"] for u in result["unjudged"]])
        self.assertIn("computed attribute name", result["unjudged"][0]["reason"])

    def test_a_module_that_declares_but_never_parses_is_unjudged(self) -> None:
        """The shared `add_*_arg` helpers declare onto the caller's parser; the value is read in
        whichever module parses it. Judged here, every one of them reads as dead."""
        src = ("def add_format_arg(parser):\n"
               "    parser.add_argument('--format', choices=('text', 'json'), default='text')\n")
        result = self._judge(src)
        self.assertEqual([], result["dead"])
        self.assertEqual(["format"], [u["dest"] for u in result["unjudged"]])
        self.assertIn("never parses", result["unjudged"][0]["reason"])

    def test_an_unresolvable_escape_makes_unread_destinations_unjudged(self) -> None:
        """The namespace goes to a callee this module cannot follow, which may read anything."""
        src = ("import argparse\n"
               "import somewhere_else\n"
               "def main(argv=None):\n"
               "    p = argparse.ArgumentParser()\n"
               "    p.add_argument('--depth', type=int, default=1)\n"
               "    args = p.parse_args(argv)\n"
               "    return somewhere_else.run(args)\n")
        result = self._judge(src)
        self.assertEqual([], result["dead"])
        self.assertEqual(["depth"], [u["dest"] for u in result["unjudged"]])
        self.assertIn("somewhere_else.run", result["unjudged"][0]["reason"])

    def test_an_escape_into_a_SIBLING_module_is_followed_rather_than_given_up_on(self) -> None:
        """`sdlc_md.resolve_root(args)` is in every module of the family and reads exactly one
        destination. Unresolved, it makes every unread destination in all ninety-one modules
        cannot-judge, and the detector reports nothing about anything."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "lib").mkdir()
            (root / "lib" / "shared.py").write_text(
                "def resolve_root(args):\n"
                "    return getattr(args, 'root', None) or '.'\n", encoding="utf-8")
            mod = root / "tool.py"
            mod.write_text("import argparse\n"
                           "from lib import shared\n"
                           "def main(argv=None):\n"
                           "    p = argparse.ArgumentParser()\n"
                           "    p.add_argument('--root', default='.')\n"
                           "    p.add_argument('--spare', action='store_true')\n"
                           "    args = p.parse_args(argv)\n"
                           "    args.root = shared.resolve_root(args)\n"
                           "    return 0\n", encoding="utf-8")
            result = self._judge(mod.read_text(encoding="utf-8"), mod)
            self.assertEqual([], [u["dest"] for u in result["unjudged"]],
                             "the sibling escape was not followed, so nothing could be judged")
            self.assertEqual(["spare"], [d["dest"] for d in result["dead"]],
                             "following the escape must not also excuse the flag it does not read")

    def test_an_existence_TEST_of_the_namespace_is_not_an_escape(self) -> None:
        """`if args is not None` reads no destination off the namespace. Counted as an escape, it
        made every flag in gate.py cannot-judge - including the dead one."""
        src = ("import argparse\n"
               "def resolve(args=None):\n"
               "    if args is not None and args:\n"
               "        return getattr(args, 'boundary', None)\n"
               "    return None\n"
               "def main(argv=None):\n"
               "    p = argparse.ArgumentParser()\n"
               "    p.add_argument('--boundary')\n"
               "    p.add_argument('--spare', action='store_true')\n"
               "    args = p.parse_args(argv)\n"
               "    print(resolve(args))\n"
               "    return 0\n")
        result = self._judge(src)
        self.assertEqual([], result["unjudged"])
        self.assertEqual(["spare"], [d["dest"] for d in result["dead"]])

    def test_a_same_named_local_INSIDE_a_namespace_scope_is_not_the_namespace(self) -> None:
        """A nested `def _git(*args)` and a nested `args = shlex.split(tail)` both reuse the
        family's name for its namespace, INSIDE a function that really does hold one - so the
        enclosing scope's answer is the wrong one and the binding here has to win.

        Pooled, the varargs tuple leaving in a list literal read as the namespace escaping, and
        every flag in gate.py became cannot-judge. The nesting is the point: without it the
        module scope answers "not a namespace" anyway and the test proves nothing.
        """
        src = ("import argparse\n"
               "import shlex\n"
               "import subprocess\n"
               "def cmd(args):\n"
               "    def _git(*args):\n"
               "        return subprocess.run(['git', *args], cwd=args_root)\n"
               "    def _split(tail):\n"
               "        args = shlex.split(tail)\n"
               "        return subprocess.run([*args])\n"
               "    args_root = args.root\n"
               "    _split('a b')\n"
               "    return _git('status')\n"
               "def main(argv=None):\n"
               "    p = argparse.ArgumentParser()\n"
               "    p.add_argument('--root', default='.')\n"
               "    p.add_argument('--spare', action='store_true')\n"
               "    p.set_defaults(func=cmd)\n"
               "    args = p.parse_args(argv)\n"
               "    return args.func(args)\n")
        result = self._judge(src)
        self.assertEqual([], result["unjudged"],
                         "a same-named local was followed as the namespace and escaped")
        self.assertEqual(["spare"], [d["dest"] for d in result["dead"]])

    def test_a_namespace_handed_to_a_CLASS_is_followed_into_its_init(self) -> None:
        """`_PushState(args)` reads its flags in `__init__`; unfollowed, a live flag is unjudged
        and the `self` parameter would have absorbed the argument."""
        src = ("import argparse\n"
               "class State:\n"
               "    def __init__(self, args):\n"
               "        self.allow = getattr(args, 'allow', False)\n"
               "def cmd(args):\n"
               "    st = State(args)\n"
               "    if st.allow:\n"
               "        return 1\n"
               "    return 0\n"
               "def main(argv=None):\n"
               "    p = argparse.ArgumentParser()\n"
               "    p.add_argument('--allow', action='store_true')\n"
               "    p.set_defaults(func=cmd)\n"
               "    args = p.parse_args(argv)\n"
               "    return args.func(args)\n")
        result = self._judge(src)
        self.assertEqual([], result["dead"])
        self.assertEqual([], result["unjudged"])

    def test_a_verb_table_registered_by_LOOP_VARIABLE_resolves(self) -> None:
        """`for name, fn, help in (...): p.set_defaults(func=fn)` - the argument is a loop
        variable, so reading it names no handler. Thirteen live flags in one module went unjudged
        for exactly this."""
        src = ("import argparse\n"
               "def cmd_a(args):\n"
               "    print(args.alpha)\n"
               "    return 0\n"
               "def cmd_b(args):\n"
               "    print(args.beta)\n"
               "    return 0\n"
               "def main(argv=None):\n"
               "    ap = argparse.ArgumentParser()\n"
               "    sub = ap.add_subparsers(dest='cmd', required=True)\n"
               "    for name, fn in (('a', cmd_a), ('b', cmd_b)):\n"
               "        p = sub.add_parser(name)\n"
               "        p.add_argument('--alpha')\n"
               "        p.add_argument('--beta')\n"
               "        p.set_defaults(func=fn)\n"
               "    args = ap.parse_args(argv)\n"
               "    return args.func(args)\n")
        result = self._judge(src)
        self.assertEqual([], result["dead"])
        self.assertEqual([], result["unjudged"])


class LiveCorpusDeadFlagTests(unittest.TestCase):
    """The lane's own verdict on this repository, so the contract is a test and not just a run."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.result = command_audit.scan_dead_flags(_REPO)

    def test_no_shipped_flag_is_dead(self) -> None:
        self.assertTrue(self.result["applicable"])
        self.assertEqual([], self.result["dead"],
                         "a shipped flag is documented and does nothing")

    def test_the_scan_actually_reached_the_corpus(self) -> None:
        """The control. A scan that judged nothing would satisfy the assertion above."""
        self.assertGreater(self.result["modules"], 50,
                           "the scan found almost no modules - it is passing by not looking")

    def test_every_unjudged_destination_carries_a_REASON(self) -> None:
        for u in self.result["unjudged"]:
            with self.subTest(module=u["module"], dest=u["dest"]):
                self.assertGreaterEqual(len(u["reason"]), 20,
                                        "a destination nobody could judge, with no reason given, "
                                        "reads as one that passed")


if __name__ == "__main__":
    unittest.main()
