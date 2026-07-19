"""Test-suite hygiene guards (CR0204/US0114).

A mid-file `if __name__` guard silently drops every class below it on a direct
`python3 test_x.py` run (22 tests once vanished while reporting OK) and invites
append-truncation. The guard must be the LAST top-level statement of every test file.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent


def _guard_index(tree: ast.Module) -> int | None:
    """Index of the `if __name__ == "__main__"` statement in the module body, or None."""
    for i, node in enumerate(tree.body):
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"):
            return i
    return None


class GuardAtEofTests(unittest.TestCase):
    def test_every_main_guard_is_the_last_statement(self) -> None:
        offenders = []
        for p in sorted(TESTS_DIR.glob("test_*.py")):
            tree = ast.parse(p.read_text(encoding="utf-8"))
            gi = _guard_index(tree)
            if gi is not None and gi != len(tree.body) - 1:
                after = [type(n).__name__ for n in tree.body[gi + 1:]]
                offenders.append(f"{p.name}: guard at statement {gi}, followed by {after}")
        self.assertEqual(offenders, [],
                         "mid-file __main__ guards silently drop the classes below them "
                         "on direct runs - move the guard to true end-of-file:\n"
                         + "\n".join(offenders))


class DirectRunParityTests(unittest.TestCase):
    def test_direct_run_count_equals_discover_count(self) -> None:
        # The historical liar: a direct run of test_validate.py once executed 49 of 71
        # tests and reported OK. Post-normalisation the two counts must agree.
        target = TESTS_DIR / "test_validate.py"

        def ran(cmd: list[str]) -> int:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                               cwd=str(TESTS_DIR.parent.parent.parent.parent.parent))
            m = re.search(r"Ran (\d+) tests?", r.stderr + r.stdout)
            self.assertIsNotNone(m, (r.stderr + r.stdout)[-500:])
            return int(m.group(1))

        direct = ran([sys.executable, str(target)])
        discover = ran([sys.executable, "-m", "unittest", "discover",
                        "-s", ".claude/skills/sdlc-studio/scripts/tests",
                        "-p", "test_validate.py"])
        self.assertEqual(direct, discover)


SCRIPTS_DIR = TESTS_DIR.parent

#: Helper modules that live beside the tests rather than under `scripts/`. Importing one by
#: its bare name only resolves when the tests directory is on `sys.path`, which
#: `unittest discover -s tests` arranges and `unittest tests.test_x` does not.
SIBLING_HELPERS = ("loader", "gitutil")


def _modules_importing_a_sibling() -> list[str]:
    """Test modules with a top-level `import loader` / `import gitutil`.

    AST-based, so a helper named inside a string or a comment does not count. These are
    exactly the modules that need the tests directory on `sys.path` before the import.
    """
    out = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) and any(
                    a.name in SIBLING_HELPERS for a in node.names):
                out.append(path.stem)
                break
    return out


class SiblingImportRunnabilityTests(unittest.TestCase):
    """A test module must import under BOTH run forms, not just under discover.

    `unittest discover -s tests` puts the tests directory on `sys.path`, so a bare
    `import loader` resolves; `unittest tests.test_x` does not, so the same line raises
    ModuleNotFoundError naming the helper. The failure says nothing about the module the
    operator was actually running, and it cost a diagnosis cycle during a sprint close when
    the mutation gate was handed the module form, refused on a red baseline, and pointed at
    a stranded mutant from a killed run - a plausible and completely wrong lead (BG0206).
    """

    def test_the_census_finds_the_modules_it_is_meant_to_guard(self) -> None:
        # A census that silently returned nothing would make the sweep below vacuous.
        found = _modules_importing_a_sibling()
        self.assertGreater(len(found), 5, "the sibling-import census has stopped detecting")
        self.assertIn("test_reconcile", found)

    def test_every_sibling_importing_module_imports_by_module_name(self) -> None:
        # ONE PROCESS PER MODULE, deliberately. Importing them all in a single process
        # passes vacuously: the first module to run its own `sys.path.insert` puts the
        # tests directory on the path and registers `loader` in sys.modules, so every
        # module imported after it succeeds regardless of its own setup. That is the
        # incidental-pass trap this sweep exists to catch, so each import gets a fresh
        # interpreter. cwd is scripts/ - the run form that omits tests/ from sys.path.
        bad = []
        for mod in _modules_importing_a_sibling():
            r = subprocess.run(
                [sys.executable, "-B", "-c", f"import importlib; importlib.import_module('tests.{mod}')"],
                capture_output=True, text=True, timeout=120, cwd=str(SCRIPTS_DIR))
            if r.returncode != 0:
                last = (r.stderr.strip().splitlines() or ["(no output)"])[-1]
                bad.append(f"{mod}: {last}")
        self.assertEqual(
            bad, [],
            "these test modules import a sibling helper but cannot be run as "
            f"`python3 -m unittest tests.<name>`:\n" + "\n".join(bad) + "\n"
            "Fix: insert the tests directory on sys.path immediately before the import, as "
            "the other modules do.")

# A bare read: `<expr>.read_text(...)`. `read_text_safe(` never matches - the character after
# `read_text` is `_`, not `(`.
BARE_READ_RE = re.compile(r"\.read_text\s*\(")

# The one visible exemption channel. A bare read stays bare only when the line carries
# `# bare-read-ok: <reason>`, so every exemption is readable at the read site itself rather
# than hidden in a list somewhere else.
EXEMPT_RE = re.compile(r"#\s*bare-read-ok:\s*(\S.*)$")

# Modules known to stream the artefact tree today. The census is mechanical, but an
# enumeration that silently returned nothing would pass every assertion below while checking
# nothing. This floor is the anti-vacuity guard: the census must CONTAIN it, never be reduced
# to it.
KNOWN_SCANNERS = {"deploy.py", "flow.py", "status.py", "verify_ac.py"}

# The marker for "this module walks the whole artefact tree". `artifact_files` is a thin
# wrapper over `iter_artifact_files`, so a direct caller of the enumerator is the module that
# streams the tree, and therefore the module one corrupt file can abort mid-pass.
SCANNER_MARKER = "iter_artifact_files"


def _scanner_modules() -> dict[str, str]:
    """{filename: source} for every top-level script that walks the artefact tree.

    Scoped to `scripts/*.py` (non-recursive): `lib/sdlc_md.py` defines both the enumerator and
    `read_text_safe` itself, so its own bare read is the primitive, not a scanner site.
    """
    out = {}
    for path in sorted(SCRIPTS_DIR.glob("*.py")):
        src = path.read_text(encoding="utf-8")
        if SCANNER_MARKER in src:
            out[path.name] = src
    return out


class BareArtefactReadSweepTests(unittest.TestCase):
    """Every artefact-body read in a tree-walking scanner goes through `read_text_safe`.

    One corrupt or non-UTF-8 artefact from a crashed session must not abort a pass over the
    whole workspace. Index reads are the deliberate exception and stay loud - see
    `LoudIndexReadTests` in test_reconcile.py for the other direction.
    """

    def test_the_census_actually_enumerates_scanners(self) -> None:
        """A census that found nothing would pass the sweep below vacuously."""
        found = set(_scanner_modules())
        self.assertTrue(found, "the scanner census found no modules - the enumeration is broken")
        missing = KNOWN_SCANNERS - found
        self.assertFalse(
            missing,
            f"the census no longer sees known scanners {sorted(missing)} - "
            "the enumeration is broken, not the tree",
        )

    def test_no_bare_artefact_body_reads_in_scanners(self) -> None:
        offenders = []
        for name, src in _scanner_modules().items():
            for lineno, line in enumerate(src.splitlines(), 1):
                if BARE_READ_RE.search(line) and not EXEMPT_RE.search(line):
                    offenders.append(f"{name}:{lineno}: {line.strip()}")
        self.assertEqual(
            offenders,
            [],
            "bare artefact-body read(s) in a tree-walking scanner - route through "
            "`sdlc_md.read_text_safe`, or mark the line `# bare-read-ok: <reason>` when the "
            "read must stay loud (an index, or an already-guarded config read):\n"
            + "\n".join(offenders),
        )

    def test_every_exemption_states_a_reason(self) -> None:
        """An exemption with no reason is an invisible exemption."""
        bad = []
        for name, src in _scanner_modules().items():
            for lineno, line in enumerate(src.splitlines(), 1):
                m = EXEMPT_RE.search(line)
                if m and len(m.group(1).strip()) < 10:
                    bad.append(f"{name}:{lineno}: {line.strip()}")
        self.assertEqual(bad, [], "`# bare-read-ok:` with no usable reason:\n" + "\n".join(bad))


if __name__ == "__main__":
    unittest.main()
