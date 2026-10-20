"""BG1054: the scheduled corpus-verify job installs what the criteria it runs need, and one Done
criterion stops reading the live backlog.

The job read four criteria red that pass on a developer machine or passed at the cut: US0892 AC1
(its test skips without pytest-xdist, and the lane reads an all-skipped verifier as red), US0957
AC3 (its verifier runs `pdftotext`), US0985 AC2 (its verifier ran `known_issues.py bar` against
the live backlog, which every High defect filed after the cut turns red), and US0940 AC1 (276 s
on a developer machine, under a 300 s per-verifier ceiling).

What each criterion needs is read from its own Verify line and the file that line names, never
typed here (LL0043), and what the job installs is read from the workflow.
"""
# test-census-subject: tools/verify-corpus.sh
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
STORIES = REPO / "sdlc-studio" / "stories"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _verify(story: str, ac: str) -> str:
    """The Verify expression of `story`'s criterion `ac`, as written."""
    text = _read(next(STORIES.glob(f"{story}-*.md")))
    m = re.search(rf"\*\*{ac}:\*\*.*?\n\s+- \*\*Verify:\*\* (.+)", text)
    assert m, f"{story} {ac} has no Verify line"
    return m.group(1).strip()


def _job_steps() -> list[dict]:
    return yaml.safe_load(_read(WORKFLOW))["jobs"]["corpus-verify"]["steps"]


def _installed(step: dict) -> set[str]:
    """The distribution names a step's `pip install` lines name."""
    names: set[str] = set()
    for line in str(step.get("run", "")).splitlines():
        m = re.search(r"\bpip3?\s+install\b(.*)$", line.split("#", 1)[0])
        if m:
            for word in m.group(1).split():
                if not word.startswith("-"):
                    names.add(re.split(r"[<>=!~;\[ ]", word.strip("'\""), maxsplit=1)[0].lower())
    return names


def _env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


class CorpusVerifyEnvTests(unittest.TestCase):

    def test_the_job_installs_the_plugin_us0892_needs(self) -> None:
        """AC1. Mutant: the job's install line without pytest-xdist."""
        verifier = _verify("US0892", "AC1")
        self.assertTrue(verifier.startswith("pytest "), verifier)
        module = REPO / verifier.split()[1].split("::")[0]
        self.assertIn("xdist", _read(module), "US0892 AC1's test no longer depends on xdist")
        declared = {re.split(r"[<>=!~;\[ ]", ln.strip(), maxsplit=1)[0].lower()
                    for ln in _read(REPO / "requirements-dev.txt").splitlines()
                    if ln.strip() and not ln.lstrip().startswith("#")}
        plugin = [d for d in declared if "xdist" in d]
        self.assertEqual(plugin, ["pytest-xdist"], "the xdist plugin is not on the declared list")
        installed = set().union(*(_installed(s) for s in _job_steps()))
        self.assertIn("pytest", installed, "the job's install line was not read")
        self.assertIn(plugin[0], installed, "corpus-verify does not install the plugin US0892 AC1 needs")

    def test_the_job_installs_the_pdf_tool_us0957_runs(self) -> None:
        """AC2. Mutant: the job installing no pdftotext."""
        verifier = _verify("US0957", "AC3")
        self.assertRegex(verifier, r"\bpdftotext\b", "US0957 AC3 no longer runs pdftotext")
        steps = _job_steps()
        installs = [i for i, s in enumerate(steps)
                    if re.search(r"apt-get install\b[^\n]*\bpoppler-utils\b", str(s.get("run", "")))]
        self.assertTrue(installs, "corpus-verify does not install poppler-utils, which provides pdftotext")
        verify_at = [i for i, s in enumerate(steps) if "verify-corpus.sh" in str(s.get("run", ""))]
        self.assertTrue(verify_at and installs[0] < verify_at[0], "pdftotext is installed after the verification step")

    def test_us0985_ac2_does_not_redden_on_a_later_defect(self) -> None:
        """AC3. A clone of this repository with one more open High defect than the cut disclosed
        still passes US0985 AC2, run as its Verify line runs it. Mutant: the verifier reading
        `known_issues.py bar` against the working tree."""
        verifier = _verify("US0985", "AC2")
        self.assertTrue(verifier.startswith("shell "), verifier)
        self.assertIn("known_issues.py bar", verifier, "US0985 AC2 no longer pins known_issues.py bar")
        tags = subprocess.run(["git", "tag", "-l", "v6.1.0"], cwd=REPO, env=_env(),
                              capture_output=True, text=True).stdout.split()
        if not tags:
            self.skipTest("v6.1.0 is not in this clone (a shallow checkout carries no tags)")
        with tempfile.TemporaryDirectory() as d:
            clone = Path(d) / "clone"
            subprocess.run(["git", "clone", "-q", str(REPO), str(clone)], env=_env(), check=True,
                           capture_output=True, timeout=300)
            bugs = clone / "sdlc-studio" / "bugs"
            source = next(p for p in sorted(bugs.glob("BG*.md")) if not p.name.startswith("BG9999"))
            text = re.sub(r"^# BG\d+:", "# BG9999:", _read(source), count=1, flags=re.M)
            text = re.sub(r"(> \*\*Status:\*\*) .*", r"\1 Open", text, count=1)
            text = re.sub(r"(> \*\*Severity:\*\*) .*", r"\1 High", text, count=1)
            (bugs / "BG9999-a-high-defect-filed-after-the-cut.md").write_text(text, encoding="utf-8")
            live = subprocess.run(["python3", "tools/known_issues.py", "bar"], cwd=clone, env=_env(),
                                  capture_output=True, text=True, timeout=120)
            self.assertNotEqual(live.returncode, 0, "the fixture's later High defect does not fail the live bar")
            r = subprocess.run(["bash", "-c", verifier.removeprefix("shell ")], cwd=clone, env=_env(),
                               capture_output=True, text=True, timeout=300)
            self.assertEqual(r.returncode, 0, "US0985 AC2 reddens on a defect filed after the cut:\n"
                             + r.stdout + r.stderr)


    def test_the_ceiling_clears_the_slowest_measured_verifier(self) -> None:
        """AC4. The verification step's per-verifier ceiling clears the time the job measured for
        the criterion its timing step times, by the headroom recorded beside it, from a named run.
        Mutants: a ceiling below the measured time; a measurement with no run id; a headroom that
        does not match the ceiling; a timing step that times nothing."""
        steps = _job_steps()
        timed = [s for s in steps if "verifier-time:" in str(s.get("run", ""))]
        self.assertEqual(len(timed), 1, "the job has no step timing the slowest criterion")
        criterion = re.search(r"verifier-time: (\S+)", timed[0]["run"]).group(1)
        self.assertEqual(criterion, "US0940::AC1", "the timed criterion was not read")
        story = criterion.split("::")[0]
        self.assertIn(f"stories/{story}-", timed[0]["run"], "the timing step does not read the criterion's own Verify line")
        verify = [s for s in steps if "verify-corpus.sh" in str(s.get("run", ""))]
        self.assertEqual(len(verify), 1)
        ceiling = int(verify[0]["env"]["SDLC_VERIFY_TIMEOUT"])
        text = _read(WORKFLOW)
        block = text[text.index("- name: Corpus verification"):text.index("run: bash tools/verify-corpus.sh full")]
        m = re.search(r"measured: (\S+) (\d+) s in run (\d{6,}), headroom (\d+) s", block)
        self.assertTrue(m, "no measured time, run id and headroom are recorded beside the ceiling")
        self.assertEqual(m.group(1), criterion, "the recorded measurement is not of the timed criterion")
        measured, headroom = int(m.group(2)), int(m.group(4))
        self.assertGreater(ceiling, measured, f"the {ceiling} s ceiling does not clear the measured {measured} s")
        self.assertEqual(ceiling - measured, headroom, "the recorded headroom is not the ceiling less the measured time")

if __name__ == "__main__":
    unittest.main()
