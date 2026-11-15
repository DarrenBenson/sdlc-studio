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

The brief side is `digest` and `render`: a persona's live learnings (approved and within their
horizon), ranked so one whose evidence shares the unit's files comes first, capped at
`personas.memory.inject_max` (default 5), each carried as its id, title and a short gist. A
store that cannot be read is reported as unreadable, never as a store with nothing in it.
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
from lib import sdlc_md  # noqa: E402

MEMORY_REL = "sdlc-studio/personas/memory"
PERSONAS_REL = "sdlc-studio/personas"
TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "personas" / "memory-template.md"
ENTRY_RE = re.compile(r"^##\s+(M-\d{4}):\s*(.+?)\s*$")
ID_RE = re.compile(r"^M-\d{4}$")
#: Every state an entry can hold. Only `add` writes proposed; approval and revalidation
#: move the rest, and observed records usage evidence.
STATES = ("proposed", "approved", "rejected", "retired", "observed")
#: Every field an entry may carry, in the order `add` stamps the first five. The rest are
#: written later through `set_field`: who approved it, what it addresses, the close that
#: listed it, a strike, a retirement.
FIELDS = ("Persona", "Evidence", "Added", "Review-by", "State",
          "Approved-by", "Addresses", "Listed-in", "Struck", "Retired")
VALIDITY_DAYS_KEY = "personas.memory.validity_days"
INJECT_MAX_KEY = "personas.memory.inject_max"
DEFAULT_INJECT_MAX = 5
GIST_MAX = 200
_DECISION_RE = re.compile(r"^D\d{4}$")
_RUN_RE = re.compile(r"^RUN-[0-9A-Z]+$")
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
    new id allocated without it could collide with one it holds."""
    mdir = Path(root) / MEMORY_REL
    return {p: read_store(p) for p in sorted(mdir.glob("*.md"))} if mdir.is_dir() else {}


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
    rdir = root / "sdlc-studio" / "reports"
    return rdir.is_dir() and any(run_id.lower() in p.read_text(encoding="utf-8", errors="replace")
                                 .lower() for p in rdir.glob("*.md"))


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


def add(root: Path | str, key: str, title: str, body: str, evidence: list[str]) -> dict:
    """Write one proposed learning for `key` and return it. Refuses, writing nothing: no
    evidence, any cited id that resolves to nothing, an unknown or ambiguous key, a blank
    title or body, and a memory directory git would never hold."""
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
    path = memory_path(root, key)
    rel = path.relative_to(root).as_posix()
    held = lessons.ignored_reason(root, rel)
    if held:
        raise MemoryRefusal(held)
    try:
        stores = all_stores(root)
    except StoreError as exc:
        raise MemoryRefusal(f"a memory file cannot be read, so a new id could collide: {exc}")
    today = sdlc_md.now_date()
    new = {"id": next_id(stores),
           "title": lessons.heading_title(title), "fields": {}, "body": body.strip()}
    for name, value in (("Persona", key), ("Evidence", ", ".join(cited)), ("Added", today),
                        ("Review-by", lessons.add_days(today, validity_days(root))),
                        ("State", "proposed")):
        lessons.upsert_field(new, name, value)
    if path.exists():
        text = path.read_text(encoding="utf-8")
        header = lessons.project_header_of(text, entry_re=ENTRY_RE)
        entries = stores.get(path, [])
    else:
        header, entries = _new_header(key), []
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, _render_file(header, [*entries, new]))
    return new


def set_field(root: Path | str, entry_id: str, name: str, value: str) -> dict:
    """Set one field on the entry `entry_id`, wherever it lives, through
    `lessons.upsert_field`, and rewrite its file. Refuses a field outside FIELDS, a State
    outside STATES and an id no memory file holds."""
    canonical = next((f for f in FIELDS if f.lower() == (name or "").strip().lower()), None)
    if canonical is None:
        raise MemoryRefusal(f"{name!r} is not a memory field ({', '.join(FIELDS)})")
    if canonical == "State" and value.strip().lower() not in STATES:
        raise MemoryRefusal(f"State {value!r} is not one of {', '.join(STATES)}")
    try:
        stores = all_stores(root)
    except StoreError as exc:
        raise MemoryRefusal(str(exc))
    for path, entries in stores.items():
        for e in entries:
            if e["id"] == entry_id:
                lessons.upsert_field(e, canonical, value)
                header = lessons.project_header_of(path.read_text(encoding="utf-8"),
                                                   entry_re=ENTRY_RE)
                sdlc_md.atomic_write(path, _render_file(header, entries))
                return e
    raise MemoryRefusal(f"no memory file holds {entry_id}")


# ----------------------------------------------------------------------------- listing


def _row(entry: dict, days: int) -> dict:
    f = entry["fields"]
    return {"id": entry["id"], "title": entry["title"], "persona": f.get("persona", ""),
            "state": state_of(entry), "horizon": lessons.horizon_of(entry, days),
            "evidence": f.get("evidence", ""), "added": f.get("added", ""),
            "body": prose_of(entry)}


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
    """What a brief carries for `key`: its live learnings (State approved, Review-by not yet
    passed), ranked by relevance to `affects` and then recency, capped at `inject_max`.

    Returns `{persona, path, learnings, live, withheld, expired, cap, absent, error}`. Only the
    persona's own file is read. A file that cannot be parsed sets `error`, never reads as
    empty; a missing file sets `absent`."""
    root = Path(root)
    path = memory_path(root, key)
    rel = path.relative_to(root).as_posix()
    cap = inject_max(root)
    out = {"persona": key, "path": rel, "learnings": [], "live": 0, "withheld": 0,
           "expired": 0, "cap": cap, "absent": not path.exists(), "error": ""}
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
    live = []
    for e in entries:
        if state_of(e) != "approved":
            continue
        horizon = lessons.horizon_of(e, days)
        if horizon is None or horizon < today:
            out["expired"] += 1
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
    return lines


def brief_block(root: Path | str, key: str, render_name: str, affects=()) -> str:
    """The learnings block a brief or a framing appends for `key`."""
    return "\n".join(render(digest(root, key, affects), render_name))


# ----------------------------------------------------------------------------- CLI


def cmd_add(args: argparse.Namespace) -> int:
    try:
        # The title and body through the one shared prose loader (file_finding's, by way of
        # lessons), so a learning quoting a command is stored as written, not as a shell ate it.
        lessons.resolve_prose(args, ("title", "body"), required=("title", "body"))
        new = add(args.root, args.persona, args.title, args.body, args.evidence)
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
        print(f"{r['id']}  {r['state']:<9} review by {r['horizon'] or 'unknown'}  {r['title']}")
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
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root once and write it back, so every verb anchors on the run's tree.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
