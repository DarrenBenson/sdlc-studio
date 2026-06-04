#!/usr/bin/env python3
"""SDLC Studio GitHub Issues sync.

Two-way sync between local CR / Story / Epic files and GitHub Issues
via the `gh` CLI. No direct API calls, no token handling.

Label convention:
    sdlc:cr                 Issue mirrors a Change Request
    sdlc:story              Issue mirrors a User Story
    sdlc:epic               Issue mirrors an Epic
    sdlc:status:<state>     Current status (proposed, ready, done, ...)
    sdlc:priority:P1..P4    Optional priority
    sdlc:type:<kind>        Optional type

Subcommands:
    pull    Fetch labelled issues, create missing local files
    push    Create or update issues from local files
    cascade List merged PRs since last run, trigger Story Completion
            Cascade on referenced stories
    state   Print the sync state file

State lives in sdlc-studio/.local/github-sync-state.json and is
never committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

LABEL_PREFIX = "sdlc"

TYPE_LABELS = {
    "cr": f"{LABEL_PREFIX}:cr",
    "story": f"{LABEL_PREFIX}:story",
    "epic": f"{LABEL_PREFIX}:epic",
}

TYPE_DIRS = {
    "cr": ("sdlc-studio/change-requests", "CR"),
    "story": ("sdlc-studio/stories", "US"),
    "epic": ("sdlc-studio/epics", "EP"),
}

STATE_PATH = "sdlc-studio/.local/github-sync-state.json"


# -----------------------------------------------------------------------------
# gh CLI wrapper
# -----------------------------------------------------------------------------


def gh(*args: str, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a `gh` subcommand, raising RuntimeError if the CLI is absent."""
    if shutil.which("gh") is None:
        raise RuntimeError("gh CLI not on PATH. Install https://cli.github.com/")
    return subprocess.run(
        ["gh", *args],
        capture_output=capture,
        text=True,
        check=False,
    )


def _loads(text: str, default):
    """Parse JSON, returning `default` (not raising) on malformed input."""
    try:
        return json.loads(text or "null") if text and text.strip() else default
    except json.JSONDecodeError:
        return default


def gh_issue_list(label: str) -> list[dict]:
    """Return all issues carrying `label` (open and closed), or [] on error."""
    result = gh(
        "issue", "list",
        "--label", label,
        "--state", "all",
        "--json", "number,title,state,body,labels,url,updatedAt,createdAt",
        "--limit", "500",
    )
    if result.returncode != 0:
        print(f"gh issue list failed: {result.stderr}", file=sys.stderr)
        return []
    return _loads(result.stdout, [])


def gh_issue_create(title: str, body: str, labels: list[str]) -> int | None:
    """Create an issue, returning its number, or None on failure."""
    args = ["issue", "create", "--title", title, "--body", body]
    for lbl in labels:
        args.extend(["--label", lbl])
    result = gh(*args)
    if result.returncode != 0:
        print(f"gh issue create failed: {result.stderr}", file=sys.stderr)
        return None
    # Output is the issue URL; extract the number
    match = re.search(r"/issues/(\d+)", result.stdout or "")
    return int(match.group(1)) if match else None


def gh_issue_edit(number: int, labels_add: list[str], labels_remove: list[str]) -> bool:
    """Add and remove labels on an issue. Returns True on success."""
    if not labels_add and not labels_remove:
        return True
    args = ["issue", "edit", str(number)]
    for lbl in labels_add:
        args.extend(["--add-label", lbl])
    for lbl in labels_remove:
        args.extend(["--remove-label", lbl])
    result = gh(*args)
    if result.returncode != 0:
        print(f"gh issue edit failed for #{number}: {result.stderr}", file=sys.stderr)
        return False
    return True


def gh_pr_list_merged(since_ref: str | None) -> list[dict]:
    """Return merged PRs, optionally only those merged after `since_ref`."""
    # Use --search to filter by merge date if given; otherwise list the last 100 merged
    args = [
        "pr", "list",
        "--state", "merged",
        "--json", "number,title,body,mergedAt,mergeCommit",
        "--limit", "200",
    ]
    result = gh(*args)
    if result.returncode != 0:
        print(f"gh pr list failed: {result.stderr}", file=sys.stderr)
        return []
    prs = _loads(result.stdout, [])
    if since_ref:
        since = since_ref
        prs = [p for p in prs if (p.get("mergedAt") or "") > since]
    return prs


# -----------------------------------------------------------------------------
# Local file parsing
# -----------------------------------------------------------------------------


@dataclass
class LocalRecord:
    type: str
    rec_id: str  # e.g. CR-0001, US0023, EP0004
    path: Path
    title: str
    status: str
    priority: str | None
    rec_type: str | None  # CR "type" (feature-request, etc.)
    github_issue: int | None
    body: str
    content_hash: str

    def labels(self) -> list[str]:
        """Build the full sdlc label set for this record."""
        labels = [TYPE_LABELS[self.type]]
        if self.status:
            labels.append(f"{LABEL_PREFIX}:status:{_slug(self.status)}")
        if self.priority:
            labels.append(f"{LABEL_PREFIX}:priority:{self.priority}")
        if self.rec_type:
            labels.append(f"{LABEL_PREFIX}:type:{_slug(self.rec_type)}")
        return labels


def _slug(value: str) -> str:
    """Lowercase, hyphenate, and trim a label component."""
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def _hash_body(body: str) -> str:
    """Return a short content hash used to detect local edits since last push."""
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def _extract_field(text: str, name: str) -> str | None:
    """Pull the value of a `> **Name:** value` metadata line, if present."""
    pattern = rf"^>\s*\*\*{re.escape(name)}:\*\*\s*(.+?)\s*$"
    m = re.search(pattern, text, re.M)
    return m.group(1) if m else None


def _extract_github_issue(text: str) -> int | None:
    """Return the linked GitHub issue number from the metadata, if any."""
    value = _extract_field(text, "GitHub Issue")
    if not value:
        return None
    m = re.search(r"(\d+)", value)
    return int(m.group(1)) if m else None


def parse_local_file(path: Path, type_: str) -> LocalRecord | None:
    """Parse one CR/Story/Epic markdown file into a LocalRecord."""
    text = path.read_text(encoding="utf-8")
    # Title: first `# ` heading
    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_match.group(1).strip() if title_match else path.stem
    # Extract metadata fields
    status = _extract_field(text, "Status") or ""
    priority = _extract_field(text, "Priority")
    rec_type = _extract_field(text, "Type")
    github_issue = _extract_github_issue(text)
    # rec_id is the file's ID prefix. CR files use CR-NNNN-slug, US/EP
    # files use US0001-slug / EP0001-slug with no dash inside the ID.
    id_match = re.match(r"^(CR-\d{4}|US\d{4}|EP\d{4})", path.stem)
    rec_id = id_match.group(1) if id_match else path.stem
    return LocalRecord(
        type=type_,
        rec_id=rec_id,
        path=path,
        title=title,
        status=status,
        priority=priority,
        rec_type=rec_type,
        github_issue=github_issue,
        body=text,
        content_hash=_hash_body(text),
    )


def walk_local(type_: str) -> Iterable[LocalRecord]:
    """Yield parsed records for every CR/Story/Epic file of `type_`."""
    if type_ not in TYPE_DIRS:
        return []
    dir_path, prefix = TYPE_DIRS[type_]
    base = Path(dir_path)
    if not base.exists():
        return []
    result: list[LocalRecord] = []
    for p in sorted(base.glob(f"{prefix}*.md")):
        if p.name == "_index.md":
            continue
        rec = parse_local_file(p, type_)
        if rec:
            result.append(rec)
    return result


# -----------------------------------------------------------------------------
# State file
# -----------------------------------------------------------------------------


def _empty_state() -> dict:
    """Return a fresh, empty sync-state structure."""
    return {
        "version": 1,
        "last_pull": None,
        "last_push": None,
        "last_cascade_ref": None,
        "mappings": {},
    }


def load_state(path: Path = Path(STATE_PATH)) -> dict:
    """Load the sync state, falling back to an empty state if missing or corrupt."""
    if not path.exists():
        return _empty_state()
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(
            f"warning: {path} is not valid JSON; starting from empty state",
            file=sys.stderr,
        )
        return _empty_state()


def save_state(state: dict, path: Path = Path(STATE_PATH)) -> None:
    """Write the sync state to disk, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# -----------------------------------------------------------------------------
# Local file mutation
# -----------------------------------------------------------------------------


def set_github_issue_field(path: Path, number: int) -> None:
    """Write the `> **GitHub Issue:** #N` metadata line into a local file."""
    text = path.read_text(encoding="utf-8")
    if _extract_github_issue(text) == number:
        return
    if _extract_field(text, "GitHub Issue") is not None:
        # Replace existing line
        new_text = re.sub(
            r"^(>\s*\*\*GitHub Issue:\*\*).*$",
            lambda m: f"{m.group(1)} #{number}",
            text,
            count=1,
            flags=re.M,
        )
    else:
        # Insert after Status line if present, else after the title
        insert_line = f"> **GitHub Issue:** #{number}"
        if re.search(r"^>\s*\*\*Status:\*\*", text, re.M):
            new_text = re.sub(
                r"(^>\s*\*\*Status:\*\*.*$)",
                r"\1\n" + insert_line,
                text,
                count=1,
                flags=re.M,
            )
        else:
            new_text = text.rstrip() + "\n\n" + insert_line + "\n"
    path.write_text(new_text, encoding="utf-8")


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------


def cmd_push(args: argparse.Namespace) -> int:
    """Create or update GitHub issues from local CR/Story/Epic files."""
    types = _resolve_types(args.type)
    state = load_state()
    mappings = state.get("mappings", {})
    created = 0
    updated = 0

    for type_ in types:
        for rec in walk_local(type_):
            if rec.github_issue is None:
                title = f"[{rec.rec_id}] {rec.title}"
                labels = rec.labels()
                if args.dry_run:
                    print(f"[DRY] would create issue for {rec.rec_id}: {title}")
                    continue
                number = gh_issue_create(title, rec.body, labels)
                if number is None:
                    print(f"failed to create issue for {rec.rec_id}", file=sys.stderr)
                    continue
                set_github_issue_field(rec.path, number)
                # Re-parse to pick up the new hash
                refreshed = parse_local_file(rec.path, type_)
                if refreshed is None:
                    continue
                mappings[refreshed.rec_id] = {
                    "type": type_,
                    "issue": number,
                    "hash": refreshed.content_hash,
                    "updated_at": now_iso(),
                }
                created += 1
                print(f"[APL] created issue #{number} for {rec.rec_id}")
            else:
                mapped = mappings.get(rec.rec_id)
                if mapped and mapped.get("hash") == rec.content_hash:
                    continue  # No local change since last push
                # Label sync: compute current desired labels, diff against
                # the issue's existing labels
                if args.dry_run:
                    print(
                        f"[DRY] would sync labels on issue #{rec.github_issue} "
                        f"for {rec.rec_id}"
                    )
                    continue
                issues = gh_issue_list(TYPE_LABELS[type_])
                issue = next((i for i in issues if i.get("number") == rec.github_issue), None)
                if issue is None:
                    print(
                        f"issue #{rec.github_issue} not found via gh for "
                        f"{rec.rec_id}; skipping",
                        file=sys.stderr,
                    )
                    continue
                existing_labels = {l["name"] for l in issue.get("labels", [])}
                desired_labels = set(rec.labels())
                add = [l for l in desired_labels if l not in existing_labels]
                remove = [
                    l
                    for l in existing_labels
                    if l.startswith(f"{LABEL_PREFIX}:") and l not in desired_labels
                ]
                if gh_issue_edit(rec.github_issue, add, remove):
                    mappings[rec.rec_id] = {
                        "type": type_,
                        "issue": rec.github_issue,
                        "hash": rec.content_hash,
                        "updated_at": now_iso(),
                    }
                    updated += 1
                    print(
                        f"[APL] synced labels on #{rec.github_issue} "
                        f"for {rec.rec_id}: +{add} -{remove}"
                    )

    if not args.dry_run:
        state["last_push"] = now_iso()
        state["mappings"] = mappings
        save_state(state)

    print(f"push: created={created} updated={updated}")
    return 0


def cmd_pull(args: argparse.Namespace) -> int:
    """List labelled issues that have no local file and need ingesting."""
    types = _resolve_types(args.type)
    state = load_state()
    mappings = state.get("mappings", {})
    pulled = 0

    # Build a reverse index of local records keyed by github_issue for
    # fast "already synced?" checks
    by_issue: dict[int, LocalRecord] = {}
    for type_ in types:
        for rec in walk_local(type_):
            if rec.github_issue is not None:
                by_issue[rec.github_issue] = rec

    for type_ in types:
        label = TYPE_LABELS[type_]
        issues = gh_issue_list(label)
        for issue in issues:
            number = issue.get("number")
            if number in by_issue:
                continue  # Already linked locally
            title = issue.get("title", "")
            body = issue.get("body") or ""
            if args.dry_run:
                print(f"[DRY] would create local {type_} from issue #{number}: {title}")
                continue
            # Defer to the workflow reference files for actually creating
            # the file correctly from a template. This command prints
            # instructions rather than guessing template field values.
            print(
                f"[TODO] pull: issue #{number} labelled {label} has no local "
                f"{type_} file. Run the matching `/sdlc-studio {type_} create` "
                f"workflow with --from-issue {number} to ingest the body into "
                f"the correct template, then re-run `github_sync.py push` to "
                f"write the mapping."
            )
            pulled += 1

    if not args.dry_run:
        state["last_pull"] = now_iso()
        state["mappings"] = mappings
        save_state(state)

    print(f"pull: issues_needing_ingest={pulled}")
    return 0


_CLOSES_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.I)
_STORY_REF_RE = re.compile(r"sdlc:story\s+(US\d{4})", re.I)
_CR_REF_RE = re.compile(r"sdlc:cr\s+(CR-\d{4})", re.I)


def cmd_cascade(args: argparse.Namespace) -> int:
    """Find merged PRs whose bodies reference stories/CRs to cascade."""
    state = load_state()
    since = args.since or state.get("last_cascade_ref")
    prs = gh_pr_list_merged(since)
    if not prs:
        print("no merged PRs found in range")
        return 0

    referenced_stories: set[int] = set()
    referenced_story_ids: set[str] = set()
    referenced_cr_ids: set[str] = set()

    for pr in prs:
        body = pr.get("body") or ""
        for m in _CLOSES_RE.finditer(body):
            referenced_stories.add(int(m.group(1)))
        for m in _STORY_REF_RE.finditer(body):
            referenced_story_ids.add(m.group(1).upper())
        for m in _CR_REF_RE.finditer(body):
            referenced_cr_ids.add(m.group(1).upper())

    if not (referenced_stories or referenced_story_ids or referenced_cr_ids):
        print("no sdlc references found in merged PR bodies")
        return 0

    # Map issue numbers back to local stories via github_issue field
    local_stories_by_issue: dict[int, LocalRecord] = {}
    for rec in walk_local("story"):
        if rec.github_issue is not None:
            local_stories_by_issue[rec.github_issue] = rec

    triggered: list[str] = []
    for issue_num in referenced_stories:
        rec = local_stories_by_issue.get(issue_num)
        if rec is None:
            continue
        triggered.append(rec.rec_id)
    for sid in referenced_story_ids:
        triggered.append(sid)
    for cid in referenced_cr_ids:
        triggered.append(cid)

    if not triggered:
        print("found sdlc references but no matching local records")
        return 0

    print(
        "cascade candidates (trigger Story Completion Cascade via reconcile):"
    )
    for ident in sorted(set(triggered)):
        print(f"  - {ident}")
    print(
        "next step: `/sdlc-studio reconcile --story <id>` (or --scope stories)"
        " to mark these Done after PR merge."
    )

    if not args.dry_run and prs:
        state["last_cascade_ref"] = prs[0].get("mergedAt")
        save_state(state)

    return 0


def cmd_state(args: argparse.Namespace) -> int:
    """Print the current sync-state file as JSON."""
    state = load_state()
    print(json.dumps(state, indent=2))
    return 0


def _resolve_types(type_arg: str) -> list[str]:
    """Expand a --type argument (including `all`) into a list of types."""
    if type_arg == "all":
        return ["cr", "story", "epic"]
    if type_arg in TYPE_LABELS:
        return [type_arg]
    raise SystemExit(f"error: unknown --type: {type_arg}")


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for all subcommands."""
    p = argparse.ArgumentParser(
        prog="github_sync.py",
        description="Two-way sync between local sdlc-studio records and GitHub Issues.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    push = sub.add_parser("push", help="Create or update issues from local files")
    push.add_argument("--type", default="cr", choices=["cr", "story", "epic", "all"])
    push.add_argument("--dry-run", action="store_true")
    push.set_defaults(func=cmd_push)

    pull = sub.add_parser("pull", help="Fetch labelled issues for local ingest")
    pull.add_argument("--type", default="cr", choices=["cr", "story", "epic", "all"])
    pull.add_argument("--dry-run", action="store_true")
    pull.set_defaults(func=cmd_pull)

    cas = sub.add_parser("cascade", help="Find merged PRs that should trigger cascades")
    cas.add_argument("--since", help="Only consider PRs merged after this ISO timestamp")
    cas.add_argument("--dry-run", action="store_true")
    cas.set_defaults(func=cmd_cascade)

    st = sub.add_parser("state", help="Print sync state")
    st.set_defaults(func=cmd_state)

    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 127


if __name__ == "__main__":
    sys.exit(main())
