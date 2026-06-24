#!/usr/bin/env python3
"""SDLC Studio status transition (CR0042).

`transition --id <ID> --status <new>` performs the one mechanical write-side cascade
that was still hand-driven: set an artifact's `Status` field, sync its index row and the
summary counts, and (for a story) tick/untick its checkbox in the parent epic's Story
Breakdown. Deterministic once the new status is chosen - it reuses the validated
`reconcile.apply_type` to bring the index into line with the file, so there is no
bespoke index-row editing.

Subcommand:
  set  Transition one artifact to a new status and cascade the index/epic updates.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import reconcile  # noqa: E402  (sibling - reuse the tested index-row + count sync)

# Statuses that mean "complete" for the epic-breakdown checkbox (a story is ticked).
_STORY_TICKED = {"Done", "Won't Implement", "Deferred", "Superseded"}
_REPORT_REL = "sdlc-studio/.local/verify-report.json"


def _story_has_executable_acs(text: str) -> bool:
    """True if the story declares any non-manual `Verify:` line (an executable AC). A story
    with only `manual` ACs (or none) has nothing the deterministic gate can check."""
    for line in text.splitlines():
        m = sdlc_md.VERIFY_RE.match(line)
        if m and m.group(2).strip().split(None, 1)[0].lower() not in ("manual", "manually"):
            return True
    return False


def _done_verify_gate(root: Path, path: Path, text: str) -> str | None:
    """Definition-of-Done safety net on the hand-driven path (CR0084). A story may not reach
    Done with executable ACs that are red or never run - the 0/7 a hand-driving agent shipped.
    Returns a block reason, or None to allow. Manual-only / AC-less stories are never blocked;
    a green report passes. The hard gate is the one deterministic fact - the verifier result;
    critic semantic findings stay advisory (handled elsewhere)."""
    if not _story_has_executable_acs(text):
        return None  # nothing executable to verify
    report_path = root / _REPORT_REL
    if not report_path.exists():
        return "this story declares executable ACs but they were never verified - run `verify_ac`"
    try:
        entry = (json.loads(report_path.read_text(encoding="utf-8")).get("stories", {}) or {}).get(path.stem)
    except (ValueError, OSError):
        entry = None
    if entry is None:
        return "this story is not in the verify-report - run `verify_ac` before Done"
    if entry.get("failed", 0) or entry.get("stale", 0):
        fails = ", ".join(f.get("ac", "?") for f in entry.get("failures", [])) or "stale AC(s)"
        return f"AC verification is red ({fails}) - fix or re-verify before Done"
    return None


def _find(repo_root: Path, artifact_id: str):
    """(path, type) of the artifact with this id, or (None, None)."""
    norm = sdlc_md.norm_id(artifact_id)
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for p in sdlc_md.artifact_files(type_, repo_root):
            rec = sdlc_md.extract_record_id(p.stem)
            if rec and sdlc_md.norm_id(rec) == norm:
                return p, type_
    return None, None


def _set_field(text: str, name: str, value: str) -> tuple[str, bool]:
    """Replace a `**Name:** value` field's value in place (blockquote or inline `·`
    form), preserving the surrounding format. Returns (new_text, changed)."""
    pat = re.compile(
        rf"((?:^>?\s*|·\s*)\*\*{re.escape(name)}:\*\*\s*)(.+?)(\s*(?=·|\s\*\*[^*\n]+:\*\*|$))",
        re.M)
    new_text, n = pat.subn(lambda m: m.group(1) + value + m.group(3), text, count=1)
    return new_text, n > 0


def _cascade_epic(repo_root: Path, story_id: str, ticked: bool) -> str | None:
    """Tick/untick the story's line in its parent epic's Story Breakdown (called only on
    a real write). Returns the epic id touched, or None."""
    spath, _ = _find(repo_root, story_id)
    if spath is None:
        return None
    epic_field = sdlc_md.extract_field(spath.read_text(encoding="utf-8"), "Epic") or ""
    m = sdlc_md.ID_SEARCH_RE.search(epic_field)
    if not m:
        return None
    epath, _ = _find(repo_root, m.group(0))
    if epath is None:
        return None
    norm = sdlc_md.norm_id(story_id)
    lines = epath.read_text(encoding="utf-8").splitlines()
    changed = False
    box = "[x]" if ticked else "[ ]"
    for i, ln in enumerate(lines):
        s = ln.lstrip()
        if s.startswith(("- [ ]", "- [x]", "- [X]")) and sdlc_md.ID_SEARCH_RE.search(ln) \
                and sdlc_md.norm_id(sdlc_md.ID_SEARCH_RE.search(ln).group(0)) == norm:
            new = re.sub(r"\[[ xX]\]", box, ln, count=1)
            if new != ln:
                lines[i] = new
                changed = True
            break
    if changed:
        epath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return m.group(0) if changed else None


def transition(repo_root: Path | str, artifact_id: str, new_status: str,
               dry_run: bool = False, force: bool = False) -> dict:
    """Set `artifact_id`'s status to `new_status`, sync its index, and cascade the epic
    breakdown for a story. Returns {id, type, from, to, index_synced, epic}.

    A story moving to Done is gated on its AC-verify result (CR0084): red or never-run
    executable ACs block the transition unless `force=True`. Scoped to stories - CR/epic/bug
    closures are unaffected. Manual-only / AC-less stories are never blocked."""
    root = Path(repo_root)
    path, type_ = _find(root, artifact_id)
    if path is None:
        raise ValueError(f"no artifact found for id {artifact_id!r}")
    vocab = sdlc_md.status_vocab(type_, root)
    if sdlc_md.canonical_status(new_status, vocab) is None:
        raise ValueError(f"{new_status!r} is not a valid {type_} status ({', '.join(vocab)})")
    text = path.read_text(encoding="utf-8")
    gate_warn = None
    if (type_ == "story" and not force and not dry_run
            and sdlc_md.canonical_status(new_status, vocab) == "Done"):
        block = _done_verify_gate(root, path, text)
        if block:
            # CR0095: the gate is hard by default; `quality.done_requires_verified: false`
            # downgrades it to advisory-warn (the project sets the policy in .config.yaml).
            import config  # sibling
            if config.get(root, "quality.done_requires_verified", True):
                raise ValueError(f"{artifact_id} -> Done blocked: {block}. Override with --force.")
            gate_warn = f"AC-verify advisory (quality.done_requires_verified=false): {block}"
    current = sdlc_md.extract_field(text, "Status")
    new_text, ok = _set_field(text, "Status", new_status)
    if not ok:
        raise ValueError(f"{path.name} has no `Status` field to transition")
    result = {"id": sdlc_md.extract_record_id(path.stem), "type": type_,
              "from": current, "to": new_status, "index_synced": False, "epic": None,
              "warning": gate_warn}
    if dry_run:
        return result
    path.write_text(new_text, encoding="utf-8")
    reconcile.apply_type(type_, root)  # sync the index row + counts
    # index_synced is the TRUTH after the sync, not "apply did something": an archived
    # row (apply only edits the live index) or a target status with no summary row both
    # leave residual drift, which we must report honestly rather than claim success.
    norm = sdlc_md.norm_id(result["id"])
    residual = [d for d in reconcile.detect_type(type_, root)["drift"]
                if (d.get("id") and sdlc_md.norm_id(d["id"]) == norm) or d["kind"] == "count-mismatch"]
    result["index_synced"] = not residual
    if residual:
        sync_warn = ("index not fully synced (the artifact may be archived, or its "
                     "new status has no summary row) - run reconcile")
        result["warning"] = f"{gate_warn}; {sync_warn}" if gate_warn else sync_warn
    if type_ == "story":
        result["epic"] = _cascade_epic(root, result["id"],
                                       sdlc_md.canonical_status(new_status, vocab) in _STORY_TICKED)
    return result


def cmd_set(args: argparse.Namespace) -> int:
    res = transition(args.root, args.id, args.status, dry_run=args.dry_run, force=args.force)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        verb = "would set" if args.dry_run else "set"
        extra = f"; epic {res['epic']} breakdown updated" if res.get("epic") else ""
        print(f"{verb} {res['id']} {res['from']} -> {res['to']}"
              + ("" if args.dry_run else f" (index synced={res['index_synced']}{extra})"))
        if res.get("warning"):
            print(f"  warning: {res['warning']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Transition an artifact's status + cascade (CR0042).")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set", help="Set an artifact's status and sync index + epic breakdown.")
    s.add_argument("--id", required=True, help="Artifact id, e.g. CR0042 / US0023")
    s.add_argument("--status", required=True, help="New status (must be in the type vocabulary)")
    s.add_argument("--root", default=".")
    s.add_argument("--force", action="store_true",
                   help="bypass the story->Done AC-verify gate (CR0084); recorded as an override")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_set)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
