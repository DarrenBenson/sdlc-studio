"""README.md is a front door: short, and opening with three routes in, each to a page that exists.

The reader is a head of engineering deciding whether to evaluate SDLC Studio, try it or upgrade
a project already on it. The page is counted as `wc -w` counts it, over the whole file, and its
first section after the badges must offer the three routes in that order, each linking the
page that carries it: evaluate to the engineering-leaders page and the evidence page, try to
the install guide, upgrade to the existing-users page. Each check returns its problems and runs
on the live README and on planted failures beside it: a route missing, out of order, or linking
a file that does not exist.

The opening paragraph claims no more than the process does: each step is reviewed independently
of its author and a named person signs each run, and no sentence has a person approving each
step. One line points an agent at llms.txt and AGENTS.md, both files that exist.
"""
# test-census-subject: README.md
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"
MAX_WORDS = 1800

#: Each route, in the order the section must offer it -> the bold lead that opens its bullet,
#: and the pages it must link, relative to the repository root.
ROUTES = (
    ("evaluate", re.compile(r"^evaluate\b", re.I),
     ("docs/engineering-leaders.md", "docs/evidence.md")),
    ("try", re.compile(r"^try\b", re.I), ("docs/INSTALL.md",)),
    ("upgrade", re.compile(r"^upgrade\b", re.I), ("docs/existing-users.md",)),
)
_LINK = re.compile(r"\]\(([^)\s]+)\)")
_BULLET = re.compile(r"^- \*\*(.+?)\*\*(.*?)(?=^- |^\S|\Z)", re.M | re.S)


def words(text: str) -> int:
    """What `wc -w` counts: runs of non-whitespace bytes."""
    return len(text.encode("utf-8").split())


def first_section(text: str) -> tuple[str, str]:
    """(heading, body) of the first level-two section after the badges' closing `</div>`."""
    body = text.split("</div>", 1)[1] if "</div>" in text else text
    m = re.search(r"^## (.*?)\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return (m.group(1), m.group(2)) if m else ("", "")


def route_problems(text: str, root: Path = REPO) -> list[str]:
    """The three routes, in order, each linking the pages it must and only pages that exist."""
    heading, body = first_section(text)
    if not heading:
        return ["the README has no section after the badges"]
    bullets = [(lead.strip(), lead + rest) for lead, rest in _BULLET.findall(body)]
    problems, positions = [], []
    for name, opens, pages in ROUTES:
        hits = [i for i, (lead, _) in enumerate(bullets) if opens.search(lead)]
        if len(hits) != 1:
            problems.append(f"the first section ('{heading}') offers the {name} route "
                            f"{len(hits)} times, not once")
            continue
        positions.append(hits[0])
        links = [t.split("#", 1)[0] for t in _LINK.findall(bullets[hits[0]][1])
                 if not re.match(r"[a-z]+:", t)]
        for page in pages:
            if page not in links:
                problems.append(f"the {name} route does not link {page}")
        for link in links:
            if link and not (root / link).is_file():
                problems.append(f"the {name} route links {link}, which does not exist")
    if positions != sorted(positions):
        problems.append("the routes are not in the order evaluate, try, upgrade")
    return problems


#: The opening's sentence before it was corrected, kept as a planted failure.
OLD_OPENING = ("You describe what you want in plain language; the agent does the work, and a "
               "person you can name reviews and approves each step.")


def opening(text: str) -> str:
    """The first paragraph after the badges' closing `</div>`, its whitespace collapsed."""
    body = text.split("</div>", 1)[1] if "</div>" in text else text
    paragraph = next((p for p in re.split(r"\n\s*\n", body) if p.strip()), "")
    return " ".join(paragraph.split())


def opening_problems(text: str) -> list[str]:
    """What the opening claims against what the process does, judged sentence by sentence."""
    sentences = re.split(r"(?<=[.;])\s+", opening(text))
    problems = []
    if any(re.search(r"\bapprov\w*\b.*\beach step\b", s, re.I) for s in sentences):
        problems.append("the opening says a person approves each step")
    if not any(re.search(r"\bindependent", s, re.I) and re.search(r"\beach step\b", s, re.I)
               for s in sentences):
        problems.append("the opening does not say each step is reviewed independently")
    if not any(re.search(r"\bsigns?\b", s, re.I) and re.search(r"\beach run\b", s, re.I)
               and re.search(r"\b(?:person|principal)\b", s, re.I) for s in sentences):
        problems.append("the opening does not say a named person signs each run")
    return problems


def agent_pointer_problems(text: str, root: Path = REPO) -> list[str]:
    """One line links both llms.txt and AGENTS.md, and both files exist."""
    wanted = ("llms.txt", "AGENTS.md")
    lines = [ln for ln in text.splitlines()
             if all(page in [t.split("#", 1)[0].removeprefix("./") for t in _LINK.findall(ln)]
                    for page in wanted)]
    if not lines:
        return ["no line links both llms.txt and AGENTS.md"]
    return [f"the agent line links {page}, which does not exist"
            for page in wanted if not (root / page).is_file()]


#: CR0742's six harnesses, as the first screen must name them.
HARNESSES = ("Claude Code", "Codex", "Cursor", "Gemini CLI", "GitHub Copilot", "opencode")
#: The two pages the first screen must link, relative to the repository root.
FIRST_SCREEN_PAGES = ("docs/harnesses.md", "docs/enterprise.md")
#: The README's count by `wc -w` at 59b649d4, before CR0742 (US1318 AC4).
CR0742_WORDS = 1500
#: The install table's rows, in alphabetical order, each labelled as docs/harnesses.md names it.
TABLE_ROWS = ("Claude Code", "Codex", "Cursor", "Gemini CLI", "GitHub Copilot", "opencode")
#: The install table's header cells this page reads, by role.
COLUMNS = {"harness": "Harness", "target": "`--target`", "global": "Global",
           "local": "Project-local", "invoke": "Invoke as", "verify": "Verify with"}


def first_screen(text: str) -> str:
    """The text before the second `##` heading: the opening and the first section."""
    heads = [m.start() for m in re.finditer(r"^## ", text, re.M)]
    return text[:heads[1]] if len(heads) > 1 else text


def first_screen_problems(text: str, root: Path = REPO) -> list[str]:
    """The opening leads with harness-agnostic and human in the lead; the first screen names
    the six harnesses and links the two pages, both of which exist."""
    screen = first_screen(text)
    flat, lead = " ".join(screen.split()), opening(text).lower()
    problems = [f"the opening does not say {phrase}"
                for phrase in ("harness-agnostic", "human in the lead") if phrase not in lead]
    problems += [f"the first screen does not name {name}" for name in HARNESSES
                 if not re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", flat)]
    links = [t.split("#", 1)[0] for t in _LINK.findall(screen) if not re.match(r"[a-z]+:", t)]
    for page in FIRST_SCREEN_PAGES:
        if page not in links:
            problems.append(f"the first screen does not link {page}")
        elif not (root / page).is_file():
            problems.append(f"the first screen links {page}, which does not exist")
    return problems


def sections(text: str) -> list[tuple[str, int, int]]:
    """(heading, start, end) of each level-two section, fenced blocks included in their span."""
    heads = list(re.finditer(r"^## (.*?)\s*$", text, re.M))
    return [(m.group(1), m.start(), heads[i + 1].start() if i + 1 < len(heads) else len(text))
            for i, m in enumerate(heads)]


def md_tables(text: str) -> list[tuple[int, list[list[str]]]]:
    """Each table outside fenced blocks: (offset of its first row, its rows of stripped cells),
    the separator row dropped."""
    out: list[tuple[int, list[list[str]]]] = []
    rows: list[list[str]] = []
    start = pos = 0
    fenced = False
    for line in text.splitlines(keepends=True):
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
        if not fenced and s.startswith("|"):
            start = start if rows else pos
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                rows.append(cells)
        elif rows:
            out.append((start, rows))
            rows = []
        pos += len(line)
    if rows:
        out.append((start, rows))
    return out


def page_row(name: str, root: Path = REPO) -> str:
    """The docs/harnesses.md matrix row for harness `name`, its cells joined; '' if none."""
    page = root / "docs" / "harnesses.md"
    text = page.read_text(encoding="utf-8") if page.is_file() else ""
    return next((" | ".join(r) for _, rows in md_tables(text) for r in rows if r[0] == name), "")


def harness_table_problems(text: str, root: Path = REPO) -> list[str]:
    """One harness table, in the quick start, its rows the six in alphabetical order, each with
    the install locations and target the harness page gives it, an invocation, and a
    verification command docs/INSTALL.md or the harness page backs, or an `ls` of the skill in
    the row's own global folder. The quick start names GitHub Copilot and its first command
    names a `--target`, so no harness is installed by default for everyone."""
    labels = set(TABLE_ROWS) | set(HARNESSES)
    found = [(at, rows) for at, rows in md_tables(text) if any(r[0] in labels for r in rows[1:])]
    if len(found) != 1:
        return [f"the README has {len(found)} harness tables, not one"]
    at, rows = found[0]
    quick = next(((s, e) for h, s, e in sections(text) if h == "Quick start"), (0, 0))
    problems = [] if quick[0] <= at < quick[1] else ["the harness table is not in the quick start"]
    body = text[quick[0]:quick[1]]
    prose = " ".join(ln for ln in body.splitlines() if not ln.startswith("|"))
    if "GitHub Copilot" not in " ".join(prose.split()):
        problems.append("the quick start does not name GitHub Copilot")
    first = re.search(r"```\w*\n(.*?)```", body, re.S)
    if not first or "--target" not in first.group(1):
        problems.append("the quick start's first command names no --target")
    header = rows[0]
    missing = [c for c in COLUMNS.values() if c not in header]
    if missing:
        return problems + [f"the harness table has no {c} column" for c in missing]
    col = {role: header.index(name) for role, name in COLUMNS.items()}
    names = [r[col["harness"]] for r in rows[1:]]
    if sorted(names) != sorted(TABLE_ROWS):
        problems.append(f"the harness table's rows are {names}, not the six")
    if names != sorted(names, key=str.casefold):
        problems.append("the harness table's rows are not in alphabetical order")
    backing = "".join((root / p).read_text(encoding="utf-8") for p in
                      ("docs/INSTALL.md", "docs/harnesses.md") if (root / p).is_file())
    for row in rows[1:]:
        cell = dict(zip(col, (row[i] if i < len(row) else "" for i in col.values())))
        name, matrix = cell["harness"], page_row(cell["harness"], root)
        paths = {k: re.findall(r"`([^`]+)`", cell[k]) for k in ("global", "local", "target")}
        for key, found_paths in paths.items():
            token = (f"`--target {found_paths[0]}`" if key == "target" and found_paths
                     else f"`{found_paths[0]}`" if found_paths else None)
            if not token or token not in matrix:
                problems.append(f"the {name} row's {COLUMNS[key]} cell is not the harness page's")
        if not cell["invoke"].strip(" -"):
            problems.append(f"the {name} row gives no invocation")
        commands = re.findall(r"`([^`]+)`", cell["verify"])
        if not commands:
            problems.append(f"the {name} row gives no verification command")
        own = f"ls {paths['global'][0]}/sdlc-studio/SKILL.md" if paths["global"] else None
        for cmd in commands:
            if f"`{cmd}`" not in backing and cmd != own:
                problems.append(f"the {name} row's verification `{cmd}` is backed by neither "
                                "docs/INSTALL.md nor docs/harnesses.md")
    return problems


def acknowledgements_problems(text: str) -> list[str]:
    """The sponsorship line sits under Acknowledgements, which says SDLC Studio does not require
    Anthropic products, and nothing on the page says "Claude Code skill"."""
    problems = []
    if re.search(r"(?i)claude\s+code\s+skill", text):
        problems.append('the README says "Claude Code skill"')
    acks = [(s, e) for h, s, e in sections(text) if h == "Acknowledgements"]
    if len(acks) != 1:
        return problems + [f"the README has {len(acks)} Acknowledgements sections, not one"]
    start, end = acks[0]
    hits = [m.start() for m in re.finditer(r"Claude\s+for\s+Open\s+Source", text)]
    if not hits:
        problems.append("the README carries no sponsorship line")
    if any(not start <= h < end for h in hits):
        problems.append("the sponsorship line sits outside Acknowledgements")
    if not re.search(r"SDLC Studio does not require Anthropic products", " ".join(
            text[start:end].split())):
        problems.append("Acknowledgements does not say SDLC Studio does not require Anthropic "
                        "products")
    return problems


class ReadmeFrontDoorTests(unittest.TestCase):
    def test_the_readme_is_at_most_1800_words(self) -> None:
        """AC1: `wc -w README.md` is at most 1,800; a page one word over is refused."""
        text = README.read_text(encoding="utf-8")
        self.assertLessEqual(words(text), MAX_WORDS,
                             f"README.md is {words(text)} words, over {MAX_WORDS}")
        self.assertEqual(words("one  two\tthree\nfour - `five`"), 6)
        self.assertGreater(words(text + " extra" * (MAX_WORDS - words(text) + 1)), MAX_WORDS)

    def test_the_first_section_offers_three_routes_each_to_a_page_that_exists(self) -> None:
        """AC2: evaluate, try, upgrade, in that order, each to the pages that carry it. A route
        cut, two routes swapped, a route's page unlinked or a link to a missing file is refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(route_problems(text), [])
        heading, body = first_section(text)
        bullets = {name: next(m.group(0) for m in _BULLET.finditer(body)
                              if opens.search(m.group(1).strip()))
                   for name, opens, _ in ROUTES}
        cut = text.replace(bullets["try"], "", 1)
        self.assertIn("the first section ('%s') offers the try route 0 times, not once" % heading,
                      route_problems(cut))
        swapped = text.replace(bullets["evaluate"], "\0", 1).replace(
            bullets["upgrade"], bullets["evaluate"], 1).replace("\0", bullets["upgrade"], 1)
        self.assertIn("the routes are not in the order evaluate, try, upgrade",
                      route_problems(swapped))
        unlinked = text.replace("(docs/evidence.md)", "(docs/evidence-missing.md)", 1)
        self.assertIn("the evaluate route does not link docs/evidence.md",
                      route_problems(unlinked))
        self.assertIn("the evaluate route links docs/evidence-missing.md, which does not exist",
                      route_problems(unlinked))
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("the try route links docs/INSTALL.md, which does not exist",
                          route_problems(text, Path(d)))
        twice = text.replace(bullets["try"], bullets["try"] + bullets["try"], 1)
        self.assertIn("the first section ('%s') offers the try route 2 times, not once" % heading,
                      route_problems(twice))
        moved = text.replace(f"## {heading}", "## Later", 1).replace(
            "</div>\n", "</div>\n\n## Something else first\n\nText.\n", 1)
        self.assertTrue(any("offers the evaluate route 0 times" in p
                            for p in route_problems(moved)))
        inside = text.replace("</div>\n", f"## {heading}\n{body}\n</div>\n\n## Other\n\nText.\n", 1)
        self.assertTrue(any("offers the evaluate route 0 times" in p
                            for p in route_problems(inside)),
                        "routes inside the badges block counted as the first section after it")

    def test_the_opening_claims_independent_review_and_one_signature_per_run(self) -> None:
        """BG1487 AC1: the opening says each step is reviewed independently and a named person
        signs each run, and never that a person approves each step. The old sentence, the
        signature clause cut, and the review clause cut are each refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(opening_problems(text), [], opening(text))
        para = opening(text)
        old = text.replace("</div>\n", f"</div>\n\n{OLD_OPENING}\n", 1)
        self.assertEqual(opening(old), OLD_OPENING)
        self.assertEqual(opening_problems(old),
                         ["the opening says a person approves each step",
                          "the opening does not say each step is reviewed independently",
                          "the opening does not say a named person signs each run"])
        unsigned = text.replace("</div>\n", "</div>\n\n" + re.sub(
            r"\bsigns\b", "reads", para) + "\n", 1)
        self.assertEqual(opening_problems(unsigned),
                         ["the opening does not say a named person signs each run"])
        for wrong in (para.replace("signs each run", "signs each step", 1),
                      para.replace("a person you name signs", "the tool signs", 1)):
            self.assertNotEqual(wrong, para)
            planted = text.replace("</div>\n", f"</div>\n\n{wrong}\n", 1)
            self.assertEqual(opening_problems(planted),
                             ["the opening does not say a named person signs each run"], wrong)
        unreviewed = text.replace("</div>\n", "</div>\n\n" + re.sub(
            r"\bindependent\w*", "", para) + "\n", 1)
        self.assertEqual(opening_problems(unreviewed),
                         ["the opening does not say each step is reviewed independently"])
        approved = text.replace("</div>\n", "</div>\n\n" + para.replace(
            "each run", "each run and approves each step", 1) + "\n", 1)
        self.assertIn("the opening says a person approves each step", opening_problems(approved))

    def test_one_line_points_agents_at_llms_txt_and_agents_md(self) -> None:
        """BG1487 AC2: one line links llms.txt and AGENTS.md, both of which exist. The line cut
        (AGENTS.md still linked elsewhere), one of its links changed, the two split across lines,
        or a missing file is refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(agent_pointer_problems(text), [])
        line = next(ln for ln in text.splitlines() if "](llms.txt)" in ln and "](AGENTS.md)" in ln)
        cut = text.replace(line, "", 1)
        self.assertIn("](AGENTS.md)", cut)
        self.assertEqual(agent_pointer_problems(cut),
                         ["no line links both llms.txt and AGENTS.md"])
        only_one = text.replace(line, line.replace("](llms.txt)", "](docs/INSTALL.md)"), 1)
        self.assertEqual(agent_pointer_problems(only_one),
                         ["no line links both llms.txt and AGENTS.md"])
        split = text.replace(line, line.replace("[AGENTS.md]", "\n[AGENTS.md]", 1), 1)
        self.assertEqual(agent_pointer_problems(split),
                         ["no line links both llms.txt and AGENTS.md"])
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "AGENTS.md").write_text("x", encoding="utf-8")
            self.assertEqual(agent_pointer_problems(text, Path(d)),
                             ["the agent line links llms.txt, which does not exist"])

    def test_the_first_screen_names_six_harnesses_and_links_the_two_pages(self) -> None:
        """US1318 AC1: the opening leads with harness-agnostic and human in the lead, and the text
        before the second `##` heading names the six harnesses and links docs/harnesses.md and
        docs/enterprise.md. Each harness cut from the screen (left below it), each link cut, a
        lead phrase cut, and a root without the pages are each refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(first_screen_problems(text), [])
        screen = first_screen(text)
        self.assertTrue(screen.rstrip().endswith(".") and "## Three ways in" in screen)
        for name in HARNESSES:
            spaced = re.escape(name).replace(r"\ ", r"\s+")
            planted = re.sub(rf"(?<![\w-]){spaced}(?![\w-])", "a tool", screen)
            self.assertNotEqual(planted, screen, name)
            self.assertEqual(first_screen_problems(planted + text[len(screen):]),
                             [f"the first screen does not name {name}"])
        below = text.replace(screen, screen.replace("GitHub Copilot", "a tool"), 1)
        self.assertIn("GitHub Copilot", below)
        self.assertEqual(first_screen_problems(below),
                         ["the first screen does not name GitHub Copilot"])
        for page in FIRST_SCREEN_PAGES:
            cut = screen.replace(f"]({page})", "](docs/INSTALL.md)")
            self.assertNotEqual(cut, screen, page)
            self.assertEqual(first_screen_problems(cut + text[len(screen):]),
                             [f"the first screen does not link {page}"])
        for phrase in ("harness-agnostic", "human in the lead"):
            cut = re.sub(re.escape(phrase).replace(r"\ ", r"\s+"), "x", screen, flags=re.I)
            self.assertEqual(first_screen_problems(cut + text[len(screen):]),
                             [f"the opening does not say {phrase}"])
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(first_screen_problems(text, Path(d)),
                             [f"the first screen links {p}, which does not exist"
                              for p in FIRST_SCREEN_PAGES])

    def test_the_copilot_row_is_labelled_github_copilot(self) -> None:
        """The install table's Copilot row reads `GitHub Copilot`, the name docs/harnesses.md
        uses, and no row is labelled with the short name."""
        text = README.read_text(encoding="utf-8")
        (_, rows), = [t for t in md_tables(text) if t[1][0][0] == "Harness"]
        labels = [r[0] for r in rows[1:]]
        row, = [r for r in rows[1:] if "`copilot`" in r[1]]
        self.assertEqual("GitHub Copilot", row[0])
        self.assertNotIn("Copilot", labels)

    def test_the_harness_table_is_alphabetical_with_a_verification_command(self) -> None:
        """US1318 AC2: one harness table, in the quick start, its six rows alphabetical, each
        with the harness page's install locations, an invocation and a backed verification
        command. A second table, two rows swapped, a row cut, a verification cell emptied, an
        unbacked command, a path the harness page does not give, and a first command that
        installs the default for everyone are each refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(harness_table_problems(text), [])
        (at, rows), = [t for t in md_tables(text) if t[1][0][0] == "Harness"]
        lines = text[at:].splitlines()[:len(rows) + 1]
        table = "\n".join(lines)
        row = {ln.split("|")[1].strip(): ln for ln in lines[2:]}
        self.assertEqual(list(row), list(TABLE_ROWS))
        twice = text.replace("## FAQ", f"## FAQ\n\n{table}\n", 1)
        self.assertEqual(harness_table_problems(twice), ["the README has 2 harness tables, not one"])
        swapped = text.replace(row["Codex"], "\0", 1).replace(
            row["GitHub Copilot"], row["Codex"], 1).replace("\0", row["GitHub Copilot"], 1)
        self.assertEqual(harness_table_problems(swapped),
                         ["the harness table's rows are not in alphabetical order"])
        cut = text.replace(row["GitHub Copilot"] + "\n", "", 1)
        self.assertEqual(len(harness_table_problems(cut)), 1)
        self.assertIn("not the six", harness_table_problems(cut)[0])
        for name in TABLE_ROWS:
            cells = row[name].split("|")
            cells[-2] = " - "
            blank = text.replace(row[name], "|".join(cells), 1)
            self.assertEqual(harness_table_problems(blank),
                             [f"the {name} row gives no verification command"], name)
        unbacked = text.replace("`copilot skill list`", "`copilot skills ls`", 1)
        self.assertEqual(harness_table_problems(unbacked),
                         ["the GitHub Copilot row's verification `copilot skills ls` is backed by "
                          "neither docs/INSTALL.md nor docs/harnesses.md"])
        moved = text.replace(row["Gemini CLI"], row["Gemini CLI"].replace(
            "`~/.gemini/skills`", "`~/.gemini/skill`", 1), 1)
        self.assertEqual(harness_table_problems(moved),
                         ["the Gemini CLI row's Global cell is not the harness page's"])
        elsewhere = text.replace(row["Cursor"], row["Cursor"].replace(
            "`ls ~/.agents/skills/", "`ls ~/.cursor/skills/", 1), 1)
        self.assertEqual(harness_table_problems(elsewhere),
                         ["the Cursor row's verification `ls ~/.cursor/skills/sdlc-studio/SKILL.md`"
                          " is backed by neither docs/INSTALL.md nor docs/harnesses.md"])
        cells = row["Codex"].split("|")
        cells[-3] = " "
        silent = text.replace(row["Codex"], "|".join(cells), 1)
        self.assertEqual(harness_table_problems(silent), ["the Codex row gives no invocation"])
        body = next(text[s:e] for h, s, e in sections(text) if h == "Quick start")
        prose = "\n".join(ln if ln.startswith("|") else ln.replace("GitHub Copilot", "Copilot")
                          for ln in body.splitlines())
        unnamed = text.replace(body, prose + "\n", 1)
        self.assertEqual(harness_table_problems(unnamed),
                         ["the quick start does not name GitHub Copilot"])
        later = text.replace(table + "\n", "", 1).replace("## FAQ", f"## FAQ\n\n{table}\n", 1)
        self.assertEqual(harness_table_problems(later),
                         ["the harness table is not in the quick start"])
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("the GitHub Copilot row's Global cell is not the harness page's",
                          harness_table_problems(text, Path(d)))
        default = text.replace(" | bash -s -- --target auto\n", " | bash\n", 1)
        self.assertNotEqual(default, text)
        self.assertEqual(harness_table_problems(default),
                         ["the quick start's first command names no --target"])

    def test_acknowledgements_carries_the_sponsorship_and_no_anthropic_requirement(self) -> None:
        """US1318 AC3: the sponsorship line sits under Acknowledgements, which says SDLC Studio
        does not require Anthropic products, and the page never says "Claude Code skill". The
        line moved to its own section, the statement cut, and the phrase planted across a line
        break are each refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(acknowledgements_problems(text), [])
        line = re.search(r"[^.\n]*Claude\s+for\s+Open\s+Source[^.]*\.", text).group(0)
        moved = text.replace(line, "", 1).replace("## Licence", f"## Sponsor\n\n{line}\n\n## Licence")
        self.assertEqual(acknowledgements_problems(moved),
                         ["the sponsorship line sits outside Acknowledgements"])
        unsaid = re.sub(r"does\s+not\s+require\s+Anthropic\s+products", "uses Anthropic products",
                        text)
        self.assertNotEqual(unsaid, text)
        self.assertEqual(acknowledgements_problems(unsaid),
                         ["Acknowledgements does not say SDLC Studio does not require Anthropic "
                          "products"])
        statement = re.search(r"SDLC\s+Studio\s+does\s+not\s+require[^.]*\.", text).group(0)
        away = text.replace(statement, "", 1).replace("</div>\n", f"</div>\n\n{statement}\n", 1)
        self.assertEqual(acknowledgements_problems(away),
                         ["Acknowledgements does not say SDLC Studio does not require Anthropic "
                          "products"])
        self.assertEqual(acknowledgements_problems(text.replace(line, "", 1)),
                         ["the README carries no sponsorship line"])
        planted = text.replace("</div>\n", "</div>\n\nA Claude Code\nskill.\n", 1)
        self.assertEqual(acknowledgements_problems(planted),
                         ['the README says "Claude Code skill"'])
        renamed = text.replace("## Acknowledgements", "## Thanks", 1)
        self.assertEqual(acknowledgements_problems(renamed),
                         ["the README has 0 Acknowledgements sections, not one"])

    def test_the_readme_is_no_longer_than_before_cr0742(self) -> None:
        """US1318 AC4: `wc -w README.md` is at most 1,500, its count at 59b649d4; one word over
        is refused."""
        text = README.read_text(encoding="utf-8")
        self.assertLessEqual(words(text), CR0742_WORDS,
                             f"README.md is {words(text)} words, over {CR0742_WORDS}")
        self.assertGreater(words(text + " extra" * (CR0742_WORDS - words(text) + 1)),
                           CR0742_WORDS)
        self.assertEqual(words(text + " extra" * (CR0742_WORDS - words(text))), CR0742_WORDS)


if __name__ == "__main__":
    unittest.main()
