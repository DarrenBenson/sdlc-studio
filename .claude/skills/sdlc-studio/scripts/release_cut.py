#!/usr/bin/env python3
"""Release cut: turn the accumulated changelog fragments into a versioned section, and guard the
tag so it can never assert a green that was measured on a different tree.

Two verbs:

- `changelog-cut --version X.Y.Z` composes the pending `changelog.d/` fragments into `[Unreleased]`
  (the release-time `compose --apply`), then moves that body under a new `## [X.Y.Z] - <date>`
  header, leaving `[Unreleased]` empty. This is the deterministic cut US0348 requires - the notes
  come from the per-unit fragments, never a hand-written section.

- `record-green --commit <sha>` stamps the commit the pre-tag gate passed on; `tag-check --commit
  <sha>` refuses unless that stamp names the same commit. A tag asserting a green measured on a
  different tree is the false claim this exists to prevent (US0348 AC3).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import changelog  # noqa: E402
from lib import sdlc_md  # noqa: E402

#: Where the pre-tag gate records the commit it judged. Read by `tag-check`, so a tag can only be
#: cut on the exact tree the gate ran over.
GREEN_MARKER = "release-gate-green.json"


def _green_path(root: Path) -> Path:
    return Path(root) / "sdlc-studio" / ".local" / GREEN_MARKER


def cut_changelog(root: Path | str, version: str) -> str:
    """Compose the pending fragments into `[Unreleased]`, then move its body under a
    `## [version] - <date>` header, leaving `[Unreleased]` empty. Returns the new header line.

    Refuses when the version already has a section (the cut is not idempotent-by-accident: a second
    cut of the same version would silently duplicate it) or when there is no `[Unreleased]`."""
    root = Path(root)
    changelog.compose(root, apply=True)          # the release-time fold + consume of the fragments
    clog = root / "CHANGELOG.md"
    text = clog.read_text(encoding="utf-8")
    header = f"## [{version}]"
    if re.search(rf"(?m)^{re.escape(header)}", text):
        raise ValueError(f"CHANGELOG.md already carries a {header} section - nothing cut")
    if "## [Unreleased]" not in text:
        raise ValueError("CHANGELOG.md has no '## [Unreleased]' section to cut from")
    head, rest = text.split("## [Unreleased]", 1)
    nxt = re.search(r"\n## \[", rest)
    body, tail = (rest[:nxt.start()], rest[nxt.start():]) if nxt else (rest, "")
    date = sdlc_md.now_date()
    new_header = f"## [{version}] - {date}"
    # [Unreleased] is emptied (header only); the accumulated body becomes the versioned section
    out = f"{head}## [Unreleased]\n\n{new_header}{body}{tail}"
    sdlc_md.atomic_write(clog, out)
    return new_header


def record_green(root: Path | str, commit: str) -> Path:
    """Stamp the commit the pre-tag gate passed on."""
    p = _green_path(Path(root))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"commit": (commit or "").strip()}) + "\n", encoding="utf-8")
    return p


def green_commit(root: Path | str) -> str | None:
    """The commit the gate was last recorded green on, or None."""
    p = _green_path(Path(root))
    if not p.is_file():
        return None
    try:
        return (json.loads(p.read_text(encoding="utf-8")).get("commit") or "").strip() or None
    except (OSError, ValueError):
        return None


def tag_check(root: Path | str, commit: str) -> tuple[bool, str]:
    """(allowed, reason). A tag of `commit` is allowed ONLY when the recorded gate-green commit is
    the same commit - so a tag can never assert a green measured on a different tree."""
    commit = (commit or "").strip()
    green = green_commit(root)
    if not green:
        return False, ("no release gate has been recorded green - run the pre-tag gate and "
                       "`release_cut.py record-green --commit <sha>` on the same commit first")
    if green != commit:
        return False, (f"the gate was recorded green on {green}, not the commit being tagged "
                       f"({commit}) - a tag asserting a green measured on a different tree is "
                       f"refused; re-run the gate on {commit}")
    return True, f"gate green on {commit} matches the tagged commit"


def _cmd_cut(args: argparse.Namespace) -> int:
    try:
        header = cut_changelog(args.root, args.version)
    except (ValueError, OSError) as exc:
        print(f"changelog-cut refused: {exc}", file=sys.stderr)
        return 2
    print(f"cut {header} from the fragments; [Unreleased] emptied")
    return 0


def _cmd_record_green(args: argparse.Namespace) -> int:
    record_green(args.root, args.commit)
    print(f"recorded release gate green on {args.commit}")
    return 0


def _cmd_tag_check(args: argparse.Namespace) -> int:
    allowed, reason = tag_check(args.root, args.commit)
    print(reason, file=sys.stderr if not allowed else sys.stdout)
    return 0 if allowed else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio release cut and tag guard.")
    sdlc_md.add_global_root(parser)
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("changelog-cut", help="compose fragments and cut a versioned section")
    c.add_argument("--version", required=True, help="the release version, e.g. 5.0.0")
    c.set_defaults(func=_cmd_cut)
    r = sub.add_parser("record-green", help="stamp the commit the pre-tag gate passed on")
    r.add_argument("--commit", required=True)
    r.set_defaults(func=_cmd_record_green)
    t = sub.add_parser("tag-check", help="refuse a tag unless the gate was green on that commit")
    t.add_argument("--commit", required=True)
    t.set_defaults(func=_cmd_tag_check)
    for p in (c, r, t):
        # SUPPRESS (not ".") so a global `--root X <verb>` set before the subcommand is not
        # clobbered by the subparser's own default - the family root-placement contract.
        p.add_argument("--root", default=argparse.SUPPRESS, help="Repo root (default: .)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Anchor the root ONCE before dispatch, so a run from a subdirectory acts on the project it
    # belongs to and a subcommand --root cannot clobber the global value (the family contract).
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
