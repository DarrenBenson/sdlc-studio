"""Risk classes: the project's component map and the one order its classes rank in.

A project declares its components in `sdlc-studio/.config.yaml` under `risk.components`, a mapping
of path prefix to class:

    risk:
      components:
        src/payments: high
        src/auth: elevated

The vocabulary is fixed and ordered, standard < elevated < high, so "the highest class a change
touches" is always defined. A prefix matches a path on whole segments (`src/pay` matches
`src/pay/charge.py` and `src/pay` itself, never `src/payroll.py`), and every prefix a path lies
under counts, so a nested prefix never lowers the class of the component around it. A path no
prefix covers is standard.

Nothing here refuses. No map, or an empty one, reads every change as standard and yields one note
saying so; an entry naming a class outside the vocabulary is kept as standard and yields one note
naming it; a `risk.components` that is not a mapping yields one note and reads as no map. The
notes are for the caller to print.

The map is read here and nowhere else, so every reader of a class applies the same prefixes and
the same order.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import sdlc_md

#: The classes, lowest first. The order is the ranking.
CLASSES: tuple[str, ...] = ("standard", "elevated", "high")
#: The class of a path no component covers, and of every path when no map is declared.
DEFAULT = CLASSES[0]
#: Where the map is declared, as a dotted key of the project config.
CONFIG_KEY = "risk.components"
#: The field a story carries its class in, from the markdown conventions module.
FIELD = sdlc_md.RISK_CLASS_FIELD

NO_MAP_NOTE = (f"risk class: no component map is declared (`{CONFIG_KEY}` in "
               f"sdlc-studio/.config.yaml), so every story is {DEFAULT}")


def rank(cls: str) -> int:
    """The position of `cls` in the order; a class outside the vocabulary ranks as the default."""
    return CLASSES.index(cls) if cls in CLASSES else CLASSES.index(DEFAULT)


def _norm(path: str) -> str:
    """A path or prefix compared on whole segments: no leading `./`, no surrounding slashes."""
    p = str(path).strip()
    while p.startswith("./"):
        p = p[2:]
    return p.strip("/")


def classify(files, components: dict[str, str]) -> tuple[str, list[str]]:
    """(the highest class among the components `files` touch, those components' prefixes in map
    order, normalised). No file, or no file under any prefix, is the default class and no
    component."""
    paths = [_norm(f) for f in files if _norm(f)]
    touched = [(_norm(prefix), cls) for prefix, cls in components.items()
               if _norm(prefix) and any(p == _norm(prefix) or p.startswith(_norm(prefix) + "/")
                                        for p in paths)]
    best = max((cls for _, cls in touched), key=rank, default=DEFAULT)
    return best, [prefix for prefix, _ in touched]


@dataclass(frozen=True)
class RiskMap:
    """A project's component map as read: prefix -> class (every class in `CLASSES`), whether
    a map was declared at all, and the one-line notes for what the reader could not honour."""
    components: dict[str, str] = field(default_factory=dict)
    declared: bool = False
    notes: tuple[str, ...] = ()

    def classify(self, files) -> tuple[str, list[str]]:
        return classify(files, self.components)

    def classify_affects(self, value: str) -> tuple[str, list[str]]:
        """Classify a raw `Affects` value, read by the one Affects parser the planner uses."""
        return self.classify(sdlc_md.affects_files(f"> **Affects:** {value or ''}"))


def load_map(repo_root) -> RiskMap:
    """Read `risk.components` from the project's override config. Never raises on the map's
    content: what it cannot honour becomes a note and reads as standard."""
    raw = sdlc_md.project_override(Path(repo_root), CONFIG_KEY, None)
    if raw is None or raw == {}:
        return RiskMap(notes=(NO_MAP_NOTE,))
    if not isinstance(raw, dict):
        return RiskMap(notes=(f"risk class: `{CONFIG_KEY}` is not a mapping of path prefix to "
                              f"class, so it is ignored and every story is {DEFAULT}",))
    components: dict[str, str] = {}
    notes: list[str] = []
    for key, value in raw.items():
        prefix = _norm(key)
        cls = str(value).strip().lower() if value is not None else ""
        if cls not in CLASSES:
            notes.append(f"risk class: `{CONFIG_KEY}` entry {str(key)!r} names unknown class "
                         f"{value!r} (known: {', '.join(CLASSES)}), so it is read as {DEFAULT}")
            cls = DEFAULT
        if prefix:
            components[prefix] = max(cls, components.get(prefix, DEFAULT), key=rank)
    return RiskMap(components=components, declared=True, notes=tuple(notes))
