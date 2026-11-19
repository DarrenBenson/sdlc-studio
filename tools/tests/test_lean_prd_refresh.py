"""US0929: the PRD describes the lean product and lists the outcomes a Sprint Goal can serve.

The outcomes are read by the planner's own reader (`sprint.prd_outcomes`) and the persona
cards by `sprint.persona_cards`, so this file holds no second parser of either; `end_goals_text`
only slices a card's End goals as written, for a word-for-word comparison. Outside
`OutcomeCitationTests` and what it pins (`O5_CITES` and `UPGRADE_GOAL`, US1082; the cited
personas, the kept citations, O10 to O13's words and the tooling Primary, US1148), it pins no
persona or End goal by hand: a card that gains, loses or renumbers an End goal moves what an
outcome may cite. Every
`<script>.py <subcommand>` the loop sections name is checked against that script's own `--help`,
so a retired subcommand cannot stay described as current. `PrdBaselineTests` (US1103) reads the
release the PRD's baseline must name from package.json (US1111), reads its capability set from
RV0028's PRD-10 row, and checks the commands those capabilities' inventory rows name the same
way. `PrdRulesTests` (US1104) reads the rules, NFRs and cost model against the code that decides
them, holds each derived count to a band around the tree's own measure, and ties the detail
criteria's ticks to the status of the bug that holds each one. `PrdFlagDefaultsTests` (BG1525,
BG1526) holds section 9's gate-key defaults to the defaults file, `PrdEnvironmentVariablesTests`
(BG1553) its environment table to what the scripts read, and `PrdCloseChainTests` (BG1555) the
account of the sprint close to `sprint._CLOSE_CHAIN`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
import ast
import functools
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
PRD = REPO / "sdlc-studio" / "prd.md"
sys.path.insert(0, str(SCRIPTS))

import doc_freshness  # noqa: E402 - the census whose measures and band ratio a count is held to
import sprint  # noqa: E402 - the outcome and persona readers US0927 ships
from lib import sdlc_md  # noqa: E402 - the id resolver an inventory row's Epic cell is read by

_spec = importlib.util.spec_from_file_location("check_versions",
                                               REPO / "tools" / "check_versions.py")
check_versions = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_versions)
#: The shipped git-fixture helper, loaded rather than copied (LC-020): the plan the O10 check
#: runs gets its confined environment.
_gitutil_spec = importlib.util.spec_from_file_location("_lean_prd_refresh_gitutil",
                                                       SCRIPTS / "tests" / "gitutil.py")
gitutil = importlib.util.module_from_spec(_gitutil_spec)
sys.modules[_gitutil_spec.name] = gitutil
_gitutil_spec.loader.exec_module(gitutil)

#: One citation inside an outcome: `(Maya Okafor, End goal 4)`; several are `;`-separated.
_CITE_RE = re.compile(r"([A-Z][\w'-]*(?: [A-Z][\w'-]*)+), End goal (\d+)")
#: A command a section names: a code span opening `<script>.py <subcommand>`.
_COMMAND_RE = re.compile(r"`([a-z_]+)\.py ([a-z][a-z0-9-]*)")
#: What the loop sections must say, as the code runs it today (AC2).
_LOOP_MARKERS = {
    "a Sprint Goal of 20 words or fewer": r"20 words or fewer",
    "the goal traces to an outcome": r"\boutcome",
    "one plan approval": r"approves? the plan once|one plan approval",
    "one reviewer per unit": r"one reviewer",
    "at most two review rounds": r"two rounds",
    "carried known issues": r"known issue",
    "persona rulings through decisions.py rule": r"`decisions\.py rule",
    "the one-page sprint report": r"one-page",
    "failure classes in lessons.jsonl": r"lessons\.jsonl",
}
_RETIRED = ("a learning loop that must produce work",
            "lifted into the store the next `sprint plan` prints unasked")
#: The citations US1082 AC2 pins: O5 on the pair D0443 rules (Maya Okafor's End goal 5 and
#: Abena Osei's End goal 6, the counterweight, in either order; US1148 AC3), and the End goal
#: CR0648 names as having no outcome. Pinned by name, since `outcome_problems` asks of a citation
#: only that its card and End goal number exist.
O5_CITES = (("Maya Okafor", "5"), ("Abena Osei", "6"))
UPGRADE_GOAL = ("Jonah Reyes", "4")
#: The personas every End goal of whom one outcome cites, cited or not (US1148 AC4), and the
#: citations O1 to O4 and O6 to O9 keep (D0438: O1-O9 stay).
CITED_PERSONAS = ("Maya Okafor", "Jonah Reyes", "Abena Osei", "Graham Doyle")
KEPT_CITES = {**{f"O{n}": [("Maya Okafor", str(n))] for n in range(1, 5)},
              **{f"O{n + 5}": [("Jonah Reyes", str(n))] for n in range(1, 5)}}
#: O10 to O13 word for word, as D0438 drafts them and D0446 rules them (US1148 AC2).
NEW_OUTCOMES = {
    "O10": ("A change that reaches a change board carries one evidence pack, built from what the "
            "run recorded rather than written afterwards and readable without running the tool: "
            "what changed, which criteria passed, who reviewed it independently, what is known to "
            "be wrong, and the person accountable for it, never 'the agent'; every specification "
            "it rests on names its accountable owner the same way (Abena Osei, End goal 1; Abena "
            "Osei, End goal 2; Graham Doyle, End goal 1; Graham Doyle, End goal 2)"),
    "O11": ("Each team sees what its delivery costs per point, in money, against a monthly budget "
            "it declares, whichever harness ran the work (Abena Osei, End goal 3)"),
    "O12": ("A defect that escapes to production is traced to the unit and the verdict that let "
            "it through, and the next plan, build and review carry what it taught, so the same "
            "mistake does not ship twice (Abena Osei, End goal 4; Graham Doyle, End goal 3)"),
    "O13": ("The committed record of reports, run records, verdicts and lessons is versioned and "
            "complete, so people who never open a terminal follow progress, evidence and cost on "
            "the read-only companion dashboard, without the operator's machine or anyone to "
            "translate (Abena Osei, End goal 5)"),
}
#: The tooling Primary, whose interface does not ship, so no outcome names him (D0380).
TOOLING_PRIMARY = "Rowan Achterberg"
#: The commit Jonah Reyes's End goals 1 to 4 are held to, word for word (US1082 AC3).
GOALS_BASE = "7f3e91a9"


def outcome_problems(root: Path) -> list[str]:
    """Why the PRD's outcomes do not trace to real persona End goals; empty when they do."""
    outcomes = sprint.prd_outcomes(root)
    if not outcomes:
        return ["the PRD has no parseable `## Outcomes` section"]
    goals = {c["name"]: {n for n, _ in c["end_goals"]} for c in sprint.persona_cards(root)}
    problems = []
    for oid, text in outcomes.items():
        cites = _CITE_RE.findall(text)
        if not cites:
            problems.append(f"{oid} cites no persona End goal: {text}")
        for name, number in cites:
            if name not in goals:
                problems.append(f"{oid} cites {name}, who has no card in sdlc-studio/personas/")
            elif number not in goals[name]:
                problems.append(f"{oid} cites {name} End goal {number}; the card has "
                                f"{sorted(goals[name])}")
    return problems


def citation_problems(root: Path, required: tuple[str, ...] = ()) -> list[str]:
    """Why the outcomes do not cite every End goal of each persona they cite or `required` names,
    once each; empty when they do. A pair cited twice inside one outcome is one outcome's
    citation, and a `required` persona whose card states no End goal is a problem of its own."""
    goals = {c["name"]: [n for n, _ in c["end_goals"]] for c in sprint.persona_cards(root)}
    cited: dict[tuple[str, str], list[str]] = {}
    for oid, text in sprint.prd_outcomes(root).items():
        for pair in dict.fromkeys(_CITE_RE.findall(text)):
            cited.setdefault(pair, []).append(oid)
    problems = [f"{name} End goal {number} is cited by {', '.join(oids)}"
                for (name, number), oids in cited.items() if len(oids) > 1]
    problems += [f"{name} has no card that states an End goal"
                 for name in required if not goals.get(name)]
    for name in dict.fromkeys([*required, *(name for name, _ in cited)]):
        problems += [f"no outcome cites {name} End goal {number}"
                     for number in goals.get(name, []) if (name, number) not in cited]
    return problems


def kept_citation_problems(root: Path) -> list[str]:
    """Why an outcome `KEPT_CITES` names does not cite exactly what it cited before O10 to O13
    were added; empty when each does."""
    outcomes = sprint.prd_outcomes(root)
    return [f"{oid} cites {_CITE_RE.findall(outcomes.get(oid, ''))}, not {want}"
            for oid, want in KEPT_CITES.items()
            if _CITE_RE.findall(outcomes.get(oid, "")) != want]


def new_outcome_problems(root: Path) -> list[str]:
    """Why O10 to O13 are not each the one line `- **On:** <text>` with `NEW_OUTCOMES`'s text,
    straight after O9 and in order, or why an outcome names `TOOLING_PRIMARY`; empty when
    neither holds."""
    prd = (root / "sdlc-studio" / "prd.md").read_text(encoding="utf-8")
    outcomes = sprint.prd_outcomes(root)
    problems = [f"{oid} is not the one line `- **{oid}:** ` and the ruled text"
                for oid, text in NEW_OUTCOMES.items()
                if _outcome_line(prd, oid) != f"- **{oid}:** {text}"]
    ids = list(outcomes)
    after = ids[ids.index("O9") + 1:][:len(NEW_OUTCOMES)] if "O9" in ids else []
    if after != list(NEW_OUTCOMES):
        problems.append(f"the outcomes after O9 are {after}, not {list(NEW_OUTCOMES)}")
    problems += [f"{oid} names {TOOLING_PRIMARY} (D0380)" for oid, text in outcomes.items()
                 if TOOLING_PRIMARY in text]
    return problems


def o10_trace_problems(said: str) -> list[str]:
    """Why `sprint.py plan --serves O10` output `said` does not print one `goal serves: O10 -`
    line naming Abena Osei and Graham Doyle with no `goal serves: NONE` line; empty when it
    does (US1148 AC5)."""
    lines = [ln for ln in said.splitlines() if ln.startswith("goal serves:")]
    o10 = [ln for ln in lines if ln.startswith("goal serves: O10 -")]
    problems = [] if len(o10) == 1 else [f"{len(o10)} lines start `goal serves: O10 -`"]
    problems += [f"the goal serving O10 does not name {name}"
                 for name in ("Abena Osei", "Graham Doyle") if not any(name in ln for ln in o10)]
    return problems + [ln for ln in lines if ln.startswith("goal serves: NONE")]


def card_of(name: str) -> Path | None:
    """The card in `sdlc-studio/personas/` whose first `# ` heading is `name`, or None."""
    for path in sorted((REPO / "sdlc-studio" / "personas").glob("*.md")):
        m = re.search(r"^#\s+(.+?)\s*$", path.read_text(encoding="utf-8"), re.M)
        if m and m.group(1) == name:
            return path
    return None


def committed_text(commit: str, path: Path) -> str:
    """`path` as it is at `commit`, read with `git show`."""
    run = subprocess.run(["git", "show", f"{commit}:{path.relative_to(REPO).as_posix()}"],
                         cwd=REPO, capture_output=True, text=True, check=False)
    if run.returncode:
        raise AssertionError(f"cannot read {path.name} at {commit}: {run.stderr.strip()}")
    return run.stdout


def end_goals_text(card: str) -> str:
    """A card's `## End Goals` section from its first numbered line on, as written, trailing
    whitespace trimmed: the words of every End goal, continuation lines included."""
    body = section(card, "## End Goals")
    m = re.search(r"^\d+[.)]\s", body, re.M)
    return body[m.start():].rstrip() if m else ""


def section(text: str, heading: str) -> str:
    """The body under `heading` (a whole heading line), up to the next heading of its level or
    above; empty when the heading is absent."""
    level = len(heading) - len(heading.lstrip("#"))
    m = re.search(rf"^{re.escape(heading)}\s*$(.*?)(?=^#{{1,{level}}}\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


@functools.lru_cache(maxsize=None)
def subcommands(script: str) -> frozenset[str] | None:
    """The subcommands `<script>.py --help` lists, or None when there is no such script. Cached,
    since the inventory checks ask the same scripts once per mutant."""
    path = SCRIPTS / f"{script}.py"
    if not path.is_file():
        return None
    out = subprocess.run([sys.executable, str(path), "--help"], capture_output=True,
                         text=True, check=False, cwd=REPO).stdout
    names: set[str] = set()
    for group in re.findall(r"\{([^{}]*)\}", out, re.S):
        names.update(n.strip() for n in group.split(",") if n.strip())
    return frozenset(names)


def unknown_commands(text: str) -> list[str]:
    """Each `<script>.py <subcommand>` in `text` that the script's `--help` does not list."""
    bad = []
    for script, sub in dict.fromkeys(_COMMAND_RE.findall(text)):
        known = subcommands(script)
        if known is None or sub not in known:
            bad.append(f"{script}.py {sub}")
    return bad


def loop_sections(text: str) -> str:
    return section(text, "## Mission") + section(text, "### Core Behaviours")


def status_note_problems(prd: str) -> list[str]:
    """Why the Complete versus calibrated note of section 3 calls the shipped forecast
    falsified, drops the distinction, or loses its pointer to section 10 (BG1527)."""
    m = re.search(r"^> \*\*Complete vs Ready:\*\*.*?(?=^> \*\*Location)", prd, re.M | re.S)
    note = flat(re.sub(r"^\s*>\s?", "", m.group(0), flags=re.M)) if m else ""
    problems = []
    if not re.search(r"Complete is not the same as calibrated", note):
        problems.append("the status note drops the Complete versus calibrated distinction")
    if not re.search(r"first token predictor .{0,60}was falsified and replaced", note):
        problems.append("the status note does not say the earlier predictor was falsified and "
                        "replaced")
    if not re.search(r"points-based forecast .{0,60}cleared the bar", note):
        problems.append("the status note does not say the points-based forecast cleared the bar")
    if "falsified hypothesis" in note:
        problems.append("the status note calls the shipped forecast a falsified hypothesis")
    if "(see §10)" not in note:
        problems.append("the status note does not point to section 10")
    return problems


def context_problems(prd: str) -> list[str]:
    """Why the Context paragraph does not say fixes land here and `tools/forward-port.sh`
    mirrors them to the installed copy, citing AGENTS.md's Forward-porting section (BG1528)."""
    context = flat(section(prd, "### Context"))
    problems = []
    if "back-port" in context:
        problems.append("the Context calls the installed copy the back-port source")
    if "`tools/forward-port.sh`" not in context:
        problems.append("the Context does not name `tools/forward-port.sh`")
    if "fixes land here" not in context:
        problems.append("the Context does not say fixes land in this repository")
    if "Forward-porting in `AGENTS.md`" not in context:
        problems.append("the Context does not cite the Forward-porting section of `AGENTS.md`")
    return problems


_STOP_CLAIM_RE = re.compile(r"\bStop[- ]hook installer\b|"
                            r"\binstalls? (?:the |a )?(?:\w+ )?Stop[- ]hook\b", re.I)


def stop_hook_writers(sources: dict[str, str]) -> list[str]:
    """The scripts whose source writes a `Stop` hook entry into a settings file: one that names
    the `"Stop"` key, a settings file, and a write primitive. The close guard itself only reads."""
    return sorted(name for name, src in sources.items()
                  if re.search(r"""["']Stop["']""", src) and re.search(r"settings(?:\.json)?", src)
                  and _WRITE_RE.search(src))


def stop_hook_claims(prd: str) -> list[str]:
    """Each sentence of the PRD that credits a Stop-hook installer."""
    return [s for s in _SENTENCE_RE.split(body(prd)) if _STOP_CLAIM_RE.search(s)]


def stop_hook_problems(prd: str, sources: dict[str, str]) -> list[str]:
    """Each claim of a Stop-hook installer while no script writes one."""
    if stop_hook_writers(sources):
        return []
    return [f"the PRD claims a Stop-hook installer and no script writes one: {s!r}"
            for s in stop_hook_claims(prd)]


class PrdRefreshTests(unittest.TestCase):

    def test_every_outcome_traces_to_a_real_end_goal(self):
        """AC1. Mutants: drop the Outcomes section; cite End goal 9 on a real card; cite a
        persona with no card - each must be refused."""
        self.assertEqual([], outcome_problems(REPO))
        self.assertTrue(sprint.prd_outcomes(REPO), "the PRD lists no outcomes")
        prd = PRD.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(REPO / "sdlc-studio" / "personas", root / "sdlc-studio" / "personas")

            def problems_with(prd_text: str) -> list[str]:
                (root / "sdlc-studio" / "prd.md").write_text(prd_text, encoding="utf-8")
                return outcome_problems(root)

            self.assertEqual([], problems_with(prd), "the copied fixture must start clean")
            no_section = re.sub(r"^## Outcomes\s*$", "## Aims", prd, count=1, flags=re.M)
            self.assertNotEqual(prd, no_section)
            self.assertTrue(problems_with(no_section))
            first = next(iter(sprint.prd_outcomes(REPO).values()))
            m = _CITE_RE.search(first)
            bad_goal = prd.replace(m.group(0), f"{m.group(1)}, End goal 9", 1)
            self.assertIn("End goal 9", problems_with(bad_goal)[0])
            no_card = prd.replace(m.group(0), "Ada Lovelace, End goal 1", 1)
            self.assertIn("no card", problems_with(no_card)[0])
            uncited = prd.replace(f"({m.group(0)})", "", 1)
            self.assertNotEqual(prd, uncited)
            self.assertIn("cites no persona", problems_with(uncited)[0])

    def test_the_loop_section_names_only_commands_that_exist(self):
        """AC2. Mutants: name a subcommand the script lacks, or a script that does not exist;
        drop any one loop element from the Mission and Core Behaviours."""
        loop = loop_sections(PRD.read_text(encoding="utf-8"))
        self.assertTrue(loop.strip(), "no Mission or Core Behaviours section found")
        missing = [what for what, pattern in _LOOP_MARKERS.items()
                   if not re.search(pattern, loop, re.I)]
        self.assertEqual([], missing, "the loop sections do not describe these")
        named = _COMMAND_RE.findall(loop)
        self.assertIn(("decisions", "rule"), named)
        self.assertEqual([], unknown_commands(loop))
        # the check itself must be able to refuse
        self.assertEqual(["sprint.py frobnicate"], unknown_commands("`sprint.py frobnicate`"))
        self.assertEqual(["nosuch.py plan"], unknown_commands("`nosuch.py plan`"))
        self.assertEqual([], unknown_commands("`sprint.py plan` and `critic.py brief`"))

    def test_the_status_note_does_not_call_the_shipped_forecast_falsified(self):
        """BG1527. The Complete-versus-calibrated note keeps its distinction and says the
        earlier token predictor was falsified and replaced and the points forecast cleared the
        bar. Mutants: the old sentence put back; the section 10 reference dropped."""
        prd = PRD.read_text(encoding="utf-8")
        self.assertEqual([], status_note_problems(prd))
        old = ("the first token predictor under \"Sizing and velocity\" was\n> falsified and "
               "replaced, and the points-based forecast that ships cleared the bar set\n> before "
               "its data was seen (see §10).")
        self.assertIn(old, prd)
        put_back = ("the token forecast under \"Sizing and velocity\" ships and\n> runs, and "
                    "its prediction is a falsified hypothesis (see §10).")
        self.assertEqual(3, len(status_note_problems(prd.replace(old, put_back, 1))))
        no_ref = status_note_problems(prd.replace("its data was seen (see §10).",
                                                  "its data was seen.", 1))
        self.assertEqual(["the status note does not point to section 10"], no_ref)
        no_distinction = status_note_problems(prd.replace("Complete is not the\n> same as "
                                                          "calibrated:", "Complete:", 1))
        self.assertEqual(["the status note drops the Complete versus calibrated distinction"],
                         no_distinction)

    def test_the_context_names_forward_port_as_the_direction_of_flow(self):
        """BG1528. Mutants: `back-port source` put back; `tools/forward-port.sh` or the
        AGENTS.md citation dropped."""
        prd = PRD.read_text(encoding="utf-8")
        self.assertEqual([], context_problems(prd))
        self.assertTrue((REPO / "tools" / "forward-port.sh").is_file())
        self.assertIn("## Forward-porting", (REPO / "AGENTS.md").read_text(encoding="utf-8"))
        context = section(prd, "### Context")
        for old, new, says in (("`tools/forward-port.sh` mirrors", "a tool mirrors",
                                "does not name `tools/forward-port.sh`"),
                               ("Forward-porting in\n`AGENTS.md`", "`CLAUDE.md`",
                                "does not cite the Forward-porting section of `AGENTS.md`"),
                               ("fixes land here and", "the installed copy is the back-port "
                                "source for production fixes and",
                                "calls the installed copy the back-port source")):
            problems = context_problems(prd.replace(context, context.replace(old, new, 1), 1))
            self.assertIn(f"the Context {says}", problems, (new, problems))

    def test_the_close_down_row_describes_the_hand_wired_reminder(self):
        """BG1554 AC1. Mutants: the row crediting a Stop-hook installer, saying the hook
        redefines when a sprint is done, or the feature name calling the advisory a gate."""
        prd = PRD.read_text(encoding="utf-8")
        row = next(r for r in feature_rows(prd) if r["Feature"].startswith("Sprint close-down"))
        self.assertEqual("Sprint close-down reminder", row["Feature"])
        self.assertIn("`close_guard.py`", row["Location"])
        self.assertIn("scripts/hooks/", row["Location"])
        text = row["Description"]
        self.assertRegex(text, r"optional Stop hook")
        self.assertRegex(text, r"wires into its own settings by hand")
        self.assertRegex(text, r"reminds once at a turn end and never locks")
        self.assertNotRegex(text, r"installer|redefines|close-gate-green")
        self.assertNotRegex(row["Feature"], r"\bgate\b")
        guard = (SCRIPTS / "hooks" / "close_guard.py").read_text(encoding="utf-8")
        self.assertIn("Opt-in", guard)
        self.assertIn("never HARD-locks", guard)

    def test_no_stop_hook_installer_is_claimed_while_none_ships(self):
        """BG1554 AC2. A script that writes a `Stop` hook entry into a settings file would
        allow the claim; none does today. Mutants: the claim written back into the row, and a
        writer added to a script's source."""
        prd = PRD.read_text(encoding="utf-8")
        sources = script_sources()
        self.assertEqual([], stop_hook_writers(sources), "a script now installs the hook")
        self.assertEqual([], stop_hook_claims(prd))
        self.assertEqual([], stop_hook_problems(prd, sources))
        row = next(r for r in feature_rows(prd) if r["Feature"].startswith("Sprint close-down"))
        for claim in ("a Stop-hook installer redefines sprint-done as close-gate-green",
                      "`init` installs the Stop hook into settings.json"):
            mutated = prd.replace(row["line"], row["line"].replace(
                "reminds once at a turn end and never locks", claim), 1)
            self.assertEqual(1, len(stop_hook_claims(mutated)), claim)
        writer = ('hooks = settings.setdefault("hooks", {})\n'
                  'hooks["Stop"] = [entry]\n'
                  'Path(".claude/settings.json").write_text(json.dumps(settings))\n')
        self.assertEqual(["init.py"], stop_hook_writers({**sources, "init.py": writer}))
        self.assertEqual(["init.py"], stop_hook_writers({"init.py": writer}))
        self.assertEqual([], stop_hook_writers({"init.py": 'hooks["Stop"] = [entry]\n'}))
        no_settings = 'a["Stop"] = 1\nPath("f").write_text("x")\n'
        no_stop = 'settings = 1\nPath("f").write_text("x")\n'
        self.assertEqual([], stop_hook_writers({"x.py": no_settings, "y.py": no_stop}))
        self.assertEqual([], stop_hook_problems(prd, {**sources, "init.py": writer}))
        mutated = prd.replace("reminds once at a turn end and never locks",
                              "`init` installs the Stop hook into settings.json", 1)
        self.assertEqual(1, len(stop_hook_problems(mutated, sources)))
        self.assertEqual([], stop_hook_problems(mutated, {**sources, "init.py": writer}))

    def test_the_retired_learning_loop_is_not_described_as_current(self):
        """AC3. Mutant: restore either retired phrase, or a Learning loop row that names no
        failure class."""
        prd = PRD.read_text(encoding="utf-8")
        present = [phrase for phrase in _RETIRED if phrase in prd]
        self.assertEqual([], present, "the PRD still describes the retired learning loop")
        rows = [line for line in prd.splitlines() if line.startswith("| Learning loop |")]
        self.assertEqual(1, len(rows), "the Feature Inventory has no single Learning loop row")
        self.assertRegex(rows[0], r"failure class")


def ruled_citation_problems(root: Path) -> list[str]:
    """Why O5 does not cite exactly the `O5_CITES` pair (in either order, and nothing beside
    it), no outcome cites `UPGRADE_GOAL`, or a card no longer states the End goal one of them
    names; empty when none of these holds."""
    outcomes = sprint.prd_outcomes(root)
    goals = {c["name"]: dict(c["end_goals"]) for c in sprint.persona_cards(root)}
    problems = [f"{name}'s card states no End goal {number}"
                for name, number in (*O5_CITES, UPGRADE_GOAL) if number not in goals.get(name, {})]
    o5 = _CITE_RE.findall(outcomes.get("O5", ""))
    if sorted(o5) != sorted(O5_CITES):
        problems.append(f"O5 cites {o5}, not exactly "
                        + " and ".join(f"{n} End goal {g}" for n, g in O5_CITES))
    if not any(UPGRADE_GOAL in _CITE_RE.findall(text) for text in outcomes.values()):
        problems.append(f"no outcome cites {UPGRADE_GOAL[0]} End goal {UPGRADE_GOAL[1]}")
    return problems


def goal_drift(then: str, now: str) -> str:
    """Why card text `now` does not state `then`'s End goals word for word, or "" when it does.
    What follows them in `now` must open with an End goal numbered one after `then`'s last."""
    numbered = sprint._end_goals(then)
    base, current = end_goals_text(then), end_goals_text(now)
    if not numbered or any(text not in base for _, text in numbered):
        return "the baseline card states no End goals the section reader finds"
    if not current.startswith(base):
        return "an End goal differs from the baseline's"
    after = int(numbered[-1][0]) + 1
    if not re.fullmatch(rf"(?:\s*\n{after}[.)]\s[\s\S]*)?", current[len(base):]):
        return f"End goal {numbered[-1][0]} runs on past the baseline's words"
    return ""


def _outcome_line(prd: str, oid: str) -> str:
    m = re.search(rf"^\s*[-*]\s+\*\*{oid}:?\*\*.*$", prd, re.M)
    return m.group(0) if m else ""


class OutcomeCitationTests(unittest.TestCase):
    """US1082: O5 and Jonah Reyes's upgrade goal are cited as ruled, and each End goal of a
    persona the outcomes cite has one outcome. US1148: O5 cites the counterweight pair, O10 to
    O13 read as ruled, every End goal of the four cited personas has one outcome, and a goal
    serving O10 names Abena Osei and Graham Doyle. Each check is also run on mutated copies of
    the PRD and the cards, so each is shown able to refuse."""

    def setUp(self):
        self.prd = PRD.read_text(encoding="utf-8")
        self.outcomes = sprint.prd_outcomes(REPO)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        shutil.copytree(REPO / "sdlc-studio" / "personas", self.root / "sdlc-studio" / "personas")

    def problems_with(self, check, prd_text: str) -> list[str]:
        (self.root / "sdlc-studio" / "prd.md").write_text(prd_text, encoding="utf-8")
        return check(self.root)

    def upgrade_outcomes(self) -> list[str]:
        return [oid for oid, text in self.outcomes.items()
                if UPGRADE_GOAL in _CITE_RE.findall(text)]

    def test_every_end_goal_is_cited_once(self):
        """US1082 AC1 and US1148 AC4. Mutants: O5's Maya Okafor citation back on the End goal O3
        cites (her End goal 3), so a pair is cited twice and End goal 5 by none; the outcome
        citing Jonah Reyes's End goal 4 removed; O12 losing Graham Doyle's End goal 3; O11 also
        citing Abena Osei's End goal 1; every Graham Doyle citation dropped, which only the
        required personas refuse; O1 and O2 trading citations, which only the kept citations
        refuse; Graham Doyle's card removed with his citations, which only the required
        personas' card check refuses."""
        cited_once = functools.partial(citation_problems, required=CITED_PERSONAS)
        self.assertEqual([], cited_once(REPO))
        self.assertEqual([], kept_citation_problems(REPO))
        self.assertEqual([], self.problems_with(cited_once, self.prd))
        name, number = O5_CITES[0]
        o5_line = _outcome_line(self.prd, "O5")
        o3 = _CITE_RE.findall(self.outcomes.get("O3", ""))
        self.assertTrue(o5_line and o3, "no O5, or an O3 that cites no End goal")
        held = o3[0]
        holders = [oid for oid, text in self.outcomes.items() if held in _CITE_RE.findall(text)]
        back = o5_line.replace(f"{name}, End goal {number}", f"{held[0]}, End goal {held[1]}")
        self.assertNotEqual(o5_line, back)
        self.assertEqual(
            sorted([f"{held[0]} End goal {held[1]} is cited by "
                    f"{', '.join(sorted(holders + ['O5']))}",
                    f"no outcome cites {name} End goal {number}"]),
            sorted(self.problems_with(cited_once, self.prd.replace(o5_line, back, 1))))
        upgrade = self.upgrade_outcomes()
        self.assertTrue(upgrade, f"no outcome cites {UPGRADE_GOAL[0]} End goal {UPGRADE_GOAL[1]}")
        dropped = self.prd
        for oid in upgrade:
            dropped = dropped.replace(_outcome_line(self.prd, oid) + "\n", "", 1)
        self.assertEqual([f"no outcome cites {UPGRADE_GOAL[0]} End goal {UPGRADE_GOAL[1]}"],
                         self.problems_with(cited_once, dropped))
        o11, o12 = _outcome_line(self.prd, "O11"), _outcome_line(self.prd, "O12")
        lost = o12.replace("; Graham Doyle, End goal 3", "", 1)
        self.assertNotEqual(o12, lost)
        self.assertEqual(["no outcome cites Graham Doyle End goal 3"],
                         self.problems_with(cited_once, self.prd.replace(o12, lost, 1)))
        also = o11.replace("(Abena Osei, End goal 3)", "(Abena Osei, End goal 1; Abena Osei, "
                           "End goal 3)", 1)
        self.assertNotEqual(o11, also)
        self.assertEqual(["Abena Osei End goal 1 is cited by O10, O11"],
                         self.problems_with(cited_once, self.prd.replace(o11, also, 1)))
        no_graham = re.sub(r"; Graham Doyle, End goal \d+", "", self.prd)
        self.assertNotEqual(self.prd, no_graham)
        self.assertEqual([], self.problems_with(citation_problems, no_graham))
        self.assertEqual([f"no outcome cites Graham Doyle End goal {n}" for n in "123"],
                         self.problems_with(cited_once, no_graham))
        o1, o2 = _outcome_line(self.prd, "O1"), _outcome_line(self.prd, "O2")
        traded = self.prd.replace(o1, o1.replace("End goal 1)", "End goal 2)"), 1).replace(
            o2, o2.replace("End goal 2)", "End goal 1)"), 1)
        self.assertEqual([], self.problems_with(cited_once, traded))
        self.assertEqual(["O1 cites [('Maya Okafor', '2')], not [('Maya Okafor', '1')]",
                          "O2 cites [('Maya Okafor', '1')], not [('Maya Okafor', '2')]"],
                         self.problems_with(kept_citation_problems, traded))
        # one outcome naming a pair twice is one outcome's citation, not two
        m = _CITE_RE.search(o1)
        twice = o1.replace(m.group(0), f"{m.group(0)}; {m.group(0)}", 1)
        self.assertEqual([], self.problems_with(cited_once, self.prd.replace(o1, twice, 1)))
        # a required persona whose card is gone is refused, cited or not
        (self.root / "sdlc-studio" / "personas" / card_of("Graham Doyle").name).unlink()
        self.assertEqual(["Graham Doyle has no card that states an End goal"],
                         self.problems_with(cited_once, no_graham))

    def test_o5_and_jonahs_upgrade_goal_are_cited(self):
        """US1082 AC2 and US1148 AC3. Mutants: O5 citing either End goal of the pair alone;
        either re-pointed to another End goal; a third citation beside the pair, another End
        goal or a repeat of the pair's first; no outcome
        citing Jonah Reyes's End goal 4; a card that no longer states End goal 5 or End goal 6.
        The pair in the other order passes. The goals' words are read from the cards, never
        written here."""
        self.assertEqual([], ruled_citation_problems(REPO))
        self.assertEqual([], self.problems_with(ruled_citation_problems, self.prd))
        o5_line = _outcome_line(self.prd, "O5")
        group = re.search(r"\(([^()]*)\)$", o5_line)
        self.assertIsNotNone(group, "O5 ends on no parenthesised citation")
        given = group.group(1).split("; ")
        (maya, five), (abena, six) = O5_CITES
        swapped = self.prd.replace(o5_line, o5_line.replace(
            group.group(0), f"({'; '.join(reversed(given))})"), 1)
        self.assertNotEqual(self.prd, swapped)
        self.assertEqual([], self.problems_with(ruled_citation_problems, swapped))
        for other in (f"{maya}, End goal {five}", f"{abena}, End goal {six}",
                      f"{maya}, End goal 3; {abena}, End goal {six}",
                      f"{maya}, End goal {five}; {abena}, End goal 4",
                      f"{group.group(1)}; {maya}, End goal 1",
                      f"{group.group(1)}; {maya}, End goal {five}"):
            moved = self.prd.replace(o5_line, o5_line.replace(group.group(0), f"({other})"), 1)
            self.assertNotEqual(self.prd, moved)
            problems = self.problems_with(ruled_citation_problems, moved)
            self.assertEqual(1, len(problems), other)
            self.assertIn("O5 cites", problems[0])
        dropped = self.prd
        for oid in self.upgrade_outcomes():
            dropped = dropped.replace(_outcome_line(self.prd, oid) + "\n", "", 1)
        self.assertEqual([f"no outcome cites {UPGRADE_GOAL[0]} End goal {UPGRADE_GOAL[1]}"],
                         self.problems_with(ruled_citation_problems, dropped))
        for name, number in O5_CITES:
            card = self.root / "sdlc-studio" / "personas" / card_of(name).name
            text = card.read_text(encoding="utf-8")
            cut = re.sub(rf"^{number}\. .*\n", "", text, count=1, flags=re.M)
            self.assertNotEqual(text, cut)
            card.write_text(cut, encoding="utf-8")
            try:
                self.assertEqual([f"{name}'s card states no End goal {number}"],
                                 self.problems_with(ruled_citation_problems, self.prd))
            finally:
                card.write_text(text, encoding="utf-8")

    def test_o10_to_o13_read_as_ruled(self):
        """US1148 AC2. Mutants: a word of any of O10 to O13 changed; any of them missing,
        wrapped onto a second line, or bulleted `- **On**:`; O10 placed before O9; an outcome
        naming Rowan Achterberg."""
        self.assertEqual([], new_outcome_problems(REPO))
        self.assertEqual([], self.problems_with(new_outcome_problems, self.prd))
        for oid, text in NEW_OUTCOMES.items():
            line = _outcome_line(self.prd, oid)
            words = text.split(" ")
            k = len(words) // 2
            reworded = " ".join([*words[:k], "altered", *words[k + 1:]])
            for mutant in (line.replace(text, reworded), "", line.replace(", ", ",\n  ", 1),
                           line.replace(f"- **{oid}:** ", f"- **{oid}**: ", 1)):
                self.assertNotEqual(line, mutant)
                problems = self.problems_with(new_outcome_problems,
                                              self.prd.replace(line, mutant, 1))
                self.assertIn(f"{oid} is not the one line `- **{oid}:** ` and the ruled text",
                              problems, mutant)
        o9, o10 = _outcome_line(self.prd, "O9"), _outcome_line(self.prd, "O10")
        early = self.prd.replace(o10 + "\n", "", 1).replace(o9, f"{o10}\n{o9}", 1)
        self.assertEqual([f"the outcomes after O9 are {list(NEW_OUTCOMES)[1:]}, "
                          f"not {list(NEW_OUTCOMES)}"],
                         self.problems_with(new_outcome_problems, early))
        rowan = o9.replace(")", f"; {TOOLING_PRIMARY}, End goal 1)", 1)
        self.assertNotEqual(o9, rowan)
        self.assertEqual([f"O9 names {TOOLING_PRIMARY} (D0380)"],
                         self.problems_with(new_outcome_problems, self.prd.replace(o9, rowan, 1)))

    def test_a_goal_serving_o10_names_the_primary_and_the_approver(self):
        """US1148 AC5, through the shipped `sprint.py plan` on copies of the PRD and the cards,
        with HOME and the harness stores confined to the fixture. Mutants run here: O10 citing
        Abena Osei alone, so the line does not name Graham Doyle; O10's line removed, which the
        plan reports as no outcome O10 and flags as serving NONE."""
        home = self.root / "home"
        env = gitutil.git_env(HOME=str(home), XDG_DATA_HOME=str(home / ".local" / "share"),
                              CLAUDE_CONFIG_DIR=str(home / ".claude"),
                              COPILOT_HOME=str(home / ".copilot"), CODEX_HOME=str(home / ".codex"),
                              OPENCODE_DB=str(home / "opencode.db"))

        def plan(prd_text: str) -> str:
            (self.root / "sdlc-studio" / "prd.md").write_text(prd_text, encoding="utf-8")
            run = subprocess.run([sys.executable, str(SCRIPTS / "sprint.py"), "plan", "--root",
                                  str(self.root), "--stories", "Ready", "--sprint-goal",
                                  "One evidence pack per change", "--serves", "O10",
                                  "--no-fetch"], capture_output=True, text=True,
                                 cwd=str(self.root), env=env, check=False)
            return run.stdout + run.stderr

        said = plan(self.prd)
        self.assertEqual([], o10_trace_problems(said), said)
        o10 = _outcome_line(self.prd, "O10")
        one = o10.replace("; Graham Doyle, End goal 1; Graham Doyle, End goal 2)", ")", 1)
        self.assertNotEqual(o10, one)
        said = plan(self.prd.replace(o10, one, 1))
        self.assertEqual(["the goal serving O10 does not name Graham Doyle"],
                         o10_trace_problems(said), said)
        said = plan(self.prd.replace(o10 + "\n", "", 1))
        self.assertIn("the PRD lists no outcome O10", said)
        self.assertIn("goal serves: NONE", "\n".join(o10_trace_problems(said)), said)

    def test_jonahs_end_goals_are_unchanged(self):
        """AC3. Mutants: Jonah Reyes's End goal 4 reworded to fit an outcome, extended on its
        line or by a continuation line, or renumbered; End goal 1 reworded; a goal appended as
        End goal 6. One appended as End goal 5 leaves 1 to 4 as they were and passes."""
        card = card_of(UPGRADE_GOAL[0])
        self.assertIsNotNone(card, f"no card is headed {UPGRADE_GOAL[0]}")
        then = committed_text(GOALS_BASE, card)
        goals = sprint._end_goals(then)
        self.assertEqual(["1", "2", "3", "4"], [n for n, _ in goals],
                         f"the {GOALS_BASE} baseline moved")
        self.assertEqual("", goal_drift(then, card.read_text(encoding="utf-8")))
        self.assertEqual("", goal_drift(then, then.replace(goals[3][1],
                                                           f"{goals[3][1]}\n5. Another goal")))
        first, last = goals[0][1], goals[3][1]
        for mutant in (then.replace(last, f"Reworded {last}"),
                       then.replace(last, f"{last}, and more"),
                       then.replace(last, f"{last}\n   and more"),
                       then.replace(f"4. {last}", f"5. {last}"),
                       then.replace(last, f"{last}\n6. Another goal"),
                       then.replace(first, first.replace(first.split()[0], "Reword", 1))):
            self.assertNotEqual(then, mutant)
            self.assertTrue(goal_drift(then, mutant), mutant[-400:])


def release_baseline() -> tuple[str, str]:
    """`(baseline, on_main)` read from the tree (US1111): the semver core of the release
    package.json declares, the version `check_versions.py --strict` holds every spec's `Version:`
    to, and the next minor series, whose work on `main` sits beside it. `6.2.0` gives
    `("6.2.0", "6.3")`. Shared with the TRD and TSD refresh tests, so a release cut moves all
    three and no literal is left to edit."""
    version = check_versions.from_package_json(REPO)
    if not version:
        raise AssertionError("package.json declares no version, so no baseline can be read")
    core = version.split("-", 1)[0]
    major, minor = (int(part) for part in core.split(".")[:2])
    return core, f"{major}.{minor + 1}"


#: The release the PRD's baseline names and the work on `main` beside it (US1103 AC1), read from
#: the tree rather than pinned: a cut that moves package.json moves these with it.
BASELINE, ON_MAIN = release_baseline()
#: The release marker a row carried while its feature was untagged. Inside a code span it names
#: CHANGELOG.md's heading, as the release-cut row does, and is not read as a marker.
UNRELEASED = "[Unreleased]"
_VERSION_RE = re.compile(r"\bv?(\d+\.\d+\.\d+)\b")
_CODE_SPAN_RE = re.compile(r"`[^`\n]*`")
_SHIPPED_RE = re.compile(r"^\W*(?:Complete|Partial)\b")
_ID_RE = re.compile(r"\b(?:EP|CR|RFC)\d{4}\b")
#: The named fixture for US1103 AC2: RV0028's PRD-10 row, whose parenthesis lists the
#: capabilities with no inventory row. No code enumerates capabilities, so the review's own row
#: is the set, read from the review rather than copied here.
RV0028 = next((REPO / "sdlc-studio" / "reviews").glob("RV0028-*.md"))
PRD10_ROW = "| PRD-10 |"
#: How many capabilities that parenthesis names, so a misread of it cannot pass.
PRD10_COUNT = 8


def baseline_problems(prd: str) -> list[str]:
    """Why the header (above the first `---` rule) or the Feature Inventory's preamble (above
    its first table) does not name v`BASELINE` plus `ON_MAIN` on main, or names another
    `X.Y.Z` release; empty when both hold."""
    preamble = section(prd, "## 3. Feature Inventory").split("\n|", 1)[0]
    problems = []
    for where, text in (("header", prd.split("\n---\n", 1)[0]),
                        ("inventory preamble", preamble)):
        other = sorted({v for v in _VERSION_RE.findall(text) if v != BASELINE})
        if other:
            problems.append(f"the {where} names {', '.join(other)}, not only {BASELINE}")
        if not re.search(rf"\bv{re.escape(BASELINE)}\b.*?\bplus\b.*?\b{re.escape(ON_MAIN)}\b"
                         r".*?\bmain\b", text, re.S):
            problems.append(f"the {where} does not name v{BASELINE} plus {ON_MAIN} on main")
    return problems


def feature_rows(prd: str) -> list[dict[str, str]]:
    """Each data row of a table in the Feature Inventory, as {header cell: cell}, plus `line`."""
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in section(prd, "## 3. Feature Inventory").splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if header is None:
            header = cells
        elif not re.fullmatch(r"[\s|:-]+", line):
            rows.append({**dict(zip(header, cells)), "line": line})
    return rows


def unreleased_marks(prd: str) -> list[str]:
    """Each shipped feature row (Status Complete or Partial) and each Feature Details block
    whose `**Status:**` reads so, carrying `UNRELEASED`. A code span exempts the marker only in
    a row's Description cell (where the release-cut row quotes it) and in a block's text below
    its Status line: in any other cell, or on the Status line itself, it still counts (BG1168)."""
    marked = []
    for row in feature_rows(prd):
        if not _SHIPPED_RE.match(row.get("Status", "")):
            continue
        cells = {k: v for k, v in row.items() if k != "line"}
        if any(UNRELEASED in (_CODE_SPAN_RE.sub("", v) if k == "Description" else v)
               for k, v in cells.items()):
            marked.append(f"row {row.get('Feature', '?')}")
    details = section(prd, "### Feature Details (representative)")
    for block in re.split(r"^(?=#### )", details, flags=re.M):
        status = re.search(r"^\*\*Status:\*\*(.*)$", block, re.M)
        if not (block.startswith("#### ") and status and _SHIPPED_RE.match(status.group(1))):
            continue
        rest = block.replace(status.group(0), "", 1)
        if UNRELEASED in status.group(0) or UNRELEASED in _CODE_SPAN_RE.sub("", rest):
            marked.append(f"details {block.splitlines()[0][5:]}")
    return marked


def prd10_capabilities(review: str) -> list[str]:
    """The capabilities RV0028's PRD-10 row names in its parenthesis, in order."""
    row = next((line for line in review.splitlines() if line.startswith(PRD10_ROW)), "")
    m = re.search(r"\(([^()]+)\)", row)
    return [name.strip() for name in m.group(1).split(",")] if m else []


def _names(name: str) -> re.Pattern:
    """`name` as whole words, case-insensitive, a space and a hyphen between words read
    alike."""
    words = r"[\s-]+".join(re.escape(w) for w in re.split(r"[\s-]+", name.strip()))
    return re.compile(rf"(?<![\w-]){words}(?![\w-])", re.I)


def location_problems(location: str) -> list[str]:
    """Each comma-separated Location entry that resolves to no file under the skill or the
    repo root, or names a `#anchor` its file does not declare as `{#anchor}`."""
    bad = []
    for entry in (e.strip() for e in location.split(",") if e.strip()):
        path, _, anchor = entry.partition("#")
        found = next((p for p in (SCRIPTS.parent / path, REPO / path) if p.is_file()), None)
        if found is None:
            bad.append(f"{entry} is no file")
        elif anchor and f"{{#{anchor}}}" not in found.read_text(encoding="utf-8"):
            bad.append(f"{entry}: {path} declares no {{#{anchor}}}")
    return bad


@functools.lru_cache(maxsize=None)
def resolves(rec_id: str) -> bool:
    """Whether an artefact with this id exists, by `sdlc_md.find_by_id`. Cached, like
    `subcommands`."""
    return bool(sdlc_md.find_by_id(REPO, rec_id))


def capability_problems(prd: str, capabilities: list[str]) -> list[str]:
    """Why a capability has no Feature Inventory row whose Feature cell names it, or why a row
    that does is not shipped, names a Location or a `<script>.py <subcommand>` that does not
    resolve, or cites no epic or request, or one that does not resolve; empty when every
    capability has a sound row."""
    rows = feature_rows(prd)
    problems = []
    for name in capabilities:
        mine = [r for r in rows if _names(name).search(r.get("Feature", ""))]
        if not mine:
            problems.append(f"no Feature Inventory row names {name}")
            continue
        for row in mine:
            feature = row["Feature"]
            if not _SHIPPED_RE.match(row.get("Status", "")):
                problems.append(f"{feature}: Status {row.get('Status')!r} is not shipped")
            problems += [f"{feature}: {p}" for p in location_problems(row.get("Location", ""))]
            problems += [f"{feature}: {c}" for c in unknown_commands(row.get("Description", ""))]
            ids = _ID_RE.findall(row.get("Epic", ""))
            if not ids:
                problems.append(f"{feature}: the Epic cell names no epic or request")
            problems += [f"{feature}: {i} does not resolve" for i in ids if not resolves(i)]
    return problems


class PrdBaselineTests(unittest.TestCase):
    """US1103: the PRD's baseline reads v`BASELINE` plus `ON_MAIN` on main, no shipped row
    carries the release marker, and each capability RV0028 PRD-10 names has a sound inventory
    row. Each check is also run on a mutated copy, so it is shown able to refuse."""

    def setUp(self):
        self.prd = PRD.read_text(encoding="utf-8")

    def test_no_shipped_row_is_unreleased(self):
        """AC1. Mutants: one [Unreleased] marker left on a shipped row's Status, or on a
        Feature Details heading; the header's baseline back at v6.0.0, or the inventory's at
        v4.1.0; the header naming no `ON_MAIN` work on main; the header's baseline put back at the
        stale v6.1.0 plus 6.2 (US1111), v6.2.0 plus 6.3 (US1139) or v6.3.0 plus 6.4 (US1173);
        the header's Coverage line removed (US1139). Near misses that must pass: the marker
        inside a code span, and on a row whose Status is not shipped."""
        self.assertEqual([], baseline_problems(self.prd))
        self.assertEqual([], unreleased_marks(self.prd))
        rows = [r for r in feature_rows(self.prd) if _SHIPPED_RE.match(r.get("Status", ""))]
        self.assertGreater(len(rows), 40, "the Feature Inventory's rows were not read")
        row = rows[-1]
        status = f"| {row['Status']} |"
        self.assertIn(status, row["line"])
        marked = row["line"].replace(status, f"| {row['Status']} **{UNRELEASED}** |", 1)
        self.assertEqual([f"row {row['Feature']}"],
                         unreleased_marks(self.prd.replace(row["line"], marked, 1)))
        spanned = row["line"].replace(status, f"| {row['Status']} `{UNRELEASED}` |", 1)
        self.assertEqual([f"row {row['Feature']}"],
                         unreleased_marks(self.prd.replace(row["line"], spanned, 1)))
        cut = next(r for r in feature_rows(self.prd) if UNRELEASED in r["Description"])
        self.assertIn(f"`{UNRELEASED}`", cut["Description"])
        self.assertEqual([], unreleased_marks(self.prd), cut["Feature"])
        block = next(b for b in re.split(r"^(?=#### )", self.prd, flags=re.M)
                     if b.startswith("#### ") and re.search(r"^\*\*Status:\*\* Complete", b, re.M))
        status_line = re.search(r"^\*\*Status:\*\* Complete.*$", block, re.M).group(0)
        self.assertEqual([f"details {block.splitlines()[0][5:]}"],
                         unreleased_marks(self.prd.replace(status_line,
                                                           f"{status_line} `{UNRELEASED}`", 1)))
        planned = row["line"].replace(status, f"| Not Started **{UNRELEASED}** |", 1)
        self.assertEqual([], unreleased_marks(self.prd.replace(row["line"], planned, 1)))
        heading = re.search(r"^#### .+$", self.prd, re.M).group(0)
        self.assertEqual([f"details {heading[5:]} {UNRELEASED}"],
                         unreleased_marks(self.prd.replace(heading,
                                                           f"{heading} {UNRELEASED}", 1)))
        coverage = re.search(r"\*\*Coverage:\*\* v\S+ as cut, plus the \S+ work", self.prd)
        self.assertIsNotNone(coverage, "the header states no Coverage baseline")
        preamble = section(self.prd, "## 3. Feature Inventory").split("\n|", 1)[0]
        self.assertIn(f"v{BASELINE}", preamble)
        unnamed = [f"the {{}} does not name v{BASELINE} plus {ON_MAIN} on main"]
        for old, new, expected in (
                (coverage.group(0), "**Coverage:** v6.0.0 as cut, plus the 6.1 work",
                 [f"the header names 6.0.0, not only {BASELINE}"] + unnamed),
                (coverage.group(0), f"**Coverage:** v{BASELINE} as cut", unnamed),
                (coverage.group(0), "**Coverage:** v6.1.0 as cut, plus the 6.2 work",
                 [f"the header names 6.1.0, not only {BASELINE}"] + unnamed),
                (coverage.group(0), "**Coverage:** v6.2.0 as cut, plus the 6.3 work",
                 [f"the header names 6.2.0, not only {BASELINE}"] + unnamed),
                (coverage.group(0), "**Coverage:** v6.3.0 as cut, plus the 6.4 work",
                 [f"the header names 6.3.0, not only {BASELINE}"] + unnamed),
                (coverage.group(0), "", unnamed),
                (preamble, preamble.replace(f"v{BASELINE}", "v4.1.0"),
                 [f"the inventory preamble names 4.1.0, not only {BASELINE}"] + unnamed)):
            where = "inventory preamble" if old == preamble else "header"
            mutant = self.prd.replace(old, new, 1)
            self.assertNotEqual(self.prd, mutant, new)
            self.assertEqual(sorted(e.format(where) for e in expected),
                             sorted(baseline_problems(mutant)), new)

    def test_every_capability_since_july_has_a_row(self):
        """AC2. Mutants: one PRD-10 capability's row dropped, moved below the Feature Inventory,
        or left named only in another row's Description; a row whose Location names no file or
        an undeclared anchor, whose Description names a subcommand its script lacks, whose Epic
        cell cites nothing or an id that does not resolve, or whose Status is not shipped."""
        capabilities = prd10_capabilities(RV0028.read_text(encoding="utf-8"))
        self.assertEqual(PRD10_COUNT, len(capabilities), capabilities)
        self.assertEqual([], capability_problems(self.prd, capabilities))
        rows = feature_rows(self.prd)
        for name in capabilities:
            row = next(r for r in rows if _names(name).search(r["Feature"]))
            line = row["line"] + "\n"
            dropped = self.prd.replace(line, "", 1)
            self.assertEqual([f"no Feature Inventory row names {name}"],
                             capability_problems(dropped, [name]))
            # moved as a whole one-row table, so a reader of the whole PRD would count it
            cells = [k for k in row if k != "line"]
            table = (f"| {' | '.join(cells)} |\n| {' | '.join('---' for _ in cells)} |\n{line}")
            moved = dropped.replace("## 4. Functional Requirements\n",
                                    f"## 4. Functional Requirements\n\n{table}", 1)
            self.assertNotEqual(dropped, moved)
            self.assertEqual([f"no Feature Inventory row names {name}"],
                             capability_problems(moved, [name]))
        other = rows[0]
        prose = self.prd.replace(f"| {other['Description']} |",
                                 f"| {other['Description']}; the {capabilities[0]} |", 1)
        prose = prose.replace(next(r for r in rows if _names(capabilities[0]).search(
            r["Feature"]))["line"] + "\n", "", 1)
        self.assertEqual([f"no Feature Inventory row names {capabilities[0]}"],
                         capability_problems(prose, capabilities[:1]))
        row = next(r for r in rows if _names(capabilities[0]).search(r["Feature"]))
        cells = (
            (row["Location"], f"{row['Location']}, scripts/nosuch.py", "scripts/nosuch.py is no"),
            (row["Location"], f"{row['Location']}, help/sprint.md#nosuch", "declares no {#nosuch}"),
            (row["Description"], f"{row['Description']}; `sprint.py nosuch`", "sprint.py nosuch"),
            (row["Epic"], "EP9999", "EP9999 does not resolve"),
            (row["Epic"], "none", "names no epic or request"),
            (row["Status"], "Not Started", "'Not Started' is not shipped"))
        for old, new, says in cells:
            mutant = self.prd.replace(row["line"],
                                      row["line"].replace(f"| {old} |", f"| {new} |", 1), 1)
            self.assertNotEqual(self.prd, mutant, new)
            problems = capability_problems(mutant, capabilities[:1])
            self.assertEqual(1, len(problems), (new, problems))
            self.assertTrue(problems[0].startswith(f"{row['Feature']}: "), problems)
            self.assertIn(says, problems[0])
        # the readers themselves: a review row with no parenthesis names nothing, and a name is
        # matched as whole words, a hyphen and a space alike
        self.assertEqual([], prd10_capabilities(f"{PRD10_ROW} Important | x | none | CR0647 |"))
        self.assertIsNone(_names("constitution").search("Constitutional review"))
        self.assertIsNotNone(_names("risk-banded review").search("Risk banded review"))



# --- US1104: the business rules, NFRs and cost model match the code; counts are bands ---------

SKILL = SCRIPTS.parent
#: The Verify code span the PRD names; read as one token, so its asterisks are not bold marks.
_VERIFY_SPAN = "`- **Verify:**`"
#: A type a sentence names, as written, to its `sdlc_md` type id.
_TYPE_WORDS = {"story": "story", "stories": "story", "bug": "bug", "bugs": "bug", "cr": "cr",
               "crs": "cr", "rfc": "rfc", "rfcs": "rfc", "epic": "epic", "epics": "epic"}
_TYPE_RE = re.compile(r"\b(" + "|".join(_TYPE_WORDS) + r")\b", re.I)
#: Where the PRD says which types execute their Verify lines, and which are prose: the types
#: are read from the clause before each phrase, back to the last `.`, `;`, `:` or `(`.
_EXECUTES_RE = re.compile(r"\bcarr(?:y|ies) executable VERIFY lines")
_PARSES_RE = re.compile(r"\bParses the VERIFY lines of ([^(.]*?)criteria")
_PROSE_RE = re.compile(r"\bacceptance criteria are prose")
#: The grooming checks `sprint.breakdown` enforces, as its source names them, and the words a
#: statement of the groomed definition must use for each. A check the code adds with no entry
#: here fails the test rather than passing unread.
_GROOMING_CALL_RE = re.compile(r"""_enforced\(\s*["'](grooming\.[a-z]+)["']\s*\)""")
_GROOMING_WORDS = {"grooming.affects": r"`Affects:`", "grooming.points": r"\bsize\b",
                   "grooming.acs": r"\bacceptance criteria\b",
                   "grooming.split": r"\bsplit ceiling\b"}
#: Each way `conformance.unit_is_ungroomed` finds criteria ungroomed, as `sprint.py` renders
#: them (`_AC_MISS_RENDERINGS`), and the words the detail criterion must use for it. The last is
#: the one a summary is most likely to drop, so every statement must name it.
_AC_SHAPE_WORDS = {"no-criteria": r"\babsent\b", "placeholder": r"\bplaceholder\b",
                   "derived-only": r"\bderived\b",
                   "no-verifier": r"`Verify:` line or (?:an? )?`manual` marker"}
#: A network call in a script's own source: a `gh` argv, a git `fetch` argument, or the stdlib
#: HTTP clients. Keyed by kind so a scan that matches nothing of one kind is caught.
_NETWORK_RES = {
    "gh": re.compile(r"""[\[(]\s*["']gh["']"""),
    "fetch": re.compile(r"""["']fetch["']\s*,\s*["']origin["']"""),
    "git-verb": re.compile(r"""(?:["']git["']\s*,|\b_git\([^,\n]*,)\s*"""
                           r"""["'](?:ls-remote|fetch|pull|push|clone)["']|["']ls-remote["']"""),
    "http": re.compile(r"urlopen\(|urllib\.request|http\.client|^import socket", re.M),
}
#: A write primitive in a script's own source.
_WRITE_RE = re.compile(r"""\.write_(?:text|bytes)\(|\batomic_write\(|\.mkdir\(|\bos\.replace\(|"""
                       r"""\.unlink\(|\bshutil\.(?:copy\w*|move|rmtree)\(|"""
                       r"""\bopen\([^)\n]*["'][wax]b?\+?["']""")
#: How each script the Performance NFR names as writing nothing is run on a fixture to show it.
#: A script named there with no entry here fails the test, so the claim cannot outrun the proof.
READONLY_RUNS = {"status.py": [], "next_id.py": ["allocate", "--type", "story"],
                 "readiness.py": ["check", "--stories", "Ready"],
                 "handoff.py": ["show", "--id", "US0001"]}
_SENTENCE_RE = re.compile(r"(?<=[.;])\s+")
#: A derived count as written: a number, or a number word, with the band markers doc_freshness
#: reads (`about N`, `~N`, `N+`).
_NUM = (r"(?P<approx>\b(?:about|around|roughly|approximately)\s+|~\s*)?"
        r"(?P<n>\b\d[\d,]*|\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b)"
        r"(?P<floor>\+)?")
_WORD_NUMBERS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve".split())}
#: Each count the PRD states or stated before US1104 (the `lib/` module count), with how the
#: tree measures it. The three doc_freshness also reads are measured by its own
#: `_CENSUS_MEASURES`, so the two cannot disagree about one count.
COUNT_CLAIMS = {
    "scripts": (_NUM + r"[\s-]+(?:[a-z-]+\s+){0,2}scripts\b",
                lambda: doc_freshness._CENSUS_MEASURES["scripts"](SKILL)),
    "reference files": (_NUM + r"[\s-]+(?:reference\s+files?\b|`reference-\*\.md`)",
                        lambda: doc_freshness._CENSUS_MEASURES["reference files"](SKILL)),
    "help files": (_NUM + r"[\s-]+(?:help\s+files?\b|`help/\*\.md`)",
                   lambda: doc_freshness._CENSUS_MEASURES["help files"](SKILL)),
    "templates": (_NUM + r"[\s-]+templates\b",
                  lambda: sum(1 for p in (SKILL / "templates").rglob("*") if p.is_file())),
    "best-practice guides": (_NUM + r"[\s-]+best-practice\s+guides?\b",
                             lambda: len(list((SKILL / "best-practices").glob("*.md")))),
    "lib modules": (_NUM + r"[\s-]+modules?\b",
                    lambda: len([p for p in (SCRIPTS / "lib").glob("*.py")
                                 if p.name != "__init__.py"])),
    "SKILL.md lines": (r"SKILL\.md`?\s+" + _NUM + r"\s+lines\b",
                       lambda: len((SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines())),
}
#: A sentence narrating a past state of the document, or a change tied to a release: the
#: per-ship history RV0028 PRD-25 found in the feature blocks, which the changelog table holds.
_HISTORY_RE = re.compile(r"\bused to (?:list|carry|say|state|read)\b|"
                         r"\b(?:was|were) (?:retired|renamed|added|removed|fixed) in v?\d", re.I)
#: The history US1104 moved out of §10 (RV0028 PRD-25), named so the move is checked both ways.
MOVED_HISTORY = ("BG0133", "BG0136", "2026-07-04")
#: The bug that holds the engagement floor's `adopt_after` escape (US1104 AC3).
FLOOR_BUG = "BG0959"
#: The open bugs the Feature Details criteria are held by, so a criterion reassigned to another of
#: them is compared with the bug it came from (BG1162).
HOLDERS = ("BG1023", "BG1063", FLOOR_BUG)
_HELD_RE = re.compile(r"\bHeld by (BG-?[0-9A-Z]+)\b")


def body(prd: str) -> str:
    """The PRD above its `## Changelog`, newlines and blockquote markers folded to spaces, the
    Verify code span read as one token and bold markers dropped: the current claims as prose."""
    text = prd.split("\n## Changelog", 1)[0].replace(_VERIFY_SPAN, "VERIFY")
    return " ".join(re.sub(r"^\s*>\s?", "", text, flags=re.M).replace("**", "").split())


def flat(text: str) -> str:
    """`text` folded as `body` folds the PRD, for a section already sliced out."""
    return " ".join(text.replace(_VERIFY_SPAN, "VERIFY").replace("**", "").split())


def types_named(text: str) -> set[str]:
    return {_TYPE_WORDS[w.lower()] for w in _TYPE_RE.findall(text)}


def clauses_before(text: str, phrase: re.Pattern) -> list[str]:
    """The clause before each match of `phrase`, back to the last `.`, `;`, `:` or `(`."""
    return [text[max(text.rfind(c, 0, m.start()) for c in ".;:(") + 1:m.start()]
            for m in phrase.finditer(text)]


def verifier_problems(prd: str) -> list[str]:
    """Why a sentence that says which types execute their Verify lines does not name exactly
    `sdlc_md.EXECUTES_VERIFIERS`, or why one that says which criteria are prose does not name
    exactly the finding types outside it; empty when every such sentence agrees with the code.
    Too few such sentences is a problem too, so a misread cannot pass."""
    text = body(prd)
    executes = set(sdlc_md.EXECUTES_VERIFIERS)
    prose = {t for t in sdlc_md.FINDING_TYPES if not sdlc_md.executes_verifiers(t)}
    said = clauses_before(text, _EXECUTES_RE) + _PARSES_RE.findall(text)
    problems = [] if len(said) >= 3 else [(f"{len(said)} sentence(s) say which types execute "
                                           "their Verify lines; the PRD states it three times")]
    problems += [f"says {sorted(types_named(s))} execute their Verify lines, not "
                 f"{sorted(executes)}: {s.strip()!r}" for s in said if types_named(s) != executes]
    for s in clauses_before(text, _PROSE_RE):
        if types_named(s) != prose:
            problems.append(f"says {sorted(types_named(s))} carry prose criteria, not "
                            f"{sorted(prose)}: {s.strip()!r}")
    return problems


def groomed_statements(prd: str) -> dict[str, str]:
    """Each place the PRD defines a groomed unit: the business rule, the breakdown gate's
    first detail criterion and its inventory row."""
    rules = section(prd, "### Business Logic Rules")
    rule = next((b for b in re.split(r"^- ", rules, flags=re.M) if "The breakdown gate" in b), "")
    details = re.split(r"^(?=#### )", section(prd, "### Feature Details (representative)"),
                       flags=re.M)
    gate = next((b for b in details if b.startswith("#### Breakdown gate")), "")
    criterion = next(iter(re.findall(r"^- \[[ x]\] (.*)$", gate, re.M)), "")
    row = next((r["Description"] for r in feature_rows(prd) if r.get("Feature") ==
                "Breakdown gate"), "")
    return {"business rule": flat(rule), "detail criterion": criterion, "inventory row": row}


def grooming_problems(prd: str) -> list[str]:
    """Why a statement of the groomed definition leaves out a grooming check `sprint.breakdown`
    enforces, read from its source, or a way `sprint._AC_MISS_RENDERINGS` names criteria
    ungroomed (every way for the detail criterion, `no-verifier` for all three), or names a
    split-ceiling default other than `sdlc_md.POINTS_SPLIT_ABOVE` or a config key the code does
    not read."""
    src = (SCRIPTS / "sprint.py").read_text(encoding="utf-8")
    checks = sorted(set(_GROOMING_CALL_RE.findall(src)))
    problems = [] if checks else ["sprint.py enforces no `grooming.*` check this reader can see"]
    for where, text in groomed_statements(prd).items():
        if not text:
            problems.append(f"the PRD has no {where} defining a groomed unit")
            continue
        for shape in sprint._AC_MISS_RENDERINGS:
            words = _AC_SHAPE_WORDS.get(shape)
            if words is None:
                problems.append(f"sprint.py renders criteria ungroomed as {shape}, which no "
                                f"statement is read for")
            elif (where == "detail criterion" or shape == "no-verifier") \
                    and not re.search(words, text):
                problems.append(f"the {where} leaves out criteria that are {shape}")
        for check in checks:
            words = _GROOMING_WORDS.get(check)
            if words is None:
                problems.append(f"sprint.py enforces {check}, which no statement is read for")
            elif not re.search(words, text, re.I):
                problems.append(f"the {where} leaves out {check}: {text[:120]!r}")
        for n in re.findall(r"\bdefault (\d+)\b", text):
            if int(n) != sdlc_md.POINTS_SPLIT_ABOVE:
                problems.append(f"the {where} gives the split ceiling's default as {n}; it is "
                                f"{sdlc_md.POINTS_SPLIT_ABOVE}")
        for key in re.findall(r"`(sprint\.[a-z_.]+)`", text):
            if f'"{key}"' not in src:
                problems.append(f"the {where} names `{key}`, which sprint.py does not read")
    return problems


def script_sources() -> dict[str, str]:
    """Each shipped script under `scripts/` and `scripts/lib/`, by file name, with its source."""
    paths = sorted(SCRIPTS.glob("*.py")) + sorted((SCRIPTS / "lib").glob("*.py"))
    return {p.name: p.read_text(encoding="utf-8") for p in paths}


def network_scripts(sources: dict[str, str]) -> dict[str, set[str]]:
    """For each kind of network call, the scripts whose own source makes one."""
    return {kind: {name for name, src in sources.items() if rx.search(src)}
            for kind, rx in _NETWORK_RES.items()}


#: A sentence's word for fetching, and the negation that says a thing does not (BG1180).
_FETCH_RE = re.compile(r"\bfetch(?:es|ed|ing)?\b", re.I)
_NO_FETCH_RE = re.compile(r"\b(?:never|not|no|without)\s+(?:\w+\s+)?fetch", re.I)


def network_problems(prd: str, sources: dict[str, str]) -> list[str]:
    """Why the Security NFR's list of scripts that reach the network differs from the scripts
    whose source makes a network call, or why any sentence of the PRD says id allocation fetches
    when `next_id.py` makes no fetch (or that it never does, when it makes one); empty when
    they agree."""
    security = section(prd, "### Security")
    found = set().union(*network_scripts(sources).values())
    named = set(re.findall(r"`([a-z_]+\.py)`", security))
    problems = [f"the Security NFR does not name {s}, whose source reaches the network"
                for s in sorted(found - named)]
    problems += [f"the Security NFR names {s}, whose source makes no network call"
                 for s in sorted(named - found)]
    fetches = "next_id.py" in found
    for sentence in _SENTENCE_RE.split(body(prd)):
        if re.search(r"\bid allocation\b", sentence, re.I) and _FETCH_RE.search(sentence) and \
                (not _NO_FETCH_RE.search(sentence)) != fetches:
            problems.append(f"the PRD misstates whether id allocation fetches: {sentence!r}")
    return problems


def readonly_claims(prd: str) -> tuple[list[str], list[str]]:
    """The scripts the Performance NFR says write nothing in the workspace, and the scripts it
    names elsewhere in that section, as `<name>.py` code spans."""
    performance = flat(section(prd, "### Performance"))
    readonly: list[str] = []
    for sentence in _SENTENCE_RE.split(performance):
        if "write nothing in the workspace" in sentence:
            readonly += re.findall(r"`([a-z_]+\.py)`", sentence.split("write nothing")[0])
    others = [s for s in re.findall(r"`([a-z_]+\.py)`", performance) if s not in readonly]
    return readonly, others


def readonly_problems(prd: str, sources: dict[str, str]) -> list[str]:
    """Why a script the Performance NFR says writes nothing has a write primitive in its own
    source or no fixture run to show it, or why a script it names as writing has none."""
    readonly, writers = readonly_claims(prd)
    problems = [] if readonly else ["the Performance NFR names no script that writes nothing"]
    for name in readonly:
        if name not in sources:
            problems.append(f"{name} is named as writing nothing and is no script")
        elif _WRITE_RE.search(sources[name]):
            problems.append(f"{name} is named as writing nothing; its source writes: "
                            f"{_WRITE_RE.search(sources[name]).group(0)!r}")
        elif name not in READONLY_RUNS:
            problems.append(f"{name} is named as writing nothing and has no fixture run")
    problems += [f"{name} is named as writing and its source has no write primitive"
                 for name in writers if name in sources and not _WRITE_RE.search(sources[name])]
    return problems


def workspace_writes(scripts: list[str]) -> list[str]:
    """Run each script with its `READONLY_RUNS` arguments on a fixture workspace holding one
    story, the release check off, and name each file it created, changed or removed."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "version_check:\n  enabled: false\n", encoding="utf-8")
        (root / "sdlc-studio" / "stories" / "US0001-a.md").write_text(
            "# US0001: A\n\n> **Status:** Ready\n> **Points:** 1\n> **Affects:** a.py\n\n"
            "## Acceptance Criteria\n\n- **AC1:** Given x, when y, then z\n", encoding="utf-8")

        def snapshot() -> dict[str, bytes]:
            return {p.relative_to(root).as_posix() + ("/" if p.is_dir() else ""):
                    (b"" if p.is_dir() else p.read_bytes()) for p in root.rglob("*")}

        changed: list[str] = []
        for name in scripts:
            before = snapshot()
            subprocess.run([sys.executable, str(SCRIPTS / name), *READONLY_RUNS[name],
                            "--root", str(root)], capture_output=True, text=True, cwd=root,
                           check=False)
            after = snapshot()
            changed += [f"{name}: {path}" for path in sorted(set(before) | set(after))
                        if before.get(path) != after.get(path)]
        return changed


def cost_problems(prd: str) -> list[str]:
    """Why the PRD states the tokens-per-point seed as the rate a plan prices from, pins a
    measured rate, or leaves out where the measured rate and its override are read; empty when
    it states the rate as `sprint.tokens_per_point` decides it."""
    seed = f"{sprint.POINTS_RATE_SEED:,}"
    problems = []
    for sentence in _SENTENCE_RE.split(body(prd)):
        for figure in re.findall(r"(\d[\d,]{3,})\s+tokens(?:[\s-]+per[\s-]+point)", sentence):
            if figure == seed and not re.search(r"\bseed\b", sentence):
                problems.append(f"states the seed {seed} as the rate, not as the seed: "
                                f"{sentence!r}")
            elif figure != seed:
                problems.append(f"pins {figure} tokens per point; the measured rate is derived "
                                f"from the history each time it is read: {sentence!r}")
    cost = section(prd, "### The cost model: a falsified predictor, then Fibonacci points")
    if "velocity" not in (subcommands("retro") or ()) or "`retro.py velocity`" not in cost:
        problems.append("the cost model does not name `retro.py velocity`, which prints the "
                        "measured rate")
    if f"`{sprint.TOKENS_PER_POINT_KEY}`" not in cost:
        problems.append(f"the cost model does not name the override "
                        f"`{sprint.TOKENS_PER_POINT_KEY}`")
    if seed not in cost:
        problems.append(f"the cost model does not name the seed, {seed}")
    key = f"`{sprint.TOKENS_PER_POINT_KEY}`"
    for sentence in _SENTENCE_RE.split(flat(cost)):
        if key in sentence and not 0 <= sentence.find("measured") < sentence.find("unless") \
                < sentence.find(key):
            problems.append(f"the cost model does not say the override {key} replaces the "
                            f"measured rate (the override wins in `sprint.tokens_per_point`): "
                            f"{sentence!r}")
    return problems


def count_problems(prd: str) -> list[str]:
    """Why a derived count `COUNT_CLAIMS` reads is pinned (a bare number where the rule asks
    for a band) or is a band the tree's measure sits outside, by doc_freshness's ratio."""
    text, ratio = body(prd), doc_freshness._FLOOR_STALE_RATIO
    problems = []
    for name, (pattern, measure) in COUNT_CLAIMS.items():
        matches = list(re.finditer(pattern, text, re.I))
        actual = measure() if matches else None
        for m in matches:
            raw = m.group("n").replace(",", "").lower()
            n = _WORD_NUMBERS[raw] if raw in _WORD_NUMBERS else int(raw)
            if m.group("floor"):
                ok, band = n <= actual < n * ratio, f"[{n}, {n * ratio:g})"
            elif m.group("approx"):
                ok, band = n / ratio <= actual < n * ratio, f"[{n / ratio:g}, {n * ratio:g})"
            else:
                problems.append(f"{name}: {m.group(0)!r} is pinned; state it as a band")
                continue
            if not ok:
                problems.append(f"{name}: {m.group(0)!r} holds in {band}; {actual} counted")
    return problems


def history_problems(prd: str) -> list[str]:
    """Each sentence above the changelog that narrates per-ship history, and each item of
    `MOVED_HISTORY` named above the changelog or missing from its table."""
    text = body(prd)
    table = section(prd, "## Changelog")
    problems = [f"per-ship history outside the changelog: {s!r}"
                for s in _SENTENCE_RE.split(text) if _HISTORY_RE.search(s)]
    problems += [f"{item} is named above the changelog" for item in MOVED_HISTORY if item in text]
    problems += [f"the changelog table does not record {item}" for item in MOVED_HISTORY
                 if item not in table]
    return problems


@functools.lru_cache(maxsize=None)
def bug_status(bug_id: str) -> str:
    """A bug's Status, read from its own file. Cached, like `resolves`."""
    found = sdlc_md.find_by_id(REPO, bug_id)
    if not found:
        raise AssertionError(f"{bug_id} has no file")
    return sdlc_md.extract_field(Path(found[0]).read_text(encoding="utf-8"), "Status") or ""


def detail_blocks(prd: str) -> dict[str, dict]:
    """Each Feature Details block, by heading name: its Status and its criteria as
    (ticked, text) pairs."""
    blocks = {}
    for block in re.split(r"^(?=#### )", section(prd, "### Feature Details (representative)"),
                          flags=re.M):
        if not block.startswith("#### "):
            continue
        name = re.sub(r"\s*\(.*$", "", block.splitlines()[0][5:]).strip()
        status = re.search(r"^\*\*Status:\*\*\s*(\w+)", block, re.M)
        blocks[name] = {"status": status.group(1) if status else "",
                        "criteria": [(mark == "x", text) for mark, text in
                                     re.findall(r"^- \[([ x])\] (.*)$", block, re.M)]}
    return blocks


@functools.lru_cache(maxsize=None)
def bug_words(bug_id: str) -> set[str]:
    """The words of five letters or more in a bug's own file, lower-cased."""
    found = sdlc_md.find_by_id(REPO, bug_id)
    return set(re.findall(r"[a-z_]{5,}", Path(found[0]).read_text(encoding="utf-8").lower()))


def holder_problems(prd: str, words_of=bug_words) -> list[str]:
    """Why a criterion's `Held by BG` clause names a bug that matches its words less well than
    another bug the PRD names as a holder: a criterion reassigned to the wrong open bug (BG1162).
    The clause is the text from the bug id to the end of the criterion."""
    clauses = []
    for name, block in detail_blocks(prd).items():
        for i, (_, text) in enumerate(block["criteria"], 1):
            for m in _HELD_RE.finditer(text):
                clauses.append((name, i, m.group(1),
                                set(re.findall(r"[a-z_]{5,}", text[m.end():].lower()))))
    holders = {c[2] for c in clauses} | set(HOLDERS)
    problems = []
    for name, i, bug, said in clauses:
        scores = {b: len(said & words_of(b)) for b in holders}
        better = sorted(b for b, n in scores.items() if n > scores[bug])
        if better:
            problems.append(f"{name} criterion {i} names {bug} as its holder, but its words "
                            f"match {better[0]} better ({scores[better[0]]} against "
                            f"{scores[bug]})")
    return problems


def tick_problems(prd: str, status_of=bug_status) -> list[str]:
    """Why a Feature Details criterion is unticked without naming the open bug that holds it,
    ticked while it names one, or names one that is no longer open; why a block with an
    unticked criterion does not read Partial, or one without reads otherwise; and why the
    inventory row of a detailed feature does not carry its block's Status."""
    problems = []
    rows = {r.get("Feature"): r.get("Status", "") for r in feature_rows(prd)}
    for name, block in detail_blocks(prd).items():
        held = False
        for i, (ticked, text) in enumerate(block["criteria"], 1):
            bugs = _HELD_RE.findall(text)
            open_bugs = [b for b in bugs if not sdlc_md.is_terminal_status("bug", status_of(b))]
            if not ticked and not open_bugs:
                problems.append(f"{name} criterion {i} is unticked and no open bug holds it")
            if ticked and bugs:
                problems.append(f"{name} criterion {i} is ticked and names {bugs} as holding it")
            problems += [f"{name} criterion {i} is held by {b}, which is {status_of(b)}"
                         for b in bugs if b not in open_bugs]
            held = held or not ticked
        want = "Partial" if held else "Complete"
        if block["status"] != want:
            problems.append(f"{name} reads {block['status']!r}; its criteria make it {want}")
        if rows.get(name, want) != block["status"]:
            problems.append(f"the {name} row reads {rows.get(name)!r}; its block reads "
                            f"{block['status']!r}")
    return problems


#: The commit that cut v6.1.0, after which every commit that changed the PRD owes the Changelog
#: table a row naming its unit (BG1168).
SINCE_6_1_0 = "ddc3cda0"
_UNIT_ID_RE = re.compile(r"\b(?:US|BG|CR|RFC|EP|D)\d{4}\b")


def prd_commits(since: str = SINCE_6_1_0) -> list[tuple[str, str]] | None:
    """Each (hash, subject) of a commit after `since` that changed the PRD, or None when the
    history cannot answer (no clone, or a shallow one without `since`)."""
    env = gitutil.git_env()
    known = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"{since}^{{commit}}"],
                           cwd=REPO, capture_output=True, text=True, env=env, check=False)
    if known.returncode:
        return None
    run = subprocess.run(["git", "log", "--format=%H%x09%s", f"{since}..HEAD", "--",
                          "sdlc-studio/prd.md"], cwd=REPO, capture_output=True, text=True,
                         env=env, check=False)
    if run.returncode:
        return None
    return [tuple(line.split("\t", 1)) for line in run.stdout.splitlines() if line]


def revision_problems(prd: str, commits: list[tuple[str, str]]) -> list[str]:
    """Each commit whose subject names no unit that the PRD's Changelog table names, and whose
    hash it does not name either; empty when every content change has its row."""
    table = section(prd, "## Changelog")
    problems = []
    for sha, subject in commits:
        units = _UNIT_ID_RE.findall(subject)
        if not any(re.search(rf"\b{u}\b", table) for u in units) and sha[:8] not in table:
            problems.append(f"{sha[:8]} ({subject[:60]}) changed the PRD and the Changelog table "
                            f"names none of {units or 'its hash'}")
    return problems


class PrdRulesTests(unittest.TestCase):
    """US1104: the PRD's business rules, NFRs and cost model state what the code decides, its
    derived counts are bands the tree's measures sit inside, and the engagement floor reads
    Partial while BG0959 is open. Each check is also run on a mutated copy of the PRD, and the
    code-read facts on a patched authority, so it is shown able to refuse."""

    def setUp(self):
        self.prd = PRD.read_text(encoding="utf-8")
        self.sources = script_sources()

    def mutate(self, old: str, new: str) -> str:
        mutant = self.prd.replace(old, new, 1)
        self.assertNotEqual(self.prd, mutant, old)
        return mutant

    def test_rules_nfrs_and_cost_model_match_the_code(self):
        """AC1. Mutants: a sentence naming a type outside `sdlc_md.EXECUTES_VERIFIERS` as
        executing, or omitting one inside it, a prose clause dropping RFC, and the authority
        itself patched; the groomed definition leaving out the criteria check, the Verify-or-
        manual requirement, the placeholder shape or the split ceiling, or giving its default
        as 13; the Security NFR dropping `release_cut.py`, or naming `next_id.py`, or saying id
        allocation fetches; `critic.py` named as writing nothing, and a writer whose source no
        longer writes; the seed stated as the rate a plan prices from, and a measured rate
        pinned."""
        self.assertEqual([], verifier_problems(self.prd))
        self.assertEqual([], grooming_problems(self.prd))
        self.assertEqual([], network_problems(self.prd, self.sources))
        self.assertEqual([], readonly_problems(self.prd, self.sources))
        self.assertEqual([], cost_problems(self.prd))
        readonly, _ = readonly_claims(self.prd)
        self.assertEqual([], workspace_writes(readonly))
        # every kind of network call is found somewhere, so the scan is not vacuous
        self.assertTrue(all(network_scripts(self.sources).values()),
                        network_scripts(self.sources))

        rule = "A story and a bug carry executable"
        for new, says in (("A story carries executable", "['story'] execute"),
                          ("A story, a bug and an epic carry executable", "'epic', 'story']")):
            problems = verifier_problems(self.mutate(rule, new))
            self.assertEqual(1, len(problems), problems)
            self.assertIn(says, problems[0])
        note = "> A **story** and a **bug** carry executable"
        self.assertEqual(1, len(verifier_problems(self.mutate(note, "> Only a **story** carries "
                                                                    "executable"))))
        prose = verifier_problems(self.mutate("CR and RFC\n> acceptance", "CR\n> acceptance"))
        self.assertEqual(1, len(prose), prose)
        with mock.patch.object(sdlc_md, "EXECUTES_VERIFIERS", ("story",)):
            self.assertEqual(3, len([p for p in verifier_problems(self.prd)
                                     if "execute their Verify" in p]))

        groomed = groomed_statements(self.prd)
        for old, new, says in (("carries\n  acceptance criteria,", "carries\n  substance,",
                                "business rule leaves out grooming.acs"),
                               (("criteria, at least one with a `Verify:` line or a `manual` "
                                 "marker;"), "criteria;",
                                "business rule leaves out criteria that are no-verifier"),
                               ("the template placeholder or only", "or only",
                                "detail criterion leaves out criteria that are placeholder"),
                               ("pointed above the split ceiling", "pointed too high",
                                "inventory row leaves out grooming.split"),
                               ("`sprint.points_split_above`, default 8)",
                                "`sprint.points_split_above`, default 13)", "default as 13")):
            problems = grooming_problems(self.mutate(old, new))
            self.assertEqual(1, len(problems), (new, problems))
            self.assertIn(says, problems[0])
        self.assertTrue(all(groomed.values()), groomed)

        security = section(self.prd, "### Security")
        dropped = self.mutate(security, security.replace(
            "and `release_cut.py` (", "and the release cut (", 1))
        self.assertEqual([("the Security NFR does not name release_cut.py, whose source "
                           "reaches the network")], network_problems(dropped, self.sources))
        added = self.mutate("- the tools a project's Verify lines invoke",
                            "- `git fetch origin` from `next_id.py`;\n- the tools a project's "
                            "Verify lines invoke")
        self.assertEqual(["the Security NFR names next_id.py, whose source makes no network call"],
                         network_problems(added, self.sources))
        fetching = network_problems(self.mutate("and never fetches", "and fetches first"),
                                    self.sources)
        self.assertEqual(1, len(fetching), fetching)
        self.assertIn("misstates whether id allocation fetches", fetching[0])
        remote = "Id allocation reads `origin/main` with `git ls-tree` and does not fetch."
        self.assertIn(remote, self.prd)
        section8 = network_problems(self.mutate(remote, "Remote-aware id allocation fetches "
                                                        "first."), self.sources)
        self.assertEqual(1, len(section8), section8)
        self.assertIn("misstates whether id allocation fetches", section8[0])
        # a script given a network call the PRD does not list fails the check (BG1162 AC1)
        for call, kind in (('subprocess.run(["git", "ls-remote", "origin"])\n', "git-verb"),
                           ('subprocess.run(("gh", "api", "repos"))\n', "gh"),
                           ('subprocess.run(["git", "pull", "--ff-only"])\n', "git-verb"),
                           ('_git(root, "fetch", "origin")\n', "git-verb")):
            self.assertEqual({"readiness.py"}, network_scripts({"readiness.py": call})[kind], call)
        quiet = '_git(root, "status")\nparser.add_parser("pull")\nSTEPS = ("close", "fetch", "x")\n'
        self.assertEqual(set(), set().union(*network_scripts({"readiness.py": quiet}).values()))
        probe = network_problems(self.prd, {**self.sources, "readiness.py":
                                            self.sources["readiness.py"] +
                                            'subprocess.run(["git", "ls-remote", "origin"])\n'})
        self.assertEqual(["the Security NFR does not name readiness.py, whose source reaches "
                          "the network"], probe)

        critic = readonly_problems(self.mutate("`handoff.py` write nothing",
                                               "`handoff.py`, `critic.py` write nothing"),
                                   self.sources)
        self.assertEqual(1, len(critic), critic)
        self.assertTrue(critic[0].startswith("critic.py is named as writing nothing; its source "
                                             "writes"), critic)
        self.assertEqual(["gate.py is named as writing and its source has no write primitive"],
                         readonly_problems(self.prd, {**self.sources, "gate.py": "x = 1\n"}))

        seeded = cost_problems(self.mutate("seed of 25,000 tokens\nper point",
                                           "rate of 25,000 tokens\nper point"))
        self.assertEqual(1, len(seeded), seeded)
        self.assertIn("as the rate, not as the seed", seeded[0])
        pinned = cost_problems(self.mutate("a plan prices from its measured\ntokens-per-point "
                                           "rate", "a plan prices from 186,252\ntokens per "
                                           "point"))
        self.assertEqual(1, len(pinned), pinned)
        self.assertIn("pins 186,252 tokens per point", pinned[0])

    def test_derived_counts_are_bands(self):
        """AC2. Mutants: a count stated as a bare number, even the right one (`69 scripts`), or
        as the old shapes (`52 \\`reference-*.md\\``, a `six-module` lib); a band the tree sits
        outside (`about 40 templates`, `SKILL.md ~100 lines`); per-ship history put back in
        §10, or the changelog table losing what moved into it. Near misses that must pass: a
        floor the tree sits inside (`60+ scripts`). The census reads the PRD's three counts
        and finds them current."""
        self.assertEqual([], count_problems(self.prd))
        self.assertEqual([], history_problems(self.prd))
        text = body(self.prd)
        for name, (pattern, _) in COUNT_CLAIMS.items():
            if name != "lib modules":
                self.assertRegex(text, re.compile(pattern, re.I), f"the PRD states no {name}")
        census = doc_freshness.census_claims(REPO, "sdlc-studio/prd.md")
        self.assertEqual([], census["findings"])
        self.assertTrue({"scripts", "reference files", "help files"}
                        <= {c["claim"] for c in census["checked"]}, census["unchecked"])

        scripts = doc_freshness._CENSUS_MEASURES["scripts"](SKILL)
        for old, new, says in (
                ("about 70 scripts", f"{scripts} scripts", "is pinned"),
                ("about 55 reference files (`reference-*.md`)", "52 `reference-*.md`",
                 "is pinned"),
                ("a `lib/` package", "a six-module `lib/` package", "is pinned"),
                ("about 90 templates", "about 40 templates", "holds in [32, 50)"),
                ("SKILL.md about 300 lines", "SKILL.md ~100 lines", "holds in [80, 125)")):
            problems = count_problems(self.mutate(old, new))
            self.assertEqual(1, len(problems), (new, problems))
            self.assertIn(says, problems[0])
        self.assertEqual([], count_problems(self.mutate("about 70 scripts", "60+ scripts")))

        cost = section(self.prd, "### The cost model: a falsified predictor, then Fibonacci points")
        put_back = self.mutate(cost, cost + "The two loop defects this section used to list as "
                                            "open are fixed (BG0133, BG0136).\n")
        self.assertEqual(3, len(history_problems(put_back)), history_problems(put_back))
        retired = history_problems(self.mutate("(an advisory, not a gate;",
                                               "(an advisory: `gate --require-close` was "
                                               "retired in v6;"))
        self.assertEqual(1, len(retired), retired)
        table = section(self.prd, "## Changelog")
        lost = history_problems(self.mutate(table, table.replace("BG0133", "a bug")))
        self.assertEqual(["the changelog table does not record BG0133"], lost)

    def test_every_prd_change_since_6_1_0_has_a_changelog_row(self):
        """BG1168 AC2. Mutants, on commits made up so they need no history: a commit whose
        subject names a unit no row names, and the row put back by its hash. Then the clone's
        own history, which a clone without it skips."""
        table = section(self.prd, "## Changelog")
        named = [("a" * 40, "fix(US1104): a row names it")]
        self.assertEqual([], revision_problems(self.prd, named))
        unnamed = [("f" * 40, "fix(US9999): no row names this")]
        self.assertEqual(1, len(revision_problems(self.prd, unnamed)))
        self.assertEqual(1, len(revision_problems(self.prd, [("f" * 40, "fix: no unit named")])))
        by_hash = self.mutate(table, table + f"| x | {'f' * 8} |\n")
        self.assertEqual([], revision_problems(by_hash, [("f" * 40, "fix: no unit named")]))
        commits = prd_commits()
        if commits is None:
            self.skipTest(f"{SINCE_6_1_0} is not in this clone's history")
        self.assertGreater(len(commits), 10, commits)
        self.assertEqual([], revision_problems(self.prd, commits))
        sha, subject = commits[-1]
        units = _UNIT_ID_RE.findall(subject)
        self.assertTrue(units, subject)
        stripped = table
        for unit in units:
            stripped = stripped.replace(unit, "XX0000")
        dropped = revision_problems(self.mutate(table, stripped), [(sha, subject)])
        self.assertEqual(1, len(dropped), dropped)
        self.assertIn(sha[:8], dropped[0])

    def test_the_engagement_floor_tracks_bg0959(self):
        """AC3. Mutants: the floor's row or its block reading Complete while BG0959 is open;
        its held criterion ticked; a verified criterion left unticked; BG0959 read as Fixed
        while the PRD still says it holds the floor. BG0959's status is read from its file."""
        status = bug_status(FLOOR_BUG)
        found = sdlc_md.find_by_id(REPO, FLOOR_BUG)
        self.assertIn(f"> **Status:** {status}", Path(found[0]).read_text(encoding="utf-8"))
        self.assertEqual([], tick_problems(self.prd))
        blocks = detail_blocks(self.prd)
        floor = blocks["Engagement floor"]
        rows = {r["Feature"]: r for r in feature_rows(self.prd)}
        if not sdlc_md.is_terminal_status("bug", status):
            self.assertEqual("Partial", floor["status"])
            self.assertEqual("Partial", rows["Engagement floor"]["Status"])
            self.assertTrue(any(FLOOR_BUG in text and not ticked
                                for ticked, text in floor["criteria"]), floor)
        self.assertGreaterEqual(sum(ticked for b in blocks.values()
                                    for ticked, _ in b["criteria"]), 14, blocks)

        row = rows["Engagement floor"]["line"]
        complete_row = self.mutate(row, row.replace("| Partial |", "| Complete |", 1))
        self.assertEqual(["the Engagement floor row reads 'Complete'; its block reads 'Partial'"],
                         tick_problems(complete_row))
        block_status = "reference-doctrine.md rule 16\n**Status:** Partial"
        complete_block = self.mutate(block_status, block_status.replace("Partial", "Complete"))
        self.assertEqual(sorted(["Engagement floor reads 'Complete'; its criteria make it Partial",
                                 ("the Engagement floor row reads 'Partial'; its block reads "
                                  "'Complete'")]),
                         sorted(tick_problems(complete_block)))
        held = next(text for ticked, text in floor["criteria"] if FLOOR_BUG in text)
        self.assertIn(f"Held by {FLOOR_BUG}", held)
        ticked = tick_problems(self.mutate(f"- [ ] {held}", f"- [x] {held}"))
        self.assertIn(f"Engagement floor criterion 4 is ticked and names ['{FLOOR_BUG}'] as "
                      "holding it", ticked)
        self.assertIn("Engagement floor reads 'Partial'; its criteria make it Complete", ticked)
        first = blocks["Reconcile"]["criteria"][0][1]
        self.assertEqual(["Reconcile criterion 1 is unticked and no open bug holds it",
                          "Reconcile reads 'Complete'; its criteria make it Partial"],
                         tick_problems(self.mutate(f"- [x] {first}", f"- [ ] {first}")))
        fixed = tick_problems(self.prd, lambda b: "Fixed" if b == FLOOR_BUG else bug_status(b))
        self.assertIn(f"Engagement floor criterion 4 is held by {FLOOR_BUG}, which is Fixed",
                      fixed)
        self.assertIn("Engagement floor criterion 4 is unticked and no open bug holds it", fixed)

    def test_the_breakdown_rule_names_the_split_ceiling_for_any_pointed_unit(self):
        """BG1162 AC2. The code refuses any pointed unit above the ceiling (`sprint.py`'s
        `grooming.split` branch asks only that `points` be set), so the rule says so. Mutant:
        the rule put back to a story or bug."""
        rule = flat(section(self.prd, "### Business Logic Rules"))
        self.assertRegex(rule, r"any pointed unit, a CR included, is pointed at or under the "
                               r"split ceiling \(`sprint\.points_split_above`, default 8\)")
        old = "and any pointed unit, a CR included, is pointed"
        self.assertIn(old, flat(self.prd))
        stale = flat(self.mutate("and any pointed unit, a CR included, is pointed",
                                 "and is pointed"))
        self.assertNotRegex(flat(section(stale, "### Business Logic Rules")),
                            r"any pointed unit, a CR included")
        self.assertEqual([], grooming_problems(self.prd))

    def test_a_held_criterion_names_the_bug_its_words_describe(self):
        """BG1162 AC3. Mutants: the Verify AC criterion Held by BG1023 reassigned to BG0959, and
        the floor's criterion reassigned to BG1063; each must be named, the tree as it is not."""
        self.assertEqual([], holder_problems(self.prd))
        verify = "Held by BG1023: the vitest"
        self.assertIn(verify, self.prd)
        moved = holder_problems(self.mutate(verify, "Held by BG0959: the vitest"))
        self.assertEqual(1, len(moved), moved)
        self.assertIn("criterion 1 names BG0959 as its holder", moved[0])
        self.assertIn("match BG1023 better", moved[0])
        floor = holder_problems(self.mutate(f"Held by {FLOOR_BUG}", "Held by BG1063"))
        self.assertEqual(1, len(floor), floor)
        self.assertIn("names BG1063 as its holder", floor[0])

    def test_the_override_is_said_to_beat_the_measured_rate(self):
        """BG1162 AC3. Mutant: the sentence reversed, the override named first and the measured
        rate as the thing that applies unless one is recorded."""
        self.assertEqual([], cost_problems(self.prd))
        old = "A plan prices from the project's own measured rate:"
        self.assertIn(old, self.prd)
        reversed_ = self.mutate(old, "A plan prices from `estimate.tokens_per_point` unless the "
                                     "project has a measured rate:")
        problems = cost_problems(reversed_)
        self.assertEqual(1, len(problems), problems)
        self.assertIn("the override `estimate.tokens_per_point` replaces the measured rate",
                      problems[0])


DEFAULTS = SKILL / "templates" / "config-defaults.yaml"
REFERENCE_CONFIG = SKILL / "reference-config.md"
#: Each gate-bearing key that ships off or advisory, with where its off value is written and the
#: pattern that finds it there (BG1525). `quality.require_full_sections` is documented in the
#: reference, whose example block holds it; the defaults file holds the other five.
GATE_KEYS_OFF = {
    "review.line_coverage": (DEFAULTS, r"^  line_coverage: off\b"),
    "review.author_self_check": (DEFAULTS, r"^  author_self_check: report\b"),
    "require_ac_verification": (DEFAULTS, r"^require_ac_verification: false\b"),
    "constitution.enforce": (DEFAULTS, r"^constitution:\s*\n(?:\s*#[^\n]*\n)*  enforce: false\b"),
    "two_backlog.enforce": (DEFAULTS, r"^two_backlog:\s*\n(?:\s*#[^\n]*\n)*  enforce: false\b"),
    "quality.require_full_sections": (REFERENCE_CONFIG, r"^  require_full_sections: false\b"),
}
#: A sentence that makes `two_backlog.enforce` the only gate-bearing key that ships off.
_SINGLE_EXCEPTION_RE = re.compile(r"\b(?:the one|the only|one deliberate|single) "
                                  r"(?:deliberate )?(?:exception|gate-bearing key)\b|"
                                  r"\bevery other gate-bearing key\b", re.I)


def flag_intro(prd: str) -> str:
    """The Feature Flags introduction: the text under the heading, above its table."""
    return flat(section(prd, "### Feature Flags").split("\n| Key", 1)[0])


def flag_intro_problems(prd: str) -> list[str]:
    """Why section 9's Feature Flags introduction names fewer default-off gate keys than
    `GATE_KEYS_OFF`, gives one no reason, or still calls one the single exception."""
    intro = flag_intro(prd)
    problems = [f"the introduction does not name `{key}`" for key in GATE_KEYS_OFF
                if f"`{key}`" not in intro]
    problems += [f"the introduction gives `{key}` no incremental-adoption reason"
                 for key in GATE_KEYS_OFF
                 if re.search(rf"`{re.escape(key)}` \(`[^`]+`: [^)]{{12,}}\)", intro) is None]
    if _SINGLE_EXCEPTION_RE.search(intro):
        problems.append("the introduction still calls one key the single exception")
    return problems


class PrdFlagDefaultsTests(unittest.TestCase):
    """BG1525 and BG1526: section 9's account of the gate keys' defaults is the defaults file's."""

    def setUp(self):
        self.prd = PRD.read_text(encoding="utf-8")

    def test_section_9_names_every_gate_key_that_ships_off(self):
        """BG1525 AC1. Mutants: one key dropped from the introduction; one named without its
        reason; the single-exception sentence put back."""
        for key, (path, pattern) in GATE_KEYS_OFF.items():
            self.assertRegex(path.read_text(encoding="utf-8"), re.compile(pattern, re.M),
                             f"{path.name} does not hold {key} off")
        self.assertEqual([], flag_intro_problems(self.prd))
        intro = section(self.prd, "### Feature Flags")
        for key in GATE_KEYS_OFF:
            mutant = self.prd.replace(intro, intro.replace(f"`{key}`", "a key", 1), 1)
            self.assertEqual([f"the introduction does not name `{key}`",
                              f"the introduction gives `{key}` no incremental-adoption reason"],
                             flag_intro_problems(mutant), key)
        bare = self.prd.replace("`constitution.enforce` (`false`: a violation is advisory "
                                "until the project opts in)", "`constitution.enforce`", 1)
        self.assertEqual(["the introduction gives `constitution.enforce` no incremental-"
                          "adoption reason"], flag_intro_problems(bare))
        old = ("The one deliberate exception is `two_backlog.enforce`, which defaults **OFF**")
        put_back = flag_intro_problems(self.prd.replace(
            "Six ship **OFF** or advisory", old, 1))
        self.assertEqual(["the introduction still calls one key the single exception"],
                         put_back)

    def test_reference_config_does_not_claim_a_single_exception(self):
        """BG1525 AC2. Mutants: the old row and sentence put back."""
        text = REFERENCE_CONFIG.read_text(encoding="utf-8")
        self.assertIsNone(_SINGLE_EXCEPTION_RE.search(text))
        self.assertNotIn("the one gate-bearing key", text)
        rule = section(text, "## Two-Backlog Enforcement {#two-backlog}")
        for key in GATE_KEYS_OFF:
            self.assertIn(f"`{key}`", rule, key)
        old_row = "Deliberately OFF - the one gate-bearing key whose absence does not block"
        self.assertIsNotNone(_SINGLE_EXCEPTION_RE.search(old_row))
        old_rule = "every other gate-bearing key blocks when absent"
        self.assertIsNotNone(_SINGLE_EXCEPTION_RE.search(old_rule))

    def test_the_lessons_loop_and_schema_version_rows_match_the_defaults_file(self):
        """BG1526 AC1. Mutants: `lessons.loop` back at `loop`; `schema_version` back at 3, or
        saying nothing of what `init` stamps."""
        defaults = DEFAULTS.read_text(encoding="utf-8")
        loop = re.search(r"^lessons:\s*\n(?:  [^\n]*\n)*?  loop: (\w+)", defaults, re.M)
        fallback = re.search(r"^schema_version: (\d+)", defaults, re.M)
        stamped = re.search(r"^schema_version: (\d+)", (SKILL / "templates" / "config.yaml")
                            .read_text(encoding="utf-8"), re.M)
        self.assertEqual(("enforce", "2", "3"), (loop.group(1), fallback.group(1),
                                                 stamped.group(1)))
        self.assertEqual([], flag_row_problems(self.prd, loop.group(1), fallback.group(1),
                                               stamped.group(1)))
        for key, old, new, says in (
                ("lessons.loop", "| `lessons.loop` | `enforce` |", "| `lessons.loop` | `loop` |",
                 "the `lessons.loop` row gives `loop`, not the default `enforce`"),
                ("schema_version", "| `schema_version` | 2 (", "| `schema_version` | 3 (",
                 "the `schema_version` row does not give the fallback default 2"),
                ("schema_version", "`init` stamps 3 on a new project", "a later release",
                 "the `schema_version` row does not say `init` stamps 3 on a new project")):
            self.assertIn(old, self.prd)
            problems = flag_row_problems(self.prd.replace(old, new, 1), "enforce", "2", "3")
            self.assertIn(says, problems, (key, problems))


def flag_rows(prd: str) -> list[dict[str, str]]:
    """Each data row of the Feature Flags table, as {Key, Default, Effect} with the key's
    backticks dropped."""
    rows = []
    for line in section(prd, "### Feature Flags").splitlines():
        if line.startswith("|") and not re.fullmatch(r"[\s|:-]+", line):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            if cells[0] != "Key":
                rows.append({"Key": cells[0].strip("`"), "Default": cells[1], "Effect": cells[2]})
    return rows


def flag_row_problems(prd: str, loop: str, fallback: str, stamped: str) -> list[str]:
    """Why the `lessons.loop` or `schema_version` row gives a default the defaults file does not
    hold: `loop` is the value the file gives, `fallback` the schema version it falls back to and
    `stamped` the one `init` seeds a new project with."""
    rows = {r["Key"]: r for r in flag_rows(prd)}
    problems = []
    given = re.match(r"`(\w+)`", rows["lessons.loop"]["Default"])
    if not given or given.group(1) != loop:
        problems.append(f"the `lessons.loop` row gives `{given.group(1) if given else None}`, "
                        f"not the default `{loop}`")
    default = rows["schema_version"]["Default"]
    if not re.match(rf"{fallback}\b", default):
        problems.append(f"the `schema_version` row does not give the fallback default {fallback}")
    if f"`init` stamps {stamped} on a new project" not in default:
        problems.append(f"the `schema_version` row does not say `init` stamps {stamped} on a "
                        "new project")
    return problems


#: A name that reads as an environment variable: upper case, at least three characters.
_ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")
#: A row of the Environment Variables table that is not a script's read is marked as one of
#: these: the harness sets it, or the installer (not a script) reads it.
_NOT_A_SCRIPT_READ_RE = re.compile(r"\bthe harness sets\b|\bread by the installer\b", re.I)


def _is_env_expr(node: ast.AST) -> bool:
    """Whether `node` is an environment mapping: `os.environ`, `env`, `self.env`, `child_env`."""
    while isinstance(node, ast.Attribute):
        if node.attr in ("environ", "env") or node.attr.endswith("_env"):
            return True
        node = node.value
    return isinstance(node, ast.Name) and (node.id in ("environ", "env")
                                           or node.id.endswith("_env"))


def env_variables(sources: dict[str, str]) -> set[str]:
    """Every environment variable name the shipped scripts and their lib folder read: a `get` or
    subscript on an environment mapping, an `in` test against one, a module constant whose name
    ends `_ENV`, and the names a `SIGNALS` table lists."""
    names: set[str] = set()
    for source in sources.values():
        tree = ast.parse(source)
        for node in ast.walk(tree):
            literal = None
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in ("get", "getenv") and node.args \
                    and (node.func.attr == "getenv" or _is_env_expr(node.func.value)):
                literal = node.args[0]
            elif isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load) \
                    and _is_env_expr(node.value):
                literal = node.slice
            elif isinstance(node, ast.Compare) and any(isinstance(o, (ast.In, ast.NotIn))
                                                       for o in node.ops) \
                    and any(_is_env_expr(c) for c in node.comparators):
                literal = node.left
            if isinstance(literal, ast.Constant) and isinstance(literal.value, str):
                names.add(literal.value)
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name) \
                    and ((node.targets[0].id.endswith("_ENV")
                          and isinstance(node.value, ast.Constant))
                         or node.targets[0].id == "SIGNALS"):
                names |= {n.value for n in ast.walk(node.value)
                          if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    return {n for n in names if _ENV_NAME_RE.match(n)}


def env_rows(prd: str) -> dict[str, str]:
    """The Environment Variables table's rows, by variable, with the row's own text."""
    rows = {}
    for line in section(prd, "### Environment Variables").splitlines():
        m = re.match(r"\|\s*`([A-Z][A-Z0-9_]+)`\s*\|", line)
        if m:
            rows[m.group(1)] = line
    return rows


def env_problems(prd: str, read: set[str]) -> list[str]:
    """Each variable in `read` with no row in the Environment Variables table, and each row for
    a variable no script reads that the PRD does not mark as set by the harness or read by the
    installer."""
    rows = env_rows(prd)
    problems = [f"the Environment Variables table has no row for {v}"
                for v in sorted(read - set(rows))]
    problems += [f"the Environment Variables table names {v}, which no script reads and the "
                 "row does not mark as harness-set or installer-read"
                 for v, line in sorted(rows.items())
                 if v not in read and not _NOT_A_SCRIPT_READ_RE.search(line)]
    return problems


class PrdEnvironmentVariablesTests(unittest.TestCase):
    """BG1553: section 9's Environment Variables table lists what the scripts read."""

    @classmethod
    def setUpClass(cls):
        cls.sources = script_sources()
        cls.read = env_variables(cls.sources)

    def setUp(self):
        self.prd = PRD.read_text(encoding="utf-8")

    def test_every_variable_the_scripts_read_has_a_row(self):
        """AC1. The collector is not vacuous: it finds the four the Cursor meter and the
        harness switch added, and each of the variables has a row."""
        for name in ("SDLC_STUDIO_HARNESS", "CURSOR_API_KEY", "SDLC_STUDIO_CURSOR_AGENT_ID",
                     "SDLC_STUDIO_CURSOR_API", "SDLC_AUTHOR", "SDLC_DEBUG", "HOME"):
            self.assertIn(name, self.read)
        self.assertGreater(len(self.read), 25, sorted(self.read))
        self.assertEqual([], env_problems(self.prd, self.read))

    def test_the_secret_and_the_endpoint_override_are_marked(self):
        """AC2. Mutants: the key's row with `secret` taken out; the override's row with its
        kind taken out; the CLAUDE_SKILL_DIR row claiming a script reads it."""
        rows = env_rows(self.prd)
        self.assertRegex(rows["CURSOR_API_KEY"], r"(?i)\bsecret\b")
        self.assertRegex(rows["SDLC_STUDIO_CURSOR_API"], r"(?i)network endpoint override")
        skill_dir = rows["CLAUDE_SKILL_DIR"]
        self.assertRegex(skill_dir, r"the harness sets it")
        self.assertRegex(skill_dir, r"no script reads it")
        self.assertNotIn("CLAUDE_SKILL_DIR", self.read)
        self.assertNotRegex(rows["SDLC_AUTHOR"] + rows["HOME"], r"(?i)\bsecret\b")
        unmarked = rows["CLAUDE_SKILL_DIR"].replace("the harness sets it; no script reads it",
                                                    "used to invoke scripts")
        self.assertNotEqual(unmarked, rows["CLAUDE_SKILL_DIR"])
        mutant = self.prd.replace(rows["CLAUDE_SKILL_DIR"], unmarked, 1)
        self.assertEqual(1, len(env_problems(mutant, self.read)), env_problems(mutant, self.read))
        self.assertIn("CLAUDE_SKILL_DIR", env_problems(mutant, self.read)[0])

    def test_a_dropped_row_is_named(self):
        """AC3. Mutants: one variable's row removed, for every variable; a row added for a
        variable no script reads; the harness-set mark taken off the one that is."""
        rows = env_rows(self.prd)
        for var in sorted(self.read):
            mutant = self.prd.replace(rows[var] + "\n", "", 1)
            self.assertNotEqual(mutant, self.prd, var)
            self.assertEqual([f"the Environment Variables table has no row for {var}"],
                             env_problems(mutant, self.read), var)
        extra = self.prd.replace(rows["SDLC_DEBUG"], rows["SDLC_DEBUG"] +
                                 "\n| `SDLC_NO_SUCH_SWITCH` | Nothing reads this | No | unset |", 1)
        self.assertEqual(1, len(env_problems(extra, self.read)))
        self.assertIn("SDLC_NO_SUCH_SWITCH", env_problems(extra, self.read)[0])
        self.assertEqual([], env_problems(self.prd, self.read | {"SDLC_NO_SUCH_SWITCH"})[1:])
        self.assertEqual(["the Environment Variables table has no row for SDLC_NO_SUCH_SWITCH"],
                         env_problems(self.prd, self.read | {"SDLC_NO_SUCH_SWITCH"}))
        # the collector reads each shape: a get, a subscript, an `in` test, a `_ENV` constant
        shapes = {"a.py": 'import os\nx = os.environ.get("AAA_ONE")\ny = os.environ["BBB_TWO"]\n'
                          'z = "CCC_THREE" in os.environ\nFOUR_ENV = "DDD_FOUR"\n'
                          'w = os.environ.pop("EEE_FIVE", None)\nenv["FFF_SIX"] = "1"\n'}
        self.assertEqual({"AAA_ONE", "BBB_TWO", "CCC_THREE", "DDD_FOUR"}, env_variables(shapes))


#: The close chain's steps are named in the PRD's account of the close by this text, step by
#: step; the three retro steps are grouped, and the grouping is said (BG1555).
_RETRO_STEPS = {"retro-validate": "validate", "retro-extract": "extract",
                "retro-accuracy": "accuracy"}
_STEP_WORDS = ("review coverage", "retro", "persona memory", "lessons", "checklist", "gate",
               "reconcile", "review anchor")


def close_account(prd: str) -> str:
    """The PRD's single account of the close: the Core Behaviours bullet that runs the chain."""
    m = re.search(r"^- `sprint\.py close` runs the close chain.*?(?=^- )",
                  section(prd, "### Core Behaviours"), re.M | re.S)
    return flat(m.group(0)) if m else ""


def close_passages(prd: str) -> dict[str, str]:
    """The three passages that speak of the close: the Mission paragraph, the Sprint report and
    sign row and the account in Core Behaviours."""
    rows = [r["line"] for r in feature_rows(prd) if r["Feature"] == "Sprint report and sign"]
    return {"Mission": flat(section(prd, "## Mission")), "Sprint report and sign row":
            flat(rows[0]) if rows else "", "Core Behaviours": close_account(prd)}


def chain_problems(prd: str, chain: tuple[str, ...]) -> list[str]:
    """Each step of `chain` the PRD's account of the close does not name."""
    account = close_account(prd).lower()
    problems = []
    for step in chain:
        named = (step.replace("-", " ") in account if step not in _RETRO_STEPS
                 else "retro" in account and _RETRO_STEPS[step] in account)
        if not named:
            problems.append(f"the account of the close does not name {step}")
    return problems


def goal_verdict_problems(prd: str) -> list[str]:
    """Why a passage on the close lists the goal verdict among the chain steps, does not give the
    goal and its verdict as preconditions, lists chain steps of its own beside the account, or
    why the account loses the rule that a failed step is carried to the report."""
    problems = []
    for name, text in close_passages(prd).items():
        if not re.search(r"preconditions? hold[^.]*\bgoal verdict\b", text):
            problems.append(f"{name} does not give the sprint goal and its verdict as "
                            "preconditions of the close")
        for clause in re.split(r"[;:]|\.(?=\s)", text):
            steps = [w for w in _STEP_WORDS if w in clause.lower()]
            if "goal verdict" in clause and len(steps) >= 2:
                problems.append(f"{name} lists the goal verdict among the chain steps: "
                                f"{clause.strip()!r}")
            elif name != "Core Behaviours" and len(steps) >= 3:
                problems.append(f"{name} gives its own list of chain steps: {clause.strip()!r}")
    if not re.search(r"A step that fails is a known issue on the one-page sprint report",
                     close_account(prd)):
        problems.append("the account of the close loses the rule that a failed step is carried "
                        "to the report")
    return problems


class PrdCloseChainTests(unittest.TestCase):
    """BG1555: one account of the sprint close, and it is `sprint._CLOSE_CHAIN`."""

    def setUp(self):
        self.prd = PRD.read_text(encoding="utf-8")

    def test_every_close_chain_step_is_named(self):
        """AC1. The account names each step of the shipped chain, persona-memory, checklist and
        review-anchor included."""
        chain = tuple(sprint._CLOSE_CHAIN)
        for step in ("persona-memory", "checklist", "review-anchor"):
            self.assertIn(step, chain)
        self.assertGreaterEqual(len(chain), 10)
        self.assertEqual([], chain_problems(self.prd, chain))
        self.assertEqual(["the account of the close does not name new-step"],
                         chain_problems(self.prd, chain + ("new-step",)))

    def test_the_goal_verdict_is_a_precondition_in_all_three_passages(self):
        """AC2. Mutants: the goal verdict listed among the chain steps in the row, and a step
        list of its own in the Mission; the failed-step rule dropped."""
        self.assertEqual([], goal_verdict_problems(self.prd))
        self.assertEqual(3, len(close_passages(self.prd)))
        row = "runs the close as one chain (the steps are listed in section 4)"
        self.assertIn(row, self.prd)
        listed = goal_verdict_problems(self.prd.replace(
            row, "runs the close as one chain (goal verdict, retro, lessons, gate, reconcile)", 1))
        self.assertEqual(1, len(listed), listed)
        self.assertIn("Sprint report and sign row lists the goal verdict among the chain steps",
                      listed[0])
        own = goal_verdict_problems(self.prd.replace(
            "files the one-page sprint report", "files the one-page sprint report. The close runs "
            "review coverage, retro and the gate", 1))
        self.assertEqual(1, len(own), own)
        self.assertIn("Mission gives its own list of chain steps", own[0])
        gone = goal_verdict_problems(self.prd.replace("A step that fails is a known issue",
                                                      "A step that fails stops the close", 1))
        self.assertEqual(["the account of the close loses the rule that a failed step is "
                          "carried to the report"], gone)
        unconditioned = goal_verdict_problems(self.prd.replace("a sprint goal, a goal verdict and "
                                                               "a retro):", "a sprint goal and "
                                                               "a retro):", 1))
        self.assertEqual(["Core Behaviours does not give the sprint goal and its verdict as "
                          "preconditions of the close"], unconditioned)

    def test_a_dropped_chain_step_is_named(self):
        """AC3. Mutants: each step's name taken out of the account, in turn."""
        chain = tuple(sprint._CLOSE_CHAIN)
        account = re.search(r"^- `sprint\.py close` runs the close chain.*?(?=^- )",
                            section(self.prd, "### Core Behaviours"), re.M | re.S).group(0)
        cuts = {"review-coverage": "review coverage", "retro-validate": "validate",
                "retro-extract": "extract", "retro-accuracy": "accuracy",
                "persona-memory": "persona memory", "lessons-summary": "lessons summary",
                "checklist": "checklist", "gate": "gate", "reconcile": "reconcile",
                "review-anchor": "review anchor"}
        self.assertEqual(set(chain), set(cuts))
        for step, words in cuts.items():
            mutant = self.prd.replace(account, account.replace(words, "XXXX"), 1)
            self.assertNotEqual(mutant, self.prd, step)
            self.assertIn(f"the account of the close does not name {step}",
                          chain_problems(mutant, chain), step)


if __name__ == "__main__":
    unittest.main()
