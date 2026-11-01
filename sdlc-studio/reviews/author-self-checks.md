# Author Self-Checks

> Append-only. The author's own claim inventory and mutation pass per unit, recorded by
> `critic.py self-check record` before a reviewer is briefed. The digest is over the
> content of the unit's Affects files, less the review tooling's own writes, when the row
> was written, followed by the commit it was taken at. A row is current when its digest
> matches that content now, or that content with each file that has no uncommitted edit
> read at its newest commit since the row's commit that is not another unit's (or at the
> row's commit when all are); a commit is another unit's when its subject names a unit id
> and none is this unit's. `critic.py brief` reads any other row as stale.

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
| US1087 | orchestrator (US1087's author); repair round 1 11e0d5cf by a delegated agent | 2026-10-22 | TRUE 46, FALSE 0, UNVERIFIABLE 2 | killed 16, survived 0 | 43937025bd00a202 |
| US1091 | builder-US1091 | 2026-10-22 | TRUE 34, FALSE 0, UNVERIFIABLE 1 | killed 22, survived 1 | 516b1d029bcaade6 |
| BG1117 | builder-BG1117; doc fixes and rebase by the orchestrator | 2026-10-22 | TRUE 29, FALSE 0, UNVERIFIABLE 0 | killed 21, survived 1 | 1225d492e6dc28b0 at 0849a8c025b5 |
| BG1113 | builder-BG1113 | 2026-10-22 | TRUE 15, FALSE 0, UNVERIFIABLE 3 | killed 5, survived 1 | 931b94b68fae6c90 at 3caabff0c2ce |
| US1097 | builder-US1097; fixture marking and rebase by the orchestrator | 2026-10-22 | TRUE 27, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 1 | 6d0931d6f49faed7 at 16f8544b896b |
| US1094 | builder-US1094 | 2026-10-22 | TRUE 31, FALSE 0, UNVERIFIABLE 0 | killed 23, survived 0 | f378a7b5c7c28c07 at be243a2fe212 |
| US1096 | builder-US1096 | 2026-10-22 | TRUE 36, FALSE 0, UNVERIFIABLE 0 | killed 19, survived 0 | 5321cd3302dd9dc0 at be243a2fe212 |
| BG1117 | builder-BG1117; repair round 1 681e5ec4, rebased onto US1094 by the orchestrator | 2026-10-22 | TRUE 35, FALSE 0, UNVERIFIABLE 0 | killed 28, survived 1 | 90577d29769c028e at 681e5ec4b361 |
| US1091 | builder-US1091; repair round 1 bd362d90, rebased by the orchestrator | 2026-10-22 | TRUE 51, FALSE 0, UNVERIFIABLE 1 | killed 41, survived 0 | 49434ba4d8c25d72 at 92c3fcab206f |
| BG1095 | builder-BG1095 | 2026-10-22 | TRUE 29, FALSE 0, UNVERIFIABLE 0 | killed 20, survived 2 | 214de96c384a4614 at 92c3fcab206f |
| US1093 | builder-US1093 | 2026-10-22 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 19, survived 0 | a90822bde2b86b56 at 92c3fcab206f |
| US1096 | builder-US1096; repair round 1 c3182209, rebased by the orchestrator | 2026-10-26 | TRUE 39, FALSE 0, UNVERIFIABLE 0 | killed 28, survived 1 | 97888e63ac136570 at d65ef2709fa5 |
| BG1078 | builder-BG1078 | 2026-10-26 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 1 | 21d10aa2bce18555 at d65ef2709fa5 |
| US1097 | builder of US1091's repair; US1097 repair round 1 979c2d83, rebased by the orchestrator | 2026-10-26 | TRUE 36, FALSE 0, UNVERIFIABLE 0 | killed 32, survived 0 | 3b6ac5b59c69498c at 979c2d835a7e |
| BG1127 | builder of US1091's repair; landed by the orchestrator | 2026-10-26 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 457d084209d57134 at 07fe889d4a57 |
| BG0962 | builder-BG0962 | 2026-10-26 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | f9227114d0097134 at 07fe889d4a57 |
| US1092 | builder-US1092; rebased by the orchestrator | 2026-10-26 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 22, survived 0 | 9c771fae1ce72e72 at 877c377187f4 |
| US1095 | builder-US1095; the two Affects additions by the orchestrator | 2026-10-26 | TRUE 30, FALSE 0, UNVERIFIABLE 0 | killed 26, survived 0 | 3975a9d8bd665aff at cada3e159b67 |
| US1086 | Claude Opus 5.5 | 2026-10-31 | TRUE 48, FALSE 0, UNVERIFIABLE 0 | killed 29, survived 5 | 405fd68d7fbd69ed at 772509ec2911 |
| US1076 | Claude Opus 5.5 | 2026-10-31 | TRUE 63, FALSE 0, UNVERIFIABLE 5 | killed 22, survived 5 | 0e2b37b96c4794b6 at cf46669d26f6 |
| US1098 | Claude Opus 5.5 (builder) | 2026-10-31 | TRUE 26, FALSE 0, UNVERIFIABLE 0 | killed 19, survived 0 | 4ef310cdf7a7ad61 at bdccb0e2454f |
| US1098 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 29, FALSE 0, UNVERIFIABLE 0 | killed 38, survived 0 | 286e7bbc9d6acf53 at c2e5db91af45 |
| BG0963 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 33, FALSE 0, UNVERIFIABLE 1 | killed 22, survived 0 | acd33a073f872080 at 3fea19d6beb2 |
| BG1140 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 25, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | def9311befcae70e at 4e76c61f5a3d |
| BG1139 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 31, FALSE 0, UNVERIFIABLE 0 | killed 21, survived 1 | e032735bf8c5650a at f5d6f743349a |
| US1105 | Claude Sonnet 5.5 (builder) | 2026-11-01 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | none - no test declared | 03e607cd12c59ee7 at 64fc91441c20 |
| US1105 | Claude Sonnet 5.5 (builder) | 2026-11-01 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | none - no test declared | 35c584a847065bc3 at 9033e56686bc |
| US1106 | Claude Sonnet 5.5 (builder) | 2026-11-01 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | none - no test declared | 122ee6dcf4d11a2b at 3dc5342aad4d |
| BG0963 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 46, FALSE 0, UNVERIFIABLE 0 | killed 32, survived 2 | 8817d48dd22f1b5f at d645ef6ac0c1 |
| US1106 | Claude Sonnet 5.5 (builder) | 2026-11-01 | TRUE 24, FALSE 0, UNVERIFIABLE 2 | none - no test declared | 2bc2070b854b7d97 at ba9b1c91eeb3 |
| US1107 | Claude Sonnet 5.5 (builder) | 2026-11-01 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | none - no test declared | 48ff2501f25fd212 at fd1fd2150ece |
