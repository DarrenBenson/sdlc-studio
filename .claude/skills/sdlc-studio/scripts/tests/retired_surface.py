"""The v5 surface v6 retired, as ONE list every shipped-doc test imports (US0924).

Verbs, config keys and check ids are derived from the code that refuses them: each script's
`RETIRED_VERBS` read through `migrate._retired_verbs()`, `sdlc_md.RETIRED_CONFIG_KEYS` and
`sdlc_md.RETIRED_CHECK_IDS`, so a registry entry added later is read here without an edit. This
module adds the retired flags, read from the CHANGELOG's `#### Retired flags` tables, and holds
only what neither carries: the verbs whose script or parser was deleted outright, and the
retired phrases.

Not a test module (no `test_` prefix), so never collected; import it:

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import retired_surface
    hits = retired_surface.live_mentions(text)

The tier vocabulary (smoke, functional, conversational, soak, live) and the
`#verification-depth-tiers` anchor are advice no gate reads, so they are not listed.
"""
from __future__ import annotations

import bisect
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

migrate = loader.load_script("migrate")
sdlc_md = migrate.sdlc_md

_PY = r"(?:\.py)?"

#: The repository root, whose CHANGELOG holds the retired-flag tables.
_REPO = Path(__file__).resolve().parents[5]
_CODE_SPAN = re.compile(r"`((?:[^`\\]|\\.)+)`")


def _changelog_flags() -> list[str]:
    """The first code span of each row of EVERY `#### Retired flags` table in the CHANGELOG,
    whatever release heading it sits under, so a release cut that renames the heading, or a
    later release that retires more, is read without an edit. An empty result is refused."""
    lines = (_REPO / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
    out, inside = [], False
    for line in lines:
        if line.startswith("#"):
            inside = line.strip().lower() == "#### retired flags"
            continue
        if inside and line.startswith("| `"):
            out.append(_CODE_SPAN.search(line).group(1).replace("\\|", "|"))
    if not out:
        raise RuntimeError("CHANGELOG.md holds no `#### Retired flags` table rows")
    return out


def _live_flags() -> set[str]:
    """Every flag a shipped script still declares with a literal `add_argument("--x"`."""
    found: set[str] = set()
    for script in loader.SCRIPTS_DIR.glob("*.py"):
        found.update(re.findall(r'add_argument\(\s*"(--[\w-]+)"', script.read_text(encoding="utf-8")))
    return found


def flags() -> dict[str, str]:
    """The retired flags, label -> pattern, derived from the CHANGELOG tables. A flag no live
    parser declares is retired wherever it appears; one a live verb still declares elsewhere is
    matched only beside its retired verb, inside the same code span."""
    live = _live_flags()
    out: dict[str, str] = {}
    for label in _changelog_flags():
        tokens = label.split()
        script = tokens.pop(0)[:-3] if tokens[0].endswith(".py") else None
        verbs = tokens.pop(0).split("|") if tokens and not tokens[0].startswith("-") else []
        flag = r"[ =]".join(re.escape(tok) for tok in tokens) + r"(?![\w-])"
        if tokens[0] not in live:
            out[label] = rf"(?<![\w-]){flag}"
        elif verbs:
            lead = rf"(?:\b{re.escape(script)}{_PY}\s+|`)" if script else "`"
            out[label] = rf"{lead}(?:{'|'.join(map(re.escape, verbs))})\b[^`\n]*?{flag}"
        else:
            out[label] = rf"\b{re.escape(script)}{_PY}\s[^`\n]*?{flag}"
    return out


#: Verbs with no registry to derive from: the script, or the subparser, was deleted outright.
DELETED_VERBS: dict[str, str] = {
    "plan_review.py": r"\bplan_review\.py\b",
    "repair_plan.py": r"\brepair_plan\.py\b",
    "validate.py warning-ratchet": r"\bwarning-ratchet\b",
}

#: The retired concepts a reader would follow as prose rather than type as a command. The run's
#: signer is still its reviewer of record (`sprint sign --principal`); only one approving each
#: unit is retired.
PHRASES: dict[str, str] = {
    # The two-role shape: a reviewer filing findings as evidence, beside a signer who approves.
    "two-role review": r"\btwo-role\b|(?i:\bfindings as evidence\b)",
    "a reviewer of record approving each unit":
        r"(?i:\breviewer[- ]of[- ]record\b[^\n]*\b(?:each|every|per)[- ]unit\b"
        r"|\b(?:each|every|per)[- ]unit\b[^\n]*\breviewer[- ]of[- ]record\b)"
        r"|\bunits hold at Review\b",
    "the Verification depth and Verification target fields":
        r"\bVerification (?:depth|target)\b(?![- ]tiers?\b)",
    "Mutation-checked": r"\bMutation-checked\b",
    # The tiers stay as advice; a gate on them, or a unit held from Done or Fixed by them, is gone.
    "the verification-depth gate":
        r"(?i)(?<![#\w-])(?:verification[- ])?depth(?:[- ](?:gate|parity)\b"
        r"|\b[^\n]*\b(?:cannot|can.t|may not|must not)\s+reach\b)"
        r"|\b(?:cannot|can.t|may not|must not)\s+reach\b[^\n]*(?<![#\w-])(?:verification[- ])?depth\b",
    "plan review as a step": r"(?i)\bplan[- ]review\b",
    "batch review": r"(?i)\bbatch review\b",
    "the sign-off brief": r"(?i)\bsign-?off (?:decision )?brief\b|\bsign-off chain\b"
                          r"|\bseat's sign-off\b",
    "a repair plan": r"(?i)\brepair[- ]plan\b",
    "a mutation gate, ledger or evidence":
        r"(?i)\bmutation(?:-check)?[- ](?:gate|ledger|evidence)\b",
}

#: Words saying the surface named beside them is retired, so naming it there teaches nothing.
#: They excuse a mention only inside its own clause (`_CLAUSE_BREAK`), so an unrelated
#: refusal elsewhere in the sentence excuses nothing.
RETIRED_CONTEXT = re.compile(
    r"(?i)retir|\brefuse[sd]?\b|\bremoved\b|\bdeleted\b|\bgone\b|no longer|any ?more\b"
    r"|read by nothing|\bfrozen\b|\bbefore v6\b")

#: Where a clause ends inside a sentence: a semicolon, a spaced hyphen, or a comma before a
#: conjunction that opens a new clause ("..., and so are X" continues the one before it).
_CLAUSE_BREAK = re.compile(
    r";|\s-\s|,\s+(?:and(?!\s+(?:so|nor|neither)\b)|but|so|while|whereas|then|yet)\b")

#: Where a sentence starts: after a full stop, at a list item, table row, quote or heading, or
#: after a blank line. A retirement sentence wrapped over several lines is read whole.
_SENTENCE_START = re.compile(r"[.!?](?=\s)|\n(?=[ \t]*(?:[-*+|>#]|\d+\.)\s)|\n[ \t]*\n")


def derived() -> dict[str, str]:
    """The surface the code holds, label -> pattern: each script's `RETIRED_VERBS`, the
    retired config keys and the retired check ids, read at call time."""
    out: dict[str, str] = {}
    for label in migrate._retired_verbs():
        script, verb = label.split(" ")
        out[label] = rf"\b{re.escape(script[:-3])}{_PY}\s+{re.escape(verb)}\b"
    for key in sdlc_md.RETIRED_CONFIG_KEYS:
        out[key] = rf"(?<![\w.]){re.escape(key)}(?![\w-])"
    for check in sdlc_md.RETIRED_CHECK_IDS:
        out[check] = rf"(?<![\w.]){re.escape(check)}(?![\w-])"
    return out


def surfaces() -> dict[str, re.Pattern]:
    """Every retired surface, label -> compiled pattern: the derived half and the lists above."""
    return {label: re.compile(rx)
            for label, rx in {**derived(), **flags(), **DELETED_VERBS, **PHRASES}.items()}


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


def live_mentions(text: str, pats: dict[str, re.Pattern] | None = None
                  ) -> list[tuple[int, str, str]]:
    """(line number, surface label, line) for each line naming a retired surface in a clause
    that does not say it is retired. A clause wrapped from the line before counts; an unrelated
    clause or sentence beside it on the same line does not."""
    pats = surfaces() if pats is None else pats
    lines = text.splitlines(keepends=True)
    starts = [m.end() for m in _SENTENCE_START.finditer(text)]
    out = []
    offset = 0
    for i, line in enumerate(lines):
        at, offset = offset, offset + len(line)
        for label, rx in pats.items():
            m = rx.search(line)
            if not m:
                continue
            if not RETIRED_CONTEXT.search(_clause(text, starts, at + m.start())):
                out.append((i + 1, label, line.rstrip("\n")))
    return out
