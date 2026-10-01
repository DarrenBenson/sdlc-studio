"""The retired v5 surface for this repository's shipped-doc tests: a thin import of the shipped
scanner, `scripts/lib/retired_surface.py`, which holds the one list (US0975).

What is added here is strictness this repository can afford and a consuming project cannot:
the retired flags matched bare, wherever no live parser still declares them (the shipped scan
needs the flag's script on the line), the verbs whose script was deleted outright, and the
retired PHRASES ("plan review", "two-role") - words that mean something else in a consumer's
docs. The flags are read from this repository's own CHANGELOG, and a CHANGELOG holding no
`#### Retired flags` table is refused rather than read as "nothing retired".

Not a test module (no `test_` prefix), so never collected; import it:

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import retired_surface
    hits = retired_surface.live_mentions(text)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

migrate = loader.load_script("migrate")
sdlc_md = migrate.sdlc_md
from lib import retired_surface as _shipped  # noqa: E402

#: The repository root, whose CHANGELOG holds the retired-flag tables.
_REPO = Path(__file__).resolve().parents[5]

RETIRED_CONTEXT = _shipped.RETIRED_CONTEXT
_SENTENCE_START = _shipped._SENTENCE_START
_clause = _shipped._clause
derived = _shipped.derived
_PY = r"(?:\.py)?"


def _live_flags() -> set[str]:
    """Every flag a shipped script still declares with a literal `add_argument("--x"`."""
    found: set[str] = set()
    for script in _shipped.SCRIPTS_DIR.glob("*.py"):
        found.update(re.findall(r'add_argument\(\s*"(--[\w-]+)"', script.read_text(encoding="utf-8")))
    return found


def flags() -> dict[str, str]:
    """The retired flags, label -> pattern, from this repository's CHANGELOG (an empty result is
    refused). A flag no live parser declares is retired wherever it appears; one a live verb
    still declares elsewhere is matched only beside its retired verb, inside the same code span.
    Stricter than the shipped `consumer_flags`, which needs the flag's script on the line."""
    labels = _shipped.changelog_flags(_REPO / "CHANGELOG.md")
    if not labels:
        raise RuntimeError("CHANGELOG.md holds no `#### Retired flags` table rows")
    live = _live_flags()
    out: dict[str, str] = {}
    for label in labels:
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
#: A deleted script is labelled as one, never by its bare file name, so this shipped module
#: carries no string a load-by-name could import.
DELETED_VERBS: dict[str, str] = {
    "plan_review.py (deleted script)": r"\bplan_review\.py\b",
    "repair_plan.py (deleted script)": r"\brepair_plan\.py\b",
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


def surfaces():
    """Every retired surface this repository's own docs are held to, label -> compiled pattern:
    the shipped derived half, the strict flags, the deleted verbs and the phrases."""
    return {label: re.compile(rx)
            for label, rx in {**derived(), **flags(), **DELETED_VERBS, **PHRASES}.items()}


def live_mentions(text: str, pats=None):
    """The shipped `live_mentions`, against this repository's full surface by default."""
    return _shipped.live_mentions(text, surfaces() if pats is None else pats)
