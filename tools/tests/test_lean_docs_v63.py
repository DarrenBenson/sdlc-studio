"""US1137: the help, the reference and the public pages describe what 6.3 ships.

Each test names its mutant first: the page as it stood before US1137, which must fail it. What a
page claims is read against the code rather than a hand list where the code holds it: the lane's
hand-in path and call budget from `sprint.py`'s constants, the agent definitions from `init.py`'s
list, the harnesses from `token_meters.HARNESSES`, the start budget from the shipped config
defaults, the price table's path from `prices.TABLE_PATH`, the anatomy's JSON keys from
`cost_anatomy`'s source, the reference's line ceiling from `tools/check_budgets.py`, and whether a
6.2 project owes `migrate` anything from a real `migrate.py` run on a 6.2-shaped fixture.
"""
# test-census-subject: docs/existing-users.md
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
HELP = SKILL / "help" / "sprint.md"
REFERENCE = SKILL / "reference-sprint.md"
README = REPO / "README.md"
LLMS = REPO / "llms.txt"
WHY = REPO / "docs" / "why-sdlc-studio.md"
UPGRADE = REPO / "docs" / "existing-users.md"

sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(REPO / "tools"))
import check_budgets  # noqa: E402
import prices  # noqa: E402
import token_meters  # noqa: E402

#: How the public pages name each harness `token_meters.HARNESSES` meters.
HARNESS_NAMES = {"claude": "Claude Code", "codex": "Codex CLI", "copilot": "Copilot CLI",
                 "opencode": "OpenCode", "cursor": "Cursor"}


def _env() -> dict:
    """The caller's environment minus every git locating variable, so a hook's GIT_DIR cannot
    steer a fixture at the outer repository."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _py(script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv],
                          capture_output=True, text=True, check=False, timeout=600, env=_env())


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _between(text: str, start: str, end: str) -> str:
    """`text` from the first `start` up to the first `end` after it; '' when `start` is absent."""
    at = text.find(start)
    if at < 0:
        return ""
    stop = text.find(end, at + len(start))
    return text[at:] if stop < 0 else text[at:stop]


def _section(text: str, anchor: str) -> str:
    """The body of the heading carrying `{#anchor}`, up to the next heading of any level."""
    found = re.search(rf"(?m)^#+ .*\{{#{re.escape(anchor)}\}}\s*$", text)
    if not found:
        return ""
    rest = text[found.end():]
    nxt = re.search(r"(?m)^#+ ", rest)
    return rest[:nxt.start()] if nxt else rest


def _heading_section(text: str, heading: str) -> str:
    """The body under the heading line `heading`, up to the next heading of its level or higher."""
    found = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    if not found:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    rest = text[found.end():]
    nxt = re.search(rf"(?m)^#{{1,{level}}} ", rest)
    return rest[:nxt.start()] if nxt else rest


def _paragraph(text: str, start: str) -> str:
    """The paragraph that opens with `start`, or '' when none does."""
    at = text.find(start)
    if at < 0:
        return ""
    stop = text.find("\n\n", at)
    return text[at:] if stop < 0 else text[at:stop]


def _flat(text: str) -> str:
    """`text` with each run of whitespace read as one space, so a wrapped phrase still matches."""
    return re.sub(r"\s+", " ", text)


def _constants(path: Path, *names: str) -> dict:
    """The module-level literal each of `names` is bound to in `path`, read without importing."""
    out = {}
    for node in ast.parse(_read(path)).body:
        target = node.targets[0] if isinstance(node, ast.Assign) else (
            node.target if isinstance(node, ast.AnnAssign) else None)
        if isinstance(target, ast.Name) and target.id in names and node.value is not None:
            out[target.id] = ast.literal_eval(node.value)
    return out


class DocsV63Tests(unittest.TestCase):

    def test_the_lane_help_says_land_commits(self):
        """Mutant: the lane paragraph as US1120 left it, ending 'record the self-check
        (`critic.py self-check record --unit <id>`) and commit it: `git add -- <its Affects>`'
        and naming no hand-in file and no agent definition. AC1."""
        lane = _flat(_between(_read(HELP), "A brief is also a builder's whole brief", "```bash"))
        self.assertTrue(lane, "help/sprint.md has no lane brief paragraph")
        self.assertNotIn("critic.py self-check record", lane,
                         "the brief no longer records the self-check: `lane land` does")
        self.assertNotIn("and commit it", lane, "the brief no longer commits: `lane land` does")
        consts = _constants(SCRIPTS / "sprint.py", "LANE_HAND_IN", "LANE_HAND_OFF",
                            "LANE_CALLS_FIXED", "LANE_CALLS_PER_POINT")
        for needle in ("author self-check", "verify_ac.py run --id <id>", "git add -- <its Affects>",
                       "stage exactly its Affects", f"`{consts['LANE_HAND_IN']}/`",
                       "`commit-msg.txt`", "`<unit>-claims.json`", "`<unit>-mutants.json`",
                       f"`{consts['LANE_HAND_OFF']}`", "`sprint lane land` commits",
                       "records its self-check", "`general-purpose`"):
            self.assertIn(needle, lane, f"the lane paragraph does not say {needle!r}")
        fixed, per = consts["LANE_CALLS_FIXED"], consts["LANE_CALLS_PER_POINT"]
        self.assertIn(f"{fixed} plus {per} per point", lane,
                      "the call budget the help states is not the one sprint.py computes")
        defs = _constants(SCRIPTS / "init.py", "AGENT_DEFINITIONS")["AGENT_DEFINITIONS"]
        names = [Path(dst).stem for _src, dst in defs]
        self.assertEqual(sorted(names), ["sdlc-builder", "sdlc-reviewer"])
        for name in names:
            self.assertIn(f"`{name}`", lane, f"the lane paragraph does not name `{name}`")

    def test_the_meter_and_cost_pages_name_every_harness_and_the_price_table(self):
        """Mutant: the help's meter paragraph opening 'The meter reads the main thread and every
        subagent', which names Claude transcripts as the only meter, its `cost --anatomy`
        paragraph naming no window or start budget, and the reference's anatomy and dollar
        sections naming neither the start budget nor the price table. AC2."""
        help_text = _read(HELP)
        meter = _flat(_paragraph(help_text, "**The meter reads"))
        self.assertTrue(meter, "help/sprint.md has no meter paragraph")
        self.assertIn(f"`{token_meters.HARNESS_ENV}`", meter)
        for harness in token_meters.HARNESSES:
            self.assertIn(f"`{harness}`", meter, f"the meter paragraph does not name {harness}")
        self.assertIn("the environment signals", meter)
        self.assertIn("Under Claude Code", meter,
                      "the transcript reading must be stated as Claude Code's, not the only meter")
        self.assertIn("templates/model-prices.json", _flat(help_text))

        defaults = _read(SKILL / "templates" / "config-defaults.yaml")
        budget = re.search(r"(?m)^\s+agent_start_budget:\s*(\d+)\s*$", defaults)
        self.assertIsNotNone(budget, "config-defaults.yaml holds no cost.agent_start_budget")
        budget = budget.group(1)
        anatomy = _flat(_paragraph(help_text, "`cost --anatomy` reads"))
        for needle in ("open run's window", "`--session` reads the whole session",
                       "`cost.agent_start_budget`", budget, "`off` flags none"):
            self.assertIn(needle, anatomy, f"the help's anatomy paragraph does not say {needle!r}")

        ref = _read(REFERENCE)
        ref_anatomy = _flat(_section(ref, "cost-anatomy"))
        source = _read(SCRIPTS / "lib" / "cost_anatomy.py")
        for needle in ("`--session`", "`started_at`", "`cost.agent_start_budget`", budget,
                       "`off` flags none", "Subagent starts"):
            self.assertIn(needle, ref_anatomy, f"the reference's anatomy does not say {needle!r}")
        for key in ("start_budget", "over_start_budget", "start_not_available"):
            self.assertIn(f'"{key}"', source, f"cost_anatomy no longer emits {key}")
            self.assertIn(f"`{key}`", ref_anatomy, f"the reference does not name the {key} key")

        dollars = _flat(_section(ref, "dollar-cost"))
        table = prices.TABLE_PATH.relative_to(SKILL).as_posix()
        self.assertEqual(table, "templates/model-prices.json")
        for needle in (f"`{table}`", "`pricing.models`", f"`pricing.{prices.PREMIUM_REQUEST}`",
                       "reference-config.md#pricing"):
            self.assertIn(needle, dollars, f"the dollar section does not name {needle!r}")

        ceiling = check_budgets.ALLOWLIST["reference-sprint.md"]
        lines = len(ref.splitlines())
        self.assertLessEqual(lines, ceiling,
                             f"reference-sprint.md is {lines} lines, over its {ceiling} ceiling")

    def test_the_public_pages_name_what_63_adds(self):
        """Mutant: README naming no 6.3 feature, llms.txt installing into five tools without
        Cursor and naming no meter, and the economics section with three facts and no measured
        cost per point. AC3."""
        self.assertEqual(sorted(HARNESS_NAMES), sorted(token_meters.HARNESSES),
                         "a harness the meter reads has no public name here")
        cost = [b for b in re.split(r"\n\s*\n|\n(?=- )", _read(README)) if "US dollars" in b]
        self.assertEqual(len(cost), 1, "README states no single 6.3 cost paragraph")
        cost = _flat(cost[0])
        for name in HARNESS_NAMES.values():
            self.assertIn(name, cost, f"README's 6.3 paragraph does not name {name}")
        for needle in ("per point", "`sprint lane run --harness <h>`", "headless"):
            self.assertIn(needle, cost, f"README's 6.3 paragraph does not say {needle!r}")

        llms = _flat(" ".join(ln.lstrip("> ") for ln in _read(LLMS).splitlines()
                              if ln.startswith(">")))
        installs = re.search(r"Installs into (.*?)(?:, and meters|;)", llms)
        self.assertIsNotNone(installs, "llms.txt names no harness it installs into")
        self.assertIn("Cursor", installs.group(1))
        meters = re.search(r"meters a run's token cost on (.*?);", llms)
        self.assertIsNotNone(meters, "llms.txt names no harness it meters")
        for name in ("Claude Code", "Codex", "Copilot CLI", "opencode", "Cursor"):
            self.assertIn(name, meters.group(1), f"llms.txt does not say it meters {name}")

        economics = _flat(_heading_section(_read(WHY), "## The economics"))
        self.assertTrue(economics, "why-sdlc-studio.md has no economics section")
        for needle in ("Every run states what it cost", "priced cost per point", "US dollars"):
            self.assertIn(needle, economics, f"the economics section does not say {needle!r}")

    def test_existing_users_has_the_62_and_63_upgrade_paths(self):
        """Mutant: the upgrade page whose newest section is still 'From 6.0 to 6.1', with no 6.2
        section (BG1175) and no 6.3 one. AC4."""
        page = _read(UPGRADE)
        froms = re.findall(r"(?m)^### (From \S+ to \S+)\s*$", page)
        self.assertEqual(froms[:3], ["From 6.2 to 6.3", "From 6.1 to 6.2", "From 6.0 to 6.1"])
        six_two = _flat(_heading_section(page, "### From 6.1 to 6.2"))
        self.assertIn("release-notes-v6.2.0.md", six_two)
        six_three = _flat(_heading_section(page, "### From 6.2 to 6.3"))
        for needle in ("Reinstall", "`migrate`", "`migrate --apply`", "`sdlc-studio/.version`",
                       "retires no config key", "`release_strategy: pr-required`",
                       "`sprint lane land`", "commits"):
            self.assertIn(needle, six_three, f"the 6.3 section does not say {needle!r}")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "p"
            root.mkdir()
            made = _py("init.py", "--root", str(root), "run")
            self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
            (root / "sdlc-studio" / ".version").write_text(
                'schema_version: 2\nupgraded_from: 6.1.0\nupgraded_at: 2026-11-02\n'
                'skill_version: "6.2.0"\n', encoding="utf-8")
            config = root / "sdlc-studio" / ".config.yaml"
            body = re.sub(r"(?m)^release_strategy:.*\n", "", _read(config))
            config.write_text(body + "release_strategy: pr-required\n", encoding="utf-8")
            proc = _py("migrate.py", "--root", str(root), "--format", "json")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            owed = [item.get("detail", "") for item in json.loads(proc.stdout)["deterministic"]]
        self.assertTrue(all(".version" in detail for detail in owed),
                        f"migrate owes a 6.2 project more than its version stamp: {owed}")


if __name__ == "__main__":
    unittest.main()
