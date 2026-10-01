"""US0972: derived figures read honestly.

Four figures the tools derive read wrong: extension-less root files (`CODEOWNERS`, `Gemfile`)
were not taken as Affects paths, so the plan said a unit declared no Affects when its tokens
were only unrecognised; `reconcile apply` left the story index's `Stories by Epic` view at its
header; and the TSD's staleness compared commit-time strings, so a time written in another
offset could read as later than it was. Each runs the shipped entry point in a temporary tree.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402


def _cli(root: Path, script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(_SCRIPTS / script), *argv, "--root", str(root)],
                          cwd=root, env=gitutil.git_env(), capture_output=True, text=True,
                          timeout=300)


def _project(root: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], env=gitutil.git_env(), check=True,
                   capture_output=True)
    r = _cli(root, "init.py", "run")
    if r.returncode != 0:
        raise AssertionError(r.stdout + r.stderr)
    return root


def _story(root: Path, sid: str, affects: str, epic: str = "EP0001") -> None:
    (root / "sdlc-studio" / "stories" / f"{sid}-s.md").write_text(
        f"# {sid}: s\n\n> **Status:** Ready\n> **Epic:** {epic}\n> **Points:** 2\n"
        f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n### AC1: works\n\n"
        "- **Given** a\n- **When** b\n- **Then** c\n- **Verify:** shell true\n",
        encoding="utf-8")


def _sprint():
    spec = importlib.util.spec_from_file_location("sprint", _SCRIPTS / "sprint.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod


class DerivedFiguresHonestTests(unittest.TestCase):

    def test_extensionless_root_files_are_read_as_files(self) -> None:
        """AC1. MUTANTS: (1) HEAD's fixed list - all four dropped and the unit reported as
        lacking Affects; (2) any bare word taken as a file - `none` and an id would be paths;
        (3) an upper-case shape - a placeholder (`UNKNOWN`, `PENDING`) read as a file."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            _story(root, "US0001", "CODEOWNERS, VERSION, Gemfile, Procfile")
            r = _cli(root, "sprint.py", "breakdown", "--stories", "Ready", "--format", "json")
            report = json.loads(r.stdout)
        self.assertEqual([], [u for u in report["ungroomed"] if "Affects" in u["missing"]],
                         report["ungroomed"])
        sys.path.insert(0, str(_SCRIPTS / "lib"))
        import sdlc_md  # noqa: PLC0415
        self.assertEqual(["CODEOWNERS", "VERSION", "Gemfile", "Procfile"],
                         sdlc_md.affects_files("> **Affects:** CODEOWNERS, VERSION, Gemfile, "
                                               "Procfile\n"))
        self.assertEqual([], sdlc_md.affects_files("> **Affects:** none, US0001, TBD\n"))
        self.assertEqual([], sdlc_md.affects_files("> **Affects:** UNKNOWN, PENDING, "
                                                   "TODO_LATER\n"))

    def test_dropped_tokens_are_named_not_called_absent(self) -> None:
        """AC2. MUTANT: HEAD's single wording - `declare no Affects` for a unit whose Affects
        holds tokens, with the tokens unnamed."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            cfg = root / "sdlc-studio" / ".config.yaml"
            cfg.write_text(cfg.read_text(encoding="utf-8")
                           + "\nsprint:\n  breakdown: judgement\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("", encoding="utf-8")
            _story(root, "US0001", "src/a.py")
            _story(root, "US0002", "the parser, the docs")
            r = _cli(root, "sprint.py", "plan", "--stories", "Ready", "--no-fetch")
        line = next(ln for ln in (r.stdout + r.stderr).splitlines() if "delivery mode" in ln)
        self.assertNotIn("declare no Affects", line)
        self.assertIn("US0002", line)
        self.assertIn("the parser", line)
        self.assertIn("not recognised", line)

    def test_reconcile_fills_the_stories_by_epic_table(self) -> None:
        """AC3. MUTANTS: (1) HEAD - the view left at its header;
        (2) every story put under one epic; (3) a second apply rewrites the view again (not a
        fixed point)."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            epics = []
            for title in ("Alpha", "Beta"):
                r = _cli(root, "artifact.py", "new", "--type", "epic", "--title", title,
                         "--format", "json")
                self.assertEqual(0, r.returncode, r.stderr)
                epics.append(json.loads(r.stdout)["id"])
            spec = root / "spec.json"
            spec.write_text(json.dumps([{"title": "one", "epic": epics[0]},
                                        {"title": "two", "epic": epics[1]},
                                        {"title": "three", "epic": epics[0]}]),
                            encoding="utf-8")
            r = _cli(root, "artifact.py", "batch", "--type", "story", "--spec", str(spec),
                     "--format", "json")
            self.assertEqual(0, r.returncode, r.stderr)
            minted = {it["path"].rsplit("-", 1)[1][:-3]: it["id"]
                      for it in json.loads(r.stdout)["created"]}
            r = _cli(root, "reconcile.py", "apply")
            self.assertEqual(0, r.returncode, r.stderr)
            index = (root / "sdlc-studio" / "stories" / "_index.md").read_text(encoding="utf-8")
            again = _cli(root, "reconcile.py", "apply")
            self.assertEqual(index, (root / "sdlc-studio" / "stories" / "_index.md")
                             .read_text(encoding="utf-8"), again.stdout)
        view = index.split("## Stories by Epic", 1)[1].split("\n## ", 1)[0]
        sections = {}
        for chunk in view.split("\n### ")[1:]:
            head, _, body = chunk.partition("\n")
            sections[next(e for e in epics if e in head)] = body
        self.assertEqual(set(epics), set(sections))
        for title, epic in (("one", epics[0]), ("two", epics[1]), ("three", epics[0])):
            self.assertIn(f"[{minted[title]}]({minted[title]}-{title}.md) | {title} |",
                          sections[epic])
            other = next(e for e in epics if e != epic)
            self.assertNotIn(f"[{minted[title]}]", sections[other])

    def test_the_view_escapes_once_and_counts_only_what_changed(self) -> None:
        """US0972 round 1. MUTANTS: (1) the title escaped before `join_row` escapes it again -
        `three \\\\| pipe` splits the cell; (2) every row in the view reported as changed."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            r = _cli(root, "artifact.py", "new", "--type", "epic", "--title", "Alpha",
                     "--format", "json")
            epic = json.loads(r.stdout)["id"]
            for title in ("three | pipe", "plain"):
                r = _cli(root, "artifact.py", "new", "--type", "story", "--title", title,
                         "--epic", epic)
                self.assertEqual(0, r.returncode, r.stderr)
            index = root / "sdlc-studio" / "stories" / "_index.md"
            view = index.read_text(encoding="utf-8").split("## Stories by Epic")[1]
            view = view.split("\n## ")[0]
            self.assertIn("| three \\| pipe |", view)
            self.assertNotIn("\\\\|", view)
            r = _cli(root, "artifact.py", "new", "--type", "story", "--title", "third",
                     "--epic", epic)
            self.assertEqual(0, r.returncode, r.stderr)
            sys.path.insert(0, str(_SCRIPTS))
            import reconcile  # noqa: PLC0415
            text = index.read_text(encoding="utf-8")
            index.write_text(text.replace("| third |", "| stale |"), encoding="utf-8")
            res = reconcile.project_epic_view(root, dry_run=True)
        self.assertTrue(res["rewrote"])
        self.assertEqual(1, len(res["rows"]), res)

    def test_a_view_in_a_house_layout_is_left_as_written(self) -> None:
        """US0972 round 1. MUTANT: the prose guard removed - a section carrying the project's own
        line is rewritten."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            _story(root, "US0001", "src/a.py")
            index = root / "sdlc-studio" / "stories" / "_index.md"
            text = index.read_text(encoding="utf-8").replace(
                "## Stories by Epic\n", "## Stories by Epic\n\nMaintained by hand each sprint.\n")
            index.write_text(text, encoding="utf-8")
            r = _cli(root, "reconcile.py", "apply")
            self.assertEqual(0, r.returncode, r.stderr)
            after = index.read_text(encoding="utf-8")
        def section(s: str) -> str:
            return s.split("## Stories by Epic")[1].split("## All Stories")[0]
        self.assertEqual(section(text), section(after))

    def test_staleness_compares_instants_not_strings(self) -> None:
        """AC4. MUTANT: HEAD's string compare - `11:00+01:00` (10:00Z) reads later than
        `10:30+00:00` and the TSD is called stale; a code commit truly later still is (the
        positive control)."""
        env = gitutil.git_env()

        def commit(root: Path, rel: str, when: str) -> None:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(when, encoding="utf-8")
            subprocess.run(["git", "add", rel], cwd=root, env=env, check=True)
            subprocess.run(["git", "commit", "-q", "-m", rel], cwd=root, check=True,
                           env={**env, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when})

        sprint = _sprint()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], env=env, check=True)
            commit(root, "sdlc-studio/tsd.md", "2026-03-02T10:30:00+00:00")
            commit(root, "src/app.py", "2026-03-02T11:00:00+01:00")
            current = sprint.tsd_staleness(root)
            commit(root, "src/app.py", "2026-03-02T12:00:00+01:00")
            later = sprint.tsd_staleness(root)
        self.assertTrue(current["known"], current)
        self.assertFalse(current["stale"], current)
        self.assertTrue(later["stale"], later)


if __name__ == "__main__":
    unittest.main()
