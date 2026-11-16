"""US1170: the v6.4.0 release notes lead with what changed for the person answering for the release.

The reader is a head of engineering on 6.3.0 deciding whether her teams take 6.4 to the change
board. Each check is a function returning its problems, run on the notes and on a control it must
refuse: the 6.3.0 notes as they stand and with the version changed, a draft composed from the 6.4
changelog fragments, a theme with its units cut, a changed default with its replacement cut, a
breaking change no fragment records, a configuration default `reference-config.md` contradicts,
and a cost figure with its report cut, its value changed or its report unsigned. The defaults and
the figures are read from their sources when the test runs, never typed here, and the upgrade path
is checked by running the notes' own steps on a project v6.3.0's `init.py` created.

The 6.4.0 skill is the v6.4.0 tag's tree once the tag exists, and before then this tree with its
version read as 6.4.0, so the checks judge 6.4.0's own CLI before the cut and after it. The
CHANGELOG link is judged against the layout the CHANGELOG has at the time: `[Unreleased]` before
the cut, `[6.4.0]` after it.
"""
# test-census-subject: docs/release-notes-v6.4.0.md
from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SKILL_REL = ".claude/skills/sdlc-studio"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.append(str(REPO / SKILL_REL / "scripts" / "tests"))
from test_lean_release_notes_v6 import (  # noqa: E402
    UNIT_ID, _blank, changelog_sections, section, sections, units)
from test_lean_release_notes_v61 import _norm, _run  # noqa: E402
from test_lean_release_notes_v62 import _blocks, _cli, _extract, _tree  # noqa: E402

NOTES = REPO / "docs" / "release-notes-v6.4.0.md"
NOTES_63 = REPO / "docs" / "release-notes-v6.3.0.md"
CHANGELOG = REPO / "CHANGELOG.md"
FRAGMENTS = REPO / "changelog.d"
REPORTS = REPO / "sdlc-studio" / "reports"

#: Each theme of the first section -> the units its bullet names, and no others.
THEMES = {
    "a release carries evidence a change board accepts":
        {"US0992", "US0993", "US0994", "US0995", "US0996", "US0997", "US0998", "US1155",
         "US1156", "US1160", "US1161"},
    "a run's cost is forecast before it starts and set beside the actual, priced at each "
    "model's own rate":
        {"US0999", "US1000", "US1143", "US1144", "US1145", "US1149", "US1150", "US1151",
         "US1165", "US1166"},
    "each review seat has a record, an escaped defect is traced to the approval that missed it, "
    "a seat learns only from a signed run, and a high-risk unit gets a second independent seat":
        {"US1011", "US1012", "US1013", "US1015", "US1058", "US1059", "US1061", "US1062",
         "US1064", "US1065", "US1066", "US1067", "US1068", "US1152", "US1153", "US1154",
         "US1157", "US1158", "US1159"},
    "the front door is written for a head of engineering":
        {"US1146", "US1147", "US1148", "US1162", "US1163", "US1164"},
}
COUNT_LINE = re.compile(r"^\*\*v6\.4\.0 discloses \d+ open defects: \d+ Medium, \d+ Low\.\*\*$")
NO_BREAKING = re.compile(r"No 6\.4 fragment is filed under Breaking, Removed or Security\.")
NOT_FILED = ("Breaking", "Removed", "Security")
#: Each change a 6.3 habit meets, label -> (what names its bullet, what the bullet must also say,
#: what its `Instead:` clause must carry).
CHANGES = {
    "the replayed verdict file": (
        r"`critic\.py record --from-verdict` refuses",
        (r"exits 2", r"earlier row's `Source` already carries", r"`UNIT` line names another unit"),
        r"fresh verdict file"),
    "the self-review": (
        r"recorded as a self-review",
        (r"`self-review:<path>`", r"review-coverage step", r"`sprint\.py sign`"),
        r"`critic\.py brief`"),
    "the Source column": (
        r"ledger gains a `Source` column",
        (r"ninth column", r"6\.3\.0 install reads a nine-cell row as malformed"),
        r"`--from-verdict`"),
    "the Copilot billing default": (
        r"`pricing\.copilot_billing` defaults to", (r"premium requests",),
        r"`pricing\.copilot_billing: requests`"),
    "the run record citation": (
        r"cites the committed run record, not `\.local/run-state\.json`",
        (r"`sdlc-studio/reports/runs/<RUN-ID>\.json`", r"checks VALID"),
        r"`sdlc-studio/reports/runs/`"),
    "the plan digest": (r"names its plan by digest", (r"`plan_digest`", r"`plan` is now null"),
                        r"`plan_digest`"),
    "the partly skipped Verify line": (r"Verify line that ran only in part fails",
                                       (r"`partly_skipped=N`",), r"skipped tests run"),
    "the stacked Verify lines": (
        r"`transition\.py set <story> Ready` refuses a criterion with more than one Verify line",
        (r"`--force` does not waive it",), r"split the criterion"),
    "the fresh-session warning": (
        r"`sprint\.py resume` warns", (r"`sprint\.fresh_session` defaults to", r"exits 2"),
        r"`sprint\.py handoff`"),
    "the report envelope": (
        r"new rows and envelope keys",
        (r"`evidence_schema`", r"`cost_forecast`", r"re-derives as it was filed"),
        r"tolerate keys"),
}
#: A changed default the section states -> the configuration key whose default it must equal.
CHANGED_DEFAULTS = {r"`pricing\.copilot_billing` defaults to `([^`]+)`": "pricing.copilot_billing",
                    r"`sprint\.fresh_session` defaults to `([^`]+)`": "sprint.fresh_session"}
#: The keys AC3 names -> what reads the default `reference-config.md` states for each.
REFERENCE_DEFAULTS = {
    "risk.components": r"`risk\.components` \(default `([^`]+)`\)",
    "routing.effort.builder":
        r"^\| `routing\.effort\.builder`, `routing\.effort\.reviewer` \|.*\| `([^`]+)` \|\s*$",
    "routing.effort.reviewer":
        r"^\| `routing\.effort\.builder`, `routing\.effort\.reviewer` \|.*\| `([^`]+)` \|\s*$",
    "routing.effort.reviewer_below_builder":
        r"^\| `routing\.effort\.reviewer_below_builder` \|.*\| `([^`]+)` \|\s*$",
    "pricing.copilot_billing": r"^\| `pricing\.copilot_billing` \| `([^`]+)` \|",
    "personas.memory.validity_days": r"^\| `personas\.memory\.validity_days` \| `?(\w+)`? \|",
    "personas.memory.inject_max": r"^\| `personas\.memory\.inject_max` \| `?(\w+)`? \|",
}
STAMP = "sdlc-studio/.version stale (skill 6.3.0 -> 6.4.0)"
#: A cost figure: dollars, points, or priced tokens.
COST = re.compile(r"\$(\d[\d,]*(?:\.\d+)?)|\b(\d[\d,]*) (?:delivered )?points?\b|"
                  r"\b(\d[\d,]*(?:\.\d+)?) priced tokens\b")
REPORT_ID = re.compile(r"\bRPT\d{4}\b")
#: The signed reports of the runs that built 6.4, runs nine to fourteen.
RUNS_64 = {f"RPT{n:04d}" for n in range(28, 34)}
_FIX: dict[str, Path | str] = {}
#: A `migrate.py` that reports what the notes quote but writes a file of its own, the control
#: `step_problems` must refuse on both steps.
_STRAY = """import json, sys
from pathlib import Path
root = Path(sys.argv[sys.argv.index("--root") + 1])
(root / "stray.txt").write_text(" ".join(sys.argv[1:]))
print(json.dumps({"deterministic": [{"detail": "%s"}]}))
""" % STAMP


def shipped(rel: str, tag: str = "v6.4.0") -> str:
    """`rel` at `tag` once this clone holds it, else, for v6.4.0 alone, as this tree holds it.
    An earlier release is never this tree. A tree holding no `.git`, which git does not read as a
    work tree, is not a clone and holds none, so the check reading it is skipped, naming why. A
    clone fails instead: where its git fails, naming the failure, and where it lacks the tag."""
    ref = _run("git", "-C", str(REPO), "rev-parse", "-q", "--verify", f"refs/tags/{tag}")
    if ref.returncode != 0:
        if tag == "v6.4.0":
            return (REPO / rel).read_text(encoding="utf-8")
        top = _run("git", "-C", str(REPO), "rev-parse", "--show-toplevel")
        if not (REPO / ".git").exists() and (
                top.returncode != 0 or Path(top.stdout.strip()).resolve() != REPO.resolve()):
            raise unittest.SkipTest(f"this tree is not a git clone, so it holds no {tag} "
                                    f"tree to read {rel} from")
        if top.returncode != 0 or ref.returncode != 1:
            bad = top if top.returncode != 0 else ref
            raise AssertionError(f"git failed in this clone reading the {tag} tag for {rel}: "
                                 f"exit {bad.returncode}: {bad.stderr.strip()}")
        raise AssertionError(f"this clone has no {tag} tag to read {rel} from: fetch tags")
    proc = _run("git", "-C", str(REPO), "show", f"{tag}:{rel}")
    if proc.returncode != 0:
        raise AssertionError(f"git show {tag}:{rel} failed: {proc.stderr}")
    return proc.stdout


def entries_64(changelog: str, fragments: Path = FRAGMENTS) -> list[tuple[str, str]]:
    """(section, body) of each 6.4 entry wherever the layout holds it at the time: the
    `## [6.4.0]` section's subsections once the cut has written it, the pending `changelog.d/`
    fragments only before then (a fragment present after the cut belongs to the next release)."""
    cut = re.search(r"^## \[6\.4\.0\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.M | re.S)
    if cut:
        return [(m.group(1), m.group(2)) for m in
                re.finditer(r"^### (\w+)\n(.*?)(?=^### |\Z)", cut.group(1), re.M | re.S)]
    out = []
    for p in sorted(fragments.glob("*.md")) if fragments.is_dir() else []:
        head, _, body = p.read_text(encoding="utf-8").partition("\n")
        m = re.match(r"<!-- section: (\w+) -->", head)
        out.append((m.group(1) if m else "", body))
    return out


def _value(value: object) -> str:
    """A configuration value as the notes and `reference-config.md` write it in a code span."""
    if value == {}:
        return "{}"
    if value == "" or value is None:
        return '""'
    return str(value).lower() if isinstance(value, bool) else str(value)


def _flat(tree: dict, prefix: str = "") -> dict[str, str]:
    out = {}
    for key, value in (tree or {}).items():
        if isinstance(value, dict) and value:
            out.update(_flat(value, f"{prefix}{key}."))
        else:
            out[f"{prefix}{key}"] = _value(value)
    return out


def stated_defaults(reference: str | None = None) -> dict:
    """The default 6.4's `reference-config.md` states for each key AC3 names, or None where it
    states none. No earlier release is read, so this holds in a tree that is not a git clone."""
    reference = shipped(f"{SKILL_REL}/reference-config.md") if reference is None else reference
    stated = {}
    for key, rx in REFERENCE_DEFAULTS.items():
        m = re.search(rx, reference, re.M)
        stated[key] = m.group(1) if m else None
    return stated


def defaults(reference: str | None = None, new: str | None = None,
             old: str | None = None) -> tuple[dict, dict]:
    """(`stated_defaults`; each key 6.4's `config-defaults.yaml` holds and 6.3.0's does not, with
    its value). 6.3.0's is read from the v6.3.0 tag, so a check calling this is skipped where
    `shipped` finds no git clone."""
    import yaml  # noqa: PLC0415 - config.py, whose defaults this reads, needs it too
    rel = f"{SKILL_REL}/templates/config-defaults.yaml"
    stated = stated_defaults(reference)
    new = shipped(rel) if new is None else new
    old = shipped(rel, "v6.3.0") if old is None else old
    was = _flat(yaml.safe_load(old) or {})
    added = {k: v for k, v in _flat(yaml.safe_load(new) or {}).items() if k not in was}
    return stated, added


def lead_problems(text: str, changelog: str) -> list[str]:
    """AC1: a one-sentence headline naming 6.4.0 as current, a first section holding the four
    themes and nothing else, each naming exactly its units, no unit id outside a theme bullet but
    in the known-issues and sources passages, and the CHANGELOG section holding 6.4's entries
    linked."""
    problems = []
    body = text.split("\n", 1)[1] if text.startswith("# ") else text
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    headline = " ".join(paras[0].replace("**", "").split()) if paras else ""
    if len(re.findall(r"[.!?](?:\s|$)", headline)) != 1 or not re.search(
            r"\b6\.4\.0 is the current release\b", headline):
        problems.append(f"the opening is not one sentence naming 6.4.0 the current release: "
                        f"{headline[:120]!r}")
    blank = _blank(text)
    firsts = sections(blank)
    first = firsts[0][1] if firsts else ""
    bullets, paras = _blocks(first)
    problems += [f"the first section holds text outside its theme bullets: "
                 f"{' '.join(p.split())[:80]!r}" for p in paras]
    problems += [f"the first section lists a theme that is not one of the four: "
                 f"{' '.join(b.split())[:80]!r}" for b in bullets
                 if not any(theme in _norm(b) for theme in THEMES)]
    rest = blank
    for theme, want in THEMES.items():
        hits = [b for b in bullets if theme in _norm(b)]
        if not hits:
            problems.append(f"the first section lists no theme {theme[:60]!r}")
            continue
        if len(hits) > 1:
            problems.append(f"the first section lists the theme {theme[:60]!r} {len(hits)} times")
        rest = rest.replace(hits[0], "", 1)
        named = set(UNIT_ID.findall(hits[0]))
        if not named:
            problems.append(f"the theme {theme[:60]!r} names no unit")
            continue
        problems += [f"the theme {theme[:60]!r} does not name {u}" for u in sorted(want - named)]
        problems += [f"the theme {theme[:60]!r} names {u}, not one of its units"
                     for u in sorted(named - want)]
    for heading, sbody in sections(rest):
        if re.search(r"known issues|sources", heading, re.I):
            continue
        problems += [f"unit id {m} outside a theme, under '{heading}'"
                     for m in UNIT_ID.findall(sbody)]
    labels = changelog_sections(changelog)
    linked = {labels.get(a) for a in re.findall(r"\]\(\.\./CHANGELOG\.md#([\w-]+)\)", text)}
    want = "6.4.0" if "6.4.0" in labels.values() else "Unreleased"
    if want not in linked:
        problems.append(f"no link to the CHANGELOG's {want} section")
    return problems


def breaking_problems(text: str, entries: list[tuple[str, str]]) -> list[str]:
    """AC2: the notes say no 6.4 fragment is filed under Breaking, Removed or Security exactly
    when none is, and claim no breaking change when none is filed."""
    filed = [s for s, _b in entries if s in NOT_FILED]
    said = bool(NO_BREAKING.search(" ".join(_blank(text).split())))
    if filed:
        return [f"the notes say no fragment is Breaking, Removed or Security, but {len(filed)} "
                f"are"] if said else []
    problems = [] if said else ["the notes do not state that no 6.4 fragment is filed under "
                                "Breaking, Removed or Security"]
    problems += [f"a heading claims a breaking change no fragment records: {h!r}"
                 for h in re.findall(r"^#{1,6} (.*)$", _blank(text), re.M)
                 if re.search(r"(?i)\bbreaking\b|\bremoved\b|\bsecurity\b", h)]
    problems += [f"a sentence claims a breaking change no fragment records: {u[:100]!r}"
                 for u in units(text) if re.search(r"(?i)\bbreaking\b|\bsecurity fix\b", u)
                 and not NO_BREAKING.search(u)]
    return problems


def changed_problems(text: str, entries: list[tuple[str, str]]) -> list[str]:
    """AC2: each listed change a 6.3 habit meets in exactly one bullet, beside what to do
    instead, no bullet but a listed change, and no text but the no-Breaking paragraph outside
    them. `default_problems` judges the defaults the section states."""
    body = section(text, r"^Changed defaults and new refusals$")
    if body is None:
        return ["no 'Changed defaults and new refusals' section"]
    found, paras = _blocks(body)
    bullets = [" ".join(b.split()) for b in found]
    problems = [f"the section holds text outside its change bullets: {' '.join(p.split())[:80]!r}"
                for p in paras if not NO_BREAKING.search(" ".join(p.split()))]
    for b in bullets:
        if "Instead:" not in b:
            problems.append(f"a change named with no replacement: {b[:90]!r}")
        elif len(re.findall(r"\w[\w-]*", b.partition("Instead:")[2])) < 3:
            problems.append(f"a change whose `Instead:` says nothing: {b[:90]!r}")
        named = [label for label, (names, _s, _i) in CHANGES.items() if re.search(names, b)]
        if not named:
            problems.append(f"a bullet no listed change names: {b[:90]!r}")
        elif len(named) > 1:
            problems.append(f"one bullet names {len(named)} listed changes ({', '.join(named)})")
    for label, (names, says, instead) in CHANGES.items():
        hits = [b for b in bullets if re.search(names, b)]
        if not hits:
            problems.append(f"the section never names {label}")
            continue
        if len(hits) > 1:
            problems.append(f"{label} is named by {len(hits)} bullets")
        hit = hits[0]
        problems += [f"{label} does not say {rx!r}" for rx in says
                     if not re.search(rx, hit.partition("Instead:")[0])]
        if not re.search(instead, hit.partition("Instead:")[2]):
            problems.append(f"{label} is named with no replacement beside it")
    return problems + breaking_problems(text, entries)


def configured(stated: dict, added: dict) -> dict:
    """Each key's default as the configuration states it: `reference-config.md`'s where it
    states one, else the value 6.4's shipped defaults add."""
    return {**added, **{k: v for k, v in stated.items() if v is not None}}


def default_problems(text: str, config: dict) -> list[str]:
    """AC2: each changed default the 'Changed defaults and new refusals' section states equal to
    the one `config` holds for its key."""
    body = section(text, r"^Changed defaults and new refusals$")
    if body is None:
        return ["no 'Changed defaults and new refusals' section"]
    flat = " ".join(body.split())
    return [f"the section says {key} defaults to {v!r}, where the configuration states "
            f"{config.get(key)!r}" for rx, key in CHANGED_DEFAULTS.items()
            for v in re.findall(rx, flat) if v != config.get(key)]


def _steps(text: str) -> list[tuple[str, list[str]]]:
    """(script, arguments) of each `python3 .../scripts/<script>` step in the upgrade section's
    code, in order."""
    old = section(text, r"^Upgrading from 6\.3$") or ""
    fence = re.search(r"^```bash\n(.*?)^```", old, re.M | re.S)
    out = []
    for line in (fence.group(1) if fence else "").splitlines():
        argv = shlex.split(line, comments=True)
        if argv[:1] == ["python3"] and argv[1:2] and "/scripts/" in argv[1]:
            out.append((argv[1].rsplit("/", 1)[1], argv[2:]))
    return out


def config_problems(old: str, stated: dict, added: dict) -> list[str]:
    """AC3: the upgrade section names each key AC3 lists with the default `reference-config.md`
    states for it, and each key 6.4's shipped defaults add with the value they ship."""
    said: dict[str, str] = {}
    for bullet in _blocks(old)[0]:
        m = re.match(r"- (.*?) default `([^`]*)`", " ".join(bullet.split()))
        if m:
            for key in re.findall(r"`([a-z_]+(?:\.[a-z_]+)+)`", m.group(1)):
                said[key] = m.group(2)
    problems = []
    for key, want in stated.items():
        if want is None:
            problems.append(f"reference-config.md states no default for {key}")
        elif key not in said:
            problems.append(f"the path does not name {key} with its default")
        elif said[key] != want:
            problems.append(f"the path gives {key} the default {said[key]!r}, and "
                            f"reference-config.md states {want!r}")
    for key, want in added.items():
        if key not in said:
            problems.append(f"the path does not name {key}, a key 6.4 adds")
        elif said[key] != want:
            problems.append(f"the path gives {key} the default {said[key]!r}, and 6.4 ships "
                            f"{want!r}")
    problems += [f"the path names {key}, a key 6.4 does not add" for key in said
                 if key not in stated and key not in added]
    return problems


def upgrade_problems(text: str) -> list[str]:
    """AC3: reinstall, `migrate` then `migrate --apply`, and what each reports for a 6.3 project
    as the notes say it. `config_problems` judges the keys the path names with their defaults."""
    old = section(text, r"^Upgrading from 6\.3$")
    if old is None:
        return ["no 'Upgrading from 6.3' section"]
    problems = []
    if not re.search(r"(?i)\breinstall\b", old) or "latest published release" not in old:
        problems.append("the path does not say to reinstall for the latest published release")
    fence = re.search(r"^```bash\n(.*?)^```", old, re.M | re.S)
    given = {ln.strip() for ln in shipped("docs/INSTALL.md").splitlines()}
    curls = [ln for ln in (fence.group(1) if fence else "").splitlines() if ln.startswith("curl ")]
    if not curls:
        problems.append("the path gives no reinstall command")
    problems += [f"the reinstall line is not one docs/INSTALL.md gives: {ln[:90]!r}"
                 for ln in curls if ln.strip() not in given]
    steps = _steps(text)
    dry = [i for i, (s, a) in enumerate(steps) if s == "migrate.py" and "--apply" not in a]
    wet = [i for i, (s, a) in enumerate(steps) if s == "migrate.py" and "--apply" in a]
    if not (dry and wet and dry[0] < wet[0]):
        problems.append("the steps are not `migrate` then `migrate --apply`")
    flat = " ".join(old.split())
    para = lambda lead: re.search(rf"\*\*`{lead}`\*\*,? (.*?)(?= \*\*`|$)", flat)  # noqa: E731
    dry_para, apply = (m.group(1) if m else "" for m in (para("migrate"), para("migrate --apply")))
    if not re.search(r"\bwrites nothing\b", dry_para):
        problems.append("the path does not say the dry run writes nothing")
    if f"`{STAMP}`" not in dry_para:
        problems.append("the path does not quote the version stamp the dry run reports")
    if not re.search(r"writes that stamp to `sdlc-studio/\.version` and changes nothing else",
                     apply):
        problems.append("the path does not say `migrate --apply` writes the stamp and nothing else")
    if re.search(r"(?i)\bremoves\b", apply):
        problems.append("the path says `migrate --apply` removes something")
    return problems


def step_problems(text: str, scripts: Path, project: Path) -> list[str]:
    """AC3: the notes' steps, run in their order on `project` (a 6.3 project), do what the notes
    say: the dry run writes nothing and reports exactly the version stamp the notes quote, and
    `--apply` writes `sdlc-studio/.version` alone, stamped 6.4.0."""
    problems = []
    flat = " ".join(text.split())
    for script, argv in _steps(text):
        before = _tree(project)
        extra = ("--format", "json") if script == "migrate.py" else ()
        proc = _cli(scripts, project, script, *argv, *extra)
        shown = " ".join([script, *argv])
        if proc.returncode != 0:
            problems.append(f"the step `{shown}` is refused by the shipped CLI "
                            f"(exit {proc.returncode}): {proc.stderr.strip()[:120]}")
            continue
        after = _tree(project)
        moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        if script != "migrate.py":
            problems.append(f"the step `{shown}` is not a `migrate` step")
            continue
        details = [d["detail"] for d in json.loads(proc.stdout)["deterministic"]]
        if "--apply" not in argv:
            if moved:
                problems.append(f"the dry run `{shown}` wrote {moved}")
            problems += [f"the dry run reports {d!r}, which the notes do not quote"
                         for d in details if f"`{d}`" not in flat]
            if not details:
                problems.append("the dry run reports no version stamp for a 6.3 project")
        else:
            if moved != ["sdlc-studio/.version"]:
                problems.append(f"`{shown}` changed {moved}, not `sdlc-studio/.version` alone")
            stamp = (project / "sdlc-studio" / ".version").read_text(encoding="utf-8")
            if 'skill_version: "6.4.0"' not in stamp:
                problems.append(f"`{shown}` did not stamp 6.4.0: {stamp!r}")
    return problems


def report_figures(rpt: str, reports: Path = REPORTS) -> tuple[set[str], str | None]:
    """(each forecast and actual value the report's committed JSON Estimates rows carry, written
    without `$` or thousands commas; why the report cannot be cited, or None)."""
    path = reports / f"{rpt}.json"
    if not path.is_file():
        return set(), f"has no committed JSON, {rpt}.json, beside its report"
    page = json.loads(path.read_text(encoding="utf-8"))
    sig = page.get("signature") or {}
    if sig.get("report") != rpt or not str(sig.get("principal") or "").strip():
        return set(), "is not signed"
    values = set()
    for sec in page.get("sections") or []:
        if sec.get("key") != "estimates":
            continue
        for row in sec.get("rows") or []:
            for cell in ("est_forecast", "est_actual"):
                values.add(str((row.get(cell) or {}).get("value")).replace("$", "").replace(",", ""))
    return values, None


def cost_problems(text: str, reports: Path = REPORTS) -> list[str]:
    """AC4: each sentence or row stating a cost figure names a signed report of a run that built
    6.4, and each figure is one the report named nearest before it (or, with none before, the
    first after it) carries in its committed JSON."""
    problems = []
    for unit in units(text):
        if COUNT_LINE.match(unit.strip()):
            continue
        figures = [(m.start(), next(g for g in m.groups() if g).replace(",", ""))
                   for m in COST.finditer(unit)]
        if not figures:
            continue
        named = [(m.start(), m.group()) for m in REPORT_ID.finditer(unit)]
        if not named:
            problems.append(f"a cost figure with no report named: {unit.strip()[:140]!r}")
            continue
        for at, value in figures:
            before = [rpt for pos, rpt in named if pos < at]
            rpt = before[-1] if before else named[0][1]
            if rpt not in RUNS_64:
                problems.append(f"{rpt}, named for {value}, is not the report of a run that "
                                f"built 6.4")
                continue
            carried, why = report_figures(rpt, reports)
            if why:
                problems.append(f"{rpt}, named for {value}, {why}")
            elif value not in carried:
                problems.append(f"{rpt} does not carry the figure {value}")
    return problems


def setUpModule() -> None:
    """A 6.3 project made by v6.3.0's own `init.py`, and the 6.4.0 skill: the v6.4.0 tag's tree,
    or before the tag this tree with its version read as 6.4.0, the cut's one change to it. A
    tree that is not a git clone holds neither tag: the checks that run the CLI are skipped
    there, naming why, and the checks of the text still run. A clone lacking the v6.3.0 tag
    fails rather than skips."""
    top = _run("git", "-C", str(REPO), "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != REPO.resolve():
        _FIX["skip"] = ("this tree is not a git clone, so it holds no v6.3.0 tree to make a "
                        "6.3 project from")
        return
    home = Path(tempfile.mkdtemp(prefix="us1170_"))
    _FIX["home"] = home
    skill63 = _extract("v6.3.0", home)
    if skill63 is None:
        raise AssertionError("this clone has no v6.3.0 tag to make a 6.3 project from: fetch tags")
    project = home / "p63"
    project.mkdir()
    proc = _cli(skill63 / "scripts", project, "init.py", "run")
    if proc.returncode != 0:
        raise AssertionError(f"v6.3.0's init.py failed: {proc.stdout}{proc.stderr}")
    skill64 = _extract("v6.4.0", home)
    if skill64 is None:
        skill64 = home / "v6.4.0-pending" / "sdlc-studio"
        shutil.copytree(REPO / SKILL_REL, skill64,
                        ignore=shutil.ignore_patterns("tests", "__pycache__", ".local"))
        md = skill64 / "SKILL.md"
        md.write_text(re.sub(r'(?m)^(  version: )"[^"]+"$', r'\1"6.4.0"',
                             md.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    _FIX.update(project=project, scripts=skill64 / "scripts")


def tearDownModule() -> None:
    if "home" in _FIX:
        shutil.rmtree(_FIX["home"], ignore_errors=True)


class ReleaseNotesTests(unittest.TestCase):

    def setUp(self) -> None:
        self.text = NOTES.read_text(encoding="utf-8")
        self.changelog = CHANGELOG.read_text(encoding="utf-8")

    def mutant(self, old: str, new: str) -> str:
        """The notes with `old`, which must occur exactly once, replaced."""
        self.assertEqual(1, self.text.count(old), f"mutant anchor not unique: {old[:60]!r}")
        return self.text.replace(old, new)

    def assertFlags(self, problems: list[str], expected: str) -> None:
        self.assertTrue([p for p in problems if expected in p],
                        f"no problem naming {expected!r}: {problems}")

    def needs_cli(self) -> None:
        """Skip the rest of a test where `setUpModule` found no git clone to build from, once a
        second signal agrees: a tree holding `.git` is a clone, and its CLI checks must run."""
        if "skip" in _FIX:
            self.assertFalse((REPO / ".git").exists(), "a git clone skipped the CLI checks")
            self.skipTest(str(_FIX["skip"]))

    def project(self) -> Path:
        """A fresh copy of the 6.3 project."""
        d = Path(tempfile.mkdtemp(prefix="us1170_p_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        shutil.copytree(_FIX["project"], d / "p")
        return d / "p"

    def test_the_notes_lead_with_what_changed_for_you(self) -> None:
        """AC1. MUTANTS: the 6.3.0 notes as they stand (headline '6.3.0 is the current release')
        and with the version changed (no 6.4 theme); a draft composed from the 6.4 fragments,
        whose ids sit outside any theme; a theme with its units cut, one short (US1164 dropped)
        or one over (US1014 added); a fifth theme, as a bullet or a paragraph; a theme listed
        twice; the `#unreleased` link left in place after the cut moved 6.4's entries under
        [6.4.0]."""
        lead = lambda text: lead_problems(text, self.changelog)  # noqa: E731
        copied = NOTES_63.read_text(encoding="utf-8")
        self.assertFlags(lead(copied), "the opening")
        self.assertFlags(lead(copied.replace("6.3.0", "6.4.0")), "lists no theme")
        fragments = "\n".join(body for _section, body in entries_64(self.changelog))
        self.assertTrue(UNIT_ID.search(fragments), "premise: the 6.4 entries name their units")
        composed = self.mutant("\n## Changed defaults", f"\n{fragments}\n\n## Changed defaults")
        self.assertFlags(lead(composed), "outside a theme")
        self.assertFlags(lead(self.mutant(
            " Delivered by US1146, US1147, US1148,\n  US1162, US1163 and US1164.", "")),
            "names no unit")
        self.assertFlags(lead(self.mutant("US1162, US1163 and US1164.", "US1162 and US1163.")),
                         "does not name US1164")
        self.assertFlags(lead(self.mutant("Delivered by US1011, US1012,",
                                          "Delivered by US1011, US1014, US1012,")),
                         "names US1014, not one of its units")
        fifth = "- **Installs are faster.** Install is quicker.\n"
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          f"{fifth}\n## Changed defaults")), "not one of the four")
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          f"\n{fifth[2:]}\n## Changed defaults")),
                         "outside its theme bullets")
        self.assertFlags(lead(self.mutant(
            "\n## Changed defaults",
            "- **The front door is written for a head of engineering.**\n\n## Changed defaults")),
            "2 times")
        self.assertEqual([], lead(self.text))

        before = re.sub(r"#640---\d{4}-\d{2}-\d{2}\)", "#unreleased)", self.text)
        self.assertIn("](../CHANGELOG.md#unreleased)", before)
        cut = "## [Unreleased]\n\n## [6.4.0] - 2026-11-17\n\n## [6.3.0] - 2026-11-08\n"
        precut = "## [Unreleased]\n\n## [6.3.0] - 2026-11-08\n"
        self.assertEqual([], lead_problems(before, precut))
        self.assertFlags(lead_problems(before, cut), "6.4.0 section")
        self.assertEqual([], lead_problems(before.replace("#unreleased)", "#640---2026-11-17)"),
                                           cut))

    def test_every_changed_behaviour_names_what_to_do(self) -> None:
        """AC2. MUTANTS: a section copied from the entries filed under Changed alone, which never
        names the replayed verdict file (filed under Added); the Copilot billing bullet with its
        'Instead:' cut; an added bullet whose 'Instead:' says nothing, one no listed change
        names, and a change given as a paragraph; a 'Breaking changes' heading no fragment records;
        the no-Breaking statement cut, and kept beside a Breaking entry; a bullet naming two
        listed changes; `tokens` read as `requests`, against `reference-config.md`. Each changed
        default is then judged against the configuration, whose keys 6.4 adds are read against
        v6.3.0's defaults: that subtest alone is skipped in a tree that is not a git clone."""
        entries = entries_64(self.changelog)
        self.assertGreater(len(entries), 1, "premise: the 6.4 entries are read")
        self.assertEqual([], [s for s, _b in entries if s in NOT_FILED])
        changed = ("## Changed defaults and new refusals\n\n"
                   + "\n".join(b for s, b in entries if s == "Changed") + "\n")
        self.assertFlags(changed_problems(changed, entries), "never names the replayed verdict")
        self.assertFlags(changed_problems(self.mutant(
            "\n  Instead: a plan still billed per premium request, such as a Copilot Pro or Pro+ "
            "annual plan,\n  sets `pricing.copilot_billing: requests` in "
            "`sdlc-studio/.config.yaml`.", ""), entries), "a change named with no replacement")
        tail = "\n## Upgrading from 6.3"
        for bullet, expected in (
                ("- **`foo` now refuses bar.** Instead: .\n", "`Instead:` says nothing"),
                ("- **`foo` now refuses bar.** Instead: pass `--bar` to keep it.\n",
                 "a bullet no listed change names"),
                ("\n`foo` now refuses bar. Instead: pass `--bar` to keep it.\n",
                 "outside its change bullets")):
            with self.subTest(added=bullet):
                self.assertFlags(changed_problems(self.mutant(tail, f"{bullet}{tail}"), entries),
                                 expected)
        self.assertFlags(changed_problems(self.mutant(
            "\n## Upgrading from 6.3", "\n## Breaking changes\n\nNone.\n\n## Upgrading from 6.3"),
            entries), "a heading claims a breaking change")
        self.assertFlags(changed_problems(self.mutant(
            "No 6.4 fragment is filed under Breaking, Removed or Security. ", ""), entries),
            "do not state that no 6.4 fragment")
        self.assertFlags(breaking_problems(self.text, [*entries, ("Breaking", "- Gone.\n")]),
                         "but 1 are")
        self.assertFlags(changed_problems(self.mutant(
            "- **The run record names its plan by digest.**",
            "- **The run record names its plan by digest, and `sprint.py resume` warns.**"),
            entries), "names 2 listed changes")
        self.assertEqual([], changed_problems(self.text, entries))

        stated = configured(stated_defaults(), {})
        self.assertFlags(default_problems(self.mutant(
            "`pricing.copilot_billing` defaults to `tokens`.**",
            "`pricing.copilot_billing` defaults to `requests`.**"), stated),
            "defaults to 'requests', where the configuration states 'tokens'")
        with self.subTest("each changed default, with the keys 6.4 adds read against v6.3.0"):
            self.assertEqual([], default_problems(self.text, configured(*defaults())))

    def test_the_63_upgrade_path_is_given(self) -> None:
        """AC3. MUTANTS: notes telling a 6.3 project a reinstall is all it needs (no `migrate`
        lines); the two `migrate` steps in the wrong order; a step naming a flag the shipped CLI
        refuses (`--write` for `--apply`); the reinstall URL misspelt (`instal.sh`); `--apply`
        said to remove a config key; the dry run's version stamp misquoted; a default
        `reference-config.md` contradicts (`requests` for `tokens`); `reference-config.md` with a
        default moved; a key 6.4 adds left out (`sprint.fresh_session`); a `migrate.py` that
        writes a file of its own. The keys 6.4 adds are read against v6.3.0's defaults, and the
        notes' own steps are run, in their order, on a project v6.3.0's `init.py` made: in a tree
        that is not a git clone those two are skipped, and every check of the text still runs."""
        old = section(self.text, r"^Upgrading from 6\.3$")
        steps = [ln for ln in old.splitlines() if "/migrate.py" in ln and ln.startswith("python3")]
        self.assertEqual(2, len(steps), steps)
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps) + "\n", "")),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps),
                                                      "\n".join(reversed(steps)))),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant(
            "and changes nothing else.", "and removes `review.policy`.")), "removes something")
        self.assertFlags(upgrade_problems(self.mutant("main/install.sh |", "main/instal.sh |")),
                         "not one docs/INSTALL.md gives")
        self.assertEqual([], upgrade_problems(self.text))

        # The defaults `reference-config.md` states, judged with no key 6.4 adds given.
        path = lambda text: section(text, r"^Upgrading from 6\.3$")  # noqa: E731
        self.assertFlags(config_problems(path(self.mutant(
            "- `pricing.copilot_billing`, default `tokens`:",
            "- `pricing.copilot_billing`, default `requests`:")), stated_defaults(), {}),
            "reference-config.md states 'tokens'")
        moved = re.sub(r"(?m)^(\| `personas\.memory\.inject_max` \| )5 ", r"\g<1>7 ",
                       shipped(f"{SKILL_REL}/reference-config.md"))
        self.assertFlags(config_problems(old, stated_defaults(moved), {}),
                         "reference-config.md states '7'")
        with self.subTest("the keys 6.4 adds, read against v6.3.0's defaults"):
            stated, added = defaults()
            self.assertTrue(added, "premise: 6.4's shipped defaults add keys")
            start = self.text.index("- `sprint.fresh_session`, default")
            dropped = self.text[:start] + self.text[self.text.index("\n## Known issues", start):]
            self.assertFlags(config_problems(path(dropped), stated, added),
                             "does not name sprint.fresh_session")
            self.assertEqual([], config_problems(old, stated, added))

        self.needs_cli()
        scripts = _FIX["scripts"]
        refused = self.mutant('migrate.py" --apply ', 'migrate.py" --write ')
        self.assertFlags(step_problems(refused, scripts, self.project()),
                         "refused by the shipped CLI")
        misquoted = self.mutant("(skill 6.3.0 -> 6.4.0)`", "(skill 6.2.0 -> 6.4.0)`")
        self.assertFlags(step_problems(misquoted, scripts, self.project()), "do not quote")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "migrate.py").write_text(_STRAY, encoding="utf-8")
            stray = step_problems(self.text, Path(d), self.project())
        self.assertFlags(stray, "the dry run `migrate.py` wrote")
        self.assertFlags(stray, "not `sdlc-studio/.version` alone")
        self.assertEqual([], step_problems(self.text, scripts, self.project()))

    def test_every_cost_figure_names_its_signed_report(self) -> None:
        """AC4. MUTANTS: a figure's sentence with its report cut; a dollar figure and a points
        figure each changed; a figure's report renamed to one that does not carry it (RPT0031)
        and to one that is not a 6.4 run's (RPT0027); the named report's committed JSON
        unsigned, and absent."""
        figures = [m for u in units(self.text) for m in COST.finditer(u)]
        self.assertGreaterEqual(len(figures), 6, "premise: the notes state cost figures")
        self.assertFlags(cost_problems(self.mutant(
            "RPT0028, the report of the first run that built 6.4, recorded",
            "The first run that built 6.4 recorded")), "a cost figure with no report named")
        self.assertFlags(cost_problems(self.mutant("$126.86", "$162.86")),
                         "RPT0032 does not carry the figure 162.86")
        self.assertFlags(cost_problems(self.mutant("over 50 delivered", "over 55 delivered")),
                         "RPT0033 does not carry the figure 55")
        self.assertFlags(cost_problems(self.mutant("RPT0033 forecast", "RPT0031 forecast")),
                         "RPT0031 does not carry the figure 169.11")
        self.assertFlags(cost_problems(self.mutant("RPT0033 forecast", "RPT0027 forecast")),
                         "is not the report of a run that built 6.4")
        # Two reports in one sentence: each figure is read against the report named before it.
        paired = "\nRPT0032 recorded $126.86 and RPT0033 recorded $108.81.\n"
        self.assertEqual([], cost_problems(self.mutant("\n## Known issues",
                                                       f"{paired}\n## Known issues")))
        swapped = "\nRPT0032 recorded $108.81 and RPT0033 recorded $126.86.\n"
        self.assertFlags(cost_problems(self.mutant("\n## Known issues",
                                                   f"{swapped}\n## Known issues")),
                         "RPT0032 does not carry the figure 108.81")
        with tempfile.TemporaryDirectory() as d:
            for n in sorted(RUNS_64):
                page = json.loads((REPORTS / f"{n}.json").read_text(encoding="utf-8"))
                if n == "RPT0032":
                    page["signature"] = None
                if n != "RPT0033":
                    (Path(d) / f"{n}.json").write_text(json.dumps(page), encoding="utf-8")
            fixture = cost_problems(self.text, Path(d))
        self.assertFlags(fixture, "RPT0032, named for 126.86, is not signed")
        self.assertFlags(fixture, "RPT0033, named for 108.81, has no committed JSON")
        self.assertEqual([], cost_problems(self.text))

    def test_a_fragment_written_after_the_cut_leaves_the_64_entries_read(self) -> None:
        """MUTANT: `entries_64` reading any pending fragment in preference to a cut
        `## [6.4.0]` section, so the first fragment of the next release (a Breaking BG9999 here)
        replaced 6.4's entries and AC2 refused the no-Breaking statement. Both the CHANGELOG and
        the fragment are fixtures; the real `changelog.d/` is never written."""
        cut = ("## [Unreleased]\n\n## [6.4.0] - 2026-11-17\n\n### Added\n\n- **New (US1170).**\n\n"
               "### Fixed\n\n- **Mended (BG1493).**\n\n## [6.3.0] - 2026-11-08\n\n### Breaking\n\n"
               "- **Old (US0978).**\n")
        late = "- **A break after the cut (BG9999).** Gone.\n"
        with tempfile.TemporaryDirectory() as d:
            frags = Path(d)
            (frags / "BG9999.md").write_text(f"<!-- section: Breaking -->\n{late}", encoding="utf-8")
            after = entries_64(cut, frags)
            self.assertEqual(["Added", "Fixed"], [s for s, _b in after])
            self.assertEqual(after, entries_64(cut, frags / "absent"))
            self.assertEqual([], breaking_problems(self.text, after))
            precut = "## [Unreleased]\n\n## [6.3.0] - 2026-11-08\n"
            self.assertEqual([("Breaking", late)], entries_64(precut, frags))


class EarlierReleaseTests(unittest.TestCase):
    """`shipped` reading a release before 6.4 skips only where both signals say the tree is not a
    git clone: it holds no `.git`, and git does not read it as a work tree."""

    @staticmethod
    def git(verify: int, top: str | None):
        """A git whose `rev-parse --verify` exits `verify` and whose `--show-toplevel` prints `top`,
        or exits 128 where `top` is None, as a git refusing a repository it does not trust does."""
        def run(*argv: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
            refused = "fatal: detected dubious ownership in repository"
            if "--verify" in argv:
                return subprocess.CompletedProcess(argv, verify, "",
                                                   "" if verify in (0, 1) else refused)
            if "--show-toplevel" in argv:
                return (subprocess.CompletedProcess(argv, 128, "", refused) if top is None
                        else subprocess.CompletedProcess(argv, 0, f"{top}\n", ""))
            raise AssertionError(f"an unexpected git call: {argv}")
        return run

    def outcome(self, root: Path, git) -> str:
        """What `shipped` does reading v6.3.0 in `root` under `git`: skip or fail, with why."""
        with mock.patch.dict(shipped.__globals__, REPO=root, _run=git):
            try:
                shipped("docs/notes.md", "v6.3.0")
            except unittest.SkipTest as e:
                return f"skip: {e}"
            except AssertionError as e:
                return f"fail: {e}"
        return "read"

    def test_only_a_tree_both_signals_call_no_clone_skips(self) -> None:
        """MUTANTS: the skip decided from a failing git alone, so a clone whose git exits 128
        skipped; the skip decided from a missing `.git` alone, so a tree git reads as its work
        tree skipped; a clone's git failure reported as a missing tag, without its exit status
        or message."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertRegex(self.outcome(root, self.git(128, None)), r"^skip: .*not a git clone")
            self.assertRegex(self.outcome(root, self.git(1, d)), r"^fail: .*fetch tags")
            (root / ".git").mkdir()
            for top in (None, d):
                with self.subTest(top=top):
                    self.assertRegex(self.outcome(root, self.git(128, top)),
                                     r"^fail: git failed in this clone.*exit 128.*dubious")
            self.assertRegex(self.outcome(root, self.git(1, d)),
                             r"^fail: .*no v6\.3\.0 tag.*fetch tags")


class WithoutAnEarlierReleaseTests(unittest.TestCase):
    """Where v6.3.0's defaults cannot be read, only the checks reading them skip: every check of
    the notes' text still runs, so a text defect fails there as it does in a clone."""

    def outcome(self, name: str, notes: str) -> unittest.TestResult:
        """`ReleaseNotesTests.<name>` run on `notes`, with v6.3.0's defaults unreadable."""
        def unreadable(*_args: object, **_kwargs: object) -> tuple[dict, dict]:
            raise unittest.SkipTest("no v6.3.0 tree to read")
        result = unittest.TestResult()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "release-notes-v6.4.0.md"
            path.write_text(notes, encoding="utf-8")
            with mock.patch.dict(shipped.__globals__, NOTES=path, defaults=unreadable):
                ReleaseNotesTests(name).run(result)
        return result

    def test_a_text_defect_fails_where_the_defaults_cannot_be_read(self) -> None:
        """MUTANTS: AC2 or AC3 reading v6.3.0's defaults before its text checks, so a tree that
        is not a git clone skipped the whole test and passed notes with the reinstall URL
        misspelt (`instal.sh`) or the Copilot bullet's `Instead:` renamed."""
        text = NOTES.read_text(encoding="utf-8")
        for name, old, new in (
                ("test_the_63_upgrade_path_is_given", "main/install.sh |", "main/instal.sh |"),
                ("test_every_changed_behaviour_names_what_to_do",
                 "\n  Instead: a plan still billed", "\n  Otherwise: a plan still billed")):
            with self.subTest(name):
                self.assertEqual(1, text.count(old), f"mutant anchor not unique: {old!r}")
                result = self.outcome(name, text.replace(old, new))
                self.assertEqual(1, len(result.failures) + len(result.errors),
                                 f"a text defect passed with the defaults unreadable: {result}")
        result = self.outcome("test_every_changed_behaviour_names_what_to_do", text)
        self.assertTrue(result.wasSuccessful(), result.failures + result.errors)
        self.assertEqual(["no v6.3.0 tree to read"], [why for _t, why in result.skipped])


if __name__ == "__main__":
    unittest.main()
