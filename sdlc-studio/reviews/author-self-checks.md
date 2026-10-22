# Author Self-Checks

> Append-only. The author's own claim inventory and mutation pass per unit, recorded by
> `critic.py self-check record` before a reviewer is briefed. The digest is over the
> content of the unit's Affects files when the row was written, so a row whose digest no
> longer matches is a self-check of an earlier diff.

| Unit | Author | Date | Claims | Mutants | Digest |
| --- | --- | --- | --- | --- | --- |
| US1088 | builder-US1088 (agent), orchestrator for the --root fix | 2026-10-22 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | eb8be939da1f2dbb |
| US1089 | builder-US1089 | 2026-10-22 | TRUE 22, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 9bd147390c4ef20f |
| US1088 | builder-US1088, re-recorded on main: US1089's critic.py commit moved the digest | 2026-10-22 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | 76639d3ebb87efb1 |
| US1089 | builder-US1089, re-recorded on main: US1090's AGENTS.md commit moved the digest | 2026-10-22 | TRUE 22, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 35a254c6a60ff071 |
| US1090 | builder-US1090 | 2026-10-22 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 16, survived 2 | 3947227e944c536c |
| US1088 | builder-US1088, repair round 1 (ad17ce6a) | 2026-10-22 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 22, survived 0 | 382a9df3e67d3dc6 |
| BG1111 | builder-BG1111 | 2026-10-22 | TRUE 25, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 4 | 0fd445b5b4167d9a |
| BG1000 | orchestrator (BG1000's author), evidence by a delegated self-check agent; repairs 0d32fb0d and 12325e02 | 2026-10-22 | TRUE 41, FALSE 0, UNVERIFIABLE 5 | killed 10, survived 6 | 9a51e34e38bf6851 |
| US1087 | orchestrator (US1087's author), evidence by a delegated self-check agent; repair 0f7acbbd | 2026-10-22 | TRUE 34, FALSE 0, UNVERIFIABLE 2 | killed 12, survived 0 | d5ed0acb0d037d85 |
| BG1000 | orchestrator (BG1000's author); repair round 1 a5550c96 by a delegated agent | 2026-10-22 | TRUE 48, FALSE 0, UNVERIFIABLE 4 | killed 26, survived 0 | 477566a4020f102c |
