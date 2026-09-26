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
and the frozen review ledgers are reported as history and left as written. Dry-run by default;
`--apply` writes only the deterministic set.

Skill/consuming-project tool: it operates on the `sdlc-studio/` workspace under the root. Reuses
`project_upgrade`, `migrate_v3` and `reconcile`; pure stdlib.
"""
from __future__ import annotations

import argparse
import ast
import json
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

    # 4. aggregate into one report. Deterministic = the conventions auto-fixes, the retired tags
    # and keys removed, and the sizing conversions; `applied` reflects the mode, and the
    # classification is identical either way.
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

    needs_human: list[dict] = []
    for m in au["manual"]:                       # conventions that need judgement (index drift, etc.)
        needs_human.append({"kind": m["kind"], "detail": m["detail"], "command": None})
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
