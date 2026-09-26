"""BG0789: a pre-release tag is published as a pre-release, never as the latest release.

`version_check.latest_release` reads the forge's `/releases/latest`, so whichever Release the
workflow leaves marked latest is what every installed copy is prompted to upgrade to. A tag such
as `v6.0.0-rc.1` published as a plain Release would prompt every v5 install onto a candidate.

WHY THE TEST RUNS THE STEP. Grepping release.yml for `--prerelease` stays green while the flag
sits on the wrong branch, behind a condition that never matches, or on both kinds of tag. So the
publish step's own script is read from the workflow and executed in a throwaway directory with a
stub `gh` earlier on PATH that records its arguments; the assertions judge what `gh` was handed.
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "release.yml"
STEP = "Publish the Release with its assets"
TAG_EXPR = "${{ steps.tag.outputs.tag }}"

#: A stub `gh`: records each call's argv (unit separator between arguments, record separator
#: between calls) and answers `release view` with "no such Release", so the step takes a create
#: branch.
GH_STUB = r"""#!/usr/bin/env bash
{ printf '%s\x1f' "$@"; printf '\x1e'; } >> "$GH_LOG"
if [[ "$1 $2" == "release view" ]]; then exit 1; fi
exit 0
"""


def _publish_script() -> str:
    steps = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["publish"]["steps"]
    matches = [s["run"] for s in steps if s.get("name") == STEP]
    if len(matches) != 1:
        raise AssertionError(f"expected one step named {STEP!r}, found {len(matches)}")
    return matches[0]


def _run_publish(tag: str, with_notes: bool) -> list[list[str]]:
    """Run the publish step for `tag` and return every argv the stub `gh` received."""
    script = _publish_script()
    if script.count(TAG_EXPR) != 1:
        raise AssertionError(f"the publish step no longer reads the tag from {TAG_EXPR}")
    script = script.replace(TAG_EXPR, tag)
    with tempfile.TemporaryDirectory() as tmp:
        work, bindir = Path(tmp) / "work", Path(tmp) / "bin"
        (work / "dist").mkdir(parents=True)
        (work / "dist" / f"sdlc-studio-{tag}.tar.gz").write_bytes(b"asset")
        if with_notes:
            (work / "docs").mkdir()
            (work / "docs" / f"release-notes-{tag}.md").write_text("notes\n", encoding="utf-8")
        bindir.mkdir()
        gh = bindir / "gh"
        gh.write_text(GH_STUB, encoding="utf-8")
        gh.chmod(0o755)
        log = Path(tmp) / "gh.log"
        env = {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}",
               "GH_LOG": str(log), "GH_TOKEN": "stub"}
        proc = subprocess.run([shutil.which("bash") or "bash", "-c", script], cwd=work,
                              env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            raise AssertionError(f"publish step failed for {tag}: {proc.stderr}")
        raw = log.read_text(encoding="utf-8") if log.exists() else ""
    return [rec.split("\x1f")[:-1] for rec in raw.split("\x1e") if rec]


def _creates(calls: list[list[str]]) -> list[list[str]]:
    return [argv for argv in calls if argv[:2] == ["release", "create"]]


class ReleasePrereleaseTests(unittest.TestCase):

    def _both_branches(self, tag: str) -> dict[str, list[str]]:
        out = {}
        for with_notes, branch in ((True, "notes-file"), (False, "generate-notes")):
            creates = _creates(_run_publish(tag, with_notes))
            self.assertEqual(len(creates), 1, f"{tag} {branch}: expected one `gh release create`")
            flag = "--notes-file" if with_notes else "--generate-notes"
            self.assertIn(flag, creates[0], f"{tag}: the {branch} branch did not run")
            out[branch] = creates[0]
        return out

    def test_a_suffixed_tag_is_published_as_a_prerelease(self) -> None:
        """AC1. Mutant: drop the pre-release flags from either `gh release create`. Must redden."""
        for tag in ("v6.0.0-rc.1", "v6.1.0-beta.2", "v7.0.0-alpha.1"):
            for branch, argv in self._both_branches(tag).items():
                with self.subTest(tag=tag, branch=branch):
                    self.assertIn("--prerelease", argv)
                    self.assertIn("--latest=false", argv)

    def test_a_final_tag_is_published_as_the_latest(self) -> None:
        """AC2. Mutant: mark every release a pre-release. Must redden."""
        for branch, argv in self._both_branches("v6.0.0").items():
            with self.subTest(branch=branch):
                self.assertNotIn("--prerelease", argv)
                self.assertFalse([a for a in argv if a.startswith("--latest")], argv)


if __name__ == "__main__":
    unittest.main()
