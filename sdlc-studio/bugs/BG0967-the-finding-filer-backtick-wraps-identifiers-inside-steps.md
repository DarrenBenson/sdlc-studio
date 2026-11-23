# BG0967: The finding filer backtick-wraps identifiers inside Steps to Reproduce, corrupting the shell commands a repro depends on

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_steps_commands.py, changelog.d/BG0967.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. Filing BG0949-BG0952 here: every `python3 -c "..."` repro had identifiers such as sdlc_md and critic.parse_verdict_block( wrapped in backticks, and each had to be re-fenced by hand.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:45Z

## Summary

The markdown-safety pass that wraps `snake_case` identifiers in backticks (BG0097) ran over the `steps` field, so `from lib import sdlc_md` inside a repro command came out as ``from lib import `sdlc_md` ``, which the shell reads as command substitution, and a copied repro no longer ran. A repro is the part of a bug a reviewer executes first.

Run twenty-three's three rounds (2d716316, 268b2933, 774af9c7, all on main) put a classifier in front of that pass that guesses which Steps lines are commands and fences them. Each round added a rule for quotes, heredocs, continuations or apostrophes, and each review found inputs the rules misread. At HEAD (3791e519) a command whose first word the classifier does not know (`export A_B=1`, `echo my_var`, `cat > x.md <<'EOF'`) is still safed as prose, with `A_B` and `my_var` back-ticked inside it; a sentence holding `&&` and a plural possessive pulls the prose line after it into its fence; and a list item's heredoc is filed under an added `<!-- -->` marker with three spaces added to its first line.

## Steps to Reproduce

1. In a scratch directory holding `src/thing.py`, write `f.json` as `{"summary": "s", "fix": "f", "steps": "export A_B=1\necho my_var"}`.
2. From the repository root, file it:

   ```text
   python3 .claude/skills/sdlc-studio/scripts/file_finding.py file --root <scratch> \
     --type bug --title t --severity low --points 1 --affects src/thing.py \
     --ac a --verify "pytest tests/test_x.py" --fields-file <scratch>/f.json
   ```

3. Read the filed bug's Steps to Reproduce. It holds `` export `A_B`=1 `` and `` echo `my_var` ``, and the shell runs each back-ticked name as a command.

## Proposed Fix

**The rule.** Write a Steps to Reproduce value as its author gave it. `_steps_safe` (which `artifact.py new` and `batch` reach through `_field_safe`, and a CR's landed Steps through `_land_unhomed`) adds no backtick, fence, marker or indentation and drops no prompt, so what the author fenced or back-ticked stays exactly as fenced or back-ticked and every other character is written as given. Two changes remain, and neither depends on what a line means: the metadata-line guard (`_META_DECL_RE`) still escapes the bold markers of a field declaration at a line start (after an optional `>`) or after a middle dot, inside an author's fence too, because `extract_field` reads one there (round one's injection finding); and a fence the author left open, as `sdlc_md.fence_step` reads it, is closed at the end of the value so it cannot swallow the sections below. The whole-body `normalise_fence_languages` pass still labels an author's bare fence opener `text`, as it did before this bug.

**Why this rule.** Fencing a Steps item only when it starts with a known command word is still a classifier, so it keeps the failure three rounds could not close: it misses every command whose first word is not on its list (`cat`, `export`, `echo`, `cd`, `VAR=1 cmd`), which then go to the prose pass and are corrupted silently, which is this bug; it fences prose that opens with a listed word; and it cuts a command that runs over a blank line or past its item, round two's finding. Writing the value as given reads nothing, so no input can be misread, and its code is shorter than any one of the rules it replaces. The filer stops classifying lines as commands, reading quotes, heredocs and backslash continuations, fencing commands and list-item bodies, dropping `$` prompts, moving lines to an item's content column, and back-ticking names and code-spanning URLs in the Steps. The cost is lint, not correctness: a name markdown reads as emphasis (`__init__`, two `_private` names on one line), a bare URL, or an unfenced command holding a `#` line is no longer rewritten, so markdownlint reports it at its line (MD050, MD037, MD034, MD022) and the author back-ticks the name or fences the command. A loud error at the line replaces a silent change to a command. As a bound on how often that falls to an author, 125 of the 1,714 filed bugs carry a code span opening or closing on an underscore in their Steps today. The Summary, Proposed Fix, Impact and Recommendation fields keep `_prose_safe` unchanged.

**The change.** Delete the classifier and what only it uses from `file_finding.py`: `_command_line`, `_command_lines`, `_shell_read`, `_HEREDOC_RE`, `_fence`, `_fenced_at`, `_ITEM_LEAD`, `_indent`, `_LIST_ITEM_RE`, `_PROMPT_RE`, `_unprompted`, `_FENCE_LABEL` and `_FENCE_LABEL_RE`. `_unlabelled`, and the `_content` in `artifact.py` that calls it, exist only to see past the `text` label the classifier wrote; both drop guards run before `normalise_fence_languages` labels anything, so they go back to comparing letters and digits. Keep `command_shaped`, which `pseudo_verify` uses, and leave `_md_safe` and BG0974's title, Evidence and link-destination safing alone. Rewrite `test_file_finding_steps_commands.py` around the criteria below, keeping its fence-close, author's-fence, inline-triple-backtick and only-the-steps tests and deleting the classes that pin the classifier. Rewrite `changelog.d/BG0967.md` to state the rule, what the filer stops doing, the two changes that remain (naming the escape inside an author's fence, BG1723's second finding) and the lint consequence; correct the comments on `_text`, `_rendered`, `_content` and `new_batch` in `artifact.py`; and make the `--steps` help in both CLIs say the value is written as given, so an author fences a command.

A dozen-line `_steps_safe` doing exactly this, in a throwaway copy at HEAD, passed every criterion below through all five creation paths, and `test_file_finding.py`, `test_artifact.py`, `test_filing_markdown_safe_title.py` and nine other filer-adjacent modules showed no failure the unpatched copy did not also show.

## Acceptance Criteria

- [ ] **AC1** Given a Steps value its author did not fence, each of: BG0967's one-line `python3 -c "import sys; from lib import sdlc_md; print(sdlc_md.__name__)"`; that program over lines inside double quotes; a `python3 - <<'EOF'` heredoc; a backslash-continued `python3 -c`; `export A_B=1` then `echo my_var`; a heredoc under a numbered item with an unindented body; and the three prose lines `Run git status && check the users' list`, `Then read Bob's note on my_x`, `and the my_y value`; when each is filed through `file_finding.py file`, then its Steps to Reproduce section is the value byte for byte, and each of the four `python3` commands, copied out of that section and run from the scripts folder, prints `lib.sdlc_md`. Fails on: HEAD, which wraps the `python3` commands in a `text` fence, back-ticks `A_B` and `my_var` inside their commands, pulls `Then read Bob's note on my_x` into the first line's fence, and files the item's heredoc under a `<!-- -->` marker with three spaces added to its first line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_steps_commands.py::StepsAsWrittenTests
- [ ] **AC2** Given BG0967's one-line command, the heredoc, and `export A_B=1` then `echo my_var`, when each is created through `artifact.py new`, `artifact.py new --template full`, `artifact.py batch` and `file_finding.py file --type cr` (whose Steps section the lander adds), then each Steps to Reproduce section is the value byte for byte. Fails on: HEAD, which fences the two `python3` commands and back-ticks `A_B` and `my_var` on all four paths.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_steps_commands.py::StepsAsWrittenEveryCreatorTests
- [ ] **AC3** Given an author's `markdown` fence holding a `Status` declaration line, a `Depends on` declaration line and `plain my_line`; a blockquoted `Waived` declaration followed by `yes && true`; a list item whose `printf` argument holds a middle dot and then a `Verified` declaration; and an author's backtick fence and tilde fence each left open; when each is filed through `file_finding.py file`, then every line is kept byte for byte save that each declaration's bold markers are escaped, `extract_field` reads Status as `Open` and reads no Waived, Verified or Depends on field, and an open fence is closed on its own marker after the value, so `verify_ac.py run --id <the bug> --dry-run` still parses the bug's criterion. Fails on: nothing at HEAD, which holds all of this; it fails on a fix that drops the guard or the fence close along with the classifier, which reopens round one's injection finding.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_steps_commands.py::StepsGuardTests
- [ ] **AC4** Given the prose `Read the __init__ module, my_file.md and https://example.com/a_b` as both the Steps and the Summary, when filed through `file_finding.py file`, then the Steps to Reproduce section is that text byte for byte while the Summary has `__init__`, `my_file.md` and the URL each in a code span: the filer adds no backtick to the Steps, and every other prose field keeps `_prose_safe`. Fails on: HEAD, which back-ticks all three in the Steps.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_steps_commands.py::StepsProseTests

## Triage

- More evidence, 2026-10-07: BG0987 and BG0988 were filed with a closing paren swallowed into a code span (`(`close_is_a_noop)``), the same safing reaching past the identifier.

- Reproduced at 8b844a80 in a scratch root: a steps value `python3 -c "import sys; from lib import sdlc_md; ..."` is filed with `sdlc_md` back-ticked and a broken span after it. Not a regression. BG0974 is the opposite failure in the same safing (the title and Evidence are left bare); fix the two together.

- Reproduced again at 3791e519, after run twenty-three's three rejected rounds (verdicts under `sdlc-studio/reviews/verdicts/BG0967/`; BG1723 carries round two and closes when this is Fixed). The rule above leaves `_md_safe` alone, so this no longer needs to ship with BG0974.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
| 2026-11-23 | Dani Okafor (engineering) | Groomed for run twenty-four: reproduced at 3791e519 (the classifier still back-ticks names inside commands it does not know and pulls prose into its fences); the classifier is replaced by one rule, write the Steps as given save the metadata guard and the close of an open fence, explained in the Proposed Fix; four executable criteria, three failing at HEAD and one guarding the two kept changes; Affects narrowed to the four files the fix touches; Points 2 to 3 |
