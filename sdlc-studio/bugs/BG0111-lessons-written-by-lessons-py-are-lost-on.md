# BG0111: Lessons written by lessons.py are lost on the next skill update, and project-specific lessons are dumped into the shared cross-project registry

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio new
> **Raised-by:** Darren; human; v3
> **Triaged-by:** Priya Nair; persona; v3

## Summary

Two defects in the lessons mechanism, found while using it heavily on a consuming project
(`sdlc-studio-lens`) across five sprints.

### Defect 1 (data loss): `--global` writes to the INSTALL, which is not version-controlled

`scripts/lessons.py` resolves the skill tier as:

```python
SKILL_LESSONS_DIR = Path(__file__).resolve().parent.parent / "lessons"
```

i.e. **relative to the running script**. In real use that script is the *installed* copy at
`~/.claude/skills/sdlc-studio/`, not the source checkout. So every `lessons add --global`
writes into the install.

**`~/.claude` is not a git repository.** Neither is `~/.claude/skills/sdlc-studio`. Measured
on this machine today:

| Copy | Path | Lessons | Tracked |
| --- | --- | --- | --- |
| Source | `~/code/DarrenBenson/sdlc-studio/.claude/skills/sdlc-studio/lessons/` | **12** | yes |
| Install | `~/.claude/skills/sdlc-studio/lessons/` | **21** | **no** |

Nine lessons (LL0013-LL0021) exist **only in the untracked install**. The next
`skill-update` - which overwrites the install from the release - **destroys them**. There is
no path from install back to source, and nothing warns the author.

The skill's own `lessons/_index.md` says: *"This folder ships with the skill, so the seed set
is release-curatable; Claudes add to it as they work, and additions are blessed into the next
skill release."* **There is no mechanism that performs that blessing.** The doc describes an
intention; the code writes into a directory that gets replaced.

This is `LL0008` ("a deterministic tool must fail loud, never report success it did not
achieve") turned on the skill itself: `lessons.py` prints *"Wrote LL0021 ... and appended the
index row"*, which is true, and useless, because the file is on a road to deletion.

### Defect 2 (modelling): project-specific lessons land in a cross-project registry

A lesson learned on project A is not automatically true for project B. The two tiers exist
precisely to separate them:

- **Project tier:** `sdlc-studio/.local/lessons.md` in the consuming project.
- **Skill tier:** the shared `lessons/` registry.

But **`--global` is what every workflow reaches for**, because the retro template says
*"promote the durable, cross-project ones: lessons add --global"* and that is the only tier
anybody sees named. On the consuming project used here, the project tier was **never written
to once** across five sprints; nine lessons went straight to the shared registry.

Some genuinely generalise (LL0017: *"a function that only ever appears inside `patch()` is
untested"*). Others are arguable. Nothing forces that judgement, and nothing makes the cheap,
correct default - **project tier, promote later** - the easy path.

## Steps to Reproduce

```bash
python3 ~/.claude/skills/sdlc-studio/scripts/lessons.py add --global --title "x" --body "y"
# -> Wrote LL00NN to ~/.claude/skills/sdlc-studio/lessons/...

cd ~/.claude/skills/sdlc-studio && git status
# fatal: not a git repository

# and the source repo never sees it:
ls ~/code/DarrenBenson/sdlc-studio/.claude/skills/sdlc-studio/lessons/LL00NN* 
# no such file
```

## Proposed Fix

1. **Make `--global` refuse to write into an untracked install.** If `SKILL_LESSONS_DIR` is
   not inside a git work tree, **fail loud** with the reason and the remedy, rather than
   writing a file that a future update will delete. A tool must not report a success it did
   not achieve.
2. **Give it somewhere real to write.** Either resolve the skill source from config
   (`skill_source_repo`), or emit the lesson to the project tier and record a
   `promote-to-skill` intent that `skill-update` can pick up. The install must stop being the
   destination of authored content.
3. **Make the project tier the default in the prompts, not just in the code.** The retro
   template should say *"record it as a project lesson; promote with `--global` only once it
   clearly generalises beyond this repo"* - which is what `lessons/_index.md` already asks for
   and what nobody does.
4. **Recover the nine orphaned lessons** (LL0013-LL0021) into the source repo before the next
   skill update destroys them.

## Acceptance Criteria

- [ ] `lessons add --global` into an untracked skill install FAILS LOUD; it never silently writes a file that the next update will delete
- [ ] A `--global` lesson lands somewhere version-controlled, and `git status` in the source repo shows it
- [ ] The project tier is the documented default; `--global` is the deliberate promotion
- [ ] LL0013-LL0021 are recovered into the source repo
- [ ] Mutation-checked: reverting the fail-loud guard turns a test red

## Lessons

- **A tool that authors content into a directory it does not own is writing to /dev/null with
  extra steps.** The install is a *deployment artefact*; it is replaced, not curated. Anything
  authored must land in a source of truth.
- **"Additions are blessed into the next release" is a workflow, and it had no implementation.**
  A documented intention with no mechanism is a lie with a good conscience.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Darren | Found on sdlc-studio-lens: nine lessons written across five sprints exist only in the untracked install and would be destroyed by the next skill update. |
