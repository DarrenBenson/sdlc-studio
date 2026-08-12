#!/usr/bin/env python3
"""The release assets the verified install verifies against (BG0575, CR0545).

`SDLC_STUDIO_REQUIRE_CHECKSUM=1` checks a download against a `.sha256` published beside it.
GitHub serves no sidecar next to a generated source archive, so that only works if THIS project
publishes both halves - which `.github/workflows/release.yml` does on every tag.

Three things then have to agree, and nothing made them agree before:

  * the command the workflow builds each asset with,
  * the filename it uploads it under, and
  * the URL `install.sh` and `install.ps1` construct to fetch it.

Change any one and the install 404s, falls back to the unverified archive, and refuses - at the
user, at install time. So the workflow is READ here rather than restated: `build_commands` returns
the `git archive` lines the workflow actually runs, and the tests execute THOSE. A test that
hardcodes its own `git archive` proves that git honours `--prefix`, which is a property of git and
not of this repository - it stays green while the workflow drifts.

`check` is the gate. It refuses a tag whose Release does not carry the full set, so a release that
would leave the documented verified install broken fails at the boundary rather than at a reader.

Usage:
    python3 tools/release_assets.py names   --tag v5.0.1
    python3 tools/release_assets.py check   --tag v5.0.1     # needs `gh`, authenticated
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_REL = ".github/workflows/release.yml"

#: The archive formats published per tag. Each ships with a `.sha256` beside it, and the pair is
#: what a verified install needs: `install.sh` takes the tarball, `install.ps1` takes the zip.
FORMATS = ("tar.gz", "zip")

#: A `git archive` invocation inside the workflow, captured whole so a test can run it verbatim.
_ARCHIVE_RE = re.compile(r"^\s*(git archive\s+[^\n]*)$", re.MULTILINE)


def asset_names(tag: str) -> list[str]:
    """Every filename a Release must carry for `tag`, assets and sidecars.

    This is the single statement of the naming convention. `install.sh` and `install.ps1` build
    their URLs from the same shape, and `test_release_assets.py` pins that they still match.
    """
    out: list[str] = []
    for fmt in FORMATS:
        name = f"sdlc-studio-{tag}.{fmt}"
        out.extend((name, f"{name}.sha256"))
    return out


def build_commands(root: Path | str | None = None) -> list[str]:
    """The `git archive` command lines the release workflow actually runs.

    Read from the workflow rather than restated, so a test executing these executes what ships.
    """
    base = Path(root) if root else REPO_ROOT
    text = (base / WORKFLOW_REL).read_text(encoding="utf-8")
    return [m.group(1).strip() for m in _ARCHIVE_RE.finditer(text)]


def expand(command: str, tag: str, outdir: Path | str | None = None,
           ref: str | None = None) -> str:
    """A workflow `git archive` line with its shell variables resolved for `tag`.

    The workflow computes `prefix` from the tag with the leading `v` stripped, exactly as the
    installers' extraction step expects to find it.

    `outdir` redirects the workflow's `-o dist/...` somewhere a test owns, and `ref` substitutes
    the revision - a fixture tag does not exist in the repository. Both are rewrites of the
    workflow's OWN command rather than a reimplementation of it, which is the point: what runs
    in the test is what runs in CI, minus the two things a test cannot share with it.
    """
    prefix = f"sdlc-studio-{tag.lstrip('v')}/"
    out = command.replace('"$prefix"', prefix).replace("$prefix", prefix)
    out = out.replace('"$tag"', tag).replace("$tag", tag)
    if outdir is not None:
        out = re.sub(r'-o\s+"?dist/([^"\s]+)"?', rf'-o {Path(outdir)}/\1', out)
    if ref is not None:
        out = re.sub(rf'\s{re.escape(tag)}\s*$', f" {ref}", out)
    return out


def built_names(tag: str, root: Path | str | None = None) -> list[str]:
    """The filenames the workflow's `git archive` lines actually WRITE, for `tag`.

    Taken from each command's own `-o` path rather than from anywhere the name merely appears.
    A test asserting the expected name occurs somewhere in the workflow passes while the build
    writes something else entirely - the name is repeated on the digest line, so a rename in the
    `-o` alone leaves the file present and the assertion green.
    """
    out: list[str] = []
    for command in build_commands(root):
        m = re.search(r'-o\s+"?dist/([^"\s]+)"?', expand(command, tag))
        if m:
            out.append(m.group(1))
    return out


def published(tag: str) -> list[str]:
    """The asset filenames the Release for `tag` currently carries.

    Returns an empty list when there is no Release. A `gh` that is missing or unauthenticated
    raises, because "I could not look" must never be reported as "there is nothing there".
    """
    proc = subprocess.run(
        ["gh", "release", "view", tag, "--json", "assets"],
        capture_output=True, text=True, cwd=str(REPO_ROOT))
    if proc.returncode != 0:
        stderr = proc.stderr.lower()
        if "release not found" in stderr or "not found" in stderr:
            return []
        raise RuntimeError(f"could not read the Release for {tag}: {proc.stderr.strip()}")
    data = json.loads(proc.stdout or "{}")
    return [a.get("name", "") for a in data.get("assets", [])]


def missing(tag: str) -> list[str]:
    """The asset filenames `tag` needs and does not have."""
    have = set(published(tag))
    return [n for n in asset_names(tag) if n not in have]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="release_assets.py",
        description="The release assets a verified install verifies against.")
    sub = parser.add_subparsers(dest="verb", required=True)
    for verb, helptext in (("names", "print the filenames a Release must carry"),
                           ("check", "refuse a tag whose Release is missing any of them")):
        p = sub.add_parser(verb, help=helptext)
        p.add_argument("--tag", required=True)
    args = parser.parse_args(argv)

    if args.verb == "names":
        for name in asset_names(args.tag):
            print(name)
        return 0

    try:
        gone = missing(args.tag)
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"release-assets: {exc}", file=sys.stderr)
        return 2
    if not gone:
        print(f"release-assets: {args.tag} carries all {len(asset_names(args.tag))} assets")
        return 0
    print(f"release-assets: {args.tag} is missing {len(gone)} asset(s):", file=sys.stderr)
    for name in gone:
        print(f"  {name}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Without these the documented `SDLC_STUDIO_REQUIRE_CHECKSUM=1` install falls back to "
          "GitHub's generated archive, finds no digest, and refuses. Publish them with "
          f"`gh workflow run release.yml -f tag={args.tag}`.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
