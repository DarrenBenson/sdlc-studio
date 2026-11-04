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
| US1107 | Claude Opus 5.5 (orchestrator, repair round 1) | 2026-11-01 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | none - no test declared | 9dde8cd62f3e1b9d at 37ca7ead4d65 |
| US1080 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 33, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 0 | fec3f80a7cc2ec04 at a845af8b095d |
| BG1109 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | 3573302c2bccdc53 at 3e2b0383360f |
| US1108 | Claude Sonnet 5.5 (builder) | 2026-11-01 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | none - no test declared | bdbb3fc9107d395a at 3f0a768f4eae |
| US1108 | Claude Opus 5.5 (orchestrator, repair round 1) | 2026-11-01 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | none - no test declared | f46fdb6d4b49bbb6 at 0c6503fbb5df |
| US1109 | Claude Sonnet 5.5 (builder) | 2026-11-01 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | none - no test declared | fe746e6821772c4a at ce4d25252665 |
| US1081 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 45, FALSE 0, UNVERIFIABLE 0 | killed 26, survived 0 | 3750365af15b644f at 5fac0d2b38c9 |
| US1109 | Claude Opus 5.5 (orchestrator, repair round 1) | 2026-11-01 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | none - no test declared | d438c24434413f5c at 5fac0d2b38c9 |
| BG1137 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 7 | f42010bd559b75c1 at 59df073fd7f2 |
| BG1138 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 43d448c106d33972 at 00891ced8c29 |
| US1099 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | killed 16, survived 0 | eea4fb223b9bf60d at 4ddefceb7d98 |
| US1083 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 37, FALSE 0, UNVERIFIABLE 1 | killed 25, survived 0 | c0be1dfbba0d0db6 at c24be54bf7a4 |
| US1082 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 32, FALSE 0, UNVERIFIABLE 0 | killed 21, survived 0 | 3fd34174a902ac3d at 75c53a6d3339 |
| US1099 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 31, survived 1 | 2a9e6b7064f2cb4f at b652390507a3 |
| BG1135 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 25, FALSE 0, UNVERIFIABLE 0 | killed 18, survived 0 | db01751b1a8829e4 at a49a38150383 |
| US1103 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 33, FALSE 0, UNVERIFIABLE 1 | killed 21, survived 0 | 437e546c24f9e39f at 90f0f86371a8 |
| BG1065 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 31, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 0 | 581454a3b20c9cdb at 69ccd9202e5c |
| US1104 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 47, FALSE 0, UNVERIFIABLE 0 | killed 25, survived 0 | d1f332ac3ebacddb at 8f380767dc53 |
| US1100 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 24, survived 0 | 8d25241f7cd9eef1 at cd61ddab04c1 |
| BG1065 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 44, FALSE 0, UNVERIFIABLE 0 | killed 24, survived 2 | 9d52eb5ded05b0f4 at c50422a793dc |
| US1101 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 25, FALSE 0, UNVERIFIABLE 0 | killed 34, survived 0 | 7e289b9132168453 at 0f26c3e85eb6 |
| US1102 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 25, FALSE 0, UNVERIFIABLE 0 | killed 30, survived 0 | 223aee4d4356af4a at d4028a31c57c |
| US1102 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 30, FALSE 0, UNVERIFIABLE 0 | killed 26, survived 0 | 54bcc390439c6752 at cf4d02bca7e3 |
| BG1166 | Claude Opus 5.5 (builder) | 2026-11-01 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | b39622267ef8bdd8 at 6a7404b5c5c9 |
| US1110 | Claude Opus 5.5 (builder) | 2026-11-02 | TRUE 49, FALSE 0, UNVERIFIABLE 0 | killed 24, survived 0 | de4d8750a1291789 at 8da27ca2d635 |
| US1110 | Claude Opus 5.5 (builder) | 2026-11-02 | TRUE 27, FALSE 0, UNVERIFIABLE 2 | killed 41, survived 0 | 659d5a17bd92d655 at c9e1a9c394b7 |
| US1111 | Claude Opus 5.5 (builder) | 2026-11-02 | TRUE 40, FALSE 0, UNVERIFIABLE 0 | killed 28, survived 1 | 222a0cd7521848e2 at 8267f2755376 |
| BG1176 | Claude Opus 5.5 (builder) | 2026-11-02 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | none - no test declared | 992dedf274075c5e at 729890cc4ff2 |
| BG1167 | Claude Opus 5.5 (builder) | 2026-11-02 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | c522bda328fc4bea at 6c6ba3553ca7 |
| BG1167 | Claude Opus 5.5 (builder) | 2026-11-03 | TRUE 32, FALSE 0, UNVERIFIABLE 0 | killed 21, survived 5 | bec0e83144a8a9d0 at 1696cce8e03f |
| US1112 | Claude Opus 5.5 (builder) | 2026-11-03 | TRUE 31, FALSE 0, UNVERIFIABLE 3 | killed 17, survived 0 | 849d7753cb622071 at a3e63eeaa754 |
| US1113 | Claude Opus 5.5 (builder) | 2026-11-03 | TRUE 41, FALSE 0, UNVERIFIABLE 1 | killed 26, survived 2 | 33d04697ac39ccc9 at eeeba8615fec |
| US1112 | Claude Opus 5.5 (builder) | 2026-11-03 | TRUE 42, FALSE 0, UNVERIFIABLE 3 | killed 33, survived 3 | 445c00a77e23e62f at 2107c701ac64 |
| US1113 | Claude Opus 5.5 (builder) | 2026-11-03 | TRUE 54, FALSE 0, UNVERIFIABLE 6 | killed 51, survived 4 | 0d598a9ec491f180 at b7a11ce291cd |
| US1114 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 45, FALSE 0, UNVERIFIABLE 0 | killed 30, survived 3 | 530196ba32876b72 at 9af09ea6ab5a |
| US1115 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 25, FALSE 0, UNVERIFIABLE 1 | killed 13, survived 0 | b8281176cb81255e at 8c1c1cd8bb15 |
| US1116 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | d632ae19fa19523c at 8c1c1cd8bb15 |
| US0986 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 45, FALSE 0, UNVERIFIABLE 0 | killed 49, survived 2 | 96368b5d8dca6c87 at b8b7f4176086 |
| BG0958 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 3 | c0ac7763690c5898 at adff99e2162e |
| BG1116 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 13, FALSE 0, UNVERIFIABLE 1 | killed 9, survived 0 | f89f5073ef5a0eaa at adff99e2162e |
| BG1090 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 13, FALSE 0, UNVERIFIABLE 1 | killed 6, survived 1 | 96e7952b33c86f86 at adff99e2162e |
| US0989 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 35, FALSE 0, UNVERIFIABLE 3 | killed 21, survived 6 | db510e7b257574b6 at d4e1ca5381de |
| US0991 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 31, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 2 | 4f954584274a61f2 at b27472d7c9f1 |
| US0986 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 43, FALSE 0, UNVERIFIABLE 0 | killed 56, survived 3 | 9c56fd0c8d676f96 at 68335aff0ce9 |
| BG1116 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 14, FALSE 0, UNVERIFIABLE 1 | killed 15, survived 0 | 54de61172cd14760 at 4544d4eb4b32 |
| US0990 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 31, FALSE 0, UNVERIFIABLE 6 | killed 19, survived 2 | f6017ad0e1c4e7cb at 22662d8650ee |
| BG1197 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 33, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 1 | 49bb157dc374290d at 0d866324834f |
| US0990 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 45, FALSE 0, UNVERIFIABLE 5 | killed 26, survived 5 | 8dd595196124133e at 3d06e00c90ca |
| BG1122 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 34, FALSE 0, UNVERIFIABLE 1 | killed 20, survived 2 | ee2efcde2579e376 at 7b18b011915c |
| BG1147 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 2 | 01bde3361fb93579 at c983c2113787 |
| BG1163 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 29, FALSE 0, UNVERIFIABLE 0 | killed 19, survived 0 | 45ec5d63a5166d5c at c983c2113787 |
| BG1183 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 48, FALSE 0, UNVERIFIABLE 1 | killed 40, survived 0 | cac88fca9ca759ad at 39243dc40ce4 |
| BG1163 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 22, survived 0 | 4eb67685dbcb85fb at cc7589844d84 |
| BG1210 | Claude Opus 5.5 (orchestrator) | 2026-11-04 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | none - no test declared | 96586c531f63bc2e at 87c527de7251 |
