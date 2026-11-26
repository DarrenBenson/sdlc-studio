#!/usr/bin/env python3
"""Release cut: turn the accumulated changelog fragments into a versioned section, and guard the
tag so it can never assert a green that was measured on a different tree.

Its verbs:

- `changelog-cut --version X.Y.Z` composes the pending `changelog.d/` fragments into `[Unreleased]`
  (the release-time `compose --apply`), then moves that body under a new `## [X.Y.Z] - <date>`
  header, leaving `[Unreleased]` empty. This is the deterministic cut US0348 requires - the notes
  come from the per-unit fragments, never a hand-written section. A version that already has a
  section, or a changelog with no `[Unreleased]`, is refused before anything is composed, so a
  refused cut leaves CHANGELOG.md and every fragment as they were. The cut also appends the
  release's record to `sdlc-studio/reports/releases.jsonl` (see `RELEASES_REL`) and prints it; a
  re-run for a version already recorded keeps that record as it is. It then prints one `persona
  review owed:` line per persona or seat card `persona_review.owed` names, on stdout and never
  in CHANGELOG.md: an owed review is reported, never a refusal.

- `record-green --commit <sha>` stamps the full sha the named commit resolves to, and refuses a
  name git cannot resolve to a commit; `tag-check --commit <sha>` resolves its argument the same
  way and refuses unless the stamp names the same commit. A tag asserting a green measured on a
  different tree is the false claim this exists to prevent (US0348 AC3). It also refuses a
  generated evidence page or evidence pack the tagged commit holds out of date with the records
  beside it (see `stale_release_records`).

- `evidence-pack --version X.Y.Z --reports RPT0001,RPT0002` writes the release's evidence pack
  under `sdlc-studio/reports/` from the named signed reports, read as committed. The logic lives
  in `evidence_pack.py`; this verb only delegates to it.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import changelog  # noqa: E402
from lib import sdlc_md  # noqa: E402

#: Where the pre-tag gate records the commit it judged. Read by `tag-check`, so a tag can only be
#: cut on the exact tree the gate ran over.
GREEN_MARKER = "release-gate-green.json"


def _green_path(root: Path) -> Path:
    return Path(root) / "sdlc-studio" / ".local" / GREEN_MARKER


#: The committed record of every release the cut made, one JSON object per line, oldest first:
#: `{"version", "date", "previous", "reports"}`, the version as given, the date of the cut, the
#: release before it (a tag in its own spelling, or the newest earlier record's version, or null)
#: and the ids of the signed reports it shipped. Kept beside the evidence packs and committed, so
#: the releases a change failure rate divides by are read from the tree.
RELEASES_REL = "sdlc-studio/reports/releases.jsonl"


def _release_records(root: Path) -> tuple[str, list[dict]]:
    """The record file's text and its records, oldest first ("" and [] when there is no file).
    A blank line is skipped. Raises ValueError naming the first other line that is not a JSON
    object with a string `version` and a `reports` list of strings, so the cut refuses before it
    writes anything."""
    path = root / RELEASES_REL
    if not path.is_file():
        return "", []
    text = path.read_text(encoding="utf-8")
    records = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            rec = None
        if not (isinstance(rec, dict) and isinstance(rec.get("version"), str)
                and isinstance(rec.get("reports"), list)
                and all(isinstance(rid, str) for rid in rec["reports"])):
            raise ValueError(f"{RELEASES_REL} line {n} is not a release record: {line[:80]}")
        records.append(rec)
    return text, records


def _previous_tag(root: Path) -> str | None:
    """The tag on the nearest tagged commit in HEAD's history, by its ref name, or None when there
    is none: git missing, no repository, no commit or no tag on a commit HEAD holds.

    Nearest is the first tagged commit `git rev-list --topo-order HEAD` lists, so a tag on a
    commit comes before a tag on any of its ancestors, however late either tag was made and
    however the commits are dated. Between tags on one commit, the latest creator date wins (an
    annotated tag's tagger date; a lightweight tag has none, so it takes its commit's date), then
    the first name. The ref name, never the name a tag object records inside it, which a renamed
    tag no longer matches and which `git describe` reports instead. Raises ValueError when git
    cannot list the tags or the history of a repository that has a commit."""
    try:
        head = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"],
                              capture_output=True, text=True, cwd=str(root), timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if head.returncode != 0:
        return None
    what = "the tags reachable from HEAD"
    try:
        listing = _git_bytes(root, ["for-each-ref", "--sort=-creatordate", "--format="
                                    "%(objecttype) %(objectname) %(refname:strip=2)",
                                    "refs/tags"], what)
        refs = [line.split(" ", 2) for line in listing.decode("utf-8", "replace").splitlines()]
        # an annotated tag, or a tag of a tag, is peeled through every tag to its commit
        peeled = iter(_git_bytes(root, ["rev-parse", *(f"refs/tags/{name}^{{}}" for kind, _, name
                                                       in refs if kind == "tag")], what).split())
        tagged: dict[str, str] = {}
        for kind, obj, name in refs:
            commit = next(peeled).decode("ascii") if kind == "tag" else obj
            tagged.setdefault(commit, name)      # the first is the newest on its commit
        history = _git_bytes(root, ["rev-list", "--topo-order", "HEAD"], what)
    except UnreadableRecord as exc:
        raise ValueError(str(exc)) from exc
    return next((tagged[sha] for sha in history.decode("ascii", "replace").split()
                 if sha in tagged), None)


def _shipped_reports(root: Path, records: list[dict], tag: str | None) -> list[str]:
    """The ids of the signed reports this release shipped, oldest signature first: those no
    earlier record names. For the first record, those not already signed as committed at the
    previous tag's commit, or every signed report when there is no tag. So once a record exists,
    a report signed between a cut and its tag is named by the next release's record. A report
    file that cannot be read, or a tag git cannot read, raises ValueError."""
    import sprint_report  # noqa: PLC0415 - lazy: the reader the evidence page uses
    try:
        signed = [rep.get("report_id") for rep in sprint_report._signed_reports(root)]
        if records:
            named = {rid for rec in records for rid in rec["reports"]}
        elif tag:
            sha = _git_bytes(root, ["rev-parse", "--verify", "-q", f"refs/tags/{tag}^{{commit}}"],
                             f"the tag {tag}").decode("utf-8", "replace").strip()
            named = {rep.get("report_id") for rep in _signed_reports_at(root, sha)}
        else:
            named = set()
    except (sprint_report.ReportError, UnreadableRecord) as exc:
        raise ValueError(str(exc)) from exc
    return [rid for rid in signed if rid not in named]


def _release_record_text(root: Path, version: str, date: str) -> str | None:
    """The record file with `version`'s record appended, every earlier line left as it is, or
    None when a record already names `version`: a re-run after an interrupted cut keeps the
    first record byte for byte."""
    text, records = _release_records(root)
    if any(rec["version"] == version for rec in records):
        return None
    tag = _previous_tag(root)
    previous = tag or (records[-1]["version"] if records else None)
    line = json.dumps({"version": version, "date": date, "previous": previous,
                       "reports": _shipped_reports(root, records, tag)})
    sep = "\n" if text and not text.endswith("\n") else ""
    return f"{text}{sep}{line}\n"


def release_record(root: Path | str, version: str) -> dict | None:
    """The record of `version` in the record file, or None."""
    return next((rec for rec in _release_records(Path(root))[1] if rec["version"] == version),
                None)


def cut_changelog(root: Path | str, version: str) -> str:
    """Compose the pending fragments into `[Unreleased]`, then move its body under a
    `## [version] - <date>` header, leaving `[Unreleased]` empty. Returns the new header line.

    Refuses when the version already has a section (the cut is not idempotent-by-accident: a second
    cut of the same version would silently duplicate it) or when there is no `[Unreleased]`. Both
    are asked of CHANGELOG.md BEFORE the fragments are composed, because composing rewrites
    `[Unreleased]` and deletes every fragment: a refusal that says nothing was cut must leave
    nothing changed. The release record (`RELEASES_REL`) is planned after those checks and
    before the compose, so a malformed record file refuses with nothing changed too, and it is
    written before CHANGELOG.md: a cut stopped between the two re-runs to the same record."""
    root = Path(root)
    clog = root / "CHANGELOG.md"
    header = f"## [{version}]"
    before = clog.read_text(encoding="utf-8")
    if re.search(rf"(?m)^{re.escape(header)}", before):
        raise ValueError(f"CHANGELOG.md already carries a {header} section - nothing cut")
    if "## [Unreleased]" not in before:
        raise ValueError("CHANGELOG.md has no '## [Unreleased]' section to cut from")
    date = sdlc_md.now_date()
    record = _release_record_text(root, version, date)
    changelog.compose(root, apply=True)          # the release-time fold + consume of the fragments
    text = clog.read_text(encoding="utf-8")
    head, rest = text.split("## [Unreleased]", 1)
    nxt = re.search(r"\n## \[", rest)
    body, tail = (rest[:nxt.start()], rest[nxt.start():]) if nxt else (rest, "")
    new_header = f"## [{version}] - {date}"
    # [Unreleased] is emptied (header only); the accumulated body becomes the versioned section
    out = f"{head}## [Unreleased]\n\n{new_header}{body}{tail}"
    if record is not None:
        sdlc_md.atomic_write(root / RELEASES_REL, record)
    sdlc_md.atomic_write(clog, out)
    return new_header


def record_green(root: Path | str, commit: str) -> Path:
    """Stamp the commit the pre-tag gate passed on, as the full sha `commit` resolves to.

    A name such as HEAD or a branch moves with every commit, so a stamp holding it would match
    whatever commit it names when the tag is checked, a tree the gate never ran on. Raises
    ValueError, writing nothing, when git cannot resolve `commit` to a commit."""
    sha = _resolve_commit(root, commit)
    if sha is None:
        raise ValueError(f"`{(commit or '').strip()}` does not resolve to a commit in this "
                         f"repository - no stamp was written")
    p = _green_path(Path(root))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"commit": sha}) + "\n", encoding="utf-8")
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


#: Conclusions that are not a failure. `skipped` and `neutral` are how a workflow says "this run
#: did not apply", which is not the same as "this run went wrong" - refusing them would make a
#: path-filtered workflow un-taggable. Anything else, including an empty conclusion, blocks.
CI_OK_CONCLUSIONS = frozenset({"success", "skipped", "neutral"})

#: A hung `gh` (proxy, auth prompt) must fail rather than block the release forever.
GH_TIMEOUT = 120


#: What `gh` says when it can reach neither github.com nor a configured Enterprise host for this
#: clone's remotes. It is the authority on what it can address - a URL test of our own would have
#: to enumerate every Enterprise domain, and would call a reachable GHE remote unsupported.
_GH_NOT_GITHUB = "known github host"

#: git's own words for "there is no repository here", which is a DEFINITE answer about
#: whether a forge exists - unlike every other way git can fail, which leaves it open.
_GIT_NOT_A_REPO = "not a git repository"


def _git_dir_exists(root: Path | str) -> bool:
    """Whether a `.git` sits at `root` or above it, checked WITHOUT asking git.

    The corroborating half of the "not a git repository" reading. git prints those words both
    for a directory that genuinely holds no repository and for a repository it cannot read, and
    only the first may pass a tag - so the message is believed only when the filesystem agrees
    with it. Deliberately does not shell out: the thing being corroborated is git's own answer.
    """
    try:
        here = Path(root).resolve()
    except OSError:
        return False
    for d in [here, *here.parents]:
        try:
            if (d / ".git").exists():
                return True
        except OSError:
            return True          # cannot tell: assume a repository, so the caller refuses
    return False


def _forge_remote(root: Path | str) -> tuple[str, str]:
    """`(state, detail)` where state is `has`, `none` or `unknown`.

    THREE states, not two, and the third is the one that matters. This returned a bare bool, and
    every way `git remote` can fail - a non-zero exit, git absent from PATH, a dubious-ownership
    refusal, a timeout - collapsed into `False`, which the caller read as "no forge to ask" and
    the tag guard read as a PASS. That is the exact defect this whole unit exists to remove,
    re-created inside its own fix: a question that could not be asked, answered in the
    reassuring direction. An independent review found it by running the guard in a clone git
    refused to read for dubious ownership - the commonest git failure in a container - where it
    reported "no git remote is configured" about a clone that has one.

    "There is no remote" and "I could not find out" are different facts and only the first may
    pass a tag."""
    try:
        proc = subprocess.run(["git", "remote"], capture_output=True, text=True,
                              cwd=str(root), timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return "unknown", (f"git could not be run to list this clone's remotes ({exc!r}), so "
                           f"whether there is a forge to ask is UNKNOWN")
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        if _GIT_NOT_A_REPO in stderr.lower() and not _git_dir_exists(root):
            # "not a git repository" is a definite answer ONLY when there is no `.git` to be
            # found. git prints the same words for a repository it cannot READ - `chmod 000
            # .git` produces it verbatim - so trusting the message alone re-opened the finding
            # this function was rewritten to close, one branch along. The corroborating check
            # is what makes it an answer rather than a guess.
            return "none", ""
        if _GIT_NOT_A_REPO in stderr.lower():
            return "unknown", (f"a `.git` exists here but git will not read it ({stderr}), so "
                               f"whether there is a forge to ask is UNKNOWN - an unreadable "
                               f"repository is not a repository without a remote")
        return "unknown", (f"git refused to list this clone's remotes: "
                           f"{stderr or f'exit {proc.returncode}'} - so whether there is a forge "
                           f"to ask is UNKNOWN, and an unanswered question may not pass a tag")
    if not proc.stdout.strip():
        return "none", ""
    return "has", ""


def _resolve_commit(root: Path | str, commit: str) -> str | None:
    """The full sha `commit` names, peeled to a commit, or None when git cannot resolve it to
    one: an unknown name, a sha no object here has, a tree or blob, or git not answering."""
    commit = (commit or "").strip()
    try:
        # `--end-of-options` stops a flag-shaped ref being read as a flag, and `--verify`
        # requires exactly one revision. Without them `git rev-parse` echoes an argument-shaped
        # value back with rc 0, so the "resolve to a full sha" contract was unenforced -
        # `--output=/tmp/x` came back unchanged. It failed safe only because the bogus token
        # then reached `gh` as a flag and errored into `unknown`, which is safety by accident.
        proc = subprocess.run(
            ["git", "rev-parse", "--verify", "--end-of-options", f"{commit}^{{commit}}"],
                              capture_output=True, text=True, cwd=str(root), timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    out = (proc.stdout or "").strip()
    return out if proc.returncode == 0 and out else None


def _full_sha(root: Path | str, commit: str) -> str:
    """`gh run list --commit` matches on the FULL sha and silently returns nothing for an
    abbreviated one - which this guard would read as "the forge has never run this commit" and
    refuse. A false refusal on a green tree trains the bypass just as surely as a false pass
    trains the tag, so resolve first and only then ask. An unresolvable ref is passed through
    unchanged: that is the forge's question to answer, not this helper's."""
    return _resolve_commit(root, commit) or commit


#: A sha as a stamp may hold it: the full sha `record-green` writes, or an abbreviated one an
#: older `record-green` stored as typed. Either names one object for good, unlike HEAD or a
#: branch, so it is safe to resolve when the stamp is read.
_SHA_RE = re.compile(r"^[0-9a-f]{4,64}$")


def _stamped_commit(root: Path | str, green: str) -> str | None:
    """The full sha of the commit a stored stamp names, or None when it is not the sha of a
    commit this repository holds.

    Any other name was typed into an older stamp and is never resolved: HEAD resolves to
    wherever HEAD is NOW, which is the false match the full-sha stamp exists to prevent."""
    return _resolve_commit(root, green) if _SHA_RE.match(green) else None


# ------------------------------------------------------------------ generated release records
#: The page `sprint_report.py evidence --out` generates, judged at the tag only when the tagged
#: commit holds it with its generation markers: a page with none was written by hand.
EVIDENCE_PAGE = "docs/evidence.md"
#: The topmost released section of CHANGELOG.md: the version `changelog-cut` last cut.
_CUT_VERSION_RE = re.compile(r"^## \[(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\]", re.M)
#: The pack header's report list and build commit, as `evidence_pack.build_pack` writes them.
_PACK_REPORTS_RE = re.compile(r"over the signed reports (RPT\d+(?:, RPT\d+)*)\.")
_PACK_BUILT_AT_RE = re.compile(r"(records committed at `)[0-9a-f]+(`)")


class UnreadableRecord(Exception):
    """A record at the tagged commit that git could not read, or that is not UTF-8 or JSON."""


def _git_bytes(root: Path, args: list[str], what: str) -> bytes:
    """A read-only git command's output; raises UnreadableRecord naming `what` when git fails."""
    try:
        proc = subprocess.run(["git", *args], capture_output=True, cwd=str(root), timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        raise UnreadableRecord(f"git could not read {what} ({exc!r})") from exc
    if proc.returncode != 0:
        why = proc.stderr.decode("utf-8", "replace").strip() or f"exit {proc.returncode}"
        raise UnreadableRecord(f"git could not read {what}: {why}")
    return proc.stdout


def _committed(root: Path, sha: str, rel: str) -> str | None:
    """`rel` (relative to `root`) as committed at `sha`, or None when the commit holds no such
    file. A file that is not UTF-8 raises UnreadableRecord, never a traceback."""
    what = f"{rel} at {sha[:12]}"
    if not _git_bytes(root, ["ls-tree", "--name-only", sha, "--", rel], what).strip():
        return None
    data = _git_bytes(root, ["show", f"{sha}:./{rel}"], what)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UnreadableRecord(f"{what} is not UTF-8 text ({exc.reason} at byte {exc.start})") \
            from exc


def _signed_reports_at(root: Path, sha: str) -> list[dict]:
    """The signed reports of record as committed at `sha`, read by `sprint_report`'s own reader
    (the one the evidence page is rendered from), oldest signature first."""
    import sprint_report  # noqa: PLC0415 - lazy: only a tag with release records reads reports
    reports_rel = sprint_report.REPORTS_REL
    listing = _git_bytes(root, ["ls-tree", "--name-only", sha, "--", f"{reports_rel}/"],
                         f"{reports_rel} at {sha[:12]}").decode("utf-8", "replace")
    with tempfile.TemporaryDirectory(prefix="tag_check_reports_") as tmp:
        scratch = sprint_report.report_dir(tmp)
        for listed in listing.splitlines():
            name = Path(listed).name
            if fnmatch.fnmatch(name, "RPT*.json"):
                sdlc_md.atomic_write(scratch / name,
                                     _committed(root, sha, f"{reports_rel}/{name}") or "")
        try:
            return sprint_report._signed_reports(tmp)
        except sprint_report.ReportError as exc:
            raise UnreadableRecord(str(exc)) from exc


def _row_reports(region: str) -> set[str]:
    """The report ids an evidence table names, one per row."""
    import sprint_report  # noqa: PLC0415 - the page's own row parser
    return {line.split("|")[2].strip() for line in sprint_report._page_rows(region).values()}


def _evidence_page_refusal(page: str, reports: list[dict]) -> str | None:
    """Why the committed evidence page is not what `reports` render, or None when it is."""
    import docgen  # noqa: PLC0415 - the one marker parser
    import sprint_report  # noqa: PLC0415 - the one renderer of the page
    regenerate = f"`sprint_report.py evidence --out {EVIDENCE_PAGE}`"
    if docgen.BEGIN not in page and docgen.END not in page:
        return None
    try:
        start, end = docgen.find_region(page, EVIDENCE_PAGE)
    except docgen.MarkerError as exc:
        return f"{exc}; repair the markers and regenerate it with {regenerate}"
    region, want = page[start:end], sprint_report.render_evidence(reports)
    if want.strip() == region.strip():
        return None
    missing = sorted(_row_reports(want) - _row_reports(region))
    if missing:
        return (f"{EVIDENCE_PAGE} does not carry {', '.join(missing)}, signed into the records "
                f"the tagged commit holds - regenerate it with {regenerate}, commit it, and tag "
                f"that commit")
    return (f"{EVIDENCE_PAGE} differs from what the signed reports at the tagged commit render "
            f"- regenerate it with {regenerate}, commit it, and tag that commit")


def _pack_refusal(root: Path, sha: str, version: str) -> str | None:
    """Why the committed evidence pack for `version` is missing or stale, or None when it is the
    pack its own named reports rebuild to from the records at `sha`."""
    import evidence_pack  # noqa: PLC0415 - lazy: only a cut release with signed reports reads it
    rel = evidence_pack.pack_rel(version)
    write = (f"`release_cut.py evidence-pack --version {version} --reports <the signed reports "
             f"{version} ships>`")
    pack = _committed(root, sha, rel)
    if pack is None:
        return (f"release {version} has no evidence pack at {rel} - write it with {write}, "
                f"commit it, and tag that commit")
    named = _PACK_REPORTS_RE.search(pack)
    if not named:
        return (f"{rel} names no signed reports in its header, so it cannot be rebuilt to "
                f"compare - write it again with {write}")
    reports = evidence_pack.parse_reports(named[1])
    write = f"`release_cut.py evidence-pack --version {version} --reports {','.join(reports)}`"
    try:
        rebuilt = evidence_pack.build_pack(root, version, reports, sha)
    except evidence_pack.PackError as exc:
        return (f"{rel} cannot be rebuilt from the records committed at {sha[:12]} ({exc}) - "
                f"write it again with {write} once they allow it")
    # The header names the commit the pack was READ at, which is never the commit that carries
    # it (a commit cannot hold its own sha), so that one name is set aside before comparing.
    if _PACK_BUILT_AT_RE.sub(r"\1\2", rebuilt) != _PACK_BUILT_AT_RE.sub(r"\1\2", pack):
        return (f"{rel} was built before the records it summarises last changed: rebuilt from "
                f"the records committed at {sha[:12]} it reads differently - write it again with "
                f"{write}, commit it, and tag that commit")
    return None


def stale_release_records(root: Path | str, sha: str) -> list[str]:
    """One refusal per generated release record the commit `sha` holds out of date.

    The evidence page and the evidence pack are written at the cut, but the release run's own
    report is signed after it and records keep changing, so each is compared with the records
    as committed at `sha`, never the working tree. The page is judged when the commit holds it
    between generation markers; the pack is owed for the version CHANGELOG.md last cut, once
    the commit holds a signed report for it to summarise. A project that adopted neither tags
    as before. Raises UnreadableRecord when a record cannot be read."""
    root = Path(root)
    page = _committed(root, sha, EVIDENCE_PAGE)
    cut = _CUT_VERSION_RE.search(_committed(root, sha, "CHANGELOG.md") or "")
    if page is None and cut is None:
        return []
    reports = _signed_reports_at(root, sha)
    found = [_evidence_page_refusal(page, reports) if page is not None else None,
             _pack_refusal(root, sha, cut[1]) if cut and reports else None]
    return [refusal for refusal in found if refusal]


def forge_ci_state(root: Path | str, commit: str) -> tuple[str, str]:
    """`(state, detail)` - what the FORGE says about CI on `commit`, never what a local file says.

    States: `success`, `failed`, `pending`, `none`, `no-forge`, `unsupported`, `unknown`. Only
    `success`, `no-forge` and `unsupported` may pass a tag.

    The distinctions are the whole point, because collapsing any two of them is how both v5 tags
    were cut over a red CI:

    * `none` - the forge has no run for this commit. Either it was never pushed, or the workflow
      never fired. "Nobody has judged this tree" is not a green, and reading it as one is the
      original defect one step removed.
    * `pending` - a run exists and has not finished. A tag cut now asserts an outcome that has
      not happened yet.
    * `unknown` - `gh` is absent, unauthenticated, timed out, or answered something unparseable.
      "I could not look" must never be reported as "there is nothing wrong"; that is exactly the
      rule `release_assets.published` states for the same question about the same forge.
    * `no-forge` - there is no remote, so there is no CI to ask about and the rule was never
      adopted in this clone. Distinguished from `unknown` precisely so that a missing `gh`
      cannot borrow it - and, since an independent review, so that a missing or refusing GIT
      cannot borrow it either, which is how this function first shipped.
    * `unsupported` - there IS a forge and `gh` cannot address it: GitLab, Bitbucket, a
      self-hosted git. Not the same as a forge that would not answer. This script is shipped,
      and the gate documentation states that nothing in it is GitHub-specific, so refusing here
      would have a bug fix invent a hard GitHub requirement the tool never had. It passes for
      the same reason `no-forge` does - the rule was never adopted for that forge - and says so
      rather than implying an answer was obtained.
    """
    commit = (commit or "").strip()
    if not commit:
        # `gh run list --commit ""` IGNORES the filter and returns whatever ran most recently,
        # so an empty commit would report success on another tree's evidence. Unreachable
        # through `tag_check`, which compares the stamp first - but this is a public function
        # and a guard that is safe only because of its caller is safe by luck.
        return "unknown", "no commit was named, so there is nothing to ask the forge about"
    remote_state, remote_detail = _forge_remote(root)
    if remote_state == "unknown":
        return "unknown", remote_detail
    if remote_state == "none":
        return "no-forge", ("no git remote is configured, so there is no forge CI to ask about - "
                            "the tag is judged on the local gate alone")
    if shutil.which("gh") is None:
        return "unknown", ("gh is not on PATH, so whether CI passed on the pushed commit is "
                           "UNKNOWN - install https://cli.github.com/ and authenticate")
    commit = _full_sha(root, commit)
    try:
        proc = subprocess.run(
            ["gh", "run", "list", "--commit", commit, "--limit", "50",
             "--json", "conclusion,status,workflowName"],
            capture_output=True, text=True, cwd=str(root), timeout=GH_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as exc:
        return "unknown", f"the forge could not be asked about {commit} ({exc!r})"
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        if _GH_NOT_GITHUB in stderr.lower():
            # A forge this code does not know HOW to ask, which is not the same as a forge that
            # would not answer. `release_cut.py` is SHIPPED, and consuming projects run on
            # GitLab, Bitbucket and self-hosted git; refusing them would make a bug fix invent a
            # hard GitHub requirement the tool never had, and the shipped gate documentation
            # states in terms that nothing here is GitHub-specific. So this passes for the same
            # reason a remoteless clone does: the rule was never adopted for that forge, and
            # saying so out loud is different from pretending an answer was obtained.
            return "unsupported", (f"this clone's remotes are not on a forge `gh` can query, so "
                                   f"its CI cannot be read from here - the tag is judged on the "
                                   f"local gate alone ({stderr})")
        return "unknown", (f"gh could not report CI for {commit}: "
                           f"{stderr or f'exit {proc.returncode}'}")
    try:
        runs = json.loads(proc.stdout or "[]")
    except ValueError:
        return "unknown", f"gh answered something that is not JSON when asked about {commit}"
    if not isinstance(runs, list) or not runs:
        return "none", (f"the forge has no CI run for {commit} - either it has not been pushed, "
                        f"or no workflow fired on it")
    unfinished = [r for r in runs if (r.get("status") or "") != "completed"]
    if unfinished:
        names = ", ".join(sorted({str(r.get("workflowName") or "?") for r in unfinished})[:5])
        return "pending", f"CI on {commit} has not finished ({names})"
    bad = [r for r in runs if (r.get("conclusion") or "") not in CI_OK_CONCLUSIONS]
    if bad:
        names = ", ".join(sorted({f"{r.get('workflowName') or '?'}: "
                                  f"{r.get('conclusion') or 'no conclusion'}" for r in bad})[:5])
        return "failed", f"CI on {commit} did not pass ({names})"
    if not any((r.get("conclusion") or "") == "success" for r in runs):
        return "none", (f"every CI run on {commit} was skipped or neutral, so nothing actually "
                        f"judged this tree")
    return "success", f"CI passed on {commit} on the forge"


def tag_check(root: Path | str, commit: str) -> tuple[bool, str]:
    """(allowed, reason). A tag of `commit` is allowed ONLY when the recorded gate-green commit is
    the same commit - so a tag can never assert a green measured on a different tree - and the
    forge reports CI green on it.

    Both sides are compared as full shas: the argument is resolved here and the stamp holds the
    sha `record_green` resolved, so HEAD after another commit is not the commit the gate ran on.
    The generated evidence page and evidence pack the commit holds must be current with its
    records too (`stale_release_records`).

    Those are what a release needs. Whether every delivery unit was named in a retro
    is not asked here: `sprint sign` seals each run, and the close-owed detector could not read
    a carry bug or a ruled closure, so it refused tags over work that was closed (US0942). Its
    answer stays on the `status`/`hint` advisory."""
    named = (commit or "").strip()
    commit = _resolve_commit(root, named)
    if commit is None:
        return False, (f"`{named}` does not resolve to a commit in this repository, so there is "
                       f"no tree to judge - name the commit being tagged")
    green = green_commit(root)
    if not green:
        return False, ("no release gate has been recorded green - run the pre-tag gate and "
                       "`release_cut.py record-green --commit <sha>` on the same commit first")
    stamped = _stamped_commit(root, green)
    if stamped is None:
        return False, (f"the release gate stamp holds `{green}`, which is not the sha of a "
                       f"commit this repository holds - a stamp names the commit the gate ran on "
                       f"by its sha, never by a name such as HEAD that moves with every commit; "
                       f"re-run the gate and `release_cut.py record-green --commit {commit}`")
    if stamped != commit:
        return False, (f"the gate was recorded green on {stamped}, not the commit being tagged "
                       f"({commit}) - a tag asserting a green measured on a different tree is "
                       f"refused; re-run the gate on {commit}")
    # The generated release pages are claims about the records at this commit, so they are
    # judged before the forge is asked: a stale page fails the same way on every forge.
    try:
        stale = stale_release_records(root, commit)
    except UnreadableRecord as exc:
        stale = [f"a release record could not be read, so whether it is current is UNKNOWN: "
                 f"{exc}"]
    if stale:
        return False, "refusing the tag: " + "; ".join(stale)
    # Everything above this line is a claim about the LOCAL tree, answered from a local file. That
    # was the whole guard until BG0576, and it is why v5.0.0 and v5.0.1 were both tagged over a CI
    # that had been red for two days: the gate ran green on a developer machine, the runner
    # disagreed, and nothing in the release chain ever asked it. Whether CI passed on the pushed
    # commit is a claim about the remote, and only the remote can answer it.
    state, detail = forge_ci_state(root, commit)
    if state not in ("success", "no-forge", "unsupported"):
        return False, (f"refusing the tag: {detail}. A tag asserts that this tree passed, and "
                       f"the only place that can be answered for a pushed commit is the forge - "
                       f"a local green says nothing about the runner")
    forge_note = {"no-forge": "no forge to ask",
                  "unsupported": "this clone's forge cannot be queried from here, so its CI was "
                                 "NOT consulted",
                  "success": "CI green on the forge"}[state]
    return True, f"gate green on {commit} matches the tagged commit, and {forge_note}"


def _cmd_cut(args: argparse.Namespace) -> int:
    try:
        header = cut_changelog(args.root, args.version)
    except (ValueError, OSError) as exc:
        print(f"changelog-cut refused: {exc}", file=sys.stderr)
        return 2
    print(f"cut {header} from the fragments; [Unreleased] emptied")
    print(f"recorded in {RELEASES_REL}: {json.dumps(release_record(args.root, args.version))}")
    import persona_review  # noqa: PLC0415 - sibling; the one reader of owed reviews
    for owed in persona_review.owed(args.root):
        print(owed["line"])
    return 0


def _cmd_record_green(args: argparse.Namespace) -> int:
    try:
        record_green(args.root, args.commit)
    except ValueError as exc:
        print(f"record-green refused: {exc}", file=sys.stderr)
        return 2
    print(f"recorded release gate green on {green_commit(args.root)}")
    return 0


def _cmd_tag_check(args: argparse.Namespace) -> int:
    allowed, reason = tag_check(args.root, args.commit)
    print(reason, file=sys.stderr if not allowed else sys.stdout)
    return 0 if allowed else 2


def _cmd_evidence_pack(args: argparse.Namespace) -> int:
    import evidence_pack  # noqa: PLC0415 - lazy: only this verb reads the ledger and stories
    try:
        evidence_pack.write_pack(args.root, args.version,
                                 evidence_pack.parse_reports(args.reports), args.rev)
    except evidence_pack.PackError as exc:
        print(f"evidence-pack refused: {exc}", file=sys.stderr)
        return 2
    print(f"wrote the evidence pack {evidence_pack.pack_rel(args.version)}")
    return 0


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
    e = sub.add_parser("evidence-pack",
                       help="write a release's evidence pack from committed signed reports")
    e.add_argument("--version", required=True, help="the release version, e.g. 6.4.0")
    e.add_argument("--reports", required=True,
                   help="the signed reports the release ships, comma-separated: RPT0001,RPT0002")
    e.add_argument("--rev", default="HEAD", help="the commit whose records are read (default HEAD)")
    e.set_defaults(func=_cmd_evidence_pack)
    for p in (c, r, t, e):
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
