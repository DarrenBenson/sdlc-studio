"""US1129: AGENTS.md is cut to its char budget, keeps its spine and every pinned phrase.

AGENTS.md is loaded on every call of every agent in this repository, so its size is paid on
each one. The cut keeps the four start-here steps, the refusals table and one paragraph per
non-negotiable rule, and moves the rest to CONTRIBUTING.md, linked from the line naming it.

Run from the repo root:
    python3 -m pytest tools/tests/test_agents_md_budget.py -q
"""
# test-census-subject: AGENTS.md
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AGENTS = REPO / "AGENTS.md"
CONTRIBUTING = REPO / "CONTRIBUTING.md"
#: The CONTRIBUTING.md section holding the blocks AGENTS.md moved out; each `###` in it is one.
MOVED_SECTION = "## Agent detail moved from AGENTS.md"
START_STEPS = ("sdlc-studio/reviews/LATEST.md", "/sdlc-studio status",
               ".claude/skills/sdlc-studio/lessons/_index.md", "git fetch")
REFUSAL_GATES = ("pre-commit + commit-msg hooks", "pre-push hook", "`sprint plan`",
                 "`transition -> Done`", "`transition -> Fixed`", "`sprint close`",
                 "`critic.py brief`", "`sprint sign`")
RULES = ("No ad-hoc coding.", "Review is independent of the author.",
         "Brief a reviewer with the shipped tool, never by hand.",
         "A review judges the unit's own diff.",
         "Always look for a tool before doing anything by hand.",
         "Use the deterministic tooling; never hand-roll what it wires.",
         "Exercise every claim through the shipped entry point before asking for review.",
         "Ship the paperwork in the same commit as the code.",
         "The push gate is the full-suite check.")
LINK = re.compile(r"\[([^\]]+)\]\(CONTRIBUTING\.md#([^)\s]+)\)")


def _budgets():
    spec = importlib.util.spec_from_file_location("cb_agents", REPO / "tools/check_budgets.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _squash(text: str) -> str:
    return " ".join(text.split())


def _section(text: str, heading: str) -> str:
    """The body under `heading` up to the next heading of the same or a higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    start = text.index(heading + "\n") + len(heading) + 1
    nxt = re.search(rf"^#{{1,{level}}} ", text[start:], re.M)
    return text[start:start + nxt.start()] if nxt else text[start:]


def _slug(heading: str) -> str:
    """The anchor GitHub gives a heading."""
    return re.sub(r"[^a-z0-9 -]", "", heading.strip().lower()).replace(" ", "-")


def spine_problems(agents: str, contributing: str, budget: int) -> list[str]:
    """Every way `agents` falls short of AC1; empty when it meets it."""
    out = []
    if len(agents) > budget:
        out.append(f"AGENTS.md is {len(agents)} chars, over its {budget} budget")
    steps = re.findall(r"^(\d)\. (.*)$", _section(agents, "## Start here, every session"), re.M)
    for n, want in enumerate(START_STEPS, 1):
        if not any(int(i) == n and want in line for i, line in steps):
            out.append(f"start-here step {n} ({want}) is gone")
    rows = [r for r in _section(agents, "## What will refuse you").splitlines()
            if r.startswith("| ")]
    for gate in REFUSAL_GATES:
        if not any(r.startswith(f"| {gate} |") for r in rows):
            out.append(f"the refusals table has no {gate} row")
    rules = _section(agents, "## Non-negotiable rules")
    leads = [_squash(m) for m in re.findall(r"^\*\*(.+?)\*\*", rules, re.M | re.S)]
    for rule in RULES:
        if leads.count(rule) != 1:
            out.append(f"{rule!r} leads {leads.count(rule)} paragraphs, not one")
    paras = [p for p in re.split(r"\n[ \t]*\n", rules.strip()) if p.strip()]
    if len(paras) != len(RULES):
        out.append(f"the rules section has {len(paras)} paragraphs for {len(RULES)} rules")
    if MOVED_SECTION + "\n" not in contributing:
        return out + [f"CONTRIBUTING.md has no {MOVED_SECTION!r} section"]
    moved = re.findall(r"^### (.+)$", _section(contributing, MOVED_SECTION), re.M)
    if not moved:
        out.append("the moved section holds no block")
    links = {}
    for line in agents.splitlines():
        for text, anchor in LINK.findall(line):
            links.setdefault(anchor, []).append(text)
    for heading in moved:
        texts = links.get(_slug(heading), [])
        if not texts:
            out.append(f"the moved block {heading!r} is linked from no line of AGENTS.md")
        elif not any(t.lower() in heading.lower() for t in texts):
            out.append(f"no link to {heading!r} names its subject: {texts}")
    for anchor in links:
        if anchor not in {_slug(h) for h in moved} | {_slug(MOVED_SECTION[3:])}:
            out.append(f"AGENTS.md links CONTRIBUTING.md#{anchor}, which no moved heading has")
    return out


def pin_problems(agents: str) -> list[str]:
    """Every phrase a test or a corpus Verify line reads that `agents` no longer carries."""
    out = []

    def need(ok: bool, what: str) -> None:
        if not ok:
            out.append(what)

    need(re.search("fetch", agents, re.I) is not None, "US0099: no 'fetch'")
    for phrase in ("forward-port.sh", "forward-port.sh --check", "forward-port.pin",
                   "sprint sign", "three tracked hooks", "`git push --no-verify`",
                   "`.githooks/pre-push`", "`.githooks/pre-commit --list`",
                   "`.githooks/commit-msg --list`", "critic.py self-check record",
                   "review.author_self_check"):
        need(phrase in agents, f"{phrase!r} is gone")
    need(re.search(r"reviewer of record|persona_resolve\.py panel", agents) is None,
         "US0926: a retired review term is back")
    head, _, tail = agents.partition("## What will refuse you")
    table = tail.split("**Enable the hooks", 1)[0]
    need(bool(tail) and "**Enable the hooks" in tail,
         "the hooks paragraph no longer follows the table")
    row = next((r for r in table.splitlines() if r.startswith("| pre-push hook |")), "")
    need("gate_timing.py estimate --suite boundary-push" in row,
         "the pre-push row does not name the estimate command")
    need(re.search(r"\b(?:seconds?|minutes?|hours?)\b|\d+\s*(?:s|m|h|min)\b",
                   re.sub(r"`[^`]*`", "", row), re.I) is None, "the pre-push row states a figure")
    has_rules = "## Non-negotiable rules\n" in agents
    rules = _section(agents, "## Non-negotiable rules") if has_rules else ""
    need("**The push gate is the full-suite check.**" in rules,
         "the push-gate rule left the rules section")
    need(re.search(r"the commit each\s+pushed ref points at", rules) is not None,
         "the push-gate paragraph lost 'the commit each pushed ref points at'")
    for span in ("`sdlc.gateHost`", "`tools/run-suite.sh all`"):
        need(span in rules, f"the push-gate paragraph lost {span}")
    soft = agents.find("## Soft dependencies")
    need(soft >= 0 and "`coverage` 7.10 or later" in agents[soft:soft + 2000],
         "the soft-dependency table lost `coverage` 7.10 or later")
    where = _section(agents, "## Where things live") if "## Where things live\n" in agents else ""
    need(any("amigo" in r.lower() and "`sdlc-studio/personas/seats/`" in r
             for r in where.splitlines() if r.startswith("|")),
         "the Where things live table lost its amigo seat row")
    return out


class AgentsMdBudgetTests(unittest.TestCase):

    def setUp(self) -> None:
        self.agents = AGENTS.read_text(encoding="utf-8")
        self.contributing = CONTRIBUTING.read_text(encoding="utf-8")
        self.cb = _budgets()

    def test_agents_md_fits_its_budget_and_keeps_its_spine(self) -> None:
        """AC1. MUTANTS: a budget constant above 7,000; the file one char over it; a start-here
        step dropped; a refusals row dropped; a rule's paragraph dropped or split in two; a moved
        block left unlinked, or linked by text that does not name it."""
        self.assertLessEqual(self.cb.AGENTS_MD_BUDGET, 7000, "the budget constant was raised")
        self.assertEqual([], spine_problems(self.agents, self.contributing,
                                            self.cb.AGENTS_MD_BUDGET))
        para = next(p for p in re.split(r"\n[ \t]*\n", self.agents) if p.startswith("**No ad-hoc"))
        first_link = next((m for m in LINK.finditer(self.agents)
                           if m.group(2) != _slug(MOVED_SECTION[3:])), None)
        self.assertIsNotNone(first_link,
                             "AGENTS.md links no moved block, so the link check read nothing")
        mutants = {
            "one char over": self.agents + "x" * (self.cb.AGENTS_MD_BUDGET + 1 - len(self.agents)),
            "a start-here step dropped": re.sub(r"^4\. .*$", "", self.agents, count=1, flags=re.M),
            "a refusals row dropped": re.sub(r"^\| `sprint sign` \|.*\n", "", self.agents,
                                             count=1, flags=re.M),
            "a rule dropped": self.agents.replace(para + "\n\n", "", 1),
            "a rule split in two": self.agents.replace(para, para + "\n\nAnd more.", 1),
            "a moved block unlinked": self.agents.replace(first_link.group(0),
                                                          first_link.group(1), 1),
            "a link that names nothing": self.agents.replace(
                first_link.group(0), f"[here](CONTRIBUTING.md#{first_link.group(2)})", 1),
        }
        for name, text in mutants.items():
            with self.subTest(mutant=name):
                self.assertNotEqual(self.agents, text, "the mutation did not apply")
                self.assertNotEqual([], spine_problems(text, self.contributing,
                                                       self.cb.AGENTS_MD_BUDGET))

    def test_every_pinned_phrase_survives(self) -> None:
        """AC2. The phrases the pinning modules and corpus Verify lines read, re-read here, and
        the three Verify lines run as written. MUTANTS: each pinned phrase deleted; a fixed
        figure in the pre-push row; the push-gate rule moved out of its section."""
        self.assertEqual([], pin_problems(self.agents))
        for cmd in ('grep -i "fetch" AGENTS.md', 'grep "forward-port.sh" AGENTS.md',
                    "! grep -nE 'reviewer of record|persona_resolve.py panel' AGENTS.md "
                    "&& grep -q 'sprint sign' AGENTS.md"):
            with self.subTest(verify=cmd):
                r = subprocess.run(["bash", "-c", cmd], cwd=REPO, capture_output=True,
                                   text=True, timeout=30, check=False)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        rules = _section(self.agents, "## Non-negotiable rules")
        mutants = {
            "forward-port.pin": self.agents.replace("forward-port.pin", "the pin"),
            "coverage floor": self.agents.replace("`coverage` 7.10 or later", "`coverage`"),
            "a figure in the row": re.sub(r"^(\| pre-push hook \|.*)$", r"\1 in 9 minutes",
                                          self.agents, count=1, flags=re.M),
            "the rule moved out": self.agents.replace(rules, "\n\n", 1),
            "a retired review term": self.agents + "\nThe reviewer of record signs.\n",
        }
        for name, text in mutants.items():
            with self.subTest(mutant=name):
                self.assertNotEqual(self.agents, text, "the mutation did not apply")
                self.assertNotEqual([], pin_problems(text))


if __name__ == "__main__":
    unittest.main()
