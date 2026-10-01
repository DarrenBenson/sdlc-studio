"""The retired v5 surface for this repository's shipped-doc tests: a thin import of the shipped
scanner, `scripts/lib/retired_surface.py`, which holds the one list (US0975).

The only thing added here is strictness this repository can afford and a consuming project
cannot: the retired flags are read from this repository's own CHANGELOG, and a CHANGELOG holding
no `#### Retired flags` table is refused rather than read as "nothing retired".

Not a test module (no `test_` prefix), so never collected; import it:

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import retired_surface
    hits = retired_surface.live_mentions(text)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

migrate = loader.load_script("migrate")
sdlc_md = migrate.sdlc_md
from lib import retired_surface as _shipped  # noqa: E402

#: The repository root, whose CHANGELOG holds the retired-flag tables.
_REPO = Path(__file__).resolve().parents[5]

DELETED_VERBS = _shipped.DELETED_VERBS
PHRASES = _shipped.PHRASES
RETIRED_CONTEXT = _shipped.RETIRED_CONTEXT
_SENTENCE_START = _shipped._SENTENCE_START
_clause = _shipped._clause
derived = _shipped.derived


def flags() -> dict[str, str]:
    """The retired flags from this repository's CHANGELOG; an empty result is refused."""
    labels = _shipped.changelog_flags(_REPO / "CHANGELOG.md")
    if not labels:
        raise RuntimeError("CHANGELOG.md holds no `#### Retired flags` table rows")
    return _shipped.flags(labels)


def surfaces():
    """Every retired surface, label -> compiled pattern, with this repository's flags."""
    return _shipped.surfaces(flags())


def live_mentions(text: str, pats=None):
    """The shipped `live_mentions`, against this repository's full surface by default."""
    return _shipped.live_mentions(text, surfaces() if pats is None else pats)
