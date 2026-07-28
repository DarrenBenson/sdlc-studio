#!/usr/bin/env python3
"""SDLC Studio lessons manager (both tiers).

Two lesson tiers (see help/lessons.md and reference-agentic-lessons.md):

  Project tier  `sdlc-studio/.local/lessons.md` in the consuming project -
                the DEFAULT tier: agentic-wave failure memory for this repo,
                reverse-chronological `## L-NNNN:` entries.
  Skill tier    the skill's own `lessons/` folder - durable, generalisable
                `LL{NNNN}-{slug}.md` lessons indexed in `_index.md`. Reached
                with `--global`, the deliberate promotion, never the reflex.

`add --global` only ever writes where git will actually hold the file: the lessons
registry it appends to must be version-controlled (not merely sitting inside a work
tree - a gitignored vendored install passes that and is still invisible to git). An
installed or vendored copy is a deployment artefact, replaced wholesale by the next
skill update, so a lesson authored there is deleted; the write is refused rather than
falsely reported. Set `skill_source_repo` in the project's `sdlc-studio/.config.yaml`
to give `--global` the skill SOURCE checkout to write to.

Subcommands:
  list        Print project-tier lessons (newest first); --global for the skill tier.
  add         Append a project-tier entry, stamped with a validity horizon; --global
              promotes into the skill tier (next LL id, file from _template.md, index
              row appended).
  prune       Drop project-tier entries tied to old epics.
  recall      Surface skill-tier lessons matching tags or a query; --all searches
              both tiers.
  revalidate  List open lessons with their horizon; --close / --extend / --stamp them.
  summary     Regenerate the committed LESSONS-SUMMARY.md, the digest read at sprint start.

The close loop is a mechanism, not doctrine: `summary` is DERIVED output of the lessons log,
so `gate --require-retro` (the sprint-close gate) recomputes the digest and fails loud when
the committed summary no longer matches, or when an open lesson has passed its validity
horizon without being closed or extended. `sprint plan` carries the digest into the plan an
agent reads at sprint start.

Output: text by default, or JSON with --format json.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
# The family root resolver, not a second path-joining idiom: `resolve_root` honours a root
# the caller NAMED and discovers upward from the family default `.`, `under_root` anchors a
# relative path on the result. Reached through the module, per the monkeypatch rule.
import verify_ac  # noqa: E402  (sibling)

DEFAULT_PROJECT_FILE = "sdlc-studio/.local/lessons.md"
DEFAULT_SUMMARY_FILE = "sdlc-studio/retros/LESSONS-SUMMARY.md"
SKILL_LESSONS_DIR = Path(__file__).resolve().parent.parent / "lessons"
# How long a project lesson stays valid before it must be re-validated (closed or extended).
# Override per project with `lessons.validity_days` in sdlc-studio/.config.yaml.
DEFAULT_VALIDITY_DAYS = 90
VALIDITY_DAYS_KEY = "lessons.validity_days"
SOURCE_REPO_KEY = "skill_source_repo"
RUNNING_SKILL = "the running skill"
# Repo-only files a release is cut from: present in the sdlc-studio SOURCE checkout, absent
# from every installed or vendored copy of the skill payload.
SOURCE_MARKERS = ("install.sh", "tools/validate_skill.py")

PROJECT_ENTRY_RE = re.compile(r"^##\s+(L-\d{4}):\s*(.+?)\s*$")
FIELD_BULLET_RE = re.compile(r"^-\s+\*\*([^*]+):\*\*\s*(.*)$")
# A rendered digest line, read back out of LESSONS-SUMMARY.md: `- **L-0001: title** - gist`.
# The bold delimiters make the split unambiguous even when the gist itself contains " - ".
SUMMARY_LINE_RE = re.compile(r"^-\s+\*\*(L-\d{4}):\s*(.+?)\*\*\s*(?:-\s*(.*))?$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INDEX_ROW_RE = re.compile(
    r"^\|\s*\[(LL\d{4})\]\(([^)]+)\)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$"
)
LL_FILE_RE = re.compile(r"^LL(\d{4})-")

PROJECT_HEADER = """# Project Lessons

**Last Updated:** {date}

<!-- Append new entries at the top. Keep each entry under 10 lines. -->
"""


# -----------------------------------------------------------------------------
# Project tier
# -----------------------------------------------------------------------------


def parse_project_lessons(text: str) -> list[dict]:
    """Entries from a project lessons file, in file order (newest first)."""
    entries: list[dict] = []
    current: dict | None = None
    body: list[str] = []
    for line in text.splitlines():
        m = PROJECT_ENTRY_RE.match(line)
        if m:
            if current:
                current["body"] = "\n".join(body).strip()
                entries.append(current)
            current = {"id": m.group(1), "title": m.group(2), "fields": {}}
            body = []
            continue
        if current is None:
            continue
        body.append(line)
        f = FIELD_BULLET_RE.match(line)
        if f:
            current["fields"][f.group(1).strip().lower()] = f.group(2).strip()
    if current:
        current["body"] = "\n".join(body).strip()
        entries.append(current)
    return entries


def project_header_of(text: str) -> str:
    """Everything before the first `## L-NNNN:` heading (the file header)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if PROJECT_ENTRY_RE.match(line):
            return "\n".join(lines[:i]).rstrip() + "\n"
    return text.rstrip() + "\n" if text.strip() else ""


def refresh_last_updated(header: str) -> str:
    """Set the header's `**Last Updated:**` line to today when present (the PROJECT_HEADER template
    always carries it); a header without the line is returned unchanged."""
    today = sdlc_md.now_date()
    if "**Last Updated:**" in header:
        return re.sub(r"\*\*Last Updated:\*\*.*", f"**Last Updated:** {today}", header)
    return header


def render_entry(entry: dict) -> str:
    """One project-tier entry back as markdown."""
    out = [f"## {entry['id']}: {entry['title']}", ""]
    if entry["body"]:
        out.append(entry["body"])
    return "\n".join(out).rstrip() + "\n"


def write_project_file(path: Path, header: str, entries: list[dict]) -> None:
    """Rewrite the lessons file: refreshed header, then entries newest first."""
    parts = [refresh_last_updated(header).rstrip() + "\n"]
    parts.extend("\n" + render_entry(e) for e in entries)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts), encoding="utf-8")


def next_project_id(entries: list[dict]) -> str:
    """Next free L-NNNN, scanning existing entry IDs for the maximum."""
    nums = [sdlc_md.id_number(e["id"]) or 0 for e in entries]
    return f"L-{(max(nums) if nums else 0) + 1:04d}"


# -----------------------------------------------------------------------------
# Skill tier
# -----------------------------------------------------------------------------


def parse_index_rows(index_path: Path) -> list[dict]:
    """Lesson rows from the skill tier's `_index.md` table."""
    rows: list[dict] = []
    if not index_path.is_file():
        return rows
    for line in index_path.read_text(encoding="utf-8").splitlines():
        m = INDEX_ROW_RE.match(line)
        if m:
            rows.append({
                "id": m.group(1),
                "file": m.group(2),
                "title": m.group(3),
                "tags": [t.strip() for t in m.group(4).split(",") if t.strip()],
            })
    return rows


def next_global_id(lessons_dir: Path) -> str:
    """Next free LL{NNNN}, scanning existing LL files for the maximum."""
    nums = [0]
    for p in sdlc_md.walk_glob(lessons_dir, "LL*.md"):
        m = LL_FILE_RE.match(p.name)
        if m:
            nums.append(int(m.group(1)))
    return f"LL{max(nums) + 1:04d}"


def render_global_lesson(template: str, id_: str, title: str, tags: list[str],
                         body: str, origin: str, date: str) -> str:
    """Fill `_template.md` for a new skill-tier lesson.

    Strips the leading HTML usage comment, fills the frontmatter and the
    Lesson paragraph; the remaining `{{placeholder}}` sections stay for the
    author to complete by judgement.
    """
    lines = template.splitlines()
    i = 0
    if lines and lines[0].lstrip().startswith("<!--"):
        while i < len(lines) and "-->" not in lines[i]:
            i += 1
        i += 1
        while i < len(lines) and not lines[i].strip():
            i += 1
    out: list[str] = []
    for line in lines[i:]:
        if line.startswith("id:"):
            out.append(f"id: {id_}")
        elif line.startswith("title:"):
            out.append(f"title: {title}")
        elif line.startswith("tags:"):
            out.append(f"tags: [{', '.join(tags)}]")
        elif line.startswith("added:"):
            out.append(f"added: {date}")
        elif line.startswith("origin:"):
            out.append(f"origin: {origin}")
        elif line.startswith("**Lesson.**"):
            out.append(f"**Lesson.** {body}")
        else:
            out.append(line)
    return "\n".join(out).rstrip() + "\n"


def append_index_row(index_path: Path, id_: str, filename: str, title: str,
                     tags: list[str]) -> None:
    """Append a lesson row to the `_index.md` table (after the last row)."""
    row = f"| [{id_}]({filename}) | {title} | {', '.join(tags)} |"
    lines = index_path.read_text(encoding="utf-8").splitlines()
    last_row = None
    separator = None
    for i, line in enumerate(lines):
        if INDEX_ROW_RE.match(line):
            last_row = i
        elif separator is None and re.match(r"^\|\s*-{3,}", line.replace(" ", "")):
            separator = i
    anchor = last_row if last_row is not None else separator
    if anchor is None:
        raise ValueError(f"no lessons table found in {index_path}")
    lines.insert(anchor + 1, row)
    sdlc_md.atomic_write(index_path, "\n".join(lines) + "\n")


# -----------------------------------------------------------------------------
# Skill tier: a tracked destination, or nothing
# -----------------------------------------------------------------------------


class ResolveError(Exception):
    """The skill-tier destination could not be resolved to a real lessons registry."""


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess | None:
    """Run git in `cwd`, or None when it cannot be run at all."""
    # Scrub repo-redirecting env: a run from inside another repo's hook would otherwise make
    # git answer for THAT repo, not for the destination directory.
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    try:
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                              timeout=10, env=env, check=False)
    except (OSError, subprocess.SubprocessError):
        return None


def _git_ok(args: list[str], cwd: Path) -> bool:
    """True when git ran and exited 0."""
    proc = _git(args, cwd)
    return proc is not None and proc.returncode == 0


def untracked_reason(lessons_dir: Path) -> str | None:
    """Why a lesson written into `lessons_dir` would not survive, or None when git holds it.

    Work-tree MEMBERSHIP is not enough: a gitignored directory inside a work tree passes
    `rev-parse --is-inside-work-tree` while git never sees a single file in it, so the next
    update deletes the lesson exactly as an install would. The proof that git will hold the
    write is that git already holds the registry the write joins - the `_index.md` this
    lesson's row is appended to must be in the index. Anything unprovable (git absent, git
    erroring) counts as unheld: the write is refused, never reported as a success it cannot
    stand behind.
    """
    if not lessons_dir.is_dir():
        return f"{lessons_dir} does not exist"
    inside = _git(["rev-parse", "--is-inside-work-tree"], lessons_dir)
    if inside is None or inside.returncode != 0 or inside.stdout.strip() != "true":
        return "it is not inside a git work tree"
    if _git_ok(["check-ignore", "-q", "."], lessons_dir):
        return ("git ignores it (a gitignore rule matches the directory), so a file written "
                "there is invisible to git")
    if not _git_ok(["ls-files", "--error-unmatch", "_index.md"], lessons_dir):
        return (f"git does not track its registry ({lessons_dir / '_index.md'}), so a lesson "
                "written beside it is not version-controlled either")
    return None


def is_tracked_destination(lessons_dir: Path) -> bool:
    """True when git version-controls the lessons registry in `lessons_dir`."""
    return untracked_reason(Path(lessons_dir)) is None


def is_skill_source_checkout(lessons_dir: Path) -> bool:
    """True when `lessons_dir` is the registry of an sdlc-studio SOURCE checkout - the repo a
    release is cut from - rather than a copy vendored into some other project.

    A vendored install (`install.sh --local` puts one inside the consuming project's work
    tree) can be a perfectly tracked git directory, and committing a lesson into it still
    ships that lesson with no release at all, and the next install replaces the folder. Only
    the source repo carries the repo-only release machinery, so that is what is checked.
    """
    top = _git(["rev-parse", "--show-toplevel"], lessons_dir)
    if top is None or top.returncode != 0:
        return False
    root = Path(top.stdout.strip())
    if not all((root / marker).is_file() for marker in SOURCE_MARKERS):
        return False
    try:
        canonical = root / ".claude" / "skills" / "sdlc-studio" / "lessons"
        return lessons_dir.resolve() == canonical.resolve()
    except OSError:
        return False


def resolve_global_dir(explicit: str | None, repo_root) -> tuple[Path, str]:
    """The skill-tier lessons directory to write to, plus a label naming where it came from.

    Order: an explicit `--lessons-dir`; then the project's `skill_source_repo` config key
    (the skill source checkout, which is version-controlled); then the running skill's own
    `lessons/` folder - which is the INSTALLED copy in normal use, and is caught by the
    tracked-destination guard.
    """
    if explicit:
        return Path(explicit).expanduser(), "--lessons-dir"
    configured = sdlc_md.project_override(repo_root, SOURCE_REPO_KEY)
    if configured:
        base = Path(str(configured)).expanduser()
        for cand in (base / ".claude" / "skills" / "sdlc-studio" / "lessons",
                     base / "lessons", base):
            if (cand / "_index.md").is_file():
                return cand, SOURCE_REPO_KEY
        raise ResolveError(
            f"{SOURCE_REPO_KEY} is set to {base}, but no lessons registry (a directory with "
            "an _index.md) was found under it. Point it at the root of your sdlc-studio "
            "source checkout.")
    return SKILL_LESSONS_DIR, RUNNING_SKILL


def refusal(lessons_dir: Path, source: str, reason: str) -> str:
    """The refusal: where the write was aimed, why it would not survive, and how to fix it."""
    return (
        f"error: refusing to write a skill-tier lesson into {lessons_dir}\n"
        f"  Source: {source}.\n"
        f"  Why: {reason}. The lesson would be lost with nothing to warn you.\n"
        "  Remedies:\n"
        "    1. Record it as a PROJECT lesson (drop --global). That is the default tier and "
        f"the right\n       home for most lessons: {DEFAULT_PROJECT_FILE}.\n"
        "    2. Promote deliberately: point the project at the skill SOURCE checkout in "
        "sdlc-studio/.config.yaml\n"
        f"         {SOURCE_REPO_KEY}: /path/to/sdlc-studio\n"
        "       then re-run; the lesson lands in a version-controlled file that `git status` "
        "shows, and\n       ships with the next skill release once committed.\n"
        "    3. Or pass that checkout directly: "
        "--lessons-dir <checkout>/.claude/skills/sdlc-studio/lessons"
    )


NOT_SOURCE_REASON = (
    "it is the running skill's own lessons/ folder and that is not an sdlc-studio source "
    "checkout, so it is an installed or vendored copy - the next skill update replaces the "
    "folder wholesale, and a commit there ships the lesson with no release"
)


# -----------------------------------------------------------------------------
# Subcommands
# -----------------------------------------------------------------------------


def cmd_list(args: argparse.Namespace) -> int:
    """Print lessons: project tier by default, skill tier with --global."""
    if args.global_:
        rows = parse_index_rows(Path(args.lessons_dir or SKILL_LESSONS_DIR) / "_index.md")
        if args.format == "json":
            print(json.dumps({"tier": "skill", "lessons": rows, "count": len(rows)},
                             indent=2))
            return 0
        if not rows:
            print("No skill-tier lessons found.")
            return 0
        for r in rows:
            print(f"{r['id']}  {r['title']}  [{', '.join(r['tags'])}]")
        print(f"{len(rows)} lesson(s)")
        return 0
    path = _project_file(args)
    if not path.is_file():
        if args.format == "json":
            print(json.dumps({"tier": "project", "lessons": [], "count": 0}, indent=2))
        else:
            print(f"No lessons recorded yet ({path} does not exist).")
        return 0
    entries = parse_project_lessons(path.read_text(encoding="utf-8"))
    if args.format == "json":
        print(json.dumps({"tier": "project", "lessons": entries,
                          "count": len(entries)}, indent=2))
        return 0
    if not entries:
        print(f"No lessons recorded yet in {path}.")
        return 0
    for e in entries:
        print(f"## {e['id']}: {e['title']}")
        if e["body"]:
            print(e["body"])
        print()
    print(f"{len(entries)} lesson(s), newest first")
    return 0


def resolve_prose(args: argparse.Namespace, keys: tuple[str, ...],
                  required: tuple[str, ...] = ()) -> None:
    """Resolve the subcommand's free-prose fields through the ONE shared loader and put them
    back on `args`, so the rest of the command reads them exactly as before.

    A lesson's body is the field most likely to quote a command, which is precisely what a
    shell eats out of an argument. Raises ValueError when a required field is in neither the
    document nor the flags."""
    import file_finding  # noqa: PLC0415 - the shared prose-fields loader, as elsewhere
    fields = file_finding.resolve_prose_fields(
        getattr(args, "fields_file", None),
        {k: getattr(args, k, None) for k in keys}, allowed=keys)
    for key in keys:
        setattr(args, key, fields.get(key))
    missing = [k for k in required if not str(fields.get(k) or "").strip()]
    if missing:
        raise ValueError(f"no {'/'.join(missing)} - pass --{missing[0]}, or a "
                         f"\"{missing[0]}\" key in the --fields-file document")


def _add_fields_file_arg(sp: argparse.ArgumentParser, example: str) -> None:
    """Declare the non-shell input path on a subparser, spelled the same way everywhere."""
    sp.add_argument("--fields-file", dest="fields_file", metavar="FIELDS.json",
                    help=f"read the prose from a JSON object ({example}) instead of the flags, "
                         f"so text carrying shell metacharacters is stored verbatim rather than "
                         f"interpreted by the shell; `-` reads the document from stdin")


def cmd_add(args: argparse.Namespace) -> int:
    """Append a project-tier entry, or promote to the skill tier with --global."""
    try:
        resolve_prose(args, ("title", "body"), required=("title", "body"))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    if args.global_:
        try:
            lessons_dir, source = resolve_global_dir(args.lessons_dir, getattr(args, "root", "."))
        except ResolveError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        # Structural checks first (they write nothing), so a malformed registry reports the
        # part that is missing rather than being masked by the survival guard below.
        template_path = lessons_dir / "_template.md"
        index_path = lessons_dir / "_index.md"
        if not template_path.is_file():
            print(f"error: template not found: {template_path}", file=sys.stderr)
            return 1
        if not index_path.is_file():
            print(f"error: index not found: {index_path}", file=sys.stderr)
            return 1
        # Then: nothing is authored until git provably holds the destination...
        reason = untracked_reason(lessons_dir)
        if reason:
            print(refusal(lessons_dir, source, reason), file=sys.stderr)
            return 1
        # ...and, when the destination was not chosen deliberately, until it is the skill
        # SOURCE repo. A vendored copy can be tracked and still reach no release.
        if source == RUNNING_SKILL and not is_skill_source_checkout(lessons_dir):
            print(refusal(lessons_dir, source, NOT_SOURCE_REASON), file=sys.stderr)
            return 1
        id_ = next_global_id(lessons_dir)
        filename = f"{id_}-{sdlc_md.slug(args.title)}.md"
        dest = lessons_dir / filename
        if dest.exists():
            print(f"error: refusing to overwrite {dest}", file=sys.stderr)
            return 1
        origin = args.origin or Path.cwd().name
        content = render_global_lesson(
            template_path.read_text(encoding="utf-8"),
            id_, args.title, tags, args.body, origin, sdlc_md.now_date(),
        )
        dest.write_text(content, encoding="utf-8")
        append_index_row(index_path, id_, filename, args.title, tags)
        print(f"Wrote {id_} to {dest} and appended the index row")
        print("git version-controls that registry, so `git status` there shows the lesson; "
              "commit it to ship it with the next skill release.")
        return 0
    path = _project_file(args)
    if path.is_file():
        text = path.read_text(encoding="utf-8")
    else:
        text = PROJECT_HEADER.format(date=sdlc_md.now_date())
    entries = parse_project_lessons(text)
    header = project_header_of(text)
    entry: dict = {"id": next_project_id(entries), "title": args.title, "fields": {}}
    bullets = []
    if args.epic:
        bullets.append(f"- **Epic:** {args.epic}")
    if args.wave is not None:
        bullets.append(f"- **Wave:** {args.wave}")
    if tags:
        bullets.append(f"- **Tags:** {', '.join(tags)}")
    # Every new lesson carries a validity horizon, so the close gate's re-validation step has
    # something to judge and the log cannot silently accrue lessons no one has re-read.
    today = sdlc_md.now_date()
    days = resolve_validity_days(getattr(args, "root", "."), getattr(args, "validity_days", None))
    bullets.append(f"- **Added:** {today}")
    bullets.append(f"- **Review-by:** {add_days(today, days)}")
    body_parts = []
    if bullets:
        body_parts.append("\n".join(bullets))
    if args.body:
        body_parts.append(args.body)
    entry["body"] = "\n\n".join(body_parts)
    write_project_file(path, header, [entry] + entries)
    print(f"Wrote {entry['id']} to {path}")
    return 0


def cmd_prune(args: argparse.Namespace) -> int:
    """Drop project-tier entries tied to epics <= --older, or == --epic."""
    path = _project_file(args)
    if not path.is_file():
        print(f"No lessons file at {path}; nothing to prune.")
        return 0
    text = path.read_text(encoding="utf-8")
    entries = parse_project_lessons(text)
    target = args.older or args.epic
    target_num = sdlc_md.id_number(target)
    if target_num is None:
        print(f"error: '{target}' is not a valid epic ID (expected EP000N)",
              file=sys.stderr)
        return 2

    def drops(e: dict) -> bool:
        epic = e["fields"].get("epic")
        num = sdlc_md.id_number(epic) if epic else None
        if num is None:
            return False
        return num <= target_num if args.older else num == target_num

    dropped = [e for e in entries if drops(e)]
    kept = [e for e in entries if not drops(e)]
    if not dropped:
        print("Nothing to prune.")
        return 0
    write_project_file(path, project_header_of(text), kept)
    for e in dropped:
        epic = e["fields"].get("epic", "?")
        print(f"Pruned {e['id']}: {e['title']} ({epic})")
    print(f"{len(dropped)} pruned, {len(kept)} kept")
    return 0


def _matches(title: str, tags: list[str], want_tags: list[str], query: str | None) -> bool:
    """Case-insensitive substring match of tags/query against title and tags."""
    hay_title = title.lower()
    hay_tags = [t.lower() for t in tags]
    if want_tags:
        ok = any(w in t for w in want_tags for t in hay_tags)
        if not ok:
            return False
    if query:
        q = query.lower()
        if q not in hay_title and not any(q in t for t in hay_tags):
            return False
    return True


def cmd_recall(args: argparse.Namespace) -> int:
    """Print skill-tier lessons matching --tags/--query (both tiers with --all)."""
    want_tags = [t.strip().lower() for t in (args.tags or "").split(",") if t.strip()]
    rows = parse_index_rows(Path(args.lessons_dir or SKILL_LESSONS_DIR) / "_index.md")
    matches = [
        {**r, "tier": "skill"}
        for r in rows if _matches(r["title"], r["tags"], want_tags, args.query)
    ]
    if args.all:
        path = _project_file(args)
        if path.is_file():
            for e in parse_project_lessons(path.read_text(encoding="utf-8")):
                tags = [t.strip() for t in e["fields"].get("tags", "").split(",") if t.strip()]
                if _matches(e["title"], tags, want_tags, args.query):
                    matches.append({"id": e["id"], "file": str(path),
                                    "title": e["title"], "tags": tags,
                                    "tier": "project"})
    if args.format == "json":
        print(json.dumps({"matches": matches, "count": len(matches)}, indent=2))
        return 0
    if not matches:
        print("No matching lessons.")
        return 0
    for m in matches:
        tier = "" if m["tier"] == "skill" else "  (project tier)"
        print(f"{m['id']}  {m['title']}  [{', '.join(m['tags'])}]  -> {m['file']}{tier}")
    print(f"{len(matches)} match(es)")
    return 0


# -----------------------------------------------------------------------------
# Re-validation + rolling summary
# -----------------------------------------------------------------------------


def is_closed(entry: dict) -> bool:
    """A lesson is closed (no longer valid) when it carries a Status field starting 'Closed'."""
    return entry["fields"].get("status", "").strip().lower().startswith("closed")


def upsert_field(entry: dict, name: str, value: str) -> None:
    """Set `- **Name:** value` on an entry, in place: replace the existing bullet, or insert
    one at the end of the entry's leading bullet block (so field bullets stay together and a
    prose paragraph never gets a bullet stranded after it)."""
    key = name.strip().lower()
    lines = entry["body"].splitlines() if entry["body"] else []
    bullet = f"- **{name}:** {value}"
    for i, line in enumerate(lines):
        m = FIELD_BULLET_RE.match(line)
        if m and m.group(1).strip().lower() == key:
            lines[i] = bullet
            break
    else:
        last = -1  # end of the leading run of bullets/blanks
        for i, line in enumerate(lines):
            if FIELD_BULLET_RE.match(line):
                last = i
            elif line.strip():
                break
        lines.insert(last + 1, bullet)
        # An entry whose body is a bare paragraph gets its first bullet inserted above prose.
        # Without a blank line the paragraph renders as a lazy continuation of the list item.
        nxt = last + 2
        if nxt < len(lines) and lines[nxt].strip() and not FIELD_BULLET_RE.match(lines[nxt]):
            lines.insert(nxt, "")
    entry["body"] = "\n".join(lines).strip()
    entry["fields"][key] = value


def _is_iso_date(value: str) -> bool:
    return bool(ISO_DATE_RE.match(value.strip()))


def add_days(iso: str, days: int) -> str:
    """`iso` + `days`, as a YYYY-MM-DD string."""
    return (date.fromisoformat(iso.strip()) + timedelta(days=days)).isoformat()


def resolve_validity_days(repo_root, explicit: int | None = None) -> int:
    """The validity window: an explicit flag, else the project's `lessons.validity_days`,
    else the default. A non-integer config value degrades to the default rather than
    crashing the gate that reads it."""
    if explicit is not None:
        return int(explicit)
    configured = sdlc_md.project_override(repo_root, VALIDITY_DAYS_KEY)
    try:
        return int(configured) if configured is not None else DEFAULT_VALIDITY_DAYS
    except (TypeError, ValueError):
        return DEFAULT_VALIDITY_DAYS


def horizon_of(entry: dict, validity_days: int = DEFAULT_VALIDITY_DAYS) -> str | None:
    """The date an open lesson must be re-validated by: its explicit `Review-by`, else its
    `Added` date plus the validity window. None when the entry carries neither, or carries an
    unparseable date - an UNPROVABLE horizon, which the close gate reports rather than waves
    through (unproven is not proof; a legacy log must not pass vacuously)."""
    review_by = entry["fields"].get("review-by", "").strip()
    if review_by:
        return review_by if _is_iso_date(review_by) else None
    added = entry["fields"].get("added", "").strip()
    if added and _is_iso_date(added):
        return add_days(added, validity_days)
    return None


def default_project_file(repo_root) -> Path:
    return Path(repo_root) / DEFAULT_PROJECT_FILE


def default_summary_path(repo_root) -> Path:
    return Path(repo_root) / DEFAULT_SUMMARY_FILE


def digest_items(entries: list[dict]) -> list[dict]:
    """The still-valid lessons, in log order (newest first): id, title, and the one-line gist
    the summary carries. The single source of the digest's content - the renderer, the
    staleness check, and the sprint plan all read this, so they cannot drift apart."""
    items = []
    for e in entries:
        if is_closed(e):
            continue
        gist = (e["fields"].get("rule") or e["fields"].get("fix")
                or e["fields"].get("applies to") or "").strip()
        items.append({"id": e["id"], "title": e["title"].strip(), "gist": gist})
    return items


def _canon(item: dict) -> str:
    """One digest item as a comparable string, with runs of whitespace collapsed and EMPHASIS
    MARKERS REMOVED. The comparison unit for staleness: it is insensitive to how the summary is
    laid out (blank lines, indentation, trailing spaces, boilerplate prose) and sensitive to
    every part of a lesson the digest actually carries (id, title, gist).

    Asterisks are dropped because the round trip through the file is not stable across them. The
    renderer writes `- **{id}: {title}**`, and `SUMMARY_LINE_RE` finds the title by scanning to
    the first `**` - so a lesson whose OWN text starts with bold splits at the wrong marker, and
    the same lesson reads back with the emphasis in a different place. The parts are all still
    there and still compared; only the markers move. Comparing on markup made the blocking
    `lessons-summary` lane report one lesson as BOTH added and removed, with no edit that could
    satisfy it - `lessons summary` regenerated the identical file every time.

    ONLY asterisks. Underscores and backticks are NOT stripped: the renderer emits neither, so
    neither can move in the round trip, and both are load-bearing in the identifiers these
    lessons carry - stripping them made `two_role_after` compare equal to `tworoleafter`, so the
    digest would have stopped noticing a real edit. A normalisation wider than the instability it
    corrects buys nothing and blinds the check.
    """
    text = f"{item['id']}: {item['title']}"
    if item["gist"]:
        text += f" - {item['gist']}"
    text = re.sub(r"\*+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def expected_digest(entries: list[dict]) -> list[str]:
    """What the summary must say, computed from the lessons log."""
    return [_canon(i) for i in digest_items(entries)]


def _unwrapped_lines(text: str) -> list[str]:
    """The summary's lines, with hard-wrapped bullets folded back into one line.

    A consuming project whose markdown linter enforces a line length wraps a long digest
    bullet onto a second, INDENTED line. That is the same lesson, so it must read as the same
    lesson - otherwise the project's linter and this gate are in permanent, unfixable
    disagreement. The join is anchored on the indentation: a flush-left paragraph after the
    bullets (someone's footer note) is left alone rather than folded into the last lesson's
    gist, where it would corrupt the comparison instead of being ignored by it.
    """
    out: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            out.append("")
            continue
        if (out and raw[:1].isspace() and out[-1].startswith("- ")
                and not stripped.startswith("- ")):
            out[-1] += " " + stripped
        else:
            out.append(stripped)
    return out


def summary_items(text: str) -> list[dict]:
    """The digest items a LESSONS-SUMMARY.md actually carries (its bullet lines)."""
    items = []
    for line in _unwrapped_lines(text):
        m = SUMMARY_LINE_RE.match(line)
        if m:
            items.append({"id": m.group(1), "title": m.group(2).strip(),
                          "gist": (m.group(3) or "").strip()})
    return items


def parse_summary_digest(text: str) -> list[str]:
    """What the summary says, in the same comparable form as `expected_digest`."""
    return [_canon(i) for i in summary_items(text)]


def _elide(names: list[str]) -> str:
    """Name up to three digest items by id, bound the line."""
    return ", ".join(n.split(" - ")[0] for n in names[:3]) + \
        (f" (+{len(names) - 3} more)" if len(names) > 3 else "")


def _drift_reason(summary: Path, added: list[str], removed: list[str]) -> str:
    """Name what changed, bounded. Reordering (same lessons, different order) is drift too:
    the generator's order is deterministic, so a differently-ordered file was not generated
    from this log."""
    elide = _elide
    parts = []
    if added:
        parts.append(f"{len(added)} lesson(s) added since it was regenerated: {elide(added)}")
    if removed:
        parts.append(f"{len(removed)} closed or removed since: {elide(removed)}")
    if not parts:
        parts.append("its lessons are out of order")
    return (f"{summary.name} is STALE - {'; '.join(parts)}. "
            "Regenerate it: scripts/lessons.py summary")


def summary_status(repo_root, project_file=None, summary_path=None) -> dict:
    """Is the committed LESSONS-SUMMARY.md the digest of the CURRENT lessons log?

    The summary is derived output, like an `_index.md`: the check recomputes the digest from
    the log and compares it with the digest parsed back out of the file. Nothing is stamped
    and nothing is trusted - the only way to a green verdict is for the file to actually say
    what the log implies. That is what makes it robust to a lesson being CLOSED (its line
    must disappear) as well as added, and to the count staying level while the membership
    changes; and what stops it false-firing on how the file is laid out.
    """
    log = Path(project_file) if project_file else default_project_file(repo_root)
    summary = Path(summary_path) if summary_path else default_summary_path(repo_root)
    if not log.is_file():
        # An absent log is only "nothing to summarise" when the COMMITTED summary agrees that
        # there is nothing. A summary still listing lessons with no log behind it is a
        # contradiction the gate must not pass over: otherwise `rm .local/lessons.md` is a
        # one-command defeat of the whole close gate (the log is gitignored, so deleting it
        # costs nothing and shows in no diff). The asymmetry is checkable without tracking
        # the log - the summary is the tracked half, and it is the one making a claim.
        listed = parse_summary_digest(summary.read_text(encoding="utf-8")) \
            if summary.is_file() else []
        if not listed:
            return {"applicable": False, "stale": False, "open": 0, "added": [], "removed": [],
                    "log": str(log), "summary": str(summary),
                    "reason": f"no lessons log at {log} and no lessons in the summary - "
                              "nothing to summarise"}
        return {
            "applicable": True, "stale": True, "open": len(listed), "added": [],
            "removed": listed, "log": str(log), "summary": str(summary),
            "reason": (f"{summary.name} lists {len(listed)} lesson(s) ({_elide(listed)}) but "
                       f"the log they are derived from ({log}) does not exist - the lessons "
                       "cannot be re-validated or the digest regenerated. Restore the log, or "
                       "if this project genuinely has no lessons, run `lessons summary` to "
                       "clear the digest."),
        }
    entries = parse_project_lessons(log.read_text(encoding="utf-8"))
    expected = expected_digest(entries)
    base = {"applicable": True, "open": len(expected), "log": str(log),
            "summary": str(summary)}
    if not summary.is_file():
        return {**base, "stale": True, "added": expected, "removed": [],
                "reason": (f"{summary} does not exist, but {len(expected)} still-valid "
                           f"lesson(s) are logged in {log.name} - the sprint-start digest was "
                           "never generated. Create it: scripts/lessons.py summary")}
    actual = parse_summary_digest(summary.read_text(encoding="utf-8"))
    if actual == expected:
        return {**base, "stale": False, "added": [], "removed": [],
                "reason": f"{summary.name} is current ({len(expected)} still-valid lesson(s))"}
    added = [e for e in expected if e not in actual]
    removed = [a for a in actual if a not in expected]
    return {**base, "stale": True, "added": added, "removed": removed,
            "reason": _drift_reason(summary, added, removed)}


def validity_status(repo_root, project_file=None, validity_days: int | None = None,
                    today: str | None = None) -> dict:
    """Which open lessons are past their validity horizon, and which have none at all.

    Both are findings. An expired lesson must be closed (`revalidate --close`) or extended
    (`revalidate --extend`); an unstamped one has no horizon to judge, so it is unprovable
    rather than proven, and is stamped (`revalidate --stamp`). Reporting only the expired
    ones would pass every legacy log vacuously.
    """
    log = Path(project_file) if project_file else default_project_file(repo_root)
    if not log.is_file():
        return {"applicable": False, "open": 0, "expired": [], "unstamped": [],
                "log": str(log), "reason": f"no lessons log at {log} - nothing to re-validate"}
    days = resolve_validity_days(repo_root, validity_days)
    now = today or sdlc_md.now_date()
    open_entries = [e for e in parse_project_lessons(log.read_text(encoding="utf-8"))
                    if not is_closed(e)]
    expired, unstamped = [], []
    for e in open_entries:
        horizon = horizon_of(e, days)
        if horizon is None:
            unstamped.append(e["id"])
        elif horizon < now:
            expired.append({"id": e["id"], "title": e["title"], "horizon": horizon})
    return {"applicable": True, "open": len(open_entries), "expired": expired,
            "unstamped": unstamped, "validity_days": days, "today": now, "log": str(log),
            "reason": _validity_reason(expired, unstamped, len(open_entries))}


def _validity_reason(expired: list[dict], unstamped: list[str], open_count: int) -> str:
    parts = []
    if expired:
        ids = ", ".join(f"{e['id']} (horizon {e['horizon']})" for e in expired[:3])
        more = f" (+{len(expired) - 3} more)" if len(expired) > 3 else ""
        parts.append(f"{len(expired)} open lesson(s) past their validity horizon: {ids}{more}"
                     " - close them (revalidate --close) or extend them (revalidate --extend)")
    if unstamped:
        ids = ", ".join(unstamped[:3]) + (f" (+{len(unstamped) - 3} more)"
                                          if len(unstamped) > 3 else "")
        parts.append(f"{len(unstamped)} open lesson(s) carry no validity horizon: {ids}"
                     " - stamp them (revalidate --stamp)")
    return "; ".join(parts) if parts else f"{open_count} open lesson(s), all within validity"


def plan_digest(repo_root, project_file=None, summary_path=None) -> dict:
    """The still-valid lessons to READ at sprint start, carried in the plan itself.

    Source order: the project log (the source of truth), else the committed summary - the log
    is gitignored, so a fresh clone has only the summary, and a plan built there must still
    carry the lessons rather than silently carry none.
    """
    log = Path(project_file) if project_file else default_project_file(repo_root)
    summary = Path(summary_path) if summary_path else default_summary_path(repo_root)
    if log.is_file():
        items = digest_items(parse_project_lessons(log.read_text(encoding="utf-8")))
        status = summary_status(repo_root, log, summary)
        return {"source": "log", "lessons": items, "count": len(items),
                "stale": status["stale"], "reason": status["reason"], "path": str(log)}
    if summary.is_file():
        items = summary_items(summary.read_text(encoding="utf-8"))
        return {"source": "summary", "lessons": items, "count": len(items), "stale": False,
                "reason": f"read from {summary.name} (no local lessons log)",
                "path": str(summary)}
    return {"source": "none", "lessons": [], "count": 0, "stale": False,
            "reason": "no lessons recorded yet", "path": str(log)}


# -----------------------------------------------------------------------------
# The carried set: a fixed-size curation, held by construction
# -----------------------------------------------------------------------------
#
# 252 open lessons sat in the summary, ranked and printed at the top of every plan, and were
# still not applied - the recorded scar 'a test rename is cross-unit coupling' was violated four
# times in one repair by the author who had filed it that same night. A ranking of 252 is a fact
# about the past; nobody reads it and nobody holds it.
#
# So the retro CURATES a small set for the NEXT batch, and the size is held BY CONSTRUCTION rather
# than by discipline: a lesson earns a place only by displacing one, named with the reason. A set
# that can grow is the 252-entry summary again, and 'we will keep it short' is exactly the promise
# that produced 252. Displaced is NOT deleted - the lesson stays in the full registry, which this
# file never writes to; what changes is only what is carried forward.

#: The carried set lives beside the retros and is COMMITTED, like LESSONS-SUMMARY.md: the log is
#: gitignored, and a curation a fresh clone cannot read is a curation nobody reads.
#: THE carried-lessons file. One constant, read by the writer (`lessons`) and by every
#: reader (`sprint`'s plan digest and every lane brief). It named CARRIED-LESSONS.md
#: while the readers named - and the tree carried - LESSONS-TOP.md, so the curation a
#: retro wrote and the set a lane was briefed on were two different files, and neither
#: side had any way to notice. One truth held in two places diverges, and the looser
#: copy is the one that runs.
CARRIED_FILE = "sdlc-studio/retros/LESSONS-TOP.md"
DEFAULT_CARRIED_MAX = 5
CARRIED_MAX_KEY = "lessons.carried_max"

CARRIED_HEADING = "## Carried"
DISPLACED_HEADING = "## Displaced"
DECLINED_HEADING = "## Declined proposals"
_DISPLACED_ROW_RE = re.compile(
    r"^\|\s*([0-9-]{10})\s*\|\s*(L-\d{4})\s*\|\s*(L-\d{4}|-)\s*\|\s*(.+?)\s*\|\s*$")
_DECLINE_ROW_RE = re.compile(
    r"^\|\s*([0-9-]{10})\s*\|\s*(L-\d{4})\s*\|\s*(\d+|-)\s*\|\s*(.+?)\s*\|\s*$")

CARRIED_HEADER = """# Carried Lessons

**Last Updated:** {date}

The fixed-size set carried into the next batch, re-decided each retro. A lesson earns a place
only by displacing one, named with the reason; the displaced lesson stays in the full registry.
"""


def default_carried_path(repo_root) -> Path:
    return Path(repo_root) / CARRIED_FILE


def carried_max(repo_root, explicit: int | None = None) -> int:
    """How many lessons the carried set holds. THE reader of that number - `retro.carried_max`
    delegates here - so the writer that enforces the size and the check that judges it cannot
    drift. A non-positive or unparseable override falls back to the default rather than
    silently disabling the rule."""
    if explicit is not None:
        return explicit if explicit > 0 else DEFAULT_CARRIED_MAX
    raw = sdlc_md.project_override(repo_root, CARRIED_MAX_KEY, DEFAULT_CARRIED_MAX)
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_CARRIED_MAX
    return n if n > 0 else DEFAULT_CARRIED_MAX


def _section_lines(text: str, heading: str) -> list[str]:
    """The lines under a `## Heading`, to the next heading of the same level."""
    out: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line.strip() == heading
            continue
        if inside:
            out.append(line)
    return out


#: The carried set's rendered shape: `## N. Title`, one section per lesson. The readers
#: (`sprint.carried_lessons`, and every lane brief through it) have always read this; the
#: writer read a bullet list under a `## Carried` heading that the file does not use. Two
#: parsers over one file is the same defect as two paths to one fact - and the writer's
#: reading was the one that silently returned nothing.
CARRIED_HEADING_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$", re.M)


def parse_carried(text: str) -> list[dict]:
    """The carried set the file holds, in order.

    Reads the NUMBERED-SECTION shape the file actually uses, and falls back to the bullet form
    under a `## Carried` heading for a file written in the older shape. Both are read by one
    function so the writer and the readers cannot disagree about what the file says - which
    they did: this returned [] over a file the lane briefs were reading five lessons out of.
    """
    items = [{"id": "", "title": m.group(2).strip(), "gist": "", "n": int(m.group(1))}
             for m in CARRIED_HEADING_RE.finditer(text or "")]
    if items:
        return items
    for line in _section_lines(text, CARRIED_HEADING):
        m = SUMMARY_LINE_RE.match(line.strip())
        if m:
            items.append({"id": m.group(1), "title": m.group(2).strip(),
                          "gist": (m.group(3) or "").strip()})
    return items


def parse_displaced(text: str) -> list[dict]:
    """Every recorded displacement: what was dropped, what displaced it, and why."""
    out = []
    for line in _section_lines(text, DISPLACED_HEADING):
        m = _DISPLACED_ROW_RE.match(line.strip())
        if m:
            out.append({"date": m.group(1), "id": m.group(2),
                        "by": None if m.group(3) == "-" else m.group(3),
                        "reason": m.group(4).strip()})
    return out


def parse_declines(text: str) -> list[dict]:
    """Every declined proposal: which lesson, at what violation count, and why."""
    out = []
    for line in _section_lines(text, DECLINED_HEADING):
        m = _DECLINE_ROW_RE.match(line.strip())
        if m:
            out.append({"date": m.group(1), "id": m.group(2),
                        "count": int(m.group(3)) if m.group(3) != "-" else 0,
                        "reason": m.group(4).strip()})
    return out


def render_carried(carried: list[dict], displaced: list[dict], declines: list[dict]) -> str:
    """The whole CARRIED-LESSONS.md, rewritten from its parts. Derived output, like an
    `_index.md`: it is regenerated rather than edited in place, so the file can never hold a
    carried set and a displacement record that disagree."""
    parts = [CARRIED_HEADER.format(date=sdlc_md.now_date()).rstrip() + "\n",
             f"\n{CARRIED_HEADING}\n\n"]
    if carried:
        for c in carried:
            gist = f" - {c['gist']}" if c.get("gist") else ""
            parts.append(f"- **{c['id']}: {c['title']}**{gist}\n")
    else:
        parts.append("Nothing carried yet.\n")
    parts.append(f"\n{DISPLACED_HEADING}\n\n| Date | Lesson | Displaced by | Reason |\n"
                 f"| --- | --- | --- | --- |\n")
    for d in displaced:
        parts.append(f"| {d['date']} | {d['id']} | {d.get('by') or '-'} | {d['reason']} |\n")
    parts.append(f"\n{DECLINED_HEADING}\n\n| Date | Lesson | At repeats | Reason |\n"
                 f"| --- | --- | --- | --- |\n")
    for d in declines:
        parts.append(f"| {d['date']} | {d['id']} | {d.get('count') or 0} | {d['reason']} |\n")
    return "".join(parts)


def read_carried_file(path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """(carried, displaced, declines) from the file, or three empty lists when it is absent."""
    if not Path(path).is_file():
        return [], [], []
    text = Path(path).read_text(encoding="utf-8")
    return parse_carried(text), parse_displaced(text), parse_declines(text)


def registry_item(repo_root, lesson_id: str, project_file=None) -> dict | None:
    """One still-valid lesson from the project log, in digest form, or None when the id names
    nothing. Read from the log itself so a carried lesson is always one that exists: a set
    listing an id nobody can open is a curation of nothing."""
    log = Path(project_file) if project_file else default_project_file(repo_root)
    if not log.is_file():
        return None
    want = str(lesson_id).strip()
    for item in digest_items(parse_project_lessons(log.read_text(encoding="utf-8"))):
        if item["id"] == want:
            return item
    return None


def carry(repo_root, lesson_id: str, displaces: str | None = None, reason: str | None = None,
          carried_path=None, project_file=None, max_carried: int | None = None) -> dict:
    """Put a lesson in the carried set, displacing one when the set is full.

    Raises ValueError - having written nothing - when the id names no still-valid lesson, when
    the set is full and no displacement is named, when a displacement carries no reason, or when
    the named displacement is not in the set. The project log is never touched, so a displaced
    lesson stays in the full registry: it stopped being carried, it did not stop being true.
    """
    path = Path(carried_path) if carried_path else default_carried_path(repo_root)
    limit = carried_max(repo_root, max_carried)
    item = registry_item(repo_root, lesson_id, project_file)
    if item is None:
        raise ValueError(
            f"{lesson_id} names no still-valid lesson in "
            f"{project_file or default_project_file(repo_root)} - a carried set listing an id "
            f"nobody can open is a curation of nothing. Record the lesson first "
            f"(`lessons add`), or name one that is open.")
    carried, displaced, declines = read_carried_file(path)
    if any(c["id"] == item["id"] for c in carried):
        return {"changed": False, "id": item["id"], "displaced": None,
                "carried": [c["id"] for c in carried], "path": str(path)}
    if displaces is not None:
        gone = str(displaces).strip()
        if not any(c["id"] == gone for c in carried):
            raise ValueError(
                f"{gone} is not in the carried set, so it cannot be displaced - the set holds "
                f"{', '.join(c['id'] for c in carried) or 'nothing'}")
        if not (reason or "").strip():
            raise ValueError(
                f"displacing {gone} needs a reason - the whole point of a displacement is the "
                f"judgement it records, and a swap nobody justified is a swap nobody made a "
                f"decision about. Pass --reason.")
    elif len(carried) >= limit:
        raise ValueError(
            f"the carried set is full at {limit} - refused. A lesson earns a place only by "
            f"DISPLACING one: say which of {', '.join(c['id'] for c in carried)} matters less "
            f"than {item['id']} for the next batch, and why (--displaces <id> --reason <why>). "
            f"A set that can grow is a set nobody reads, which is the condition the full "
            f"registry is already in.")
    if displaces is not None:
        gone = str(displaces).strip()
        carried = [c for c in carried if c["id"] != gone]
        displaced = [*displaced, {"date": sdlc_md.now_date(), "id": gone, "by": item["id"],
                                  "reason": " ".join(str(reason).split())}]
    carried = [*carried, item]
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, render_carried(carried, displaced, declines))
    return {"changed": True, "id": item["id"],
            "displaced": str(displaces).strip() if displaces is not None else None,
            "carried": [c["id"] for c in carried], "path": str(path)}


def carried_digest(repo_root, carried_path=None) -> dict:
    """The carried set as the sprint plan and the delivery briefs read it. The read point that
    makes curation worth doing - a set nobody reads is a shorter list nobody reads."""
    path = Path(carried_path) if carried_path else default_carried_path(repo_root)
    carried, _displaced, _declines = read_carried_file(path)
    return {"lessons": carried, "count": len(carried), "path": str(path)}


# -----------------------------------------------------------------------------
# Repeats: a lesson violated AFTER it was carried
# -----------------------------------------------------------------------------
#
# A repeat is not a memory failure, it is a missing guard - and the only way to argue that is to
# be able to point at the unit that repeated it. So violations are recorded as they are found
# (by a reviewer, by the author, by a lane checking itself) and the close reports the ones whose
# lesson was in the CARRIED set.
#
# The scoping is the whole claim. 'You were given five lessons to hold and this one still
# happened' is evidence. 'One of 252 lessons was violated' is not, and folding the two together
# would make the repeat count mean nothing - which is how the 252 got there.

#: An append-only ledger, one JSON object per line, under `.local/`: it is working state for the
#: current cycle, and the durable record is the retro and whatever the repeat causes to be filed.
VIOLATIONS_FILE = "sdlc-studio/.local/lesson-violations.jsonl"


def default_violations_path(repo_root) -> Path:
    return Path(repo_root) / VIOLATIONS_FILE


def record_violation(repo_root, lesson_id: str, unit: str, note: str = "",
                     path=None, project_file=None, run: str | None = None) -> dict:
    """Record that `unit` violated `lesson_id`. Refuses an id that names no still-valid lesson and
    a violation with no unit: 'somebody did this somewhere' cannot be acted on, and an unattached
    repeat is exactly the shape of finding that gets absorbed into a retro and forgotten."""
    unit = str(unit or "").strip()
    if not unit:
        raise ValueError(
            "a violation needs the unit that produced it - the point of reporting a repeat is "
            "that the evidence stays attached to the work, and 'it happened somewhere' is not "
            "something an operator can act on")
    if registry_item(repo_root, lesson_id, project_file) is None:
        raise ValueError(
            f"{lesson_id} names no still-valid lesson - refusing to record a violation of "
            f"something nobody can read. Record the lesson first (`lessons add`).")
    p = Path(path) if path else default_violations_path(repo_root)
    row = {"lesson": str(lesson_id).strip(), "unit": unit,
           "note": " ".join(str(note or "").split()), "date": sdlc_md.now_date()}
    if run:
        row["run"] = str(run)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def violations(repo_root, path=None) -> list[dict]:
    """Every recorded violation, in the order it was recorded. A malformed line is skipped rather
    than fatal: a ledger one bad append cannot be read from would lose the whole record."""
    p = Path(path) if path else default_violations_path(repo_root)
    if not p.is_file():
        return []
    out: list[dict] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("lesson") and row.get("unit"):
            out.append(row)
    return out


def repeats(repo_root, carried_path=None, violations_path=None) -> list[dict]:
    """The carried lessons that were violated anyway, each naming the units that repeated them.

    A violation of a lesson OUTSIDE the carried set is deliberately not here. Most-repeated
    first, so the one nearest a guard is read first."""
    carried, _displaced, _declines = read_carried_file(
        Path(carried_path) if carried_path else default_carried_path(repo_root))
    by_id = {c["id"]: c for c in carried}
    grouped: dict[str, dict] = {}
    for v in violations(repo_root, violations_path):
        lid = v["lesson"]
        if lid not in by_id:
            continue
        entry = grouped.setdefault(lid, {"id": lid, "title": by_id[lid]["title"],
                                         "units": [], "notes": [], "count": 0})
        entry["count"] += 1
        if v["unit"] not in entry["units"]:
            entry["units"].append(v["unit"])
        if v.get("note"):
            entry["notes"].append(v["note"])
    return sorted(grouped.values(), key=lambda r: (-r["count"], r["id"]))


def repeat_report(repo_root, carried_path=None, violations_path=None) -> str:
    """The close's repeat report, or "" when nothing repeated. Names the lesson AND every unit, so
    the reader can go and look rather than take the count on trust."""
    found = repeats(repo_root, carried_path, violations_path)
    if not found:
        return ""
    lines = [f"{len(found)} carried lesson(s) were violated anyway - a repeat is evidence the "
             f"lesson needs a guard, not a louder note:"]
    for r in found:
        lines.append(f"  {r['id']}: {r['title']}")
        lines.append(f"    repeated {r['count']}x by {', '.join(r['units'])}")
        for note in r["notes"][:3]:
            lines.append(f"    - {note}")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Proposals: a repeat that keeps happening becomes work
# -----------------------------------------------------------------------------
#
# The loop has to END somewhere other than in a longer list. A lesson violated once after being
# carried is a repeat; a lesson violated repeatedly is a missing guard, and the honest response to
# a missing guard is a change request or a bug, not a better-worded note.
#
# The operator decides. Nothing is filed on the tool's own authority: a proposal is offered with
# its evidence attached, and a DECLINE is recorded against the lesson at the repeat count it was
# declined on. That last part is what stops the proposal becoming nagging - it cannot return on
# the same evidence, and it can return on new evidence, which is exactly the distinction a
# 'dismiss' button loses.

#: How many repeats it takes before a carried lesson proposes work. Strictly MORE than this, so
#: the default of 2 means 'three times is a pattern'. Override with `lessons.repeat_threshold`.
DEFAULT_REPEAT_THRESHOLD = 2
REPEAT_THRESHOLD_KEY = "lessons.repeat_threshold"


def repeat_threshold(repo_root, explicit: int | None = None) -> int:
    """The repeat count a carried lesson must exceed before it proposes work."""
    if explicit is not None:
        return explicit if explicit > 0 else DEFAULT_REPEAT_THRESHOLD
    raw = sdlc_md.project_override(repo_root, REPEAT_THRESHOLD_KEY, DEFAULT_REPEAT_THRESHOLD)
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return DEFAULT_REPEAT_THRESHOLD
    return n if n > 0 else DEFAULT_REPEAT_THRESHOLD


def _proposal_evidence(rep: dict) -> str:
    """The violations, as the evidence a proposal carries. The units are named, not counted: a
    number is something to take on trust and a list is something to go and check."""
    lines = [f"{rep['id']} was carried and violated {rep['count']} time(s) by "
             f"{', '.join(rep['units'])}."]
    lines.extend(f"- {n}" for n in rep["notes"])
    return "\n".join(lines)


def proposals(repo_root, type_: str = "cr", threshold: int | None = None,
              carried_path=None, violations_path=None) -> list[dict]:
    """The carried lessons repeated often enough to be worth a guard, each with its evidence.

    A lesson already DECLINED at this repeat count or higher is not offered again - the operator
    settled that evidence. One more violation is new evidence, and it comes back."""
    limit = repeat_threshold(repo_root, threshold)
    path = Path(carried_path) if carried_path else default_carried_path(repo_root)
    _carried, _displaced, declines = read_carried_file(path)
    declined_at = {}
    for d in declines:
        declined_at[d["id"]] = max(declined_at.get(d["id"], 0), d.get("count") or 0)
    out = []
    for rep in repeats(repo_root, carried_path, violations_path):
        if rep["count"] <= limit or rep["count"] <= declined_at.get(rep["id"], 0):
            continue
        out.append({
            "id": rep["id"], "lesson_title": rep["title"], "count": rep["count"],
            "units": rep["units"], "type": type_,
            "title": (f"Guard the repeatedly violated lesson {rep['id']}: "
                      f"{rep['title'][:90]}"),
            "evidence": _proposal_evidence(rep),
        })
    return out


def _proposal_fields(prop: dict, affects: str, size: str | None, points: int | None) -> dict:
    """The finding-filer fields for an accepted proposal. The lesson and every unit that repeated
    it travel INTO the artefact, so whoever picks the work up reads the evidence, not a reference
    to it."""
    summary = (f"The lesson `{prop['id']}` ({prop['lesson_title']}) was carried into the batch "
               f"and violated anyway, {prop['count']} time(s). A lesson repeated after being "
               f"carried is a missing guard: a note that has already failed to work is not "
               f"improved by being written again.\n\n{prop['evidence']}")
    common = {"summary": summary, "affects": affects}
    if prop["type"] == "bug":
        return {**common, "severity": "Medium", "points": points or 3,
                "steps": prop["evidence"],
                "fix": (f"Make the class {prop['id']} describes mechanically impossible, or "
                        f"detectable at the moment it happens, rather than relying on the "
                        f"lesson being read.")}
    return {**common, "priority": "Medium", "ctype": "Improvement", "size": size or "M",
            "impact": (f"Every lane and every reviewer, in this project and any consuming one: "
                       f"the lesson is being read and violated anyway, so each repeat costs a "
                       f"review round and a repair cycle. Units so far: "
                       f"{', '.join(prop['units'])}."),
            "acs": [f"The class {prop['id']} describes is caught by a guard rather than by "
                    f"whoever remembers the lesson.",
                    "The guard is proven against the recorded violations above, not only "
                    "against a fresh example."]}


def accept_proposal(repo_root, lesson_id: str, type_: str = "cr", affects: str | None = None,
                    size: str | None = None, points: int | None = None,
                    threshold: int | None = None, carried_path=None, violations_path=None,
                    dry_run: bool = False) -> dict:
    """File the proposed unit for a repeatedly violated lesson, through the ordinary finding
    filer - so it gets a collision-free id, an index row and every creation guard, exactly like
    any other artefact.

    `affects` is REQUIRED and deliberately not guessed: the tool knows the lesson kept being
    violated, it does not know where the guard belongs, and inventing a footprint is the fictional
    `Affects` the filer refuses anyway."""
    found = [p for p in proposals(repo_root, type_, threshold, carried_path, violations_path)
             if p["id"] == str(lesson_id).strip()]
    if not found:
        raise ValueError(
            f"no open proposal for {lesson_id} - it is not carried, has not been repeated more "
            f"than {repeat_threshold(repo_root, threshold)} time(s), or was already declined at "
            f"this repeat count")
    if not (affects or "").strip():
        raise ValueError(
            "accepting a proposal needs --affects: the guard has to land somewhere, and the tool "
            "knows the lesson kept being violated, not where the guard belongs. A footprint the "
            "tool invented is the fictional Affects the filer refuses anyway")
    prop = found[0]
    import file_finding  # noqa: PLC0415 - deferred: the filer imports the world, this does not
    res = file_finding.file_finding(repo_root, prop["type"], prop["title"],
                                    _proposal_fields(prop, affects, size, points),
                                    dry_run=dry_run)
    return {**res, "lesson": prop["id"], "count": prop["count"], "type": prop["type"]}


def decline_proposal(repo_root, lesson_id: str, reason: str, threshold: int | None = None,
                     carried_path=None, violations_path=None) -> dict:
    """Decline a proposal: file NOTHING, and record the decline against the lesson at the repeat
    count it was declined on.

    Recorded rather than merely dropped, for the reason a decline is recorded anywhere else in
    this workspace: a decision nobody wrote down comes back as the same question next week. The
    count is the evidence the operator ruled on - a further violation is new evidence and the
    proposal returns."""
    lid = str(lesson_id).strip()
    if not (reason or "").strip():
        raise ValueError(
            f"declining the proposal for {lid} needs a reason - a decline with no reason is "
            f"silence wearing a decision's clothes, and the next reader cannot tell whether the "
            f"guard was judged unnecessary or the question was just closed")
    found = [p for p in proposals(repo_root, "cr", threshold, carried_path, violations_path)
             if p["id"] == lid]
    if not found:
        raise ValueError(f"no open proposal for {lid} to decline")
    path = Path(carried_path) if carried_path else default_carried_path(repo_root)
    carried, displaced, declines = read_carried_file(path)
    row = {"date": sdlc_md.now_date(), "id": lid, "count": found[0]["count"],
           "reason": " ".join(str(reason).split())}
    sdlc_md.atomic_write(path, render_carried(carried, displaced, [*declines, row]))
    return {"filed": None, "lesson": lid, "count": row["count"], "path": str(path),
            "reason": row["reason"]}


def cross_digest(repo_root, lessons_dir=None) -> dict:
    """The ranked cross-project tier, in the shape the plan renders. One walk, not two."""
    ranked = rank_lessons(repo_root, lessons_dir)
    return {"lessons": ranked, "count": len(ranked)}


def cross_project_digest(repo_root, lessons_dir=None) -> dict:
    """The CROSS-PROJECT lessons, one line each, for the read points that must not miss them.

    The project tier had a reader - the sprint plan carries its digest. The cross-project
    registry had NONE: it was reachable only by explicitly running `recall`, which is a prose
    instruction, and prose instructions get skipped. So the class we already knew about could
    be written down and still bite the next project, and the one after that.

    A new project inherits this registry as its day-one lens - that is what "cross-project"
    means. It is the only tier that can help a team before they have made the mistake.

    One line per lesson: the whole registry costs a few hundred tokens in this form, so there
    is no budget argument for filtering it down to a tag and silently exempting the rest.
    Bodies are pulled on demand, never injected wholesale.
    """
    try:
        d, _src = resolve_global_dir(lessons_dir, repo_root)
    except ResolveError:
        return {"lessons": [], "count": 0, "path": None}
    rows = parse_index_rows(d / "_index.md") if (d / "_index.md").is_file() else []
    items = [{"id": r["id"], "title": r["title"], "tags": r.get("tags", [])} for r in rows]
    return {"lessons": items, "count": len(items), "path": str(d)}


# How often a lesson's id is cited across the workspace's artefacts. A class that keeps
# biting is the one to put in front of the next person, and a flat list cannot say so.
CITATION_RE_TMPL = r"\b{id}\b"


def recurrence(repo_root, lesson_ids: list[str]) -> dict[str, int]:
    """How many artefacts cite each lesson. Counted from the files, never asserted.

    This is the signal a flat log cannot carry: one lesson has been paid for once, another
    has been paid for three times in three repos. Ranking by it puts the class that keeps
    recurring in front of the person about to repeat it.

    The lesson's own file and the registry index do not count as citations of themselves.
    """
    root = Path(repo_root)
    counts = {i: 0 for i in lesson_ids}
    for p in (root / "sdlc-studio").rglob("*.md"):
        if p.name == "_index.md":
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lid in lesson_ids:
            if re.search(CITATION_RE_TMPL.format(id=re.escape(lid)), text):
                counts[lid] += 1
    return counts


def is_guarded(entry_body: str) -> bool:
    """A lesson with a shipped structural guard stops shouting.

    Once a test or gate makes the class mechanically impossible, the lesson has done its job:
    it is history, not a live hazard, and it should not crowd out the ones that can still bite
    you. Demoted, never deleted - the history is why the guard exists.

    Declared by the lesson itself with a `Guard:` field naming what defends it.
    """
    return bool(re.search(r"^\s*-?\s*\*\*Guard:\*\*\s*\S", entry_body or "", re.MULTILINE))


def close_entry(entry: dict, reason: str | None) -> bool:
    """Mark an entry closed by appending a Status bullet. Idempotent - returns False if it
    was already closed (so re-running closes nothing new)."""
    if is_closed(entry):
        return False
    label = f"Closed - {reason}" if reason else "Closed"
    bullet = f"- **Status:** {label}"
    entry["body"] = (entry["body"].rstrip() + "\n" + bullet).strip() if entry["body"] else bullet
    entry["fields"]["status"] = label
    return True


def _unknown_ids(wanted: list[str], known: set[str]) -> bool:
    """True (having printed the refusal) when an id names no lesson in the log. A typo'd id
    that reports '0 closed' and exits 0 is a no-op wearing a success: the operator believes
    the lesson was closed and the close gate is then judging something nobody looked at."""
    unknown = sorted(set(wanted) - known)
    if not unknown:
        return False
    print(f"error: unknown lesson id(s): {', '.join(unknown)} - the log holds "
          f"{', '.join(sorted(known)) if known else 'no lessons'}", file=sys.stderr)
    return True


def _revalidate_write(args: argparse.Namespace, path: Path, text: str,
                      entries: list[dict], changed: list[str], verb: str) -> int:
    """Persist a close/extend/stamp pass and report it."""
    if changed:
        write_project_file(path, project_header_of(text), entries)
    if args.format == "json":
        print(json.dumps({verb: changed}, indent=2))
    else:
        for cid in changed:
            print(f"{verb.capitalize()} {cid}")
        print(f"{len(changed)} {verb}")
    return 0


def cmd_revalidate(args: argparse.Namespace) -> int:
    """List open project lessons with their validity horizon, or act on them: `--close` the
    ones no longer true, `--extend` the ones still true past their horizon, `--stamp` the ones
    carrying no horizon at all. Deterministic; the judgement stays the operator's, the record
    is mechanical - and the close gate reads that record."""
    try:
        resolve_prose(args, ("reason",))
    except ValueError as exc:                             # pragma: no cover - nothing required
        print(f"error: {exc}", file=sys.stderr)
        return 2
    path = _project_file(args)
    if not path.is_file():
        if args.format == "json":
            print(json.dumps({"open": [], "closed": []}, indent=2))
        else:
            print(f"No lessons file at {path}; nothing to re-validate.")
        return 0
    text = path.read_text(encoding="utf-8")
    entries = parse_project_lessons(text)
    days = resolve_validity_days(getattr(args, "root", "."), getattr(args, "days", None))
    today = sdlc_md.now_date()
    known = {e["id"] for e in entries}
    if args.close:
        if _unknown_ids(args.close, known):
            return 2
        wanted = set(args.close)
        closed = [e["id"] for e in entries if e["id"] in wanted and close_entry(e, args.reason)]
        return _revalidate_write(args, path, text, entries, closed, "closed")
    if getattr(args, "extend", None):
        if _unknown_ids(args.extend, known):
            return 2
        wanted = set(args.extend)
        shut = [e["id"] for e in entries if e["id"] in wanted and is_closed(e)]
        if shut:
            print(f"error: cannot extend closed lesson(s): {', '.join(sorted(shut))} - a closed "
                  "lesson is no longer valid; record a new one instead of reviving it",
                  file=sys.stderr)
            return 2
        extended = []
        for e in entries:
            if e["id"] in wanted:
                upsert_field(e, "Review-by", add_days(today, days))
                extended.append(e["id"])
        return _revalidate_write(args, path, text, entries, extended, "extended")
    if getattr(args, "stamp", False):
        stamped = []
        for e in entries:
            if is_closed(e) or horizon_of(e, days) is not None:
                continue
            if not _is_iso_date(e["fields"].get("added", "")):
                upsert_field(e, "Added", today)
            upsert_field(e, "Review-by", add_days(today, days))
            stamped.append(e["id"])
        return _revalidate_write(args, path, text, entries, stamped, "stamped")
    open_entries = [{"id": e["id"], "title": e["title"], "horizon": horizon_of(e, days)}
                    for e in entries if not is_closed(e)]
    if args.format == "json":
        print(json.dumps({"open": open_entries, "count": len(open_entries),
                          "today": today, "validity_days": days}, indent=2))
        return 0
    if not open_entries:
        print("No open lessons.")
        return 0
    for e in open_entries:
        horizon = e["horizon"]
        mark = ("no horizon" if horizon is None
                else f"EXPIRED {horizon}" if horizon < today else f"valid to {horizon}")
        print(f"{e['id']}  {e['title']}  [{mark}]")
    print(f"{len(open_entries)} open lesson(s) - close the stale ones with "
          "`lessons revalidate --close L-NNNN`, keep the still-true ones with `--extend "
          "L-NNNN`, give the undated ones a horizon with `--stamp`")
    return 0


def build_summary_text(entries: list[dict]) -> str:
    """The rolling digest of still-valid lessons. Deterministic for a given input (no date),
    so the generator is reproducible - the byte-identical regeneration AC depends on it, and
    so does the staleness check, which recomputes this and compares."""
    items = digest_items(entries)
    out = [
        "# Lessons Summary", "",
        "Rolling digest of still-valid project lessons, read at sprint start. The full log "
        "with closed entries lives in the project tier (`.local/lessons.md`); regenerate this "
        "with `lessons summary`.", "",
    ]
    if not items:
        out.append("_No open lessons._")
    for item in items:
        line = f"- **{item['id']}: {item['title']}**"
        if item["gist"]:
            line += f" - {item['gist']}"
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def _root(args) -> Path:
    """The project root every path in this invocation anchors on.

    One answer per invocation, shared by the lessons log and the summary it writes: a run
    that reads its source from one root and writes its digest against another is how a
    summary comes to describe a project it did not read.
    """
    return verify_ac.resolve_root(args)


def _project_file(args) -> Path:
    """The project-tier lessons file, resolved against `--root`.

    `--project-file` defaults to a RELATIVE path, so taking it verbatim meant every subcommand
    read and wrote relative to the CURRENT DIRECTORY and ignored the root it was handed - then
    reported success naming the path it had used. `sprint close` passes `--root` correctly and
    inherited it: a close run from anywhere but the project root regenerated the digest in the
    wrong place and reported the step green. It worked from the repo root only because cwd
    happened to equal root.

    An ABSOLUTE `--project-file` is honoured as given, so pointing at another project's log
    still works; only the relative default is anchored.

    The root is RESOLVED, not taken verbatim: the family default `.` means "work it out from
    here", so a run from a subdirectory finds the project above it instead of summarising an
    empty log beside the cwd and reporting that as the truth.
    """
    p = Path(args.project_file)
    return p if p.is_absolute() else _root(args) / p


def _default_summary_out(project_file: Path) -> Path:
    """`<repo>/sdlc-studio/retros/LESSONS-SUMMARY.md` derived from the project-file location."""
    rf = project_file.resolve()
    root = rf.parents[2] if len(rf.parents) >= 3 else rf.parent
    return root / "sdlc-studio" / "retros" / "LESSONS-SUMMARY.md"


def rank_lessons(repo_root, lessons_dir=None) -> list[dict]:
    """The cross-project lessons, ordered by what is biting hardest RIGHT NOW.

    A flat, append-only list is what grows until someone has to evict it - and while it grows,
    the lesson that keeps costing you money sits in the middle of it, indistinguishable from
    the one you learned once and fixed. Ranking is what makes the store an instrument instead
    of a diary.

    Three signals, all computed from the files, none asserted:

      recurrence  how many artefacts cite this lesson. A class that has bitten three times in
                  three repos should be at the top of the list before anyone touches the code
                  that will make it four.
      recency     a lesson learned last week outranks one learned last year, at equal
                  recurrence. Ties break toward the newer id.
      guarded     a lesson whose class a shipped test or gate now makes impossible is DEMOTED,
                  not deleted. It has done its job; the history stays, the shouting stops.
                  Declared by the lesson with a `Guard:` field.

    Recomputed on every call, never trusted from a cached value - the same discipline the
    indexes are held to.
    """
    try:
        d, _src = resolve_global_dir(lessons_dir, repo_root)
    except ResolveError:
        return []
    index = d / "_index.md"
    if not index.is_file():
        return []
    rows = parse_index_rows(index)
    ids = [r["id"] for r in rows]
    cites = recurrence(repo_root, ids)

    out = []
    for r in rows:
        lid = r["id"]
        body = ""
        f = d / r["file"] if r.get("file") else None
        if f and f.is_file():
            body = f.read_text(encoding="utf-8", errors="ignore")
        guarded = is_guarded(body)
        # A guarded lesson sorts below every live one, whatever its recurrence: it cannot
        # bite you any more, so it must not crowd out something that can.
        out.append({
            "id": lid,
            "title": r["title"],
            "tags": r.get("tags", []),
            "recurrence": cites.get(lid, 0),
            "guarded": guarded,
            "rank_key": (0 if guarded else 1, cites.get(lid, 0), lid),
        })
    out.sort(key=lambda x: x["rank_key"], reverse=True)
    for i, item in enumerate(out, 1):
        item["rank"] = i
        del item["rank_key"]
    return out


def cmd_rank(args: argparse.Namespace) -> int:
    ranked = rank_lessons(getattr(args, "root", "."), getattr(args, "lessons_dir", None))
    if getattr(args, "limit", 0):
        ranked = ranked[:args.limit]
    if args.format == "json":
        print(json.dumps({"lessons": ranked, "count": len(ranked)}, indent=2))
        return 0
    if not ranked:
        print("no cross-project lessons to rank")
        return 0
    print("Cross-project lessons, by what is biting hardest now:\n")
    for it in ranked:
        mark = " (guarded)" if it["guarded"] else ""
        cited = f"cited x{it['recurrence']}" if it["recurrence"] else "not yet cited"
        print(f"  {it['rank']:2d}. {it['id']}  [{cited}]{mark}")
        print(f"      {it['title']}")
    live = sum(1 for i in ranked if not i["guarded"])
    print(f"\n{live} live, {len(ranked) - live} guarded (demoted - a shipped guard makes the "
          f"class impossible; the history stays, the shouting stops)")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    """Refresh the committed rolling lessons summary from the still-valid project lessons."""
    path = _project_file(args)
    entries = parse_project_lessons(path.read_text(encoding="utf-8")) if path.is_file() else []
    # A relative --out anchors on the SAME resolved root the log was read from, so the digest
    # and its source cannot come from two different projects; an absolute one is honoured as
    # given. Taken verbatim, it landed beside whichever directory the run started in.
    out_path = verify_ac.under_root(_root(args), args.out) if args.out else _default_summary_out(path)
    text = build_summary_text(entries)
    if not args.dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
    n = sum(1 for e in entries if not is_closed(e))
    if args.format == "json":
        print(json.dumps({"out": str(out_path), "open": n, "written": not args.dry_run}, indent=2))
        return 0
    print(f"{'would write' if args.dry_run else 'wrote'} {n} open lesson(s) -> {out_path}")
    return 0


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def _common(sp: argparse.ArgumentParser) -> None:
    """Flags shared by every subcommand (tier locations, project root, output format)."""
    sp.add_argument("--project-file", default=DEFAULT_PROJECT_FILE,
                    help=f"Project-tier lessons file (default: {DEFAULT_PROJECT_FILE})")
    sp.add_argument("--lessons-dir", default=None,
                    help="Skill-tier lessons directory (default: the running skill's lessons/; "
                         "for `add --global` the config key skill_source_repo wins over it)")
    sp.add_argument("--root", default=".",
                    help="Project root, read for config keys (skill_source_repo, "
                         f"{VALIDITY_DAYS_KEY}) (default: .)")
    sp.add_argument("--format", choices=("text", "json"), default="text")


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for list, add, prune, and recall."""
    p = argparse.ArgumentParser(
        prog="lessons.py",
        description="Manage sdlc-studio lessons (project and skill tiers).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list", help="Print lessons (project tier; --global for skill tier).")
    ls.add_argument("--global", dest="global_", action="store_true",
                    help="List the skill tier from lessons/_index.md")
    _common(ls)
    ls.set_defaults(func=cmd_list)

    ad = sub.add_parser("add", help="Add a lesson (project tier; --global promotes).")
    ad.add_argument("--title", help="Short descriptive title (required unless the "
                                    "--fields-file document carries one)")
    ad.add_argument("--body", help="The lesson text (required unless the --fields-file "
                                   "document carries one)")
    _add_fields_file_arg(ad, "{\"title\": \"...\", \"body\": \"...\"}")
    ad.add_argument("--epic", help="Epic context, e.g. EP0004 (project tier)")
    ad.add_argument("--wave", type=int, help="Wave number (project tier)")
    ad.add_argument("--tags", help="Comma-separated tags")
    ad.add_argument("--origin", help="Origin note for --global (default: cwd name)")
    ad.add_argument("--validity-days", type=int, dest="validity_days",
                    help=f"Validity window for the Review-by horizon (default: "
                         f"{DEFAULT_VALIDITY_DAYS}, or the {VALIDITY_DAYS_KEY} config key)")
    ad.add_argument("--global", dest="global_", action="store_true",
                    help="Promote into the skill tier: a tracked destination is required")
    _common(ad)
    ad.set_defaults(func=cmd_add)

    pr = sub.add_parser("prune", help="Drop project-tier entries tied to old epics.")
    grp = pr.add_mutually_exclusive_group(required=True)
    grp.add_argument("--older", help="Drop entries with Epic <= this, e.g. EP0003")
    grp.add_argument("--epic", help="Drop entries with Epic == this, e.g. EP0004")
    _common(pr)
    pr.set_defaults(func=cmd_prune)

    rc = sub.add_parser("recall", help="Surface skill-tier lessons by tags/query.")
    rc.add_argument("--tags", help="Comma-separated tags to match (substring)")
    rc.add_argument("--query", help="Free-text match against title/tags")
    rc.add_argument("--all", action="store_true", help="Search both tiers")
    _common(rc)
    rc.set_defaults(func=cmd_recall)

    rv = sub.add_parser("revalidate",
                        help="List open project lessons with their validity horizon, or "
                             "--close / --extend / --stamp them.")
    act = rv.add_mutually_exclusive_group()
    act.add_argument("--close", nargs="+", metavar="L-NNNN",
                     help="Close these lesson ids (mark no longer valid)")
    act.add_argument("--extend", nargs="+", metavar="L-NNNN",
                     help="Still true: push the Review-by horizon out by the validity window")
    act.add_argument("--stamp", action="store_true",
                     help="Give every open lesson that has no validity horizon one (the "
                          "backfill for a log written before horizons existed)")
    rv.add_argument("--reason", help="Reason recorded on the closed lesson(s)")
    _add_fields_file_arg(rv, "{\"reason\": \"...\"}")
    rv.add_argument("--days", type=int,
                    help=f"Validity window in days for --extend/--stamp (default: "
                         f"{DEFAULT_VALIDITY_DAYS}, or the {VALIDITY_DAYS_KEY} config key)")
    _common(rv)
    rv.set_defaults(func=cmd_revalidate)

    sm = sub.add_parser("summary",
                        help="Refresh the committed rolling lessons summary (read at sprint start).")
    sm.add_argument("--out", help="Summary output path (default: sdlc-studio/retros/LESSONS-SUMMARY.md)")
    sm.add_argument("--dry-run", action="store_true", help="Report without writing")
    _common(sm)
    sm.set_defaults(func=cmd_summary)

    rk = sub.add_parser("rank",
                        help="Rank the cross-project lessons by what is biting hardest, now.")
    rk.add_argument("--dry-run", action="store_true", help="Report without writing")
    rk.add_argument("--limit", type=int, default=0, help="Show only the top N (0 = all)")
    _common(rk)
    rk.set_defaults(func=cmd_rank)

    cy = sub.add_parser("carry",
                        help="Put a lesson in the fixed-size carried set (displacing one when "
                             "the set is full).")
    cy.add_argument("--id", required=True, metavar="L-NNNN",
                    help="The lesson to carry into the next batch")
    cy.add_argument("--displaces", metavar="L-NNNN",
                    help="The carried lesson this one replaces - required once the set is full, "
                         "because the size is held by construction, not by good intentions")
    cy.add_argument("--reason", help="Why the displaced lesson matters less now (required with "
                                     "--displaces: the judgement IS the record)")
    _common(cy)
    cy.set_defaults(func=cmd_carry)

    cd = sub.add_parser("carried", help="Show the carried set (and what it displaced).")
    _common(cd)
    cd.set_defaults(func=cmd_carried)

    vi = sub.add_parser("violated",
                        help="Record that a unit violated a lesson (a repeat, if it was carried).")
    vi.add_argument("--id", required=True, metavar="L-NNNN", help="The lesson that was violated")
    vi.add_argument("--unit", required=True, metavar="US0123",
                    help="The unit that violated it - a repeat with no unit cannot be acted on")
    vi.add_argument("--note", help="What happened, in one line")
    vi.add_argument("--run", help="The run id, when there is one")
    _common(vi)
    vi.set_defaults(func=cmd_violated)

    rp = sub.add_parser("repeats",
                        help="Report carried lessons violated anyway, naming the units.")
    _common(rp)
    rp.set_defaults(func=cmd_repeats)

    ps = sub.add_parser("propose",
                        help="Offer a CR/bug for each repeatedly violated carried lesson, or "
                             "--accept / --decline one.")
    ps.add_argument("--id", metavar="L-NNNN",
                    help="The lesson to accept or decline a proposal for (omit to list)")
    act2 = ps.add_mutually_exclusive_group()
    act2.add_argument("--accept", action="store_true",
                      help="File the proposed unit (needs --affects)")
    act2.add_argument("--decline", action="store_true",
                      help="File nothing and record the decline against the lesson (needs "
                           "--reason)")
    ps.add_argument("--type", choices=("cr", "bug"), default="cr",
                    help="What to propose (default: cr - a repeat is usually a missing guard)")
    ps.add_argument("--affects", help="Where the guard will land (required with --accept: the "
                                      "tool knows the lesson was violated, not where to fix it)")
    ps.add_argument("--size", help="T-shirt size for an accepted cr")
    ps.add_argument("--points", type=int, help="Points for an accepted bug")
    ps.add_argument("--reason", help="Why the proposal is declined (required with --decline)")
    ps.add_argument("--dry-run", action="store_true", help="Preview the filing, write nothing")
    _common(ps)
    ps.set_defaults(func=cmd_propose)

    sdlc_md.add_global_root(p)
    return p


def cmd_carry(args: argparse.Namespace) -> int:
    """Carry a lesson, refusing loudly rather than growing the set."""
    try:
        res = carry(_root(args), args.id, displaces=args.displaces, reason=args.reason,
                    project_file=_project_file(args))
    except ValueError as exc:
        print(f"carry refused: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(res, indent=2))
        return 0
    if not res["changed"]:
        print(f"{res['id']} is already carried ({len(res['carried'])} in the set)")
        return 0
    swap = f", displacing {res['displaced']}" if res["displaced"] else ""
    print(f"carried {res['id']}{swap} -> {res['path']} ({len(res['carried'])} in the set)")
    return 0


def cmd_carried(args: argparse.Namespace) -> int:
    """Print the carried set - the read point curation exists to serve."""
    path = default_carried_path(_root(args))
    carried, displaced, declines = read_carried_file(path)
    if args.format == "json":
        print(json.dumps({"carried": carried, "displaced": displaced, "declined": declines,
                          "path": str(path)}, indent=2))
        return 0
    if not carried:
        print(f"nothing carried yet ({path})")
        return 0
    print(f"{len(carried)} carried lesson(s) - read these before the batch:")
    for c in carried:
        gist = f" - {c['gist']}" if c.get("gist") else ""
        print(f"  {c['id']}: {c['title']}{gist}")
    return 0


def cmd_violated(args: argparse.Namespace) -> int:
    """Record a violation against a lesson."""
    try:
        row = record_violation(_root(args), args.id, args.unit, note=args.note or "",
                               project_file=_project_file(args), run=args.run)
    except ValueError as exc:
        print(f"violation refused: {exc}", file=sys.stderr)
        return 1
    carried = {c["id"] for c in carried_digest(_root(args))["lessons"]}
    if args.format == "json":
        print(json.dumps({**row, "repeat": row["lesson"] in carried}, indent=2))
        return 0
    kind = "REPEAT of a carried lesson" if row["lesson"] in carried else "violation"
    print(f"recorded {kind}: {row['lesson']} by {row['unit']}")
    return 0


def cmd_repeats(args: argparse.Namespace) -> int:
    """Print the carried lessons that were violated anyway."""
    root = _root(args)
    if args.format == "json":
        print(json.dumps({"repeats": repeats(root)}, indent=2))
        return 0
    text = repeat_report(root)
    print(text if text else "no carried lesson was violated - nothing to report")
    return 0


def cmd_propose(args: argparse.Namespace) -> int:
    """List, accept or decline the proposals a repeatedly violated lesson raises."""
    root = _root(args)
    if args.accept or args.decline:
        if not args.id:
            print("propose refused: --accept/--decline needs --id", file=sys.stderr)
            return 1
        try:
            if args.accept:
                res = accept_proposal(root, args.id, type_=args.type, affects=args.affects,
                                      size=args.size, points=args.points, dry_run=args.dry_run)
                print(json.dumps(res, indent=2) if args.format == "json"
                      else f"{'would file' if args.dry_run else 'filed'} {res['id']} for "
                           f"{res['lesson']} -> {res['path']}")
            else:
                res = decline_proposal(root, args.id, args.reason or "")
                print(json.dumps(res, indent=2) if args.format == "json"
                      else f"declined the proposal for {res['lesson']} at {res['count']} "
                           f"repeat(s) - nothing filed, recorded in {res['path']}")
        except (ValueError, FileExistsError) as exc:
            print(f"propose refused: {exc}", file=sys.stderr)
            return 1
        return 0
    found = proposals(root, args.type)
    if args.format == "json":
        print(json.dumps({"proposals": found}, indent=2))
        return 0
    if not found:
        print("no lesson has been repeated often enough to propose work")
        return 0
    print(f"{len(found)} proposal(s) - accept or decline each:")
    for p in found:
        print(f"  {p['id']} ({p['count']} repeats by {', '.join(p['units'])}): {p['title']}")
        print(f"    accept:  lessons.py propose --id {p['id']} --accept "
              f"--affects \"path/to/file.py, path/to/test_file.py\"")
        print(f"    decline: lessons.py propose --id {p['id']} --decline --reason \"...\"")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to, not on the cwd the run happened to start in. Per-verb resolution is
    # left in place; this makes the anchor true of a verb that forgets to ask.
    args.root = str(verify_ac.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
