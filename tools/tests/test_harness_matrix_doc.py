"""US1316: docs/harnesses.md's capability matrix is read against the tree it describes.

The page tells an enterprise reviewer which harnesses run SDLC Studio and what each one gives, so
a cell the tree cannot back is the claim that misleads them. The tests read the page's own two
tables: the matrix (one row per harness, one column per capability) and the fallbacks (one row
per harness-specific feature). The install paths are read from the installers' own resolvers,
`target_dir` in `install.sh` and the target map in `install.ps1`, never from a copy here.

Every test also runs its check on a broken copy of the page, so a check that cannot fail is
caught by the test that relies on it.
"""
# test-census-subject: docs/harnesses.md
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAGE = REPO / "docs" / "harnesses.md"
INSTALL_SH = REPO / "install.sh"
INSTALL_PS1 = REPO / "install.ps1"

#: The rows, in the order the page gives them: alphabetical, without regard to case.
HARNESSES = ("Claude Code", "Codex", "Cursor", "Gemini CLI", "GitHub Copilot", "opencode")
#: The columns after the first, which names the harness.
CAPABILITIES = ("Install path", "Invocation", "Skill discovery", "Parallel or sub-agents",
                "Token and cost reporting", "Hooks and gates", "Live reload")
#: The installer target each harness installs through. Cursor has no target of its own: it reads
#: the generic `.agents/skills` folder the `agents` target writes.
TARGET = {"Claude Code": "claude", "Codex": "codex", "Cursor": "agents", "Gemini CLI": "gemini",
          "GitHub Copilot": "copilot", "opencode": "opencode"}
#: The harness-specific features the fallbacks table must cover, at least, each found by a
#: pattern over the table's Feature cells.
FEATURES = {"epic implement --agentic": r"epic implement --agentic",
            "the git hooks": r"(?i)\bgit hooks\b",
            "live reload": r"(?i)\blive reload\b",
            "the token meter": r"(?i)\btoken meter\b"}
#: What the `--agentic` row's fallback must say a harness without it does instead.
AGENTIC_FALLBACK = (r"`epic implement`", r"(?i)\bone at a time\b", r"(?i)\bdependency order\b",
                    r"(?i)\bsame gates\b")
#: A "Without it" cell that states no fallback.
NO_FALLBACK = {"", "-", "none", "n/a", "untested", "tbd"}

MATRIX_HEADING = "## Capability matrix"
FALLBACK_HEADING = "## Fallbacks"
FALLBACK_HEADER = ("Feature", "Works in", "Without it")

_INLINE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_REFERENCE = re.compile(r"\[([^\]]+)\]\[([^\]]*)\]")
_DEFINITION = re.compile(r"^\[([^\]]+)\]:\s*(\S+)\s*$", re.M)
_CODE = re.compile(r"`([^`]+)`")


def table(text: str, heading: str) -> tuple[list[str], list[list[str]]]:
    """The header and body rows of the first table under `heading`, or ([], []) with none."""
    lines = text.splitlines()
    try:
        at = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return [], []
    rows: list[list[str]] = []
    for line in lines[at + 1:]:
        if line.startswith("## "):
            break
        if line.lstrip().startswith("|"):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif rows:
            break
    if len(rows) < 2:
        return [], []
    return rows[0], rows[2:]


def matrix(text: str) -> dict[str, dict[str, str]]:
    """Each harness row of the matrix as {capability: cell}."""
    header, rows = table(text, MATRIX_HEADING)
    return {row[0]: dict(zip(header[1:], row[1:])) for row in rows if row}


def matrix_problems(text: str) -> list[str]:
    """What keeps the matrix from being one row per harness, in order, under every capability."""
    header, rows = table(text, MATRIX_HEADING)
    if not header:
        return [f"no table under {MATRIX_HEADING!r}"]
    problems = []
    if tuple(header[1:]) != CAPABILITIES:
        problems.append(f"columns {header[1:]} are not {list(CAPABILITIES)}")
    names = [row[0] for row in rows]
    if names != list(HARNESSES):
        problems.append(f"rows {names} are not {list(HARNESSES)}, in that order")
    for row in rows:
        if len(row) != len(header):
            problems.append(f"row {row[0]!r} has {len(row)} cells under {len(header)} columns")
    return problems


def _home(path: str) -> str:
    return path.replace("$HOME", "~", 1)


def installer_targets(script: str) -> dict[str, dict[str, str]]:
    """{target: {scope: folder}} from the case arms of `install.sh`'s `target_dir`."""
    body = re.search(r"^target_dir\(\) \{\n(.*?)^\}", script, re.M | re.S)
    if body is None:
        raise AssertionError("install.sh has no target_dir() resolver")
    arms: dict[str, dict[str, str]] = {}
    for target, scope, folder in re.findall(r'^\s*(\w+):(global|local)\)\s+echo "([^"]*)"',
                                            body.group(1), re.M):
        arms.setdefault(target, {})[scope] = _home(folder)
    return arms


def ps1_targets(script: str) -> dict[str, dict[str, str]]:
    """{target: {scope: folder}} from `install.ps1`'s target map, with `/` for `\\`."""
    arms = {}
    for target, home, local in re.findall(
            r"^\s*(\w+)\s*=\s*@\{\s*global\s*=\s*\(Join-Path \$HOME '([^']+)'\);\s*"
            r"local\s*=\s*'([^']+)'\s*\}", script, re.M):
        arms[target] = {"global": "~/" + home.replace("\\", "/"), "local": local.replace("\\", "/")}
    return arms


def install_problems(text: str, targets: dict[str, dict[str, str]]) -> list[str]:
    """Each harness whose install-path cell names another target, or folders other than the
    global and local ones the installer writes for its target."""
    rows = matrix(text)
    problems = []
    for harness, target in TARGET.items():
        cell = rows.get(harness, {}).get("Install path", "")
        if target not in targets:
            problems.append(f"the installer has no {target!r} target for {harness}")
            continue
        code = _CODE.findall(cell)
        if f"--target {target}" not in code:
            problems.append(f"{harness}: {cell!r} does not name `--target {target}`")
        shown = {item for item in code if not item.startswith("--")}
        wanted = {targets[target]["global"], targets[target]["local"]}
        if shown != wanted:
            problems.append(f"{harness}: the page shows {sorted(shown)}, the installer "
                            f"writes {sorted(wanted)}")
    return problems


def sources(cell: str, definitions: dict[str, str]) -> list[tuple[str, str | None]]:
    """Each (label, target) a cell links, inline or by reference; target None when undefined."""
    found = [(label, target) for label, target in _INLINE.findall(cell)]
    for label, ref in _REFERENCE.findall(cell):
        found.append((label, definitions.get((ref or label).casefold())))
    return found


def source_problems(text: str) -> list[str]:
    """Each capability cell that neither says untested nor names a file in this repository that
    exists, and each link a cell holds that does not name such a file."""
    definitions = {ref.casefold(): target for ref, target in _DEFINITION.findall(text)}
    problems = []
    for harness, cells in matrix(text).items():
        for capability, cell in cells.items():
            where = f"{harness} / {capability}"
            linked = sources(cell, definitions)
            if not linked and not re.search(r"(?i)\buntested\b", cell):
                problems.append(f"{where}: {cell!r} names no source and does not say untested")
            for label, target in linked:
                if target is None:
                    problems.append(f"{where}: [{label}] has no link definition")
                    continue
                if re.match(r"(?i)[a-z][a-z0-9+.-]*:", target):
                    problems.append(f"{where}: {target} is not a file in this repository")
                    continue
                path = (PAGE.parent / target.split("#", 1)[0]).resolve()
                if not path.is_file() or REPO not in path.parents:
                    problems.append(f"{where}: {target} is not a file in this repository")
                elif label.strip("`") != path.name:
                    problems.append(f"{where}: [{label}] links {path.name}, another file")
    return problems


def fallback_problems(text: str) -> list[str]:
    """Each harness-specific feature the fallbacks table misses, or names with no fallback."""
    header, rows = table(text, FALLBACK_HEADING)
    if tuple(header) != FALLBACK_HEADER:
        return [f"the table under {FALLBACK_HEADING!r} has columns {header}, "
                f"not {list(FALLBACK_HEADER)}"]
    problems = []
    for name, pattern in FEATURES.items():
        if not any(re.search(pattern, row[0]) for row in rows):
            problems.append(f"no fallback row for {name}")
    for row in rows:
        without = row[2] if len(row) > 2 else ""
        if without.strip().strip(".").casefold() in NO_FALLBACK:
            problems.append(f"{row[0]!r} states no fallback ({without!r})")
        if re.search(FEATURES["epic implement --agentic"], row[0]):
            for pattern in AGENTIC_FALLBACK:
                if not re.search(pattern, without):
                    problems.append(f"the --agentic fallback {without!r} does not say "
                                    f"{pattern!r}")
    return problems


def _replace_row(text: str, heading: str, first_cell: str, new: str | None) -> str:
    """A copy of `text` whose row starting `| first_cell |` under `heading` is `new`, or gone."""
    lines, out, under = text.splitlines(), [], False
    for line in lines:
        if line.startswith("## "):
            under = line.strip() == heading
        if under and line.startswith(f"| {first_cell} |"):
            if new is not None:
                out.append(new)
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def _drop_last_column(text: str, heading: str) -> str:
    """A copy of `text` whose table under `heading` has lost its last column in every line."""
    out, under = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            under = line.strip() == heading
        if under and line.startswith("|"):
            line = "|".join(line.rstrip().rstrip("|").split("|")[:-1]) + "|"
        out.append(line)
    return "\n".join(out) + "\n"


def _row_line(text: str, heading: str, first_cell: str) -> str:
    lines, under = text.splitlines(), False
    for line in lines:
        if line.startswith("## "):
            under = line.strip() == heading
        if under and line.startswith(f"| {first_cell} |"):
            return line
    raise AssertionError(f"no {first_cell!r} row under {heading!r}")


class HarnessMatrixDocTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")

    def test_the_matrix_has_six_harnesses_and_seven_capabilities(self):
        self.assertEqual(list(HARNESSES), sorted(HARNESSES, key=str.casefold),
                         "the expected rows are not alphabetical")
        self.assertEqual(matrix_problems(self.page), [])
        cursor = _row_line(self.page, MATRIX_HEADING, "Cursor")
        codex = _row_line(self.page, MATRIX_HEADING, "Codex")
        swapped = self.page.replace(codex, "\0").replace(cursor, codex).replace("\0", cursor)
        gemini = _row_line(self.page, MATRIX_HEADING, "Gemini CLI")
        short = "|".join(gemini.rstrip().rstrip("|").split("|")[:-1]) + "|"
        broken = {
            "a harness missing": _replace_row(self.page, MATRIX_HEADING, "Cursor", None),
            "rows out of order": swapped,
            "a column missing from the whole table": _drop_last_column(self.page, MATRIX_HEADING),
            "a cell missing from one row": self.page.replace(gemini, short),
        }
        for case, copy in broken.items():
            with self.subTest(case=case):
                self.assertNotEqual(matrix_problems(copy), [], case)

    def test_install_paths_match_the_installer(self):
        targets = installer_targets(INSTALL_SH.read_text(encoding="utf-8"))
        self.assertEqual(sorted(targets), sorted(set(TARGET.values())),
                         "the installer serves a target the page does not map to a harness")
        ps1 = INSTALL_PS1.read_text(encoding="utf-8")
        self.assertEqual(ps1_targets(ps1), targets,
                         "install.ps1 resolves other folders than install.sh")
        diverged = ps1.replace("local = '.github\\skills'", "local = '.copilot\\skills'", 1)
        self.assertNotEqual(diverged, ps1, "the fixture did not alter install.ps1")
        self.assertNotEqual(ps1_targets(diverged), targets,
                            "a local folder install.ps1 changes goes unseen")
        self.assertEqual(install_problems(self.page, targets), [])
        row = _row_line(self.page, MATRIX_HEADING, "GitHub Copilot")
        cases = {
            "a path the installer does not use":
                row.replace("`.github/skills`", "`.copilot/skills`", 1),
            "another target named": row.replace("`--target copilot`", "`--target agents`", 1),
        }
        for case, altered in cases.items():
            with self.subTest(case=case):
                self.assertNotEqual(altered, row, f"the fixture did not alter the row: {case}")
                copy = self.page.replace(row, altered)
                self.assertNotEqual(install_problems(copy, targets), [], case)

    def test_every_cell_is_verified_or_marked_untested(self):
        self.assertEqual(source_problems(self.page), [])
        row = _row_line(self.page, MATRIX_HEADING, "Codex")
        token = row.split("|")[6]
        self.assertRegex(token, _REFERENCE.pattern, "the Codex token cell names no source")
        cases = {
            "a claim with no source":
                row.replace(token, " " + _REFERENCE.sub("", token).strip() + " "),
            "a source path that does not exist":
                self.page.replace("scripts/lib/meter_codex.py\n", "scripts/meter_codex.py\n"),
            "a label naming another file":
                row.replace("[meter_codex.py]", "[meter_copilot.py]", 1),
        }
        for case, altered in cases.items():
            with self.subTest(case=case):
                copy = altered if altered.count("\n") > 1 else self.page.replace(row, altered)
                self.assertNotEqual(copy, self.page, f"the fixture did not alter the page: {case}")
                self.assertNotEqual(source_problems(copy), [], case)

    def test_every_harness_specific_feature_names_a_fallback(self):
        self.assertEqual(fallback_problems(self.page), [])
        _, rows = table(self.page, FALLBACK_HEADING)
        for name, pattern in FEATURES.items():
            feature = next(row[0] for row in rows if re.search(pattern, row[0]))
            line = _row_line(self.page, FALLBACK_HEADING, feature)
            cells = line.split("|")
            blank = "|".join(cells[:3] + [" - "] + cells[4:])
            for case, copy in {
                f"{name} with no fallback stated": self.page.replace(line, blank),
                f"{name} missing": _replace_row(self.page, FALLBACK_HEADING, feature, None),
            }.items():
                with self.subTest(case=case):
                    self.assertNotEqual(fallback_problems(copy), [], case)
        agentic = next(row for row in rows if re.search(FEATURES["epic implement --agentic"],
                                                         row[0]))
        line = _row_line(self.page, FALLBACK_HEADING, agentic[0])
        with self.subTest(case="an --agentic fallback that drops the dependency order"):
            copy = self.page.replace(line, line.replace("dependency order", "any order"))
            self.assertNotEqual(fallback_problems(copy), [])


if __name__ == "__main__":
    unittest.main()
