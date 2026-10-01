#!/usr/bin/env python3
"""migrate - one command that reviews every artefact and upgrades where it safely can.

`project upgrade` refreshes conventions and the version; `migrate_v3 sizing` converts a
container's legacy Effort/Points to a T-shirt Size; `reconcile` finds an accepted item that was
never decomposed. Each is sound on its own, but an operator upgrading a project had to know to run
all three and read three reports. `migrate` is the ORCHESTRATOR: it runs the
existing pieces in order, adds the artefact-review sweep, and emits ONE report split into what it
upgraded DETERMINISTICALLY and what NEEDS A HUMAN.

The honesty rule (the estimator finding): it auto-applies only the deterministic, reversible set -
the version stamp, the config scaffold, a container's sizing conversion, and the removal of a
retired Definition of Done tag or `.config.yaml` key, line by line so every other byte stays. It never GUESSES a
judgement: a request's breakdown (`refine`), an Issue's triage (`triage`), a delivery unit's
re-size (there is no honest Effort->Points map) are REPORTED with the exact command, never done for
you. An AGENTS.md or CLAUDE.md line naming a retired key or verb is reported, never rewritten,
so is the `conformance.adopt_after` cutoff that would grandfather the units the conformance lane
fails, and the frozen review ledgers are reported as history and left as written. Dry-run by
default; `--apply` writes only the deterministic set.

Skill/consuming-project tool: it operates on the `sdlc-studio/` workspace under the root. Reuses
`project_upgrade`, `migrate_v3` and `reconcile`; pure stdlib.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import critic  # noqa: E402
import project_upgrade  # noqa: E402
import migrate_v3  # noqa: E402

# Each needs-human bucket, its human label, and how to render the command that resolves it. The
# artefact-review sweep (US0155): every open item that cannot be upgraded deterministically is named
# here with the CEREMONY that turns it into current-shape work - never guessed.
_HUMAN = {
    "needs_refine": ("a request accepted but never decomposed",
                     lambda x: f"refine apply --request {x['id']} --epic-title \"...\" --story \"title|points\" ..."),
    "needs_triage": ("an Issue accepted but never triaged",
                     lambda x: f"triage apply --issue {x['id']} --bug \"title|points|severity\" ..."),
    "needs_resize": ("a delivery unit sized in legacy Effort (no honest Effort->Points map)",
                     lambda x: f"re-size {x['id']}: set its `Points` on the Fibonacci scale by judgement"),
    "needs_manual": ("convertible but malformed (no Status line to anchor a Size)",
                     lambda x: f"fix {x['id']}'s metadata (add a `> **Status:**` line), then re-run"),
}
_HUMAN_ORDER = ("needs_refine", "needs_triage", "needs_resize", "needs_manual")

#: The review ledgers nothing writes any more. History: reported, never edited.
FROZEN_LEDGERS = ("plan-review-verdicts.md", "signoff-record.md", "repair-record.md",
                  "critic-evidence.md", "sprint-review-record.md", "plan-rulings.md")
#: The two a historical licence still reads by date, and what a row dated on or after
#: `critic.REPAIR_VERB_RETIRED` no longer does.
_DATED_LEDGERS = {"repair-record.md": "no longer answer a REJECT",
                  "sprint-review-record.md": "no longer cover a unit"}
_TAG_RE = re.compile(r"[ \t]*" + sdlc_md.CHECK_TAG_RE.pattern)
_KEY_RE = re.compile(r"( *)([A-Za-z_][\w.-]*)[ \t]*:(?=\s|$)(.*)")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _read_raw(path: Path) -> str | None:
    """A file's text with its line endings as written (a universal-newline read would turn a
    CRLF file LF on the way back), or None when it is absent or unreadable."""
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()
    except (OSError, ValueError):
        return None


def _retired_tags(root: Path) -> tuple[list[dict], dict[Path, str]]:
    """Every retired `[check: <id>]` tag in the DoR/DoD, and each file's text without them. The
    criterion stays as a human-judged item; a line that held only the tag goes with it. The ids
    are `sdlc_md.RETIRED_CHECK_IDS`, read at call time."""
    found: list[dict] = []
    rewrites: dict[Path, str] = {}
    retired = sdlc_md.RETIRED_CHECK_IDS
    for name in ("definition-of-ready.md", "definition-of-done.md"):
        path = root / "sdlc-studio" / name
        text = _read_raw(path)
        out: list[str] = []
        for n, line in enumerate((text or "").splitlines(keepends=True), 1):
            ids = [m.group(1) for m in _TAG_RE.finditer(line) if m.group(1) in retired]
            if not ids:
                out.append(line)
                continue
            kept = _TAG_RE.sub(lambda m: "" if m.group(1) in retired else m.group(0), line)
            if kept.strip():
                out.append(kept)
            found += [{"source": "dod", "kind": "retired-check-tag", "file": name, "line": n,
                       "id": cid, "detail": f"{name}:{n}: [check: {cid}] removed, the criterion "
                                           f"kept as human-judged - {retired[cid]}"}
                      for cid in ids]
        if any(f["file"] == name for f in found):
            rewrites[path] = "".join(out)
    return found, rewrites


def _block_end(lines: list[str], i: int, indent: int) -> int:
    """The last line of the block the key at `i` opens: its deeper-indented children, or a list
    at its own indent. Comments and blank lines after the last child belong to what follows."""
    last = i
    for j in range(i + 1, len(lines)):
        body = lines[j].strip()
        if not body or body.startswith("#"):
            continue
        lead = len(lines[j]) - len(lines[j].lstrip(" "))
        if lead > indent or (lead == indent and body.startswith("-")):
            last = j
            continue
        break
    return last


def _drop(data, dotted: str) -> bool:
    """Delete one dotted key from parsed YAML, and a mapping it leaves empty. True if it was
    there."""
    head, _, rest = dotted.partition(".")
    if not isinstance(data, dict) or head not in data:
        return False
    if not rest:
        del data[head]
        return True
    dropped = _drop(data[head], rest)
    if dropped and not data[head]:
        del data[head]
    return dropped


def _retired_config(root: Path) -> tuple[list[dict], list[dict], dict[Path, str]]:
    """The retired `.config.yaml` keys (`sdlc_md.RETIRED_CONFIG_KEYS`), removed line by line:
    a key's own line and its block's children go, and a parent the removal leaves empty goes
    too (an empty block would read as null and mask the shipped defaults under it). Every other
    line is kept byte for byte, comments included; a comment block directly above a removed key
    is named, never removed. With PyYAML present the result is re-parsed and must equal the
    original minus those keys, or nothing is written and the keys are handed to a human.
    Returns (removals, needs-human, rewrites)."""
    path = root / "sdlc-studio" / ".config.yaml"
    text = _read_raw(path)
    if not text:
        return [], [], {}
    retired = sdlc_md.RETIRED_CONFIG_KEYS
    lines = text.splitlines(keepends=True)
    keys: list[tuple[int, int, str, str]] = []   # (line index, indent, dotted, value on the line)
    stack: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        m = _KEY_RE.match(line)
        if not m or line.lstrip().startswith("#"):
            continue
        indent = len(m.group(1))
        while stack and stack[-1][0] >= indent:
            stack.pop()
        stack.append((indent, m.group(2)))
        keys.append((i, indent, ".".join(k for _, k in stack), m.group(3)))
    gone: set[int] = set()
    found: list[dict] = []
    for i, indent, dotted, _ in keys:
        if dotted not in retired or i in gone:
            continue
        end = _block_end(lines, i, indent)
        gone.update(range(i, end + 1))
        above = i
        while above > 0 and lines[above - 1].strip().startswith("#") and above - 1 not in gone:
            above -= 1
        comment = [above + 1, i] if above < i else None
        span = "" if not comment else (f"line {i}" if above + 1 == i else f"lines {above + 1}-{i}")
        found.append({"source": "config", "kind": "retired-config-key", "key": dotted,
                      "line": i + 1, "comment_above": comment,
                      "detail": f".config.yaml:{i + 1}: {dotted} removed"
                                f"{' with its block' if end > i else ''} - {retired[dotted]}"
                                + (f"; the comment above it ({span}) is kept for you to judge"
                                   if comment else "")})
    try:
        import yaml  # noqa: PLC0415 - soft dependency, and the check on every rewrite
    except ImportError:
        # no parser, no check: name every key the text may hold (a flow mapping included)
        suspects = [k for k in retired if re.search(
            rf"(?<![\w.-]){re.escape(k.rsplit('.', 1)[-1])}\s*:", text)]
        return [], ([{"kind": "retired-config-key", "command": None, "detail":
                      f".config.yaml: remove {', '.join(suspects)} by hand if present - "
                      f"PyYAML is not installed, so a rewrite cannot be checked"}]
                    if suspects else []), {}
    try:
        expected = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return [], [], {}              # an unparseable config is validate's report, not ours
    present = [key for key in retired if _drop(expected, key)]
    if not found and not present:
        return [], [], {}
    for i, indent, dotted, value in reversed(keys):   # children before their parents
        end = _block_end(lines, i, indent)
        content = [j for j in range(i + 1, end + 1)
                   if lines[j].strip() and not lines[j].strip().startswith("#")]
        if (i not in gone and value.split("#")[0].strip() == "" and content
                and all(j in gone for j in content)):
            gone.add(i)
            found.append({"source": "config", "kind": "emptied-block", "key": dotted,
                          "line": i + 1, "comment_above": None,
                          "detail": f".config.yaml:{i + 1}: {dotted} removed - the retired "
                                    f"keys were all it held"})
    new = "".join(line for i, line in enumerate(lines) if i not in gone)
    try:
        same = (yaml.safe_load(new) or {}) == expected
    except yaml.YAMLError:
        same = False
    if not same:
        return [], [{"kind": "retired-config-key", "command": None, "detail":
                     f".config.yaml: remove {', '.join(present)} by hand - its layout "
                     f"cannot be edited line by line without changing another setting"}], {}
    return found, [], {path: new}


def _retired_verbs() -> dict[str, str]:
    """`<script>.py <verb>` -> why, from each script's own `RETIRED_VERBS` registry, read with
    `ast` so no script is imported for it. A reason built from a name, not a literal, is left to
    the verb's own refusal, which names what replaced it."""
    out: dict[str, str] = {}
    for script in sorted(Path(__file__).resolve().parent.glob("*.py")):
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


def _retired_mentions(root: Path) -> list[dict]:
    """Each AGENTS.md/CLAUDE.md line, and each DoR/DoD line, naming a retired config key or verb,
    for a human: the files are the project's own words, so the line is reported, never
    rewritten (a DoD loses only its retired tags, above)."""
    surfaces = [(key, re.compile(rf"(?<![\w.]){re.escape(key)}(?!\w)"), why)
                for key, why in sdlc_md.RETIRED_CONFIG_KEYS.items()]
    for label, why in _retired_verbs().items():
        script, verb = label.split(" ")
        surfaces.append((label, re.compile(rf"\b{re.escape(script[:-3])}(?:\.py)?\s+"
                                           rf"{re.escape(verb)}\b"), why))
    out: list[dict] = []
    for name in ("AGENTS.md", "CLAUDE.md", "sdlc-studio/definition-of-ready.md",
                 "sdlc-studio/definition-of-done.md"):
        path = root / name
        text = sdlc_md.read_text_safe(path) if path.is_file() else None
        for n, line in enumerate((text or "").splitlines(), 1):
            out += [{"kind": "retired-surface", "file": name, "line": n, "surface": label,
                     "detail": f"{name}:{n} names the retired `{label}` ({why}) - "
                               f"edit it by judgement",
                     "command": None}
                    for label, rx, why in surfaces if rx.search(line)]
    return out


def _late_rows(path: Path, cutoff: str) -> int:
    """Rows of a ledger whose own `Date` cell is on or after `cutoff`."""
    count = 0
    for table in sdlc_md.iter_tables(sdlc_md.read_text_safe(path) or ""):
        header = [c.strip().lower() for c in table["header"] or []]
        if "date" not in header:
            continue
        col = header.index("date")
        count += sum(1 for _, cells in table["rows"]
                     if col < len(cells) and _DATE_RE.fullmatch(cells[col][:10])
                     and cells[col][:10] >= cutoff)
    return count


def _frozen(root: Path) -> list[dict]:
    """Each frozen review ledger present, reported as history. For the two a licence reads by
    date, the rows dated on or after `critic.REPAIR_VERB_RETIRED` are counted, since the licence
    does not cover them."""
    cutoff = critic.REPAIR_VERB_RETIRED
    out: list[dict] = []
    for name in FROZEN_LEDGERS:
        path = root / "sdlc-studio" / "reviews" / name
        if not path.is_file():
            continue
        late = _late_rows(path, cutoff) if name in _DATED_LEDGERS else None
        detail = f"reviews/{name}: frozen history, left as written"
        if late:
            detail += f"; {late} row(s) dated on or after {cutoff} {_DATED_LEDGERS[name]}"
        out.append({"file": f"reviews/{name}", "late_rows": late, "detail": detail})
    return out


def _conformance_cutoff(root: Path) -> list[dict]:
    """The `conformance.adopt_after` line that grandfathers every unit the conformance lane would
    fail, for a human: the cutoff is a judgement about the project's history, so it is named,
    never written. The lane itself decides which units fail, so a cutoff already covering them
    leaves nothing to name, and the one named (the highest failing id) is never below a failing
    unit. A ULID id has no number for a cutoff to reach, so it is left to the lane's report.

    The lane resolves a stamped pytest selector by running the project's `pytest --collect-only`,
    so the call runs with pytest's cache and Python's bytecode writes off, restored after: a
    migrate run, a dry one above all, leaves the project's bytes where they were."""
    import conformance  # noqa: PLC0415 - the lane is needed only here
    saved = {k: os.environ.get(k) for k in ("PYTEST_ADDOPTS", "PYTHONDONTWRITEBYTECODE")}
    opts = saved["PYTEST_ADDOPTS"] or ""
    os.environ["PYTEST_ADDOPTS"] = f"{opts} -p no:cacheprovider".strip()
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = conformance.detect_conformance(root)
    except ValueError as exc:        # a malformed existing cutoff: the lane refuses it, loudly
        return [{"kind": "conformance-cutoff", "lane": "conformance", "ids": [], "count": None,
                 "command": None,
                 "detail": f"the conformance lane cannot read this project ({exc}), so no "
                           f"`conformance.adopt_after` cutoff can be proposed - fix it, then "
                           f"re-run"}]
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    units = result["units"]
    # The lane's own count, as the gate's conformance lane takes it: every non-conformant unit
    # plus each repo-wide failure, so an item's number is the one the gate then fails on.
    lane_count = result["summary"]["nonconformant"] + result["summary"].get("global_failures", 0)
    failing = [u for u in units if not u["conformant"] and sdlc_md.id_number(u["id"]) is not None]
    if not failing:
        return []
    ids = [u["id"] for u in failing]
    top = max(ids, key=sdlc_md.id_number)
    line = f"conformance.adopt_after: {top}"
    # Units whose ONLY unmet half is an APPROVE row that records no author (the ledger before its
    # Author column) are counted apart: recording the author answers them, a cutoff need not.
    # critic's own reader decides what the row says; the table is never re-parsed here.
    import critic  # noqa: PLC0415 - needed only here

    def approve_without_author(u: dict) -> bool:
        if u["missing"] != ["critiqued"] or u.get("critiqued_missing") != [conformance.HALF_VERDICT]:
            return False
        v = critic.verdict_for(root, u["id"])
        return (bool(v) and str(v.get("verdict") or "").upper() == critic.APPROVE
                and critic.same_identity(v.get("author") or "", ""))

    no_author = [u["id"] for u in failing if approve_without_author(u)]
    other = [u for u in failing if u["id"] not in no_author]
    # Each unit's missing stages, so a human can tell old history from a recent breakage.
    why = [f"{u['id']} ({conformance.missing_detail(u)})" for u in other]
    detail = f"the conformance lane would fail {len(ids)} unit(s): "
    if no_author:
        detail += (f"{len(no_author)} of them ({_named(no_author)}) with an APPROVE row that "
                   f"records no author and nothing else unmet - recording each row's author, or "
                   f"a reviewed `{critic.PRE_GATE}` author stamp, meets them without a cutoff")
        if other:
            detail += f"; the other {len(other)} ({_named(why)})"
    else:
        detail += _named(why)
    existing = sdlc_md.project_override(root, "conformance.adopt_after")
    if existing is None:
        detail += (f". To grandfather them as pre-adoption history, add `{line}` to "
                   f"sdlc-studio/.config.yaml (the `adopt_after` key under `conformance:`) once "
                   f"you have checked none of them is new work - every id at or below it is "
                   f"exempt")
    else:
        # Already set: these units come AFTER the project's own adoption point, so they are not
        # pre-adoption history, and the key is raised rather than added.
        detail += (f". The project already sets `conformance.adopt_after: {existing}` and these "
                   f"units come after it. To exempt them anyway, raise `conformance.adopt_after` "
                   f"from {existing} to {top} (`{line}`) in sdlc-studio/.config.yaml, only once "
                   f"you have checked none of them is work the gate should still judge - every "
                   f"id at or below it is exempt")
    return [{"kind": "conformance-cutoff", "lane": "conformance", "count": lane_count, "ids": ids,
             "approve_no_author": no_author, "other": [u["id"] for u in other], "line": line,
             "command": None, "detail": detail}]


#: The gate lane `_engagement_floor_cutoff` speaks for, carried on its item.
_FLOOR_LANE = "engagement-floor"
_FLOOR_NAMED = 10


def _named(ids: list[str]) -> str:
    return ", ".join(ids[:_FLOOR_NAMED]) + (f" (+{len(ids) - _FLOOR_NAMED} more)"
                                            if len(ids) > _FLOOR_NAMED else "")


def _engagement_floor_cutoff(root: Path) -> list[dict]:
    """The `engagement_floor.adopt_after` line that grandfathers every shipped unit the
    engagement-floor lane would fail, for a human, as `_conformance_cutoff` does for its lane:
    named, never written. The lane's own `detect` decides which units fail, so a unit an existing
    cutoff or a waiver already exempts is never named, and the line (the highest failing id) is
    never below a failing unit. A cutoff that stops short is named as a raise from its value.

    Nothing is proposed in `judgement` mode, where the lane never blocks. A forward cutoff fails
    the lane as a config error, so the lane's own words are carried instead of a line. A v3 id
    has no number `adopt_after` can reach, so such a unit is named with the per-unit remedies and
    kept out of the line, which therefore always parses."""
    import engagement_floor  # noqa: PLC0415 - the lane is needed only here

    def item(ids: list[str], line: str | None, detail: str, count: int | None) -> list[dict]:
        return [{"kind": "engagement-floor-cutoff", "lane": _FLOOR_LANE, "count": count,
                 "ids": ids, "line": line, "command": None, "detail": detail}]

    try:
        result = engagement_floor.detect(root)
    except ValueError as exc:        # a malformed existing cutoff: the lane refuses it, loudly
        return item([], None, f"the engagement-floor lane cannot read this project ({exc}), so "
                              f"no `engagement_floor.adopt_after` cutoff can be proposed - fix "
                              f"it, then re-run", None)
    s = result["summary"]
    if s["cutoff_forward"]:
        return item([], None, f"the engagement-floor lane fails on its cutoff: "
                              f"{engagement_floor.remedy_detail(result)}", 1)   # the lane's count
    if result["mode"] == "judgement":
        return []
    failing = [u["id"] for u in result["units"] if u["violation"]]
    if not failing:
        return []
    numbered = [i for i in failing if sdlc_md.id_number(i) is not None]
    unnumbered = [i for i in failing if sdlc_md.id_number(i) is None]
    detail = (f"the engagement-floor lane would fail {len(failing)} shipped unit(s) (no plan and "
              f"not shown small): {_named(failing)}.")
    line = None
    if numbered:
        line = f"engagement_floor.adopt_after: {max(numbered, key=sdlc_md.id_number)}"
        top = line.split(": ", 1)[1]
        verb = (f"raise `engagement_floor.adopt_after` from {s['cutoff']} to {top} (`{line}`) in"
                if s["cutoff"] is not None else f"add `{line}` to")
        detail += (f" To grandfather them as pre-adoption history, {verb} "
                   f"sdlc-studio/.config.yaml (the `adopt_after` key under `engagement_floor:`) "
                   f"once you have checked none of them is new work - every id at or below it "
                   f"is exempt.")
    if unnumbered:
        detail += (f" {len(unnumbered)} of them ({_named(unnumbered)}) carry a v3 id, which no "
                   f"cutoff can reach: {engagement_floor.REMEDY_ADD}; or "
                   f"{engagement_floor.REMEDY_WAIVER}.")
    return item(failing, line, detail, s["violations"])


#: The per-clone CI cache a pre-6.0 close read DORA from whenever it existed. Read here only, to
#: freeze the runs a signed page read onto its tracked record; nothing re-derives from it.
_CI_CACHE = "sdlc-studio/.local/ci-runs.json"


def _page_ci_runs(root: Path, start, end) -> dict:
    """The CI runs a page signed before 6.0 read inside its window: the per-clone cache's rows,
    as that close read them, or none where this clone holds no cache (the forge's answer then
    was never kept)."""
    import sprint_report as sr  # noqa: PLC0415 - needed only for a signed report
    try:
        rows = json.loads((root / _CI_CACHE).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"source": "no forge", "runs": []}
    except (OSError, ValueError):
        rows = []                      # the old reader took an unreadable cache as no runs
    return {"source": _CI_CACHE,
            "runs": [r for r in (rows if isinstance(rows, list) else []) if isinstance(r, dict)
                     and sr._in_window(r.get("createdAt"), sr._at(start), sr._at(end))]}


def _signed_records(root: Path, apply: bool) -> tuple[list[dict], list[dict]]:
    """Each signed report whose run record lives only in this clone's `.local`, filed as the
    tracked record `sprint sign` now files (`run_state.file_tracked`), so the report checks in
    any clone. The inputs the page read that a clean clone lacks are frozen on it as a close now
    freezes them: the verdict rows its rounds count (`REVIEW_ROWS`, by the rule `check` reads a
    record that froze none with) and the CI runs inside its window (`CI_RUNS`, from the cache
    the page read). A field the record already holds is kept.

    Filed only when the page re-derives from that record, as a clean clone will read it, to the
    fingerprint it was signed at; otherwise the report is named for a human and nothing is filed,
    since a record filed then would move a signed page in every clone. A record already filed is
    never rewritten. Returns (deterministic, needs-human)."""
    import sprint_report as sr  # noqa: PLC0415 - needed only for a signed report
    from lib import run_state  # noqa: PLC0415
    det: list[dict] = []
    human: list[dict] = []
    try:
        live = run_state.read(root) or {}
    except run_state.RunStateError:
        live = {}
    for path in sorted(sr.report_dir(root).glob("RPT*.json")):
        try:
            page = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(page, dict):
            continue
        rid, run_id = sdlc_md.norm_id(path.stem), page.get("run_id")
        if (not run_id or page.get("schema") != sr.SCHEMA
                or not (page.get("signature") or {}).get("principal")
                or run_state.tracked_path(root, run_id).exists()):
            continue
        rel = sr._rel(root, run_state.tracked_path(root, run_id))
        check = f"sprint_report.py check --report {rid}"
        state = live if live.get("run_id") == run_id else run_state.read_archived(root, run_id)
        if not state:
            human.append({"kind": "run-record", "id": rid, "command": check, "detail":
                          f"{rid} is signed, but no run record of {run_id} is tracked or in "
                          f"this clone's .local, so none can be filed here - run migrate in "
                          f"the clone that signed it"})
            continue
        signed_on = (state.get("signature") or {}).get("report")
        if signed_on and sdlc_md.norm_id(str(signed_on)) != rid:
            continue                   # the run was signed on another page; that one is filed
        window = (state.get("started_at"), sr._legacy_window_end(root, page, state))
        frozen = dict(state)
        if sr.REVIEW_ROWS not in frozen:
            frozen[sr.REVIEW_ROWS] = sr.counted_review_rows(root, state, window)
        if sr.CI_RUNS not in frozen:
            frozen[sr.CI_RUNS] = _page_ci_runs(root, *window)
        record = run_state.portable(frozen, root)
        try:
            verdict = sr.revalidate(root, rid, record=record)
        except sr.ReportError as exc:
            why = str(exc)
        else:
            moved = ", ".join(verdict["moved"]) or ", ".join(
                e["figure"] for e in verdict["edited"])
            why = ("" if verdict["valid"] else verdict.get("predates") or
                   f"re-derived from the record it would file, {rid} reads "
                   f"{verdict['fingerprint']}, not the {verdict['signed_fingerprint']} it was "
                   f"signed at ({moved})")
        if why:
            human.append({"kind": "run-record", "id": rid, "command": check,
                          "detail": f"{rid}: no record filed for {run_id} - {why}"})
            continue
        det.append({"source": "run-record", "id": rid, "run": run_id, "path": rel,
                    "detail": f"{rid}: files {run_id}'s sealed record at {rel}, its review rows "
                              f"and CI runs frozen as the page read them; it re-derives to "
                              f"{verdict['fingerprint']}", "applied": apply})
        if apply:
            run_state.file_tracked(root, record)
    return det, human


def _unreadable_files(root: Path) -> list[tuple[str, str]]:
    """`(repo-relative path, why)` for each workspace Markdown or config file under
    `sdlc-studio/` that cannot be read as UTF-8 text - the files every step of the sweep reads.
    Runtime state under `.local/` is not the project's, and is skipped."""
    out = []
    store = root / "sdlc-studio"
    for path in sorted([*store.rglob("*.md"), store / ".config.yaml"]):
        if not path.is_file() or ".local" in path.relative_to(store).parts:
            continue
        try:
            path.read_text(encoding="utf-8")  # bare-read-ok: the probe IS the read
        except (UnicodeDecodeError, OSError) as exc:
            out.append((path.relative_to(root).as_posix(), type(exc).__name__))
    return out


def migrate(repo_root: Path | str, *, apply: bool = False, with_default_amigos: bool = False,
            today: str | None = None) -> dict:
    """Run the upgrade sweep. Returns
    `{applicable, applied, deterministic: [...], needs_human: [...], summary}`. `deterministic`
    lists what was (or would be) auto-applied - conventions/version from `project_upgrade` and
    sizing conversions from `migrate_v3`. `needs_human` lists every item that needs judgement, each
    with the exact command. `apply` performs only the deterministic set."""
    root = Path(repo_root)
    if not (root / "sdlc-studio").is_dir():
        return {"applicable": False, "applied": apply, "deterministic": [], "needs_human": [],
                "frozen": [], "summary": {}}
    # A workspace file that cannot be read as UTF-8 text stopped the sweep with a traceback that
    # named neither the file nor anything else in the report. Every step below reads the
    # workspace, so the files are found first and NAMED, and nothing is read past them or
    # written - an upgrade applied over files its own readers cannot read is not deterministic.
    unreadable = _unreadable_files(root)
    if unreadable:
        needs = [{"kind": "unreadable", "path": rel, "command": None,
                  "detail": f"{rel} could not be read as UTF-8 text ({why}) - re-save it as UTF-8, "
                            f"then run migrate again; nothing else was examined or written"}
                 for rel, why in unreadable]
        return {"applicable": True, "applied": False, "deterministic": [], "needs_human": needs,
                "terminal_sized": 0, "frozen": [],
                "summary": {"deterministic": 0, "needs_human": len(needs), "terminal_sized": 0,
                            "frozen": 0, "applied": False}}

    # 1. conventions + version. Classify from `audit()` in BOTH modes - never from `apply()`'s
    # free-text action strings, which mix real changes with advisories and warnings (the team-offer
    # nudge, the BG0150 "version NOT stamped" warning, "SKIPPED" notes). Reporting an advisory as an
    # applied deterministic upgrade breaks the honest split this command exists for; using the one
    # `audit` classification keeps dry-run and apply agreeing on what is deterministic vs needs-human.
    # `audit` is honest about BG0150 (an unreadable install version -> a `manual` item, not `auto`),
    # so `auto` is a faithful preview of what apply will write.
    au = project_upgrade.audit(root)
    if apply:
        project_upgrade.apply(root, with_reconcile=False, today=today,
                              with_default_amigos=with_default_amigos)

    # 2. retired review surfaces. The DoD tags and config keys are removed line by line; the
    # instructions lines and the frozen ledgers are only reported.
    tags, tag_rewrites = _retired_tags(root)
    cfg_keys, cfg_human, cfg_rewrites = _retired_config(root)
    mentions = _retired_mentions(root)   # read before the write, so its lines match a dry run
    if apply:
        for path, text in {**tag_rewrites, **cfg_rewrites}.items():
            sdlc_md.atomic_write(path, text)

    # 3. ids/sizing. Converts a container's legacy Effort/Points to a Size deterministically, and
    # reports the delivery units and undecomposed requests/issues it cannot convert safely.
    sizing = migrate_v3.migrate_sizing(root, dry_run=not apply)

    # 4. the tracked run record of each report signed before records were tracked.
    records, records_human = _signed_records(root, apply)

    # 5. aggregate into one report. Deterministic = the conventions auto-fixes, the retired tags
    # and keys removed, the sizing conversions and the run records; `applied` reflects the mode,
    # and the classification is identical either way.
    deterministic: list[dict] = []
    for a in au["auto"]:
        deterministic.append({"source": "conventions", "kind": a["kind"],
                              "detail": a["detail"], "applied": apply})
    deterministic += [{**r, "applied": apply} for r in tags + cfg_keys]
    converted_ids = set()
    for c in sizing["converted"]:
        converted_ids.add(c["id"])
        deterministic.append({"source": "sizing", "id": c["id"],
                              "detail": f"{c['id']}: Size {c['size']} (from {c['from']})",
                              "applied": apply})
    deterministic += records

    needs_human: list[dict] = []
    for m in au["manual"]:                       # conventions that need judgement (index drift, etc.)
        # The gate lane an item speaks for, and that lane's count, travel with it as the item
        # set them: a reader compares them with the gate's own output, never through a map.
        needs_human.append({"kind": m["kind"], "detail": m["detail"], "command": None,
                            **{k: m[k] for k in ("lane", "count") if k in m}})
    needs_human += cfg_human + mentions
    for bucket in _HUMAN_ORDER:                  # the artefact-review sweep, per ceremony
        label, cmd = _HUMAN[bucket]
        for item in sizing.get(bucket, []):
            # a container can be size-converted (deterministic) AND still need refining - two
            # orthogonal facts about one id. Note the overlap so the report does not read as "you
            # fixed it / you must fix it" about the same artefact.
            also = " (its Size was converted above; this is the separate decomposition)" \
                if item["id"] in converted_ids else ""
            needs_human.append({"kind": bucket.replace("_", "-"), "id": item["id"],
                                "detail": f"{item['id']} ({item['type']}): {label}{also}",
                                "command": cmd(item)})
    needs_human += records_human
    # 6. the grandfathering cutoff, judged on the tree as it now stands: migrated under --apply,
    # as found on a dry run.
    needs_human += _conformance_cutoff(root)
    needs_human += _engagement_floor_cutoff(root)

    # Terminal legacy-sized units are NOT needs-human work: a Closed/Fixed unit is never planned,
    # so re-sizing it changes nothing. Report them as a single historical count, never as an action.
    terminal_sized = len(sizing.get("terminal_sized", []))

    frozen = _frozen(root)
    return {"applicable": True, "applied": apply, "deterministic": deterministic,
            "needs_human": needs_human, "terminal_sized": terminal_sized, "frozen": frozen,
            "summary": {"deterministic": len(deterministic), "needs_human": len(needs_human),
                        "terminal_sized": terminal_sized, "frozen": len(frozen),
                        "applied": apply}}


def render(result: dict) -> str:
    if not result["applicable"]:
        return "migrate: no sdlc-studio/ under this root - not an sdlc-studio project."
    verb = "applied" if result["applied"] else "would apply"
    out = [f"migrate: {result['summary']['deterministic']} deterministic upgrade(s) {verb}, "
           f"{result['summary']['needs_human']} need(s) a human.", ""]
    if result["deterministic"]:
        out.append(f"## Deterministic ({verb})")
        for d in result["deterministic"]:
            out.append(f"  - [{d['source']}] {d['detail']}")
        out.append("")
    if result["needs_human"]:
        out.append("## Needs a human (reported, never guessed)")
        for h in result["needs_human"]:
            out.append(f"  - {h['detail']}")
            if h.get("command"):
                out.append(f"      -> {h['command']}")
        out.append("")
    if result.get("frozen"):
        out.append("## Frozen history (left as written)")
        out += [f"  - {f['detail']}" for f in result["frozen"]]
        out.append("")
    if result.get("terminal_sized"):
        out.append(f"{result['terminal_sized']} terminal unit(s) keep legacy sizing "
                   f"- historical, no action.")
        out.append("")
    if not result["applied"] and result["deterministic"]:
        out.append("Re-run with --apply to write the deterministic set (the needs-human items are "
                   "never auto-applied).")
    return "\n".join(out).rstrip("\n") + "\n"


def cmd_run(args: argparse.Namespace) -> int:
    result = migrate(args.root, apply=args.apply, with_default_amigos=args.with_default_amigos)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render(result), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="migrate", description=__doc__)
    p.add_argument("--root", default=".", help="repo root")
    p.add_argument("--apply", action="store_true",
                   help="write the deterministic set (conventions, version, sizing conversions); "
                        "the needs-human items are always only reported")
    p.add_argument("--with-default-amigos", dest="with_default_amigos", action="store_true",
                   help="install the shipped default amigo cards for roles no seat covers "
                        "(passed through to project upgrade)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
