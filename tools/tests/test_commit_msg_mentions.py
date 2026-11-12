"""US1116: the commit-msg hook's paste-ready trailers skip an id a `Mentions:` line accounts for.

When `check-commit-msg --strict` refuses, the hook prints a `Refs:` line to paste for each id the
subject names and no trailer accounts for. It read only `Refs:` lines, so beside a
`Mentions: <id>` line it still asked for `Refs: <id>`: the false attribution `Mentions:` exists
to avoid. Each test runs the real hook, the way git invokes it, in a throwaway repository.
"""
# test-census-subject: .githooks/commit-msg
from __future__ import annotations

import ast
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "commit-msg"
SUBJECT = "feat(US1110): repair the lane BG0989 raised, beside BG1000"


def _load_gitutil():
    """The shipped git-fixture helper, which confines every fixture git call to the fixture.
    Loaded rather than re-implemented, so this module carries no second copy of its list."""
    path = REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py"
    spec = importlib.util.spec_from_file_location("_commit_msg_mentions_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()


def _env() -> dict:
    env = gitutil.git_env()
    # A passing hook prints one summary line unless SDLC_GATE_VERBOSE=1, and this module reads
    # the per-lane list a pass prints, so its hooks run verbose unless a test asks otherwise.
    env.setdefault("SDLC_GATE_VERBOSE", "1")
    return env


def _hook(message: str) -> subprocess.CompletedProcess:
    """The commit-msg hook on `message`, run in a fixture repository whose skill scripts are
    this tree's own, so the refusal the script makes is the one under test."""
    with tempfile.TemporaryDirectory() as d:
        repo = Path(d)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=_env())
        skill = repo / ".claude" / "skills" / "sdlc-studio"
        skill.mkdir(parents=True)
        (skill / "scripts").symlink_to(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts")
        msg = repo / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        return subprocess.run(["bash", str(HOOK), str(msg)], cwd=repo, capture_output=True,
                              text=True, env=_env(), timeout=120)


def _pasted(out: str) -> list[str]:
    """The trailer lines the hook offers to paste: each output line that is only a trailer."""
    return re.findall(r"^\s*((?:Refs|Mentions): \S+)\s*$", out, re.MULTILINE)


class CommitMsgMentionsTests(unittest.TestCase):

    def test_the_hint_skips_an_id_a_mentions_line_covers(self):
        # AC1. Must fail on: `covered` grepping only `^Refs:` (a `Refs: BG0989` line is then
        # printed), or the hint offering no `Mentions:` line.
        for trailer in ("Mentions: BG0989", "mentions: BG0989"):
            with self.subTest(trailer=trailer):
                r = _hook(f"{SUBJECT}\n\n{trailer}\n")
                out = r.stdout + r.stderr
                self.assertNotEqual(r.returncode, 0, out)
                self.assertEqual(_pasted(out),
                                 ["Refs: BG1000", "Refs: US1110", "Mentions: <id>"], out)
                self.assertNotIn("Refs: BG0989", out)
                self.assertIn("only mentions", out)
        # Positive control: with the two owed `Refs:` lines added, the same message passes.
        r = _hook(f"{SUBJECT}\n\nRefs: US1110\nRefs: BG1000\nMentions: BG0989\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((r.stdout + r.stderr).strip(), "ok   message-refs")

    def test_the_lane_rule_names_mentions(self):
        # AC2. Must fail on: the `run "message-refs"` rule string left naming only `Refs:`.
        r = subprocess.run(["bash", str(HOOK), "--list"], cwd=REPO, capture_output=True,
                           text=True, env=_env(), timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        rules = dict(ln.split("\t", 1) for ln in r.stdout.splitlines() if "\t" in ln)
        rule = rules["message-refs"]
        self.assertIn("Refs: <id> for an id that owns the commit's files", rule)
        self.assertIn("Mentions: <id> for an id that owns none of them", rule)

    def test_enable_hooks_names_mentions(self):
        # The line `enable-hooks.sh` prints about the rule names both trailers.
        with tempfile.TemporaryDirectory() as d:
            clone = Path(d)
            subprocess.run(["git", "init", "-q"], cwd=clone, check=True, env=_env())
            (clone / ".githooks").mkdir()
            shutil.copy(HOOK, clone / ".githooks" / "commit-msg")
            (clone / "tools").mkdir()
            shutil.copy(REPO / "tools" / "enable-hooks.sh", clone / "tools" / "enable-hooks.sh")
            r = subprocess.run(["bash", "tools/enable-hooks.sh"], cwd=clone, capture_output=True,
                               text=True, env=_env(), timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        line = next(ln for ln in r.stdout.splitlines() if ln.startswith("A multi-id commit"))
        self.assertIn("'Refs: <id>' trailer per owning id", line)
        self.assertIn("'Mentions: <id>'", line)


class DerivedMentionsTests(unittest.TestCase):
    """US1133 AC2: an id the subject names but whose `Affects` declares none of the staged files
    gets a `Mentions:` line written for it, never `Refs:`."""

    def test_a_non_owning_id_gets_mentions(self):
        # Must fail on: writing `Refs:` for every id the subject names.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=_env())
            skill = repo / ".claude" / "skills" / "sdlc-studio"
            skill.mkdir(parents=True)
            (skill / "scripts").symlink_to(REPO / ".claude/skills/sdlc-studio/scripts")
            # US1110 owns the staged file; BG0989 is a unit whose Affects names another file;
            # BG1000 has no artefact here at all, so nothing can make it an owner.
            for rel, rid, owned in (("stories", "US1110", "src/lane.py"),
                                    ("bugs", "BG0989", "src/elsewhere.py")):
                folder = repo / "sdlc-studio" / rel
                folder.mkdir(parents=True)
                (folder / f"{rid}-sample.md").write_text(
                    f"# {rid}: sample\n\n> **Status:** In Progress\n> **Affects:** {owned}\n",
                    encoding="utf-8")
            # Committed first, so the one staged change is the source file, not an artefact
            # whose own filename would make its unit an owner.
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=_env())
            subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=repo, check=True,
                           env=_env())
            (repo / "src").mkdir()
            (repo / "src" / "lane.py").write_text("x = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=_env())
            msg = repo / "COMMIT_EDITMSG"
            msg.write_text(f"{SUBJECT}\n", encoding="utf-8")
            r = subprocess.run(["bash", str(HOOK), str(msg)], cwd=repo, capture_output=True,
                               text=True, env=_env(), timeout=120)
            after = msg.read_text(encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(
            after, f"{SUBJECT}\n\nRefs: US1110\nMentions: BG0989\nMentions: BG1000\n")
        self.assertNotIn("Refs: BG0989", after)
        self.assertNotIn("Refs: BG1000", after)

    def _repo(self, d: str, units: tuple[tuple[str, str, str], ...],
              files: dict[str, str]) -> Path:
        """A fixture repository running this tree's skill scripts: each (folder, id, Affects)
        unit's artefact and each of `files` committed as the seed, so whatever a test stages
        next is the commit under judgement."""
        repo = Path(d)
        gitutil.git(["init", "-q"], cwd=repo)
        skill = repo / ".claude" / "skills" / "sdlc-studio"
        skill.mkdir(parents=True)
        (skill / "scripts").symlink_to(REPO / ".claude/skills/sdlc-studio/scripts")
        for rel, rid, owned in units:
            folder = repo / "sdlc-studio" / rel
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{rid}-sample.md").write_text(
                f"# {rid}: sample\n\n> **Status:** In Progress\n> **Affects:** {owned}\n",
                encoding="utf-8")
        for rel, text in files.items():
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text(text, encoding="utf-8")
        gitutil.git(["add", "-A"], cwd=repo)
        gitutil.git(["commit", "-q", "-m", "seed"], cwd=repo)
        return repo

    def _commit(self, repo: Path, message: str) -> tuple[subprocess.CompletedProcess, str]:
        """The hook on `message` against what `repo` has staged, and the message it leaves."""
        msg = repo / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        r = subprocess.run(["bash", str(HOOK), str(msg)], cwd=repo, capture_output=True,
                           text=True, env=_env(), timeout=120)
        return r, msg.read_text(encoding="utf-8")

    @staticmethod
    def _refusal_sentences(text: str) -> list[str]:
        """Each sentence of `text` that states the refusal of a `Refs:` line ownership denies."""
        flat = re.sub(r"\s+", " ", text)
        return [s for s in re.split(r"(?<=[.;])\s+", flat)
                if "Refs:" in s and re.search(r"refus|contradict", s)
                and re.search(r"own(?:s|ing) none", s)]

    def test_a_single_id_refs_lands_and_a_multi_id_one_is_refused(self):
        # BG1264 AC1. The refusal of a `Refs:` line ownership denies judges only a subject
        # naming two or more ids; a single-id subject passes untouched, and the prose says so.
        # Must fail on: either text stating the refusal with no multi-id qualifier, or the
        # two-id case landing.
        units = (("stories", "US0001", "src/a.py"), ("stories", "US0002", "src/b.py"))
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, units, {"src/a.py": "x = 1\n", "src/b.py": "x = 1\n"})
            (repo / "src" / "a.py").write_text("x = 2\n", encoding="utf-8")
            gitutil.git(["add", "-A"], cwd=repo)
            single = "fix(US0002): x\n\nRefs: US0002\n"
            r, after = self._commit(repo, single)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(after, single)
            pair = "fix(US0001, US0002): x\n\nRefs: US0002\n"
            r, after = self._commit(repo, pair)
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, out)
        self.assertRegex(out, r"Refs: US0002[^\n]*owns none of the staged files")
        self.assertEqual(after, pair, "a refused message is not rewritten")
        header = []
        enable = (REPO / "tools" / "enable-hooks.sh").read_text(encoding="utf-8")
        for line in enable.splitlines()[1:]:
            if not line.startswith("#"):
                break
            header.append(line.lstrip("#").strip())
        tree = ast.parse((REPO / ".claude/skills/sdlc-studio/scripts/engagement_floor.py")
                         .read_text(encoding="utf-8"))
        doc = next(ast.get_docstring(n) for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "derive_trailers")
        for name, text in (("tools/enable-hooks.sh header", " ".join(header)),
                           ("derive_trailers docstring", doc or "")):
            said = self._refusal_sentences(text)
            with self.subTest(text=name):
                self.assertTrue(said, f"the {name} states no refusal of a Refs: line")
                for sentence in said:
                    self.assertIn("two or more ids", sentence)

    def test_a_paperwork_commit_refs_lands_and_a_source_contradiction_is_refused(self):
        # BG1264 AC2. A verdict, self-check or Done-transition commit names the unit it records
        # with `Refs:`; the ledger row it adds, or the unit's own artefact, makes that unit an
        # owner, so it lands at its first attempt with no line to rewrite. Must fail on: the
        # ledgers owned by no unit (the paperwork refusals of the round-1 replay), or by every unit
        # with a row anywhere in them, or a `Refs:` contradicting a staged source file landing.
        verdicts = "sdlc-studio/reviews/critic-verdicts.md"
        checks = "sdlc-studio/reviews/author-self-checks.md"
        artefact = "sdlc-studio/bugs/BG0989-sample.md"
        units = (("stories", "US1110", "src/lane.py"), ("bugs", "BG0989", "src/elsewhere.py"))
        seed = {"src/lane.py": "x = 1\n", "src/elsewhere.py": "x = 1\n",
                # BG0989 already has a row: only a row the commit ADDS makes an owner.
                verdicts: "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
                          "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                          "| BG0989 | REJECT | r | a | 2026-11-01 | x | full | old |\n",
                checks: "| Unit | Author | Date | Claims | Mutants | Digest |\n"
                        "| --- | --- | --- | --- | --- | --- |\n"}
        subject = "chore(US1110, BG0989): record the review"
        rows = {verdicts: "| {} | APPROVE | r | a | 2026-11-09 | y | full | none |\n",
                checks: "| {} | a | 2026-11-09 | TRUE 3 | killed 2 | d at e |\n"}
        cases = (  # (the rows the commit adds, a source file it stages, message, lands?)
            ({verdicts: "US1110"}, None, "Refs: US1110\nMentions: BG0989\n", True),
            ({checks: "BG0989"}, None, "Mentions: US1110\nRefs: BG0989\n", True),
            ({}, artefact, "Mentions: US1110\nRefs: BG0989\n", True),
            ({verdicts: "US1110"}, None, "Refs: US1110\nRefs: BG0989\n", False),
            ({}, "src/lane.py", "Refs: US1110\nRefs: BG0989\n", False),
        )
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d, units, seed)
            for added, source, trailers, lands in cases:
                with self.subTest(added=added, source=source, trailers=trailers):
                    gitutil.git(["reset", "-q", "--hard"], cwd=repo)
                    for rel, rid in added.items():
                        with (repo / rel).open("a", encoding="utf-8") as fh:
                            fh.write(rows[rel].format(rid))
                    if source:
                        with (repo / source).open("a", encoding="utf-8") as fh:
                            fh.write("changed\n")
                    gitutil.git(["add", "-A"], cwd=repo)
                    message = f"{subject}\n\n{trailers}"
                    r, after = self._commit(repo, message)
                    out = r.stdout + r.stderr
                    self.assertEqual(after, message, "no line is rewritten either way")
                    if lands:
                        self.assertEqual(r.returncode, 0, out)
                    else:
                        self.assertNotEqual(r.returncode, 0, out)
                        self.assertRegex(out, r"Refs: BG0989[^\n]*owns none of the staged files")
                        self.assertNotRegex(out, r"Refs: US1110[^\n]*owns none")
            # With no trailer at all, the hook writes the ledger row's unit `Refs:`.
            gitutil.git(["reset", "-q", "--hard"], cwd=repo)
            with (repo / verdicts).open("a", encoding="utf-8") as fh:
                fh.write(rows[verdicts].format("US1110"))
            gitutil.git(["add", "-A"], cwd=repo)
            r, after = self._commit(repo, f"{subject}\n")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(after, f"{subject}\n\nRefs: US1110\nMentions: BG0989\n")


if __name__ == "__main__":
    unittest.main()
