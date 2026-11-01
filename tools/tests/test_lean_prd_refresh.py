"""US0929: the PRD describes the lean product and lists the outcomes a Sprint Goal can serve.

The outcomes are read by the planner's own reader (`sprint.prd_outcomes`) and the persona
cards by `sprint.persona_cards`, so this file holds no second parser of either; `end_goals_text`
only slices a card's End goals as written, for a word-for-word comparison. Outside
`OutcomeCitationTests` and the two citations it pins (`O5_CITES`, `UPGRADE_GOAL`, US1082), it
pins no persona or End goal by hand: a card that gains, loses or renumbers an End goal moves
what an outcome may cite. Every
`<script>.py <subcommand>` the loop sections name is checked against that script's own `--help`,
so a retired subcommand cannot stay described as current. `PrdBaselineTests` (US1103) pins the
release the PRD's baseline names, reads its capability set from RV0028's PRD-10 row, and checks
the commands those capabilities' inventory rows name the same way.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
import functools
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
PRD = REPO / "sdlc-studio" / "prd.md"
sys.path.insert(0, str(SCRIPTS))

import sprint  # noqa: E402 - the outcome and persona readers US0927 ships
from lib import sdlc_md  # noqa: E402 - the id resolver an inventory row's Epic cell is read by

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


#: The release the PRD's baseline names and the work on `main` beside it (US1103 AC1), pinned
#: as the criterion names them: a PRD that moves its baseline moves these with it.
BASELINE = "6.1.0"
ON_MAIN = "6.2"
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
    """US1103: the PRD's baseline reads v6.1.0 plus 6.2 on main, no shipped row carries the
    release marker, and each capability RV0028 PRD-10 names has a sound inventory row. Each
    check is also run on a mutated copy, so it is shown able to refuse."""

    def setUp(self):
        self.prd = PRD.read_text(encoding="utf-8")

    def test_no_shipped_row_is_unreleased(self):
        """AC1. Mutants: one [Unreleased] marker left on a shipped row's Status, or on a
        Feature Details heading; the header's baseline back at v6.0.0, or the inventory's at
        v4.1.0; the header naming no 6.2 work on main. Near misses that must pass: the marker
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


if __name__ == "__main__":
    unittest.main()
