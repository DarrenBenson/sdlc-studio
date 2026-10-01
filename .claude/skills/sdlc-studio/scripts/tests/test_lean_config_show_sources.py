"""US0759: `config.py show --sources` marks each leaf key in force as `default` or `project`.

`load_config` merges the skill defaults with the project's `.config.yaml`; `--sources` prints one
line per merged leaf naming where its value came from. Each test drives the shipped CLI as a
subprocess against a throwaway project; nothing reads this repository's own `.config.yaml`.

`review.max_rounds`, the example AC1 names, has no entry in `config-defaults.yaml` (critic.py
owns its default, BG0831), so it is not a key in force there; the default-key case is pinned on
`review.blocking_priority`, which the defaults file does set.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
LINE = re.compile(r"^(default|project) +(\S+) = (.*)$")


def _show(root: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "config.py"), "show", *flags, "--root", str(root)],
        capture_output=True, text=True, check=False, timeout=120)


def _sources(stdout: str) -> dict[str, tuple[str, str]]:
    """{dotted key: (source, value)} from the --sources lines."""
    out = {}
    for ln in stdout.splitlines():
        m = LINE.match(ln)
        if m:
            out[m.group(2)] = (m.group(1), m.group(3))
    return out


class ConfigShowSourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "sdlc-studio").mkdir()
        (self.root / "sdlc-studio" / ".config.yaml").write_text("coverage:\n  unit: 75\n",
                                                                encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_a_project_key_and_a_default_key_are_marked(self) -> None:
        """AC1. MUTANT: HEAD, where `show` declares no `--sources` and argparse exits 2."""
        proc = _show(self.root, "--sources")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        src = _sources(proc.stdout)
        self.assertEqual(("project", "75"), src.get("coverage.unit"), proc.stdout)
        self.assertEqual(("default", '"high"'), src.get("review.blocking_priority"), proc.stdout)
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
        self.assertEqual(len(lines), len(src), "a line that is not `<source> <key> = <value>`")

    def test_a_sibling_of_an_overridden_leaf_stays_default(self) -> None:
        """AC2. MUTANT: mark every leaf under a section the project file names as `project`."""
        src = _sources(_show(self.root, "--sources").stdout)
        self.assertEqual("project", src["coverage.unit"][0])
        self.assertEqual("default", src["coverage.integration"][0])
        self.assertEqual("default", src["coverage.e2e"][0])
        self.assertEqual(["coverage.unit"], [k for k, (s, _) in src.items() if s == "project"])

    def test_plain_show_is_unchanged(self) -> None:
        """AC3. MUTANT: carry sources into the plain `show` output. Pinned to HEAD's own
        rendering: `json.dumps(load_config(root), indent=2)` plus its newline."""
        sys.path.insert(0, str(SCRIPTS))
        try:
            import config  # noqa: PLC0415 - the module under test, for HEAD's rendering
        finally:
            sys.path.remove(str(SCRIPTS))
        expected = json.dumps(config.load_config(self.root), indent=2,
                              default=config._json_default) + "\n"
        proc = _show(self.root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual(expected, proc.stdout)
        self.assertEqual(75, json.loads(proc.stdout)["coverage"]["unit"])


if __name__ == "__main__":
    unittest.main()
