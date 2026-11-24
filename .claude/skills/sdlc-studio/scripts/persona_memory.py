#!/usr/bin/env python3
"""Persona memory: each persona's evidenced learnings, in a committed file beside its card.

A learning lives in `sdlc-studio/personas/memory/<key>.md`. The key is a seat's declared role
(`qa`), so the memory follows the seat the review ledger attributes verdicts to, or a user
persona's card stem (`maya-okafor-founder-engineer`). A key that is both is refused rather
than guessed, and so is one that is neither.

Each entry has the project lessons log's shape, `## M-NNNN: <title>`, then `- **Field:** value`
bullets, then the learning as prose. It is read by `lessons.parse_project_lessons` with this
module's entry pattern and its fields are set by `lessons.upsert_field`, so there is one parser
and one field writer for both logs. Ids are unique across every memory file, never per file.

`add` writes an entry as proposed, stamped with its evidence, the date and a Review-by horizon
(`personas.memory.validity_days`, default 90). Every cited id must resolve on disk: an
artefact, a decisions row, a run a report under `sdlc-studio/reports/` names, or a verdict
reference `<unit> r<round>` the review ledger holds. A write git would never hold (a gitignore rule
matching the memory directory) is refused, naming the rule. `list` and `recall` read one
persona's file only. `set_field` is the helper later verbs use to record an approval, what a
learning addresses, the close that listed it, a strike or a retirement.

The brief side is `digest` and `render`: a persona's live learnings, ranked so one whose
evidence shares the unit's files comes first, capped at
`personas.memory.inject_max` (default 5), each carried as its id, title and a short gist. A
store that cannot be read is reported as unreadable, never as a store with nothing in it.

Live means approved, within its horizon, not struck or retired, and listed by a close whose
run's tracked record is signed, lists it and does not strike it (`standing`). Signed is read
from that record and never written into memory, so a reopened run holds its learnings until it
is signed again. The close lists every approved learning not yet live (`pending_listing`) and
stamps it Listed-in (`mark_listed`); the signature may strike any it listed (`strike`).

The retro side is `learn-brief` and `propose`. A seat is briefed with its own record from
`retro.py seats` (read through retro's functions, never re-derived), each adverse item with
its key, and its card framed with its live learnings; what it writes is recorded verbatim as
proposed, its evidence the ids that record lists rather than ids its text names, one open
proposal per seat and retro, which is one run's. `approve-brief` and `approve` let another seat, told apart by its
recorded role and never by name, approve it against those adverse items and the subject
card's Non-Negotiables and Authority, or reject it so no brief carries it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lessons  # noqa: E402  (sibling: the one entry parser and field writer)
import persona_resolve  # noqa: E402  (sibling: the one seat roster)
from lib import run_state, sdlc_md  # noqa: E402

MEMORY_REL = "sdlc-studio/personas/memory"
PERSONAS_REL = "sdlc-studio/personas"
TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "personas" / "memory-template.md"
ENTRY_RE = re.compile(r"^##\s+(M-\d{4}):\s*(.+?)\s*$")
ID_RE = re.compile(r"^M-\d{4}$")
#: Every state an entry can hold. Only `add` writes proposed; approval and revalidation
#: move the rest, and observed records usage evidence.
STATES = ("proposed", "approved", "rejected", "retired", "observed")
#: Every field an entry may carry, in the order `add` stamps the first five. The next five are
#: written later through `set_field`: who approved it, what it addresses, the close that
#: listed it, a strike, a retirement. `propose` stamps Run and Retro: the run the learning
#: looks back on and the retro whose seat record its evidence came from. `approve` writes
#: Rejected-by for a rejection, the Reason given and the date it Decided.
FIELDS = ("Persona", "Evidence", "Added", "Review-by", "State",
          "Approved-by", "Addresses", "Listed-in", "Struck", "Retired",
          "Run", "Retro", "Rejected-by", "Reason", "Decided")
VALIDITY_DAYS_KEY = "personas.memory.validity_days"
INJECT_MAX_KEY = "personas.memory.inject_max"
DEFAULT_INJECT_MAX = 5
GIST_MAX = 200
_DECISION_RE = re.compile(r"^D\d{4}$")
_RUN_RE = re.compile(r"^RUN-[0-9A-Z]+$")
_RUN_TOKEN_RE = re.compile(r"(?<![0-9A-Za-z])RUN-[0-9A-Z]+(?![0-9A-Za-z])")
_VERDICT_REF_RE = re.compile(r"^(\S+)\s+r(\d+)$")
_SEPARATOR_RE = re.compile(r"\s*[,;]\s*")


class MemoryRefusal(ValueError):
    """A write or a read refused, with the reason the operator is told. Nothing is written."""


class StoreError(ValueError):
    """A memory file that exists but cannot be read as one."""


# ----------------------------------------------------------------------------- keys and paths


def memory_path(root: Path | str, key: str) -> Path:
    """The memory file for `key`."""
    return Path(root) / MEMORY_REL / f"{key}.md"


def _card_stems(root: Path) -> list[str]:
    """The user persona cards' stems: the flat `personas/*.md`, less the registry files."""
    pdir = root / PERSONAS_REL
    if not pdir.is_dir():
        return []
    return sorted(p.stem for p in pdir.glob("*.md")
                  if p.name.lower() not in {"index.md", "readme.md", "consult-guide.md"}
                  and not p.name.startswith("_"))


def resolve_key(root: Path | str, key: str) -> str:
    """`key` when it names exactly one persona: a seat role or a user persona card stem.

    Both are checked before either is accepted, so a key that is both is refused rather than
    silently writing one of them."""
    root = Path(root)
    key = (key or "").strip()
    seats = persona_resolve.seat_roster(root)
    cards = _card_stems(root)
    is_seat, is_card = key in seats, key in cards
    if is_seat and is_card:
        raise MemoryRefusal(f"--persona {key!r} is both a seat role and a persona card "
                            f"({PERSONAS_REL}/{key}.md), so whose memory it is cannot be told; "
                            f"rename the card")
    if not (is_seat or is_card):
        raise MemoryRefusal(f"--persona {key!r} names neither a seat role ({', '.join(seats)}) "
                            f"nor a persona card ({', '.join(cards) or 'none'})")
    return key


# ----------------------------------------------------------------------------- reading


def parse(text: str, source: str = "memory") -> list[dict]:
    """The entries of one memory file, in file order. Refuses, as StoreError, a level-two
    heading that is not an entry, an entry with no known State, and a duplicate id."""
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## ") and not ENTRY_RE.match(line):
            raise StoreError(f"{source} line {n}: {line.strip()!r} is not an "
                             f"`## M-NNNN: title` entry heading")
    entries = lessons.parse_project_lessons(text, entry_re=ENTRY_RE)
    seen: set[str] = set()
    for e in entries:
        if e["id"] in seen:
            raise StoreError(f"{source}: {e['id']} appears twice")
        seen.add(e["id"])
        if e["fields"].get("state", "").strip().lower() not in STATES:
            raise StoreError(f"{source}: {e['id']} has no State of {', '.join(STATES)}")
    return entries


def read_store(path: Path) -> list[dict]:
    """The entries in the memory file at `path`; [] when it does not exist."""
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        raise StoreError(f"{path}: {exc}") from exc
    return parse(text, str(path))


def all_stores(root: Path | str) -> dict[Path, list[dict]]:
    """Every memory file's entries, by path. An unreadable file is raised, not skipped: a
    new id allocated without it could collide with one it holds. So is an id two files hold
    (two clones can mint the same one), as StoreError naming both: a write naming it could
    not tell which entry is meant, so none picks the first file it reads."""
    mdir = Path(root) / MEMORY_REL
    if not mdir.is_dir():
        return {}
    stores = {p: read_store(p) for p in sorted(mdir.glob("*.md"))}
    held: dict[str, Path] = {}
    for path, entries in stores.items():
        for e in entries:
            first = held.setdefault(e["id"], path)
            if first != path:
                raise StoreError(f"{e['id']} is in both {first.name} and {path.name} under "
                                 f"{MEMORY_REL}, so naming it is ambiguous; renumber one")
    return stores


def next_id(stores: dict[Path, list[dict]]) -> str:
    """The next M-NNNN, one past the highest across every memory file in `stores`."""
    nums = [sdlc_md.id_number(e["id"]) or 0 for entries in stores.values() for e in entries]
    return f"M-{(max(nums) if nums else 0) + 1:04d}"


def validity_days(root: Path | str) -> int:
    """`personas.memory.validity_days`, else the lessons' default; a bad value degrades."""
    configured = sdlc_md.project_override(root, VALIDITY_DAYS_KEY)
    try:
        return int(configured) if configured is not None else lessons.DEFAULT_VALIDITY_DAYS
    except (TypeError, ValueError):
        return lessons.DEFAULT_VALIDITY_DAYS


def state_of(entry: dict) -> str:
    return entry["fields"].get("state", "").strip().lower()


# ----------------------------------------------------------------------------- evidence


def evidence_tokens(values: list[str] | None) -> list[str]:
    """The cited ids, from repeated or comma-separated `--evidence` values."""
    out: list[str] = []
    for value in values or []:
        out += [t.strip() for t in _SEPARATOR_RE.split(value) if t.strip()]
    return out


def _decision_ids(root: Path) -> set[str]:
    texts = []
    for p in [root / "sdlc-studio" / "decisions.md",
              *sorted((root / "sdlc-studio" / "decisions").glob("*.md"))]:
        if p.is_file():
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
    return set(re.findall(r"(?m)^\|\s*(D\d{4})\s*\|", "\n".join(texts)))


def _report_names(root: Path, run_id: str) -> bool:
    """True when a report names `run_id` as a whole run id, in its own case: a report naming
    `RUN-01ABCDEF` names neither `RUN-0` nor `run-01abcdef`."""
    rdir = root / "sdlc-studio" / "reports"
    return rdir.is_dir() and any(
        run_id in _RUN_TOKEN_RE.findall(p.read_text(encoding="utf-8", errors="replace"))
        for p in rdir.glob("*.md"))


def _verdict_held(root: Path, unit: str, round_: int) -> bool:
    import critic  # noqa: PLC0415 - sibling; only a verdict reference pays for the ledger read
    return any(r.get("unit") == unit and int(r.get("round") or 0) == round_
               for r in critic.read_verdicts(root))


def resolves(root: Path | str, token: str) -> bool:
    """True when `token` names something on disk: an artefact, a decisions row, a run a
    report under `sdlc-studio/reports/` names, or a verdict reference `<unit> r<round>` the
    ledger holds."""
    root = Path(root)
    m = _VERDICT_REF_RE.match(token)
    if m:
        return bool(sdlc_md.find_by_id(root, m.group(1))) and _verdict_held(
            root, m.group(1), int(m.group(2)))
    if _DECISION_RE.match(token):
        return token in _decision_ids(root)
    if _RUN_RE.match(token):
        return _report_names(root, token)
    return bool(sdlc_md.find_by_id(root, token))


# ----------------------------------------------------------------------------- writing


def _render_file(header: str, entries: list[dict]) -> str:
    parts = [header.rstrip() + "\n"]
    parts.extend("\n" + lessons.render_entry(e) for e in entries)
    return "".join(parts)


def _new_header(key: str) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    return template.replace("{{persona}}", key).replace("{{date}}", sdlc_md.now_date())


def _field_line(body: str) -> str:
    """The first line of `body` with a `- **Field:** value` shape, or "": it would read back
    as the entry's own field, so a learning could set its own State or Evidence."""
    return next((ln for ln in (body or "").splitlines() if lessons.FIELD_BULLET_RE.match(ln)),
                "")


def _read_back_drift(read: list[dict], wrote: list[dict], body: str) -> str:
    """What the reader reads differently from what `add` stamped, or "" when nothing: the same
    entries in order, and the new one with its id, its title, every field it set and no
    other, and `body` as its prose. The stamp is compared, not the body's shape, so a line
    the reader takes as an entry or a field is refused however it is spelt."""
    ids, want = [e["id"] for e in read], [e["id"] for e in wrote]
    if ids != want:
        return f"the file reads back as {', '.join(ids)}, not {', '.join(want)}"
    back, new = read[-1], wrote[-1]
    if back["title"] != new["title"]:
        return f"its title reads back as {back['title']!r}, not {new['title']!r}"
    stamped = {k: str(v).strip() for k, v in new["fields"].items()}
    for k in sorted(set(stamped) | set(back["fields"])):
        if back["fields"].get(k) != stamped.get(k):
            return (f"its {k} reads back as {back['fields'].get(k, '(absent)')!r}, "
                    f"not {stamped.get(k, '(absent)')!r}")
    if prose_of(back) != "\n".join(body.strip().splitlines()):
        return "its prose reads back as something other than the body given"
    return ""


def add(root: Path | str, key: str, title: str, body: str, evidence: list[str],
        extra: dict | None = None) -> dict:
    """Write one proposed learning for `key` and return it, stamping `extra` (field: value)
    after its State. Refuses, writing nothing: no evidence, any cited id that resolves to
    nothing, an unknown or ambiguous key, a blank title or body, a body holding a level-two
    heading line or a field line, any learning `parse` would not read back as exactly the
    entry stamped (`_read_back_drift`), an id two memory files hold, and a memory directory
    git would never hold."""
    root = Path(root)
    cited = evidence_tokens(evidence)
    if not cited:
        raise MemoryRefusal("a learning needs --evidence: an artefact id, a decision, a run "
                            "or a verdict reference `<unit> r<round>`")
    key = resolve_key(root, key)
    missing = [t for t in cited if not resolves(root, t)]
    if missing:
        raise MemoryRefusal(f"--evidence {', '.join(missing)} resolves to nothing on disk")
    if not (title or "").strip() or not (body or "").strip():
        raise MemoryRefusal("a learning needs a --title and a --body")
    heading = next((ln for ln in body.strip().splitlines() if ln.startswith("## ")), None)
    if heading:
        raise MemoryRefusal(f"the --body line {heading.strip()!r} is a level-two heading, which "
                            "the memory file reads as an entry: use ### or plain text")
    field = _field_line(body)
    if field:
        raise MemoryRefusal(f"the --body line {field.strip()!r} has a field's shape, which the "
                            "memory file reads as the entry's own field")
    path = memory_path(root, key)
    rel = path.relative_to(root).as_posix()
    held = lessons.ignored_reason(root, rel)
    if held:
        raise MemoryRefusal(held)
    try:
        stores = all_stores(root)
    except StoreError as exc:
        raise MemoryRefusal(f"the memory files cannot be read as one store, so a new id "
                            f"could collide: {exc}")
    today = sdlc_md.now_date()
    new = {"id": next_id(stores),
           "title": lessons.heading_title(title), "fields": {}, "body": body.strip()}
    for name, value in (("Persona", key), ("Evidence", ", ".join(cited)), ("Added", today),
                        ("Review-by", lessons.add_days(today, validity_days(root))),
                        ("State", "proposed"), *(extra or {}).items()):
        lessons.upsert_field(new, name, value)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        header = lessons.project_header_of(text, entry_re=ENTRY_RE)
        entries = stores.get(path, [])
    else:
        header, entries = _new_header(key), []
    text = _render_file(header, [*entries, new])
    try:  # write only what the reader reads back, so no later add or brief meets a bad file
        drift = _read_back_drift(parse(text, rel), [*entries, new], body)
    except StoreError as exc:
        raise MemoryRefusal(f"the learning would not read back, so it is not written: {exc}")
    if drift:
        raise MemoryRefusal(f"the learning would not read back as written, so it is not "
                            f"written: {drift}")
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, text)
    return new


def set_field(root: Path | str, entry_id: str, name: str, value: str) -> dict:
    """Set one field on the entry `entry_id`, wherever it lives, through
    `lessons.upsert_field`, and rewrite its file. Refuses a field outside FIELDS, a State
    outside STATES and an id no memory file holds."""
    return set_fields(root, entry_id, [(name, value)])


def set_fields(root: Path | str, entry_id: str, pairs: list[tuple[str, str]]) -> dict:
    """`set_field` for several fields in one rewrite: every pair is checked before any is set,
    so a refused pair leaves the file as it was. The rewritten file is read back before it is
    written, as `add`'s is, and refused unless every entry reads back as held with the pairs
    set: a value holding a line break writes a line the reader takes as another field, so a
    rejection's reason could otherwise read the entry back as approved."""
    canon = []
    for name, value in pairs:
        canonical = next((f for f in FIELDS if f.lower() == (name or "").strip().lower()), None)
        if canonical is None:
            raise MemoryRefusal(f"{name!r} is not a memory field ({', '.join(FIELDS)})")
        if canonical == "State" and value.strip().lower() not in STATES:
            raise MemoryRefusal(f"State {value!r} is not one of {', '.join(STATES)}")
        canon.append((canonical, value))
    try:
        stores = all_stores(root)
    except StoreError as exc:
        raise MemoryRefusal(str(exc))
    for path, entries in stores.items():
        for e in entries:
            if e["id"] == entry_id:
                for canonical, value in canon:
                    lessons.upsert_field(e, canonical, value)
                header = lessons.project_header_of(path.read_text(encoding="utf-8"),
                                                   entry_re=ENTRY_RE)
                text = _render_file(header, entries)
                drift = _set_read_back_drift(text, path.name, entries)
                if drift:
                    raise MemoryRefusal(f"{entry_id} would not read back as set, so nothing is "
                                        f"written: {drift}; a field value is one line")
                sdlc_md.atomic_write(path, text)
                return e
    raise MemoryRefusal(f"no memory file holds {entry_id}")


def _set_read_back_drift(text: str, source: str, held: list[dict]) -> str:
    """What the reader reads differently in `text` from the entries `set_fields` holds, or ""
    when nothing: the same ids in order, and every field of each entry, no more."""
    try:
        read = parse(text, source)
    except StoreError as exc:
        return str(exc)
    ids, want = [e["id"] for e in read], [e["id"] for e in held]
    if ids != want:
        return f"the file reads back as {', '.join(ids)}, not {', '.join(want)}"
    for back, entry in zip(read, held):
        stamped = {k: str(v).strip() for k, v in entry["fields"].items()}
        for k in sorted(set(stamped) | set(back["fields"])):
            if back["fields"].get(k) != stamped.get(k):
                return (f"its {k} reads back as {back['fields'].get(k, '(absent)')!r}, "
                        f"not {stamped.get(k, '(absent)')!r}")
    return ""


# ----------------------------------------------------------------------------- listing


def _row(entry: dict, days: int) -> dict:
    f = entry["fields"]
    return {"id": entry["id"], "title": entry["title"], "persona": f.get("persona", ""),
            "state": state_of(entry), "horizon": lessons.horizon_of(entry, days),
            "evidence": f.get("evidence", ""), "added": f.get("added", ""),
            "struck": f.get("struck", ""), "body": prose_of(entry)}


def prose_of(entry: dict) -> str:
    """The learning itself: the entry body without its field bullets."""
    return "\n".join(ln for ln in entry["body"].splitlines()
                     if not lessons.FIELD_BULLET_RE.match(ln)).strip()


def list_entries(root: Path | str, key: str, query: str | None = None) -> list[dict]:
    """One persona's learnings, in file order, those whose title or body holds `query`
    (case-insensitive) when one is given. Reads that persona's file and no other."""
    root = Path(root)
    key = resolve_key(root, key)
    days = validity_days(root)
    rows = [_row(e, days) for e in read_store(memory_path(root, key))]
    if query:
        q = query.lower()
        rows = [r for r in rows if q in r["title"].lower() or q in r["body"].lower()]
    return rows


# ----------------------------------------------------------------------------- the brief


def inject_max(root: Path | str) -> int:
    """`personas.memory.inject_max`, else DEFAULT_INJECT_MAX; a bad or negative value
    degrades to the default."""
    configured = sdlc_md.project_override(root, INJECT_MAX_KEY)
    try:
        value = int(configured) if configured is not None else DEFAULT_INJECT_MAX
    except (TypeError, ValueError):
        return DEFAULT_INJECT_MAX
    return value if value >= 0 else DEFAULT_INJECT_MAX


def gist(entry: dict, limit: int = GIST_MAX) -> str:
    """The learning on one line, at most `limit` characters, cut with an ellipsis."""
    text = " ".join(prose_of(entry).split())
    return text if len(text) <= limit else text[:limit - 1].rstrip() + lessons.ELLIPSIS


def _cited_files(root: Path, evidence: str) -> set[str]:
    """The Affects paths of every unit the evidence cites (a verdict reference cites its
    unit). Relevance is derived from these, so no field records it and none can be stale."""
    files: set[str] = set()
    for token in evidence_tokens([evidence]):
        m = _VERDICT_REF_RE.match(token)
        found = sdlc_md.find_by_id(root, m.group(1) if m else token)
        if not found:
            continue
        try:
            text = Path(found[0]).read_text(encoding="utf-8")
        except (OSError, ValueError):
            continue
        files |= {_norm(p) for p in sdlc_md.affects_files(text)}
    return files


def _norm(path: str) -> str:
    return path.strip().strip("`").removeprefix("./")


def digest(root: Path | str, key: str, affects=(), *, today: str | None = None) -> dict:
    """What a brief carries for `key`: its live learnings (approved, Review-by not yet passed
    and `standing` live), ranked by relevance to `affects` and then recency, capped at
    `inject_max`.

    Returns `{persona, path, learnings, live, withheld, expired, unsigned, unreadable,
    damaged, unlisted, cap, absent, error}`: `unsigned` counts approved learnings whose listing run is not signed,
    `unreadable` those whose run's tracked record cannot be read (its repo-relative paths in
    `damaged`), `unlisted` those no signed close has listed. Only the persona's own file is read. A file
    that cannot be parsed sets `error`, never reads as empty; a missing file sets `absent`."""
    root = Path(root)
    path = memory_path(root, key)
    rel = path.relative_to(root).as_posix()
    cap = inject_max(root)
    out = {"persona": key, "path": rel, "learnings": [], "live": 0, "withheld": 0,
           "expired": 0, "unsigned": 0, "unreadable": 0, "damaged": [], "unlisted": 0,
           "cap": cap,
           "absent": not path.exists(), "error": ""}
    if out["absent"]:
        return out
    try:
        entries = read_store(path)
    except StoreError as exc:
        out["error"] = str(exc).replace(str(path), rel)  # names the file, repo-relative
        return out
    today = today or sdlc_md.now_date()
    days = validity_days(root)
    unit_files = {_norm(a) for a in affects or ()}
    live, records = [], {}
    for e in entries:
        if state_of(e) != "approved" or e["fields"].get("retired"):
            continue
        horizon = lessons.horizon_of(e, days)
        if horizon is None or horizon < today:
            out["expired"] += 1
            continue
        held = standing(root, e, records)
        if held in ("unsigned", "unreadable", "unlisted"):
            out[held] += 1
        if held == "unreadable":
            damaged = run_state.tracked_path(root, e["fields"]["listed-in"].strip()
                                             ).relative_to(root).as_posix()
            if damaged not in out["damaged"]:
                out["damaged"].append(damaged)
        if held != "live":
            continue
        relevant = bool(unit_files & _cited_files(root, e["fields"].get("evidence", "")))
        live.append((relevant, e["fields"].get("added", ""), e["id"], e))
    live.sort(key=lambda t: t[:3], reverse=True)
    out["live"] = len(live)
    out["learnings"] = [{"id": e["id"], "title": e["title"], "gist": gist(e),
                         "relevant": relevant} for relevant, _, _, e in live[:cap]]
    out["withheld"] = max(0, len(live) - cap)
    return out


def render(d: dict, render_name: str) -> list[str]:
    """A digest as brief lines, under a heading that names the persona and the render."""
    key, rel = d["persona"], d["path"]
    lines = [f"--- LEARNINGS: {key} ({render_name} render) ---"]
    if d.get("error"):
        return lines + [f"Learnings for {key} could not be read: {d['error']}. Reported rather "
                        f"than omitted: a brief that lost them cannot be told from one that "
                        f"has none."]
    if d.get("absent"):
        return lines + [f"Learnings for {key}: none recorded (no {rel})."]
    items = d.get("learnings") or []
    if items:
        lines.append(f"Learnings for {key} ({len(items)} of {d['live']} live, from {rel}) - "
                     f"weigh them; the criteria and the contract above are law:")
        lines += [f"  {i['id']} {i['title']}: {i['gist']}" for i in items]
    else:
        lines.append(f"Learnings for {key}: none live in {rel}.")
    if d.get("withheld"):
        lines.append(f"  (+{d['withheld']} more live, withheld by the cap of {d['cap']})")
    if d.get("expired"):
        one = d["expired"] == 1
        lines.append(f"  ({d['expired']} approved {'learning' if one else 'learnings'} past "
                     f"{'its' if one else 'their'} Review-by horizon, not carried: revalidate "
                     f"or retire {'it' if one else 'them'})")
    if d.get("unsigned"):
        one = d["unsigned"] == 1
        lines.append(f"  ({d['unsigned']} approved "
                     + ("learning awaits its run's signature, not carried until that run is "
                        "signed)" if one else
                        "learnings await their runs' signatures, not carried until those runs "
                        "are signed)"))
    if d.get("unreadable"):
        one = d["unreadable"] == 1
        lines.append(f"  ({d['unreadable']} approved {'learning' if one else 'learnings'} not "
                     f"carried: the run record at {', '.join(d.get('damaged') or [])} is "
                     f"unreadable, so whether {'its' if one else 'their'} run is signed is "
                     f"not known; restore it from git)")
    if d.get("unlisted"):
        one = d["unlisted"] == 1
        lines.append(f"  ({d['unlisted']} approved {'learning' if one else 'learnings'} no "
                     f"signed close has listed, not carried until one lists "
                     f"{'it' if one else 'them'})")
    return lines


def brief_block(root: Path | str, key: str, render_name: str, affects=()) -> str:
    """The learnings block a brief or a framing appends for `key`."""
    return "\n".join(render(digest(root, key, affects), render_name))


# --------------------------------------------------------------- the close and the signature


def _struck_ids(record: dict) -> set[str]:
    return {s.get("id") for s in record.get(run_state.PERSONA_STRUCK) or []
            if isinstance(s, dict)}


def standing(root: Path | str, entry: dict, records: dict | None = None) -> str:
    """Where an approved learning stands against the signature: `live` when the run its
    Listed-in names has a signed tracked record (`run_state.signed_record`) that lists it and
    does not strike it; `struck` when that record strikes it or its Struck field is set;
    `unsigned` when its run is not signed; `unreadable` when its run's tracked record is filed
    and cannot be read, which is not the same fact as unsigned; `unlisted` when no signed close
    has listed it. `records` caches each run's signed record across calls."""
    f = entry["fields"]
    if f.get("struck"):
        return "struck"
    run = (f.get("listed-in") or "").strip()
    if not run:
        return "unlisted"
    cache = records if records is not None else {}
    if run not in cache:
        cache[run] = run_state.signed_record(root, run)
    rec = cache[run]
    if rec is None:
        return "unreadable" if run_state.record_unreadable(root, run) else "unsigned"
    if entry["id"] in _struck_ids(rec):
        return "struck"
    return "live" if entry["id"] in (rec.get(run_state.PERSONA_LISTED) or []) else "unlisted"


def pending_listing(root: Path | str, *, today: str | None = None) -> list[dict]:
    """Every approved learning, across every memory file, that is not yet live and could go
    live at the next signature, whatever wrote it: within its horizon, not struck or retired,
    and `standing` unlisted or unsigned. Each as `{id, title, persona, approved_by, addresses}`.
    Raises StoreError on a memory file that cannot be read: a listing that skipped it would
    let its learnings go live unlisted."""
    root = Path(root)
    today = today or sdlc_md.now_date()
    days = validity_days(root)
    out, records = [], {}
    for entries in all_stores(root).values():
        for e in entries:
            f = e["fields"]
            if state_of(e) != "approved" or f.get("retired"):
                continue
            horizon = lessons.horizon_of(e, days)
            if horizon is None or horizon < today:
                continue
            if standing(root, e, records) in ("unlisted", "unsigned"):
                out.append({"id": e["id"], "title": e["title"], "persona": f.get("persona", ""),
                            "approved_by": f.get("approved-by", ""),
                            "addresses": f.get("addresses", "")})
    return sorted(out, key=lambda r: sdlc_md.id_number(r["id"]) or 0)


def mark_listed(root: Path | str, ids, run_id: str) -> list[str]:
    """Stamp Listed-in `run_id` on each of `ids` that does not already carry it, through
    `set_field`. Returns the repo-relative memory files written."""
    root = Path(root)
    wanted = set(ids)
    written: list[str] = []
    for path, entries in all_stores(root).items():
        for e in entries:
            if e["id"] in wanted and e["fields"].get("listed-in", "").strip() != run_id:
                set_field(root, e["id"], "Listed-in", run_id)
                rel = path.relative_to(root).as_posix()
                if rel not in written:
                    written.append(rel)
    return written


def strike_refusals(root: Path | str, run_id: str, listed, ids, reason: str = "",
                    principal: str = "") -> list[str]:
    """Why `ids` cannot be struck at `run_id`'s signature: an id no memory file holds, or one
    this run's close did not list, one line per id; and a `reason` (as `strike` is given it,
    stripped) or `principal` holding a line break, which `strike` would refuse only at its
    write, after the signature has sealed the run. Writes nothing; [] when every id may be
    struck. Raises StoreError on a memory file that cannot be read."""
    held = {e["id"]: e for entries in all_stores(root).values() for e in entries}
    out = [f"{', '.join(ids)}: the {name} holds a line break, and a learning's field is one "
           f"line, so a second line would read back as another field"
           for name, value in (("reason", (reason or "").strip()), ("principal", principal or ""))
           if "".join(value.splitlines()) != value]
    for i in ids:
        if i not in held:
            out.append(f"{i}: no memory file holds it")
        elif i not in set(listed or ()):
            other = held[i]["fields"].get("listed-in", "").strip()
            out.append(f"{i}: listed by {other}, not by {run_id}" if other and other != run_id
                       else f"{i}: {run_id}'s close did not list it")
    return out


def strike(root: Path | str, entry_id: str, principal: str, date: str, reason: str) -> dict:
    """Record the operator's strike on `entry_id`: who struck it, when and why."""
    return set_field(root, entry_id, "Struck", f"{principal} on {date}: {reason}")


# ----------------------------------------------------------------------------- the seat's learning

#: Where a seat writes its learning before `propose` records it: scratch, never committed.
LEARNING_REL = "sdlc-studio/.local/persona-learning"
_ROUND_KEY_RE = re.compile(r"^round:(\S+?)r(\d+)$")
#: The words an adverse item is told by, in the order a record's item is searched for them.
_ITEM_WORDS = ("finding", "basis", "reason", "title", "summary")


def seats_report(root: Path | str, retro_id: str) -> dict:
    """What `retro.py seats --id <retro> --format json` prints: the retro's id and the seat
    record over its batch and window, read through retro's own functions, never re-derived."""
    import retro  # noqa: PLC0415 - sibling; only the learning verbs pay for the ledger read
    path = retro.find_retro(root, retro_id)
    if path is None:
        raise MemoryRefusal(f"retro {retro_id} not found")
    rid = path.name.split("-", 1)[0]
    units = retro.batch_ids(sdlc_md.read_text_safe(path))
    if not units:
        raise MemoryRefusal(f"retro {rid} names no units in '> **Batch:**', so no seat has a "
                            f"record in it")
    return {"id": rid, **retro.seat_record(root, path, units)}


def _item_key(item) -> str:
    """An adverse item's key: the one it carries, else `bug:<id>` for a later bug charged to
    the seat (the record names the bug, not a key); "" for anything else."""
    if not isinstance(item, dict):
        return ""
    return str(item.get("key") or (f"bug:{item['bug']}" if item.get("bug") else ""))


def adverse_items(record: dict | None) -> list[dict]:
    """A seat's adverse items, each `{key, text}`: every item its record lists outside its own
    verdicts that carries a key or names a bug (a defect found after its approval, a later bug
    it missed or approved over its own finding), then each round of a unit it built that a
    blocking finding stopped. Keys are unique; the first item to carry one is kept."""
    items: dict[str, str] = {}
    for name, value in (record or {}).items():
        if name == "verdicts" or not isinstance(value, list):
            continue
        for item in value:
            key = _item_key(item)
            if not key:
                continue
            words = next((str(item[w]) for w in _ITEM_WORDS if item.get(w)), "")
            if name == "found_after_approval":
                words = (f"found only after your round {item.get('approved_round')} approval "
                         f"of {item.get('unit')}: {words}")
            elif item.get("bug"):
                words = (f"{name.replace('_', ' ')} {item['bug']} after your "
                         f"{item.get('approved', '')} approval of {item.get('unit')}: {words}")
            items.setdefault(key, words or name.replace("_", " "))
    for built in (record or {}).get("built") or []:
        for r in built.get("rounds_detail") or []:
            if r.get("blocking"):
                items.setdefault(f"round:{built['unit']}r{r['round']}",
                                 f"round {r['round']} of {built['unit']}, which you built, "
                                 f"blocked: {'; '.join(r['blocking'])}")
    return [{"key": k, "text": t} for k, t in items.items()]


def own_record(report: dict, key: str) -> dict | None:
    """`key`'s record in a seats report, or None when it holds no verdict, no unit built and
    no adverse item: a seat with nothing on record has nothing to learn from."""
    record = (report.get("seats") or {}).get(key)
    if not record or not (record.get("verdicts") or record.get("built")
                          or adverse_items(record)):
        return None
    return record


def _key_id(key: str) -> str:
    """The id an adverse item's key names, in the form `resolves` reads: `round:US0001r2` is
    the verdict reference `US0001 r2`, `bug:BG0002` the artefact `BG0002`."""
    m = _ROUND_KEY_RE.match(key)
    return f"{m.group(1)} r{m.group(2)}" if m else key.split(":", 1)[-1]


def record_ids(record: dict) -> list[str]:
    """The ids a seat's record lists, in order and once each: its verdicts as `<unit>
    r<round>`, the units it built, then its adverse items' ids. A proposal's evidence."""
    ids = [f"{v['unit']} r{v['round']}" for v in record.get("verdicts") or []]
    ids += [b["unit"] for b in record.get("built") or []]
    ids += [_key_id(i["key"]) for i in adverse_items(record)]
    return list(dict.fromkeys(ids))


def learning_file(retro_id: str, key: str) -> str:
    """The repo-relative file a seat writes its learning for `retro_id` to."""
    return f"{LEARNING_REL}/{retro_id}-{key}.md"


def _record_of(root: Path, key: str, retro_id: str) -> tuple[str, str, dict]:
    key = resolve_key(root, key)
    report = seats_report(root, retro_id)
    record = own_record(report, key)
    if record is None:
        raise MemoryRefusal(f"{key} has no record in {report['id']}: no verdict, no unit built "
                            f"and no adverse item, so there is nothing to learn from")
    return key, report["id"], record


def learn_brief(root: Path | str, key: str, retro_id: str) -> str:
    """The brief a seat writes its learning from: its own record and adverse items, what a
    learning may not change, the file to write and the command that records it, then its card
    framed with its live learnings. No other seat's record is read into it."""
    root = Path(root)
    key, rid, record = _record_of(root, key, retro_id)
    try:
        card = persona_resolve.resolve_card(root, key, render="review")
    except persona_resolve.RenderError as exc:
        raise MemoryRefusal(str(exc))
    target = learning_file(rid, key)
    lines = [f"--- LEARNING BRIEF: {key}, {rid} ---",
             f"You are the {key} seat, looking back on {rid}. Your record below is read from the "
             f"review ledger by `retro.py seats`, not from your own account. Write, in your own "
             f"words, what you will do differently, and cite by key the adverse items it answers.",
             "",
             f"--- RECORD: {key} in {rid} (`retro.py seats --id {rid} --format json`, this seat "
             f"only) ---",
             "```json", json.dumps({"id": rid, "seat": key, **record}, indent=2), "```", "",
             "Adverse items (cite each by its key; another seat approves the learning against "
             "them):"]
    lines += ([f"  [{i['key']}] {i['text']}" for i in adverse_items(record)] or
              ["  none: the record holds no adverse item, so a learning keeps a habit that held"])
    lines += ["", "--- WHAT A LEARNING MAY NOT DO ---",
              f"A learning cannot change the {key} card's Non-Negotiables or its Authority: it "
              f"shapes how the seat works within them, and the approving seat rejects one that "
              f"contradicts or loosens either.",
              "", "--- WRITE IT ---",
              f"Write the learning to {target}: its first line is the title and the whole file "
              f"is the body, kept as written. Then record it as proposed:",
              f"  persona_memory.py propose --persona {key} --retro {rid} --from-file {target}",
              "Its evidence is the ids your record lists, never the ids your text names."]
    return "\n".join(lines) + persona_resolve.frame(card, key, "review", root=root)


def _first_line_title(text: str, limit: int = 80) -> str:
    line = next((ln for ln in text.splitlines() if ln.strip()), "")
    line = re.sub(r"^\s*(?:#+|[-*])\s*", "", line).strip()
    return line if len(line) <= limit else line[:limit - 1].rstrip() + lessons.ELLIPSIS


#: A retro's own `> **Run:** RUN-...` line, which `sprint close` fills with the run it closes.
_RETRO_RUN_LINE_RE = re.compile(r"(?m)^>?\s*\*\*Run:\*\*\s*(\S*)")


def proposal_run(root: Path | str, retro_id: str, supplied: str | None = None) -> str:
    """The run a learning from `retro_id` looks back on: the run the retro's own Run line
    names, else `supplied`, else the open run, else the retro id. Refuses a `supplied` that is
    not a run id, and one naming another run than the retro's line does."""
    import retro  # noqa: PLC0415 - sibling; the one reader of the run a retro's close names
    supplied = None if supplied is None else supplied.strip()
    if supplied is not None and not _RUN_RE.match(supplied):
        raise MemoryRefusal(f"--run {supplied!r} is not a run id (RUN-<id>)")
    path = retro.find_retro(root, retro_id)
    line = _RETRO_RUN_LINE_RE.search(sdlc_md.read_text_safe(path) if path else "")
    named = line.group(1) if line and _RUN_RE.match(line.group(1)) else ""
    if named and supplied and supplied != named:
        raise MemoryRefusal(f"--run {supplied} is not the run {retro_id} names {named} on its "
                            f"Run line, which a learning from it looks back on")
    try:
        return named or retro.extract_run(root, supplied, retro_id)
    except run_state.RunStateError as exc:
        raise MemoryRefusal(str(exc))


def propose(root: Path | str, key: str, retro_id: str, text: str, title: str | None = None,
            run: str | None = None) -> dict:
    """Record a seat's learning, `text` as written less its outer blank space, as proposed
    for the retro's run (`proposal_run`), with the ids its record lists as evidence and the
    title `title` or the text's first line. Refuses, writing nothing: a seat with no record in
    the retro, and a second proposal while that seat's first from the same retro is still
    proposed. The check is keyed on the Retro field, since a retro is one run's and the Run a
    proposal is stamped with can differ while that run is open and after it closes."""
    root = Path(root)
    key, rid, record = _record_of(root, key, retro_id)
    run = proposal_run(root, rid, run)
    open_ = [e["id"] for e in read_store(memory_path(root, key))
             if state_of(e) == "proposed" and e["fields"].get("retro", "").strip() == rid]
    if open_:
        raise MemoryRefusal(f"{open_[0]} is still proposed for {key} from {rid}: a seat holds "
                            f"one open proposal per retro, its run's, so approve or reject it "
                            f"first")
    return add(root, key, title or _first_line_title(text), text, record_ids(record),
               extra={"Run": run, "Retro": rid})


# ----------------------------------------------------------------------------- approval

#: The subject card's sections an approver checks a learning against.
GUARDED_SECTIONS = ("Non-Negotiables", "Authority")
NONE_ADDRESSED = "none"


def _proposed(root: Path, entry_id: str) -> dict:
    """The entry `entry_id`, refused unless some memory file holds it and it is proposed."""
    try:
        stores = all_stores(root)
    except StoreError as exc:
        raise MemoryRefusal(str(exc))
    entry = next((e for entries in stores.values() for e in entries if e["id"] == entry_id),
                 None)
    if entry is None:
        raise MemoryRefusal(f"no memory file holds {entry_id}")
    if state_of(entry) != "proposed":
        raise MemoryRefusal(f"{entry_id} is {state_of(entry)}, not proposed: only a proposed "
                            f"learning is approved or rejected")
    return entry


def _other_seat(root: Path, entry: dict, role: str) -> None:
    """Refuse `role` unless a seat card declares it and it is not the learning's own seat.
    Judged by the recorded seat, never by name: a second holder of the card is the same seat."""
    if role not in persona_resolve.seat_roster(root):
        raise MemoryRefusal(f"no seat card declares {role}, so it cannot approve a learning")
    subject = entry["fields"].get("persona", "").strip()
    if role == subject:
        raise MemoryRefusal(f"{entry['id']} is {subject}'s learning and a seat never approves "
                            f"its own learning, whoever holds it: brief another seat")


def subject_items(root: Path | str, entry: dict) -> list[dict]:
    """The adverse items the learning's own seat record lists in the retro it was proposed
    from, each `{key, text}`; [] for an entry no retro stamped."""
    retro_id = entry["fields"].get("retro", "").strip()
    if not retro_id:
        return []
    report = seats_report(root, retro_id)
    return adverse_items((report.get("seats") or {}).get(entry["fields"].get("persona", "")))


def approve(root: Path | str, entry_id: str, reviewer: str, addresses: list[str] | None,
            reason: str | None = None, reject: bool = False) -> dict:
    """Record another seat's decision on a proposed learning and return the entry.

    An approval writes State approved, Approved-by, Decided and Addresses: the adverse items
    of the subject's record it addresses, or `none` with a Reason. A rejection writes State
    rejected, Rejected-by, Decided and its Reason. Refuses, writing nothing: an entry not
    proposed, a reviewer naming no `(<role>)` group or a role no card declares, the
    learning's own seat, an addressed item the record does not list, no `--addresses`, and
    `none` or a rejection with no reason."""
    import critic  # noqa: PLC0415 - sibling; the one reader of a recorded seat
    root = Path(root)
    entry = _proposed(root, entry_id)
    role = critic.recorded_seat(reviewer)
    if role is None:
        raise MemoryRefusal(f"--reviewer {reviewer!r} names no `(<role>)` group, so its seat "
                            f"cannot be told")
    _other_seat(root, entry, role)
    reason = (reason or "").strip()
    decided = [("Decided", sdlc_md.now_date())]
    if reject:
        if not reason:
            raise MemoryRefusal("a rejection needs --reason: what the learning dodges or loosens")
        return set_fields(root, entry_id, [("State", "rejected"), ("Rejected-by", reviewer),
                                           *decided, ("Reason", reason)])
    listed = [i["key"] for i in subject_items(root, entry)]
    named = ", ".join(listed) if listed else "none listed"
    keys = list(dict.fromkeys(evidence_tokens(addresses)))
    if keys == [NONE_ADDRESSED]:
        if not reason:
            raise MemoryRefusal(f"--addresses none needs --reason saying why the learning "
                                f"engages none of the record's adverse items ({named})")
    elif not keys or any(k not in listed for k in keys):
        wrong = [k for k in keys if k not in listed]
        said = (f"--addresses {', '.join(wrong)} is not" if wrong
                else "an approval names with --addresses")
        raise MemoryRefusal(f"{said} an adverse item {entry['fields'].get('persona')}'s record "
                            f"lists: {named}; or pass --addresses none with --reason")
    pairs = [("State", "approved"), ("Approved-by", reviewer), *decided,
             ("Addresses", ", ".join(keys))]
    return set_fields(root, entry_id, pairs + ([("Reason", reason)] if reason else []))


def _card_section(text: str, name: str) -> str:
    """The `## <name>...` section of a card, heading included, up to the next heading of the
    same or a higher level; "" when the card has none."""
    lines, out, level = text.splitlines(), [], 0
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if level and m and len(m.group(1)) <= level:
            break
        if not level and m and m.group(2).strip().startswith(name):
            level = len(m.group(1))
        if level:
            out.append(line)
    return "\n".join(out).strip()


def _subject_card(root: Path, key: str) -> Path | None:
    if key in persona_resolve.seat_roster(root):
        return persona_resolve.resolve_card(root, key, render="review")
    card = root / PERSONAS_REL / f"{key}.md"
    return card if card.is_file() else None


def approve_brief(root: Path | str, entry_id: str, seat: str) -> str:
    """The brief another seat approves or rejects a proposed learning from: the learning
    verbatim, the subject's adverse items with their keys, the subject card's Non-Negotiables
    and Authority, the question whether the learning contradicts or loosens them, the commands
    that record the decision, then the approving seat's card. Refuses the learning's own seat."""
    import critic  # noqa: PLC0415 - sibling; the one source of a seat's signature
    root = Path(root)
    entry = _proposed(root, entry_id)
    _other_seat(root, entry, seat)
    subject = entry["fields"].get("persona", "").strip()
    try:
        card = _subject_card(root, subject)
        mine = persona_resolve.resolve_card(root, seat, render="review")
    except persona_resolve.RenderError as exc:
        raise MemoryRefusal(str(exc))
    text = card.read_text(encoding="utf-8") if card else ""
    items = subject_items(root, entry)
    sig = critic.seat_signature(root, seat)
    head = f'persona_memory.py approve --id {entry_id} --reviewer "{sig}"'
    retro_id = entry["fields"].get("retro", "") or "no retro"
    lines = [f"--- APPROVAL BRIEF: {entry_id}, {subject}'s learning "
             f"(proposed for {entry['fields'].get('run', '') or 'no run'}) ---",
             f"You are the {seat} seat. Approve or reject {subject}'s learning against the "
             f"record it answers and the card it must not drift from; a seat never approves "
             f"its own learning.", "",
             f"--- THE LEARNING, VERBATIM: {entry['title']} ---", prose_of(entry), "",
             f"--- {subject.upper()}'S ADVERSE ITEMS ({retro_id}, from `retro.py seats`) ---"]
    lines += ([f"  [{i['key']}] {i['text']}" for i in items] or
              ["  none: the record lists no adverse item"])
    lines += ["", f"--- {subject.upper()}'S CARD: Non-Negotiables and Authority ---"]
    for name in GUARDED_SECTIONS:
        lines += [_card_section(text, name) or f"(the card has no {name} section)", ""]
    lines += ["--- THE QUESTION ---",
              f"Does the learning contradict or loosen any line of {subject}'s Non-Negotiables "
              f"or Authority above? If it does, reject it. If not, name the adverse items it "
              f"addresses, or say why it addresses none.", "",
              "--- RECORD THE DECISION ---",
              f"  {head} --addresses <key>[,<key>]",
              f'  {head} --addresses none --reason "..."',
              f'  {head} --reject --reason "..."']
    return "\n".join(lines) + persona_resolve.frame(mine, seat, "review", root=root)


# ----------------------------------------------------------------------------- CLI


def _prose(fields_file: str | None, flags: dict, required: tuple[str, ...] = ()) -> dict:
    """The prose fields from `--fields-file` and the flags, a flag overriding its key, through
    file_finding's one shared loader, so text quoting a command is stored as written, not as a
    shell ate it. Each caller reads its flags by name, so the dead-flag audit can judge every
    one. Raises ValueError when a required field is in neither."""
    import file_finding  # noqa: PLC0415 - the shared prose-fields loader, as lessons uses it
    fields = file_finding.resolve_prose_fields(fields_file, flags, allowed=tuple(flags))
    missing = [k for k in required if not file_finding.prose_value(fields, k)]
    if missing:
        raise ValueError(f"no {'/'.join(missing)} - pass --{missing[0]}, or a "
                         f"\"{missing[0]}\" key in the --fields-file document")
    return fields


def cmd_add(args: argparse.Namespace) -> int:
    try:
        prose = _prose(args.fields_file, {"title": args.title, "body": args.body},
                       required=("title", "body"))
        new = add(args.root, args.persona, prose.get("title"), prose.get("body"), args.evidence)
    except ValueError as exc:  # a refusal, an unreadable store or a bad --fields-file
        print(f"error: {exc}; nothing was written", file=sys.stderr)
        return 2
    print(f"{new['id']} added to {MEMORY_REL}/{new['fields']['persona']}.md "
          f"(proposed, review by {new['fields']['review-by']})")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    try:
        rows = list_entries(args.root, args.persona, args.query)
    except (MemoryRefusal, StoreError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps({"persona": args.persona, "query": args.query, "learnings": rows},
                         indent=2))
        return 0
    if not rows:
        print(f"{args.persona}: no learnings{' match ' + repr(args.query) if args.query else ''}")
        return 0
    for r in rows:
        print(f"{r['id']}  {r['state']:<9} review by {r['horizon'] or 'unknown'}  {r['title']}"
              + (f"  (struck: {r['struck']})" if r["struck"] else ""))
    return 0


def cmd_learn_brief(args: argparse.Namespace) -> int:
    try:
        print(learn_brief(args.root, args.persona, args.retro))
    except (MemoryRefusal, StoreError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_propose(args: argparse.Namespace) -> int:
    path = Path(args.from_file)
    path = path if path.is_absolute() else Path(args.root) / path
    try:
        title = _prose(args.fields_file, {"title": args.title}).get("title")
        text = path.read_text(encoding="utf-8")
        new = propose(args.root, args.persona, args.retro, text, title, args.run)
    except (OSError, ValueError) as exc:  # a refusal, an unreadable file or store
        print(f"error: {exc}; nothing was written", file=sys.stderr)
        return 2
    f = new["fields"]
    print(f"{new['id']} proposed in {MEMORY_REL}/{f['persona']}.md for {f['run']} "
          f"(evidence {f['evidence']}); another seat approves it with `approve-brief`")
    return 0


def cmd_approve_brief(args: argparse.Namespace) -> int:
    try:
        print(approve_brief(args.root, args.id, args.seat))
    except (MemoryRefusal, StoreError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    try:
        reason = _prose(args.fields_file, {"reason": args.reason}).get("reason")
        e = approve(args.root, args.id, args.reviewer, args.addresses, reason, args.reject)
    except ValueError as exc:  # a refusal, an unreadable store or a bad --fields-file
        print(f"error: {exc}; nothing was written", file=sys.stderr)
        return 2
    f = e["fields"]
    what = (f"rejected by {f['rejected-by']}" if f["state"] == "rejected"
            else f"approved by {f['approved-by']}, addressing {f['addresses']}")
    print(f"{e['id']} {what} ({f['decided']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """The parser, module-level so the surface can be enumerated without running it."""
    parser = argparse.ArgumentParser(
        description="Keep each persona's evidenced learnings in sdlc-studio/personas/memory/.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="Record a proposed learning for a persona, with evidence.")
    a.add_argument("--persona", required=True,
                   help="a seat's declared role (qa) or a persona card's stem")
    a.add_argument("--title", help="the learning in one line (or a \"title\" key in --fields-file)")
    a.add_argument("--body", help="the learning in full (or a \"body\" key in --fields-file)")
    a.add_argument("--fields-file", dest="fields_file", metavar="FIELDS.json",
                   help="read the title and body from a JSON object ({\"title\": ..., "
                        "\"body\": ...}) instead of the flags, so text carrying shell "
                        "metacharacters is stored verbatim; `-` reads it from stdin. A flag "
                        "still overrides its key")
    a.add_argument("--evidence", action="append", default=[], metavar="ID",
                   help="an artefact id, a decision, a run, or `<unit> r<round>`. Repeatable")
    a.add_argument("--root", default=".", help="project root")
    a.set_defaults(func=cmd_add)
    for verb, helptext in (("list", "List one persona's learnings, each with state and horizon."),
                           ("recall", "Find one persona's learnings that mention a query.")):
        sp = sub.add_parser(verb, help=helptext)
        sp.add_argument("--persona", required=True, help="a seat role or a persona card's stem")
        sp.add_argument("--query", required=verb == "recall", default=None,
                        help="match the title or body, case-insensitive")
        sp.add_argument("--root", default=".", help="project root")
        sdlc_md.add_format_arg(sp)
        sp.set_defaults(func=cmd_list)
    lb = sub.add_parser("learn-brief", help="Brief a seat to write its learning from its own "
                                            "record in a retro.")
    lb.add_argument("--persona", required=True, help="the seat's declared role (qa)")
    lb.add_argument("--retro", required=True, metavar="RETROxxxx",
                    help="the retro whose seat record the brief carries")
    lb.add_argument("--root", default=".", help="project root")
    lb.set_defaults(func=cmd_learn_brief)
    pr = sub.add_parser("propose", help="Record the learning a seat wrote, verbatim, as "
                                        "proposed, with its record's ids as evidence.")
    pr.add_argument("--persona", required=True, help="the seat's declared role (qa)")
    pr.add_argument("--retro", required=True, metavar="RETROxxxx",
                    help="the retro whose seat record supplies the evidence")
    pr.add_argument("--from-file", dest="from_file", required=True, metavar="PATH",
                    help="the file the seat wrote, stored as the body as written, less its "
                         "outer blank space; a relative path is read from the project root")
    pr.add_argument("--title", help="the heading (default: the file's first line)")
    pr.add_argument("--fields-file", dest="fields_file", metavar="FIELDS.json",
                    help="read the title from a JSON object ({\"title\": ...}) so text carrying "
                         "shell metacharacters is stored verbatim; `-` reads it from stdin")
    pr.add_argument("--run", default=None,
                    help="the run it looks back on, a RUN- id (default: the run the retro's "
                         "Run line names, else the open run, else the retro)")
    pr.add_argument("--root", default=".", help="project root")
    pr.set_defaults(func=cmd_propose)
    ab = sub.add_parser("approve-brief", help="Brief another seat to approve or reject a "
                                              "proposed learning.")
    ab.add_argument("--id", required=True, metavar="M-NNNN", help="the proposed learning")
    ab.add_argument("--seat", required=True, help="the approving seat's role (product)")
    ab.add_argument("--root", default=".", help="project root")
    ab.set_defaults(func=cmd_approve_brief)
    ap = sub.add_parser("approve", help="Record another seat's approval or rejection of a "
                                        "proposed learning.")
    ap.add_argument("--id", required=True, metavar="M-NNNN", help="the proposed learning")
    ap.add_argument("--reviewer", required=True,
                    help="the approving seat, as `<holder> (<role>)`")
    ap.add_argument("--addresses", action="append", default=[], metavar="KEY",
                    help="an adverse item's key the learning addresses (round:US0001r2), or "
                         "`none` with --reason. Repeatable or comma-separated")
    ap.add_argument("--reject", action="store_true", help="reject it; needs --reason")
    ap.add_argument("--reason", help="why: required to reject or with --addresses none")
    ap.add_argument("--fields-file", dest="fields_file", metavar="FIELDS.json",
                    help="read the reason from a JSON object ({\"reason\": ...}) so text "
                         "carrying shell metacharacters is stored verbatim; `-` reads stdin")
    ap.add_argument("--root", default=".", help="project root")
    ap.set_defaults(func=cmd_approve)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root once and write it back, so every verb anchors on the run's tree.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
