"""tools/lint_corpus.py - the whole-markdown-corpus lint lane (US0357).

The premise the change request was raised on turned out to be false: nothing here
lints "only changed markdown". Both `npm run lint:md` and the pre-commit `markdown`
lane already glob the whole tree. The real hole is a CONFIG SPLIT. A `**/*.md` glob
cannot match a path inside a dot-directory, so everything under `.claude/` is only
ever reached by the second lane, which runs under
`.claude/skills/sdlc-studio/.markdownlint.json` - a config that switches MD025,
MD035, MD040, MD051, MD055, MD056 and MD060 off. An unescaped table pipe in
`help/sprint.md` therefore sat green for an unknown number of commits: the strict
lane could not see the file and the lane that could see it had the rule disabled.

So the corpus lane enumerates from the TRACKED FILE LIST rather than from a shell
glob, and runs the strict root rule set over every one of them.
"""
from __future__ import annotations

import contextlib
import glob
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


lint_corpus = _load(REPO / "tools" / "lint_corpus.py", "lint_corpus")
#: The shipped git-fixture helper: it confines every fixture git call to the fixture
#: (see its own docstring). Imported rather than re-implemented so this module carries
#: no second copy of the repo-locating variable list.
gitutil = _load(REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py", "_lc_gitutil")

#: markdownlint-cli is a devDependency, so `npm install` provides it. Resolution walks up
#: from the repo, which is what makes this work from an agent worktree as well as a clone.
LINTER = lint_corpus.find_linter(REPO)

ROOT_CONFIG = (REPO / ".markdownlint.json").read_text(encoding="utf-8")
PAYLOAD_CONFIG = (REPO / ".claude/skills/sdlc-studio/.markdownlint.json").read_text(
    encoding="utf-8")

#: A table row whose cell contains unescaped pipes: markdownlint reads them as extra
#: columns (MD056) and as compact-style violations (MD060). This is the observed defect,
#: transcribed - the payload config switches both rules off.
UNESCAPED_PIPE_TABLE = (
    "# Sprint\n"
    "\n"
    "| Outcome | Meaning |\n"
    "| --- | --- |\n"
    "| achieved|partial|missed | the three sprint verdicts |\n"
)
#: The 1-indexed line the defect sits on above. Asserted as a value, not "somewhere".
DEFECT_LINE = 5


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _init_repo(root: Path) -> None:
    gitutil.git(["init", "-q", "-b", "main"], cwd=root)


def _commit_all(root: Path, message: str) -> str:
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-q", "-m", message], cwd=root)
    return gitutil.git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()


class CorpusEnumerationTests(unittest.TestCase):
    def test_tracked_payload_markdown_is_enumerated_despite_the_dot_directory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _init_repo(root)
            _write(root, ".gitignore", "node_modules/\n.claude/worktrees/\n")
            _write(root, "README.md", "# readme\n")
            payload = ".claude/skills/sdlc-studio/help/sprint.md"
            _write(root, payload, "# sprint\n")
            # Ignored trees. Both contain markdown and neither is corpus: node_modules is a
            # third party's, and .claude/worktrees/ holds an agent's in-progress checkout.
            _write(root, "node_modules/pkg/readme.md", "# vendor\n")
            _write(root, ".claude/worktrees/agent-x/scratch.md", "# scratch\n")
            _commit_all(root, "seed")
            # Untracked but not ignored: real on any working tree, still not corpus.
            _write(root, "scratch-untracked.md", "# untracked\n")

            self.assertEqual(lint_corpus.enumerate_corpus(root), [payload, "README.md"])

            # The premise, pinned. A shell glob cannot see into a dot-directory, which is
            # why enumerating from a glob is what let the payload file hide.
            globbed = sorted(glob.glob("**/*.md", root_dir=str(root), recursive=True))
            self.assertIn("README.md", globbed)
            self.assertNotIn(payload, globbed,
                             "if `**/*.md` now matches a dot-directory the config split has "
                             "changed and this lane's premise needs revisiting")


class StrictRuleSetTests(unittest.TestCase):
    def test_a_rule_the_payload_config_relaxes_is_still_reported_by_the_corpus_lane(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _init_repo(root)
            _write(root, ".markdownlint.json", ROOT_CONFIG)
            _write(root, ".claude/skills/sdlc-studio/.markdownlint.json", PAYLOAD_CONFIG)
            payload = ".claude/skills/sdlc-studio/help/sprint.md"
            _write(root, payload, UNESCAPED_PIPE_TABLE)
            _commit_all(root, "seed")

            # The hole, measured rather than asserted: under the config the per-commit
            # payload lane uses, this defect is not a finding at all.
            relaxed = lint_corpus.lint_files(
                [payload], cwd=root, linter=LINTER,
                config=root / ".claude/skills/sdlc-studio/.markdownlint.json")
            self.assertEqual([f.rule for f in relaxed if f.rule in ("MD056", "MD060")], [],
                             "the payload config no longer relaxes the observed defect - "
                             "this test's premise has moved")

            findings = lint_corpus.lint_corpus(root, linter=LINTER)

            table = [f for f in findings if f.rule == "MD056"]
            self.assertEqual(len(table), 1, f"expected one MD056 finding, got {findings}")
            self.assertEqual(table[0].path, payload)
            self.assertEqual(table[0].line, DEFECT_LINE)
            self.assertIn("MD060", {f.rule for f in findings},
                          "the strict rule set reports the pipe spacing too")

    def test_a_missing_linter_is_an_error_and_never_a_clean_report(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _init_repo(root)
            _write(root, ".markdownlint.json", ROOT_CONFIG)
            _write(root, "broken.md", UNESCAPED_PIPE_TABLE)
            _commit_all(root, "seed")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = lint_corpus.main(["--root", str(root), "--linter", str(root / "nope")])
            self.assertNotEqual(rc, 0)
            self.assertIn("markdownlint", err.getvalue())
            self.assertNotIn("0 findings", out.getvalue())


class LaneWiringTests(unittest.TestCase):
    def test_the_corpus_lane_is_scheduled_and_absent_from_the_precommit_hook(self) -> None:
        workflow = yaml.safe_load(
            (REPO / ".github/workflows/lint.yml").read_text(encoding="utf-8"))
        # A bare `on:` key parses as the YAML boolean True; accept either spelling.
        triggers = workflow.get("on", workflow.get(True)) or {}
        self.assertIn("schedule", triggers,
                      "the corpus lane must run on a schedule, not only on a push")

        owners = [name for name, job in workflow["jobs"].items()
                  for step in job.get("steps", [])
                  if "lint_corpus.py" in str(step.get("run", ""))
                  or "lint:corpus" in str(step.get("run", ""))]
        self.assertEqual(len(owners), 1, f"exactly one workflow step runs the corpus lane, "
                                         f"found {owners}")
        self.assertNotEqual(owners[0], "ci",
                            "the corpus lane must not sit in the per-push `ci` job")
        self.assertIn("schedule", str(workflow["jobs"][owners[0]].get("if", "")),
                      "the corpus job must be gated on the scheduled/dispatched event, or "
                      "every push pays for a whole-corpus lint")

        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertIn("lint:corpus", scripts)
        self.assertIn("tools/lint_corpus.py", scripts["lint:corpus"])

        hook = (REPO / ".githooks/pre-commit").read_text(encoding="utf-8")
        self.assertNotIn("lint_corpus", hook,
                         "the pre-commit gate already runs ~197s against a 120s budget - the "
                         "corpus lane must add nothing to it")
        self.assertNotIn('run "corpus"', hook)

    def test_the_corpus_lane_is_not_wired_into_the_per_commit_lint_script(self) -> None:
        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertNotIn("lint:corpus", scripts["lint"],
                         "`npm run lint` is the per-commit aggregate; the corpus lane is "
                         "periodic and pre-release")


def _rfc(number: str, status: str, decision: str) -> str:
    return (f"# RFC{number}: t\n\n> **Status:** {status}\n> **Priority:** High\n\n"
            f"## Summary\n\ns\n\n## Decision\n\n{decision}\n\n## Related Artifacts\n\nnone\n")


PENDING = "**Outcome:** pending `rfc decide`\n**Rationale:** pending\n"
FILLED = "**Outcome:** Option B, 2026-11-14 (D0474)\n**Rationale:** the operator's call\n"


class AcceptedRfcDecisionTests(unittest.TestCase):
    def _fixture(self, rfcs: dict) -> Path:
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        root = Path(d.name)
        _init_repo(root)
        _write(root, ".markdownlint.json", ROOT_CONFIG)
        for name, text in rfcs.items():
            _write(root, f"sdlc-studio/rfcs/{name}.md", text)
        _commit_all(root, "seed")
        return root

    def test_an_accepted_rfc_with_a_pending_outcome_is_reported(self) -> None:
        root = self._fixture({
            "RFC0001-accepted-pending": _rfc("0001", "Accepted", PENDING),
            "RFC0002-proposed-pending": _rfc("0002", "Proposed", PENDING),
            "RFC0003-accepted-filled": _rfc("0003", "Accepted", FILLED),
            "RFC0004-accepted-shouting": _rfc("0004", "Accepted", "**Outcome:** PENDING\n"),
            "RFC0005-accepted-empty": _rfc("0005", "Accepted", "**Outcome:**\n"),
            "RFC0006-accepted-template": _rfc("0006", "Accepted", "**Outcome:** {{outcome}}\n"),
            "RFC0007-accepted-no-outcome": _rfc("0007", "Accepted", "> *Filled on acceptance.*\n"),
            "RFC0010-pending-below-the-decision": _rfc("0010", "Accepted", "no outcome line")
            + "\n## Notes\n\n**Outcome:** pending\n",
            "RFC0008-accepted-pending-word": _rfc("0008", "Accepted",
                                                  "**Outcome:** Option B; pending is no word\n"),
        })
        found = lint_corpus.accepted_rfc_decision_findings(root)
        self.assertEqual(["sdlc-studio/rfcs/RFC0001-accepted-pending.md",
                          "sdlc-studio/rfcs/RFC0004-accepted-shouting.md",
                          "sdlc-studio/rfcs/RFC0005-accepted-empty.md",
                          "sdlc-studio/rfcs/RFC0006-accepted-template.md"],
                         [f.path for f in found])
        first = found[0]
        self.assertEqual(lint_corpus.RFC_DECISION_RULE, first.rule)
        self.assertEqual(12, first.line, "the line of the Outcome, as a value")
        self.assertEqual("**Outcome:** pending `rfc decide`", first.context)
        # The whole-corpus entry point carries the rule beside markdownlint's findings.
        linted = lint_corpus.lint_corpus(root, linter=LINTER)
        self.assertEqual([f.path for f in found],
                         [f.path for f in linted if f.rule == lint_corpus.RFC_DECISION_RULE])
        # Through the lane: the finding is in the run's result, unattributed with no baseline.
        result = lint_corpus.analyse(root, baseline=None, linter=LINTER)
        rows = [f for f in result["findings"] if f["rule"] == lint_corpus.RFC_DECISION_RULE]
        self.assertEqual(4, len(rows), rows)
        self.assertTrue(all(r["status"] == lint_corpus.UNATTRIBUTED for r in rows))
        self.assertEqual(1, lint_corpus.exit_code(result))
        self.assertIn("RFC0001-accepted-pending.md:12 RFC-DECISION",
                      lint_corpus.render(result))
        # Attributed: the same finding at the baseline is pre-existing, a new one introduced.
        base = gitutil.git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()
        _write(root, "sdlc-studio/rfcs/RFC0009-new.md", _rfc("0009", "Accepted", PENDING))
        _commit_all(root, "add")
        attributed = lint_corpus.analyse(root, baseline=base, linter=LINTER)
        by = {f["path"].split("/")[-1][:7]: f["status"] for f in attributed["findings"]
              if f["rule"] == lint_corpus.RFC_DECISION_RULE}
        self.assertEqual(lint_corpus.PRE_EXISTING, by["RFC0001"])
        self.assertEqual(lint_corpus.INTRODUCED, by["RFC0009"])

    def test_only_a_heading_reading_decision_alone_opens_the_decision_section(self) -> None:
        """A `## Decisions (...)` heading, such as RFC0020's list of resolved decisions, is not
        the Decision section: a pending Outcome under it is not reported, and it does not hide a
        pending Outcome in the `## Decision` section below it."""
        resolved_list = "## Decisions (resolved later)\n\n**Outcome:** pending\n\n"
        root = self._fixture({
            "RFC0001-decisions-heading-alone": _rfc("0001", "Accepted", "x").replace(
                "## Decision\n\nx\n\n", resolved_list),
            "RFC0002-decisions-above-decision": _rfc("0002", "Accepted", PENDING).replace(
                "## Decision\n", "## Decisions (resolved by the consultation)\n\nD1 B\n\n"
                "## Decision\n"),
        })
        alone = root / "sdlc-studio/rfcs/RFC0001-decisions-heading-alone.md"
        self.assertNotIn("\n## Decision\n", alone.read_text(encoding="utf-8"))
        found = lint_corpus.accepted_rfc_decision_findings(root)
        self.assertEqual(["sdlc-studio/rfcs/RFC0002-decisions-above-decision.md"],
                         [f.path for f in found])
        self.assertEqual("**Outcome:** pending `rfc decide`", found[0].context)

    def test_a_non_utf8_or_non_rfc_file_is_not_a_finding_and_not_a_crash(self) -> None:
        root = self._fixture({"RFC0001-bad-bytes": "x"})
        (root / "sdlc-studio/rfcs/RFC0001-bad-bytes.md").write_bytes(b"\xff\xfe\x00bad")
        _write(root, "docs/RFC0002-notes.md", _rfc("0002", "Accepted", PENDING))
        _write(root, "sdlc-studio/rfcs/RFC0003-ok.md", _rfc("0003", "Accepted", FILLED))
        _commit_all(root, "more")
        self.assertEqual([], lint_corpus.accepted_rfc_decision_findings(root))


class CorpusLaneRunsOnThisRepo(unittest.TestCase):
    """The lane against the real corpus. Not a green/red assertion - the repo carries
    hundreds of pre-existing findings - but the enumeration must be real and the run
    must complete, or the lane is wired to nothing."""

    def test_the_real_corpus_is_enumerated_and_linted(self) -> None:
        files = lint_corpus.enumerate_corpus(REPO)
        self.assertGreater(len(files), 100, "the tracked markdown corpus went missing")
        self.assertTrue(any(f.startswith(".claude/skills/sdlc-studio/") for f in files),
                        "the shipped payload is not in the enumeration")
        self.assertTrue(all(f.endswith(".md") for f in files))
        tracked = {p for p in subprocess.run(
            ["git", "ls-files", "-z"], cwd=REPO, capture_output=True, text=True,
            check=True).stdout.split("\0") if p}
        self.assertTrue(set(files) <= tracked, "the lane enumerated an untracked file")

    def test_no_accepted_rfc_here_has_a_pending_decision(self) -> None:
        self.assertEqual([], [f"{f.path}:{f.line}" for f in
                              lint_corpus.accepted_rfc_decision_findings(REPO)])
        # Positive control: the rule does read this repository's RFCs.
        rfcs = [p for p in lint_corpus.enumerate_corpus(REPO) if "sdlc-studio/rfcs/RFC" in p]
        self.assertGreater(len(rfcs), 30, "the RFCs went missing from the enumeration")
        for number in ("0063", "0064"):
            path = next(p for p in rfcs if f"/RFC{number}-" in p)
            text = (REPO / path).read_text(encoding="utf-8")
            self.assertIn("> **Status:** Accepted", text)
            decision = text.split("\n## Decision\n", 1)[1].split("\n## ", 1)[0]
            for field in ("Outcome", "Date", "Rationale", "Decisions", "Spawned CRs"):
                self.assertRegex(decision, rf"\*\*{field}:\*\*\s*\S", f"{number} {field}")
            self.assertNotRegex(decision, r"(?i):\*\*\s*pending")

    def test_rfc0063_deferred_workstreams_name_a_request_or_ruling(self) -> None:
        text = next((REPO / p).read_text(encoding="utf-8")
                    for p in lint_corpus.enumerate_corpus(REPO)
                    if "sdlc-studio/rfcs/RFC0063-" in p)
        decomposed = set(re.findall(r"CR\d{4}", re.search(
            r"^> \*\*Decomposed-into:\*\*(.*)$", text, re.M).group(1)))
        rows = {m.group(1): m.group(2) for m in re.finditer(
            r"^\| (WS\d) \|(?:[^|]*\|){2}([^|]*)\|", text, re.M)}
        self.assertEqual({f"WS{n}" for n in range(1, 9)}, set(rows))
        for ws in ("WS2", "WS5", "WS6", "WS7"):
            cell = rows[ws]
            self.assertNotIn("(new)", cell, f"{ws} still promises a CR nothing carries")
            cited = set(re.findall(r"CR\d{4}", cell))
            self.assertTrue(re.search(r"D\d{4}", cell) or cited & decomposed,
                            f"{ws} names no decomposed CR and no ruling: {cell!r}")
        for ws in ("WS1", "WS3"):
            self.assertNotIn("(new)", rows[ws], ws)
        for number in ("0063", "0064"):
            rfc = next((REPO / p).read_text(encoding="utf-8")
                       for p in lint_corpus.enumerate_corpus(REPO)
                       if f"sdlc-studio/rfcs/RFC{number}-" in p)
            history = rfc.split("## Revision History", 1)[1]
            self.assertRegex(history, r"\| Decision section filled", number)
        # RFC0063's row records the workstream rewrite too: each row that read `CR (new)`.
        row = re.search(r"^\|[^\n]*\| Decision section filled[^\n]*$", text, re.M).group(0)
        self.assertIn("`CR (new)`", row)
        for ws in ("WS1", "WS2", "WS3", "WS5", "WS6", "WS7"):
            self.assertRegex(row, rf"\b{ws}\b", f"the revision row does not name {ws}")
        self.assertNotRegex(row, r"\bWS[48]\b", "WS4 and WS8 were not rewritten")


if __name__ == "__main__":
    unittest.main()
