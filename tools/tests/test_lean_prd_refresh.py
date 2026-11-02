"""US0929: the PRD describes the lean product and lists the outcomes a Sprint Goal can serve.

The outcomes are read by the planner's own reader (`sprint.prd_outcomes`) and the persona
cards by `sprint.persona_cards`, so this file holds no second parser of either; `end_goals_text`
only slices a card's End goals as written, for a word-for-word comparison. Outside
`OutcomeCitationTests` and the two citations it pins (`O5_CITES`, `UPGRADE_GOAL`, US1082), it
pins no persona or End goal by hand: a card that gains, loses or renumbers an End goal moves
what an outcome may cite. Every
`<script>.py <subcommand>` the loop sections name is checked against that script's own `--help`,
so a retired subcommand cannot stay described as current. `PrdBaselineTests` (US1103) reads the
release the PRD's baseline must name from package.json (US1111), reads its capability set from
RV0028's PRD-10 row, and checks the commands those capabilities' inventory rows name the same
way. `PrdRulesTests` (US1104) reads the rules, NFRs and cost model against the code that decides
them, holds each derived count to a band around the tree's own measure, and ties the detail
criteria's ticks to the status of the bug that holds each one.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
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
#: The two citations US1082 AC2 pins: O5 on the End goal D0383 rules, and the End goal CR0648
#: names as having no outcome. Pinned by name, since `outcome_problems` asks of a citation only
#: that its card and End goal number exist.
O5_CITES = ("Maya Okafor", "5")
UPGRADE_GOAL = ("Jonah Reyes", "4")
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


def citation_problems(root: Path) -> list[str]:
    """Why the outcomes do not cite every End goal of each persona they cite, once each; empty
    when they do. A pair cited twice inside one outcome is one outcome's citation."""
    goals = {c["name"]: [n for n, _ in c["end_goals"]] for c in sprint.persona_cards(root)}
    cited: dict[tuple[str, str], list[str]] = {}
    for oid, text in sprint.prd_outcomes(root).items():
        for pair in dict.fromkeys(_CITE_RE.findall(text)):
            cited.setdefault(pair, []).append(oid)
    problems = [f"{name} End goal {number} is cited by {', '.join(oids)}"
                for (name, number), oids in cited.items() if len(oids) > 1]
    for name in dict.fromkeys(name for name, _ in cited):
        problems += [f"no outcome cites {name} End goal {number}"
                     for number in goals.get(name, []) if (name, number) not in cited]
    return problems


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
    """Why O5 does not cite `O5_CITES` alone, no outcome cites `UPGRADE_GOAL`, or a card no
    longer states the End goal one of them names; empty when none of these holds."""
    outcomes = sprint.prd_outcomes(root)
    goals = {c["name"]: dict(c["end_goals"]) for c in sprint.persona_cards(root)}
    problems = [f"{name}'s card states no End goal {number}"
                for name, number in (O5_CITES, UPGRADE_GOAL) if number not in goals.get(name, {})]
    o5 = _CITE_RE.findall(outcomes.get("O5", ""))
    if o5 != [O5_CITES]:
        problems.append(f"O5 cites {o5}, not {O5_CITES[0]} End goal {O5_CITES[1]} alone")
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
    persona the outcomes cite has one outcome. The three checks are also run on mutated copies
    of the PRD and the cards, so each is shown able to refuse."""

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
        """AC1. Mutants: O5 back on the End goal O3 cites (Maya Okafor's End goal 3), so a
        pair is cited twice and End goal 5 by none; the outcome citing Jonah Reyes's End goal 4
        removed; End goals required of a persona no outcome cites."""
        self.assertEqual([], citation_problems(REPO))
        self.assertEqual([], self.problems_with(citation_problems, self.prd))
        name, number = O5_CITES
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
            sorted(self.problems_with(citation_problems, self.prd.replace(o5_line, back, 1))))
        upgrade = self.upgrade_outcomes()
        self.assertTrue(upgrade, f"no outcome cites {UPGRADE_GOAL[0]} End goal {UPGRADE_GOAL[1]}")
        dropped = self.prd
        for oid in upgrade:
            dropped = dropped.replace(_outcome_line(self.prd, oid) + "\n", "", 1)
        self.assertEqual([f"no outcome cites {UPGRADE_GOAL[0]} End goal {UPGRADE_GOAL[1]}"],
                         self.problems_with(citation_problems, dropped))
        # one outcome naming a pair twice is one outcome's citation, not two
        first = _outcome_line(self.prd, "O1")
        m = _CITE_RE.search(first)
        twice = first.replace(m.group(0), f"{m.group(0)}; {m.group(0)}", 1)
        self.assertEqual([], self.problems_with(citation_problems,
                                                self.prd.replace(first, twice, 1)))

    def test_o5_and_jonahs_upgrade_goal_are_cited(self):
        """AC2. Mutants: O5 re-pointed to another End goal, or citing a second beside End goal
        5; no outcome citing Jonah Reyes's End goal 4; a card that no longer states the End goal
        cited. The goals' words are read from the cards, never written here."""
        self.assertEqual([], ruled_citation_problems(REPO))
        self.assertEqual([], self.problems_with(ruled_citation_problems, self.prd))
        name, number = O5_CITES
        o5_line = _outcome_line(self.prd, "O5")
        cite = f"{name}, End goal {number}"
        for other in ("3", "4", f"{number}; {name}, End goal 1"):
            moved = self.prd.replace(o5_line, o5_line.replace(cite, f"{name}, End goal {other}"), 1)
            self.assertNotEqual(self.prd, moved)
            problems = self.problems_with(ruled_citation_problems, moved)
            self.assertEqual(1, len(problems), other)
            self.assertIn("O5 cites", problems[0])
        dropped = self.prd
        for oid in self.upgrade_outcomes():
            dropped = dropped.replace(_outcome_line(self.prd, oid) + "\n", "", 1)
        self.assertEqual([f"no outcome cites {UPGRADE_GOAL[0]} End goal {UPGRADE_GOAL[1]}"],
                         self.problems_with(ruled_citation_problems, dropped))
        card = self.root / "sdlc-studio" / "personas" / card_of(name).name
        text = card.read_text(encoding="utf-8")
        card.write_text(re.sub(rf"^{number}\. .*\n", "", text, count=1, flags=re.M),
                        encoding="utf-8")
        self.assertEqual([f"{name}'s card states no End goal {number}"],
                         self.problems_with(ruled_citation_problems, self.prd))

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
    whose `**Status:**` reads so, carrying `UNRELEASED` outside a code span."""
    marked = [f"row {row.get('Feature', '?')}" for row in feature_rows(prd)
              if _SHIPPED_RE.match(row.get("Status", ""))
              and UNRELEASED in _CODE_SPAN_RE.sub("", row["line"])]
    details = section(prd, "### Feature Details (representative)")
    for block in re.split(r"^(?=#### )", details, flags=re.M):
        status = re.search(r"^\*\*Status:\*\*(.*)$", block, re.M)
        if block.startswith("#### ") and status and _SHIPPED_RE.match(status.group(1)) \
                and UNRELEASED in _CODE_SPAN_RE.sub("", block):
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
        stale v6.1.0 plus 6.2 (US1111). Near misses that must pass: the marker
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
        self.assertEqual([], unreleased_marks(self.prd.replace(row["line"], spanned, 1)))
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
    "gh": re.compile(r"""\[\s*["']gh["']"""),
    "fetch": re.compile(r"""["']fetch["']\s*,\s*["']origin["']"""),
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


def network_problems(prd: str, sources: dict[str, str]) -> list[str]:
    """Why the Security NFR's list of scripts that reach the network differs from the scripts
    whose source makes a network call, or why it says id allocation fetches when `next_id.py`
    makes no fetch; empty when they agree."""
    security = section(prd, "### Security")
    found = set().union(*network_scripts(sources).values())
    named = set(re.findall(r"`([a-z_]+\.py)`", security))
    problems = [f"the Security NFR does not name {s}, whose source reaches the network"
                for s in sorted(found - named)]
    problems += [f"the Security NFR names {s}, whose source makes no network call"
                 for s in sorted(named - found)]
    fetches = "next_id.py" in found
    for sentence in _SENTENCE_RE.split(flat(security)):
        if re.search(r"\bid allocation\b", sentence, re.I) and \
                bool(re.search(r"\bnever fetches\b", sentence)) == fetches:
            problems.append(f"the Security NFR misstates whether id allocation fetches: "
                            f"{sentence!r}")
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
                                 "marker,"), "criteria,",
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


if __name__ == "__main__":
    unittest.main()
