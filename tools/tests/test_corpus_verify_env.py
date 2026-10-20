"""BG1054: the scheduled corpus-verify job installs what the criteria it runs need, and one Done
criterion stops reading the live backlog.

The job read four criteria red that pass on a developer machine or passed at the cut: US0892 AC1
(its test skips without pytest-xdist, and the lane reads an all-skipped verifier as red), US0957
AC3 (its verifier runs `pdftotext`), US0985 AC2 (its verifier ran `known_issues.py bar` against
the live backlog, which every High defect filed after the cut turns red), and US0940 AC1 (276 s
on a developer machine, under a 300 s per-verifier ceiling).

The criteria are the ones this bug names. What each one needs is read from its own Verify line
and the file that line names, not typed here (LL0043), and what the job installs is read from
the workflow, in the order its steps run.
"""
# test-census-subject: tools/verify-corpus.sh
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
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
        steps = _job_steps()
        verify_at = next(i for i, s in enumerate(steps) if "verify-corpus.sh" in str(s.get("run", "")))
        before = set().union(*(_installed(s) for s in steps[:verify_at]))
        self.assertIn("pytest", before, "the job's install line was not read")
        self.assertIn(plugin[0], before, "corpus-verify does not install the plugin US0892 AC1 needs "
                      "before the verification step")

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
            # The criterion still pins `bar`: with bar made to refuse, the verifier must refuse too,
            # so a verifier that runs bar and ignores its verdict is caught.
            shim = Path(d) / "shim"
            shim.mkdir()
            (shim / "python3").write_text(
                f'#!/bin/sh\ncase "$*" in *known_issues.py\\ bar*) exit 1 ;; esac\nexec {sys.executable} "$@"\n',
                encoding="utf-8")
            (shim / "python3").chmod(0o755)
            env = {**_env(), "PATH": f"{shim}{os.pathsep}{os.environ.get('PATH', '')}"}
            r = subprocess.run(["bash", "-c", verifier.removeprefix("shell ")], cwd=clone, env=env,
                               capture_output=True, text=True, timeout=300)
            self.assertNotEqual(r.returncode, 0, "US0985 AC2 passes though known_issues.py bar refused")


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
        story, ac = criterion.split("::")
        self.assertIn(f"stories/{story}-", timed[0]["run"], "the timing step does not read the criterion's own Verify line")
        out, argv = self._run_timing_step(timed[0]["run"], python_exit=0)
        want = _verify(story, ac).removeprefix("pytest ").strip()
        self.assertEqual(argv[-1:], [want], f"the timing step times a selector other than {criterion}'s")
        self.assertRegex(out, rf"verifier-time: {re.escape(criterion)} \d+ s, exit 0",
                         "the timing step does not print the time it measured")
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

    def _run_timing_step(self, script: str, *, python_exit: int, story: str | None = None) -> tuple[str, list[str]]:
        """Run the timing step's own script as the runner does (`bash -e`), in a tree holding
        `story` (this repository's US0940 by default) and a `python` that records its arguments
        and exits `python_exit`. Returns the step's output and the arguments the verifier got."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            source = next(STORIES.glob("US0940-*.md"))
            (stories / source.name).write_text(story if story is not None else _read(source), encoding="utf-8")
            bin_dir = root / "bin"
            bin_dir.mkdir()
            record = root / "argv"
            (bin_dir / "python").write_text(
                f'#!/bin/sh\nfor a in "$@"; do printf "%s\\n" "$a"; done > {record}\nexit {python_exit}\n',
                encoding="utf-8")
            (bin_dir / "python").chmod(0o755)
            env = {**_env(), "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
            r = subprocess.run(["bash", "-e", "-c", script], cwd=root, env=env,
                               capture_output=True, text=True, timeout=120)
            self.assertEqual(r.returncode, 0, "the timing step stops the job:\n" + r.stdout + r.stderr)
            argv = record.read_text(encoding="utf-8").splitlines() if record.exists() else []
            return r.stdout, argv

    def test_the_timing_step_never_stops_the_job(self) -> None:
        """BG1054's round-1 regression: under the runner's `bash -e`, a failing verifier ended the
        timing step before it printed anything, and the verification step after it was skipped.
        Mutants: the verifier's exit not caught; an AC1 with no pytest line handed to pytest as an
        empty selector; the step without its own ceiling, or without continue-on-error."""
        step = next(s for s in _job_steps() if "verifier-time:" in str(s.get("run", "")))
        self.assertTrue(step.get("continue-on-error"), "a failed or timed-out timing step would skip the verification step")
        self.assertIsInstance(step.get("timeout-minutes"), int, "the timing step has no ceiling of its own")
        out, _ = self._run_timing_step(step["run"], python_exit=1)
        self.assertRegex(out, r"verifier-time: US0940::AC1 \d+ s, exit 1", "a failing verifier is not reported")
        bare = re.sub(r"(\*\*AC1:\*\*.*?\n)\s+- \*\*Verify:\*\* pytest [^\n]*\n", r"\1  - **Verify:** manual: read it\n",
                      _read(next(STORIES.glob("US0940-*.md"))), count=1, flags=re.S)
        out, argv = self._run_timing_step(step["run"], python_exit=0, story=bare)
        self.assertIn("not timed", out, "an AC1 with no pytest Verify line is not reported as untimed")
        self.assertEqual(argv, [], "an AC1 with no pytest Verify line still ran pytest")

if __name__ == "__main__":
    unittest.main()
