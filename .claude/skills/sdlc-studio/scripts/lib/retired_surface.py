"""The v5 surface v6 retired that a consuming project's docs can still TEACH, as one list: what
`migrate` reports in a project's own docs, and the base this repository's doc tests build on.

Only command-shaped surface ships here, because a consumer's prose is not this skill's: a
`<script>.py <retired verb>` (each script's `RETIRED_VERBS`, read with `ast`, so no script is
imported), a retired flag on the same line as its own script (from the CHANGELOG's `#### Retired
flags` tables when a CHANGELOG sits beside the skill or at the root of the repository holding
it, and from the unreleased fragments in a `changelog.d/` beside that CHANGELOG; with none, no
flags), and the retired config keys and check ids (`sdlc_md.RETIRED_CONFIG_KEYS`,
`sdlc_md.RETIRED_CHECK_IDS`). A phrase such as "plan review", or a bare `--depth`, means
something else in a consumer's docs; those are judged only by this repository's own doc tests
(`scripts/tests/retired_surface.py`), which add them.

    from lib import retired_surface
    hits = retired_surface.live_mentions(text)   # [(line number, label, line)]
    instead = retired_surface.replacements()     # {label: what replaced it}

A mention is excused when its clause says the surface is retired, and a table row when its
table's header does ("Retired in v6", "replaces"): a table of what replaced what is history.
"""
from __future__ import annotations

import ast
import bisect
import re
from pathlib import Path

from . import sdlc_md

#: The shipped scripts directory, whose `RETIRED_VERBS` registries and argparse flags are read.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
#: The skill directory (`.../sdlc-studio`), beside which an installed copy ships its CHANGELOG.
SKILL_DIR = SCRIPTS_DIR.parent

_PY = r"(?:\.py)?"
_CODE_SPAN = re.compile(r"`((?:[^`\\]|\\.)+)`")


#: Holds where an odd number of backticks follows on the line: the position is inside a code span.
_IN_CODE_SPAN = r"(?=(?:[^`\n]*`[^`\n]*`)*[^`\n]*`[^`\n]*(?:\n|$))"


def _command(script: str, rest: str) -> str:
    """`script` followed by `rest` as a consumer's docs TEACH a command: with its `.py`, or with
    the bare name inside a code span or a fenced block (`live_mentions` reads a fenced line as
    one span). Without either it is prose ("we run a mutation audit"), which names nothing."""
    name = re.escape(script)
    return rf"\b{name}(?:\.py|{_IN_CODE_SPAN}){rest}"


def retired_verbs() -> dict[str, str]:
    """`<script>.py <verb>` -> why, from each script's own `RETIRED_VERBS` registry, read with
    `ast` so no script is imported for it. A reason built from a name, not a literal, is left to
    the verb's own refusal, which names what replaced it."""
    out: dict[str, str] = {}
    for script in sorted(SCRIPTS_DIR.glob("*.py")):
        src = script.read_text(encoding="utf-8")
        if "\nRETIRED_VERBS = {" not in src:
            continue
        for node in ast.parse(src).body:
            if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict) and any(
                    getattr(t, "id", "") == "RETIRED_VERBS" for t in node.targets)):
                continue
            for key, value in zip(node.value.keys, node.value.values):
                try:
                    why = ast.literal_eval(value)
                except ValueError:
                    why = f"running `{script.name} {key.value}` names what replaced it"
                out[f"{script.name} {key.value}"] = why
    return out


def changelog_path() -> Path | None:
    """The CHANGELOG the retired-flag tables are read from: beside the skill (an installed
    copy), else at the root of the repository whose `.claude/skills/` holds it, else None."""
    beside = SKILL_DIR / "CHANGELOG.md"
    if beside.is_file():
        return beside
    repo = SKILL_DIR.parents[1] if len(SKILL_DIR.parents) > 1 else None
    if repo is not None and repo.name == ".claude":
        root_log = repo.parent / "CHANGELOG.md"
        if root_log.is_file():
            return root_log
    return None


def _flag_rows(path: Path | None) -> list[tuple[str, str]]:
    """(label, migration) for each row of EVERY `#### Retired flags` table in `path`, whatever
    release heading it sits under, then in each unreleased fragment of the `changelog.d/` beside
    it (a fragment is the CHANGELOG's next entry, folded in at the cut): the row's first code
    span and its last cell. [] when there is no CHANGELOG to read."""
    if path is None or not path.is_file():
        return []
    fragments = path.parent / "changelog.d"
    sources = [path, *(sorted(fragments.glob("*.md")) if fragments.is_dir() else [])]
    out: list[tuple[str, str]] = []
    for source in sources:
        inside = False
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                inside = line.strip().lower() == "#### retired flags"
                continue
            if inside and line.startswith("| `"):
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
                out.append((_CODE_SPAN.search(line).group(1).replace("\\|", "|"), cells[-1]))
    return out


def changelog_flags(path: Path | None) -> list[str]:
    """The label (first code span) of each retired-flag row `_flag_rows` reads from `path` and
    its unreleased fragments. [] when there is no CHANGELOG to read."""
    return [label for label, _migration in _flag_rows(path)]


def _flag_parts(label: str) -> tuple[str | None, list[str], str]:
    """(script stem, verbs, flag pattern) of a CHANGELOG retired-flag label such as
    `sprint.py close --apply-signoff` or `critic.py brief|record --phase`."""
    tokens = label.split()
    script = tokens.pop(0)[:-3] if tokens[0].endswith(".py") else None
    verbs = tokens.pop(0).split("|") if tokens and not tokens[0].startswith("-") else []
    flag = r"[ =]".join(re.escape(tok) for tok in tokens) + r"(?![\w-])"
    return script, verbs, flag


def consumer_flags(labels: list[str] | None = None) -> dict[str, str]:
    """The retired flags as a consumer's docs would TEACH them, label -> pattern: the flag on
    the same line as its own script (and verb, when the label names one). A label naming no
    script is not shipped; `--depth` alone is any tool's flag. `labels` defaults to this
    skill's CHANGELOG tables."""
    labels = changelog_flags(changelog_path()) if labels is None else labels
    out: dict[str, str] = {}
    for label in labels:
        script, verbs, flag = _flag_parts(label)
        if script is None:
            continue
        verb = rf"\s+(?:{'|'.join(map(re.escape, verbs))})\b" if verbs else r"\b"
        out[label] = _command(script, rf"{verb}[^\n]*?{flag}")
    return out


#: Words saying the surface named beside them is retired, so naming it there teaches nothing.
#: They excuse a mention only inside its own clause (`_CLAUSE_BREAK`), so an unrelated
#: refusal elsewhere in the sentence excuses nothing.
RETIRED_CONTEXT = re.compile(
    r"(?i)retir|\brefuse[sd]?\b|\bremoved\b|\bdeleted\b|\bgone\b|no longer|any ?more\b"
    r"|read by nothing|\bfrozen\b|\bbefore v6\b")

#: A table header saying its rows are history: what was retired, or what replaces it.
HISTORY_HEADER = re.compile(r"(?i)retir|\breplace|\bbefore v6\b")

#: Where a clause ends inside a sentence: a semicolon, a spaced hyphen, or a comma before a
#: conjunction that opens a new clause ("..., and so are X" continues the one before it).
_CLAUSE_BREAK = re.compile(
    r";|\s-\s|,\s+(?:and(?!\s+(?:so|nor|neither)\b)|but|so|while|whereas|then|yet)\b")

#: Where a sentence starts: after a full stop, at a list item, table row, quote or heading, or
#: after a blank line. A retirement sentence wrapped over several lines is read whole.
_SENTENCE_START = re.compile(r"[.!?](?=\s)|\n(?=[ \t]*(?:[-*+|>#]|\d+\.)\s)|\n[ \t]*\n")


def derived(commands_only: bool = False) -> dict[str, str]:
    """The surface the code holds, label -> pattern: each script's `RETIRED_VERBS`, the
    retired config keys and the retired check ids, read at call time. A verb matches its script
    with or without `.py`; `commands_only` (the consumer scan) matches it only as a command is
    written (`_command`), since a bare script name in a consumer's prose is a word."""
    out: dict[str, str] = {}
    for label in retired_verbs():
        script, verb = label.split(" ")
        rest = rf"\s+{re.escape(verb)}\b"
        out[label] = (_command(script[:-3], rest) if commands_only
                      else rf"\b{re.escape(script[:-3])}{_PY}{rest}")
    for key in sdlc_md.RETIRED_CONFIG_KEYS:
        out[key] = rf"(?<![\w.]){re.escape(key)}(?![\w-])"
    for check in sdlc_md.RETIRED_CHECK_IDS:
        out[check] = rf"(?<![\w.]){re.escape(check)}(?![\w-])"
    return out


def replacements() -> dict[str, str]:
    """Each shipped retired surface, label -> what replaced it: a verb's `RETIRED_VERBS` reason,
    a flag's Migration cell, a config key's or check id's `sdlc_md` reason. `migrate` prints it
    beside each line it names, so a reader learns the replacement where they meet the name."""
    return {**retired_verbs(), **sdlc_md.RETIRED_CONFIG_KEYS, **sdlc_md.RETIRED_CHECK_IDS,
            **dict(_flag_rows(changelog_path()))}


def surfaces(flag_patterns: dict[str, str] | None = None) -> dict[str, re.Pattern]:
    """Every shipped retired surface, label -> compiled pattern: the derived half and the
    flags (`flag_patterns`, default `consumer_flags()`)."""
    flag_patterns = consumer_flags() if flag_patterns is None else flag_patterns
    return {label: re.compile(rx)
            for label, rx in {**derived(commands_only=True), **flag_patterns}.items()}


def _table_headers(lines: list[str]) -> dict[int, str]:
    """{0-based line index of a table data row: its table's header line}, for every table."""
    out: dict[int, str] = {}
    header = None
    for i, line in enumerate(lines):
        s = line.strip()
        if not s.startswith("|"):
            header = None
        elif header is None and i + 1 < len(lines) and sdlc_md.SEP_ROW_RE.match(lines[i + 1]):
            header = line
        elif header is not None and not sdlc_md.SEP_ROW_RE.match(line):
            out[i] = header
    return out


def _clause(text: str, starts: list[int], pos: int) -> str:
    """The clause of the sentence around `pos`, wrapped lines included."""
    k = bisect.bisect_right(starts, pos)
    lo, hi = (starts[k - 1] if k else 0), (starts[k] if k < len(starts) else len(text))
    for brk in _CLAUSE_BREAK.finditer(text, lo, hi):
        if brk.end() <= pos:
            lo = brk.end()
        elif brk.start() >= pos:
            hi = brk.start()
            break
    return text[lo:hi]


def _as_code_span(line: str) -> str:
    """A fenced line read as one code span, offsets kept: its own backticks become quotes and a
    closing backtick ends it, so every position on it is inside a span (`_IN_CODE_SPAN`)."""
    return line.rstrip("\n").replace("`", "'") + "`"


def live_mentions(text: str, pats: dict[str, re.Pattern] | None = None
                  ) -> list[tuple[int, str, str]]:
    """(line number, surface label, line) for each line naming a retired surface in a clause
    that does not say it is retired, outside a table whose header says its rows are history. A clause wrapped from the line before counts; an unrelated
    clause or sentence beside it on the same line does not. A line inside a fenced block is
    code, so it is also read as a code span (`_as_code_span`)."""
    pats = surfaces() if pats is None else pats
    lines = text.splitlines(keepends=True)
    headers = _table_headers([ln.rstrip("\n") for ln in lines])
    starts = [m.end() for m in _SENTENCE_START.finditer(text)]
    out = []
    offset = 0
    fence: tuple[str, int] | None = None
    for i, line in enumerate(lines):
        at, offset = offset, offset + len(line)
        was_open = fence is not None
        fence, is_fence_line = sdlc_md.fence_step(line.strip(), fence)
        fenced = was_open and fence is not None and not is_fence_line
        if i in headers and HISTORY_HEADER.search(headers[i]):
            continue                                    # a row of a what-was-retired table
        for label, rx in pats.items():
            m = rx.search(line) or (rx.search(_as_code_span(line)) if fenced else None)
            if not m:
                continue
            if not RETIRED_CONTEXT.search(_clause(text, starts, at + m.start())):
                out.append((i + 1, label, line.rstrip("\n")))
    return out
