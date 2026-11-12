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
| BG1212 | Claude Opus 5.5 (orchestrator) | 2026-11-04 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | b7e8859f605a6e85 at eb35a6fab6d3 |
| BG1187 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 29, FALSE 0, UNVERIFIABLE 2 | killed 15, survived 5 | 8538b4f6bee7e010 at 457ac6c74b2c |
| BG1183 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 53, FALSE 0, UNVERIFIABLE 2 | killed 42, survived 1 | 779fabbc70da2936 at 8e7742dee67c |
| BG1216 | Claude Opus 5.5 (orchestrator) | 2026-11-04 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | none - no test declared | f3974e5cde4555f9 at 8e7742dee67c |
| BG1160 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 3 | 35a7351f36ee82cb at f8d7d3f7dccf |
| BG1114 | Claude Opus 5.5 (builder) | 2026-11-04 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 2 | 71cf48ac1b70be96 at f8d7d3f7dccf |
| BG1221 | Claude Opus 5.5 (orchestrator) | 2026-11-04 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 0, survived 1 | 7ca458ab386293af at 6c3209cb1e9e |
| BG1213 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 4 | fcdb53a6526ed689 at 94f4f54c53e9 |
| BG1223 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 1 | 133128b7b3daf4c1 at 2bd9fa138c56 |
| BG1220 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 11, FALSE 0, UNVERIFIABLE 1 | killed 12, survived 0 | 767fad3ee6a70994 at 92d11b7703ba |
| US1121 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 23, FALSE 0, UNVERIFIABLE 2 | killed 22, survived 1 | ee838f22cbac884f at 3dc17414ce27 |
| US1117 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 0 | 993fc3178e45b936 at c0b16912b4cd |
| BG1227 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 17d1f60b06324038 at 475b02938da0 |
| BG1217 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 3 | a6f15a9c7d40c24a at ea1d9572e97e |
| BG1190 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 12, FALSE 0, UNVERIFIABLE 1 | killed 12, survived 0 | 9933fcdcf6fc2690 at ea1d9572e97e |
| US1121 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 23, FALSE 0, UNVERIFIABLE 2 | killed 28, survived 1 | 1a37e732bef148a5 at 931f849c30af |
| US1117 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 39638bcaacc1da12 at 931f849c30af |
| US1118 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 24, FALSE 0, UNVERIFIABLE 1 | killed 27, survived 0 | f49414a40f98007e at 931f849c30af |
| US1120 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 15, FALSE 0, UNVERIFIABLE 1 | killed 15, survived 0 | 8db32a95848bf55e at 931f849c30af |
| BG1224 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 14, FALSE 0, UNVERIFIABLE 1 | killed 19, survived 0 | 9aed16456a8febe1 at 931f849c30af |
| BG1226 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 08e145c6477ca1b8 at 28778f2778e9 |
| BG1190 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 16, FALSE 0, UNVERIFIABLE 1 | killed 11, survived 0 | 114b191ff55a57d2 at e451cd7c588e |
| US1119 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 13, FALSE 0, UNVERIFIABLE 1 | killed 16, survived 0 | 67b206c6ee497a35 at c824c438a511 |
| US1120 | Claude Opus 5.5 (orchestrator repair) | 2026-11-05 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 11bc765198d86f81 at c824c438a511 |
| BG1224 | Claude Opus 5.5 (orchestrator repair) | 2026-11-05 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | 8c5a24bbc33597f6 at c824c438a511 |
| BG1226 | Claude Opus 5.5 (orchestrator repair) | 2026-11-05 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | 85ee628d0a528d25 at c824c438a511 |
| US1119 | Claude Opus 5.5 (orchestrator repair) | 2026-11-05 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | 7284fd9456cf374b at 329fad161849 |
| BG1236 | Claude Opus 5.5 (builder) | 2026-11-05 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 24c9f630a0b765a0 at 17ee4997094e |
| BG1236 | Claude Opus 5.5 (orchestrator repair) | 2026-11-05 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | 6a8ab6ad0fd6d476 at 67f3cfa4edb6 |
| US1122 | builder-US1122 | 2026-11-06 | TRUE 26, FALSE 0, UNVERIFIABLE 0 | killed 22, survived 2 | e392ab2665da0b88 at 3b5fcba949cc |
| US1124 | builder-w1b | 2026-11-06 | TRUE 16, FALSE 0, UNVERIFIABLE 1 | killed 13, survived 3 | 5d82f3de8fb24f3d at 9356d1fc4b4f |
| US1125 | builder-w1b | 2026-11-06 | TRUE 27, FALSE 0, UNVERIFIABLE 3 | killed 21, survived 3 | 236f266bca6c5a07 at 9356d1fc4b4f |
| US0987 | builder-w1b | 2026-11-06 | TRUE 27, FALSE 0, UNVERIFIABLE 1 | killed 19, survived 3 | 01b0d5cdbc8e2b0d at 9356d1fc4b4f |
| US1127 | builder-w2a | 2026-11-06 | TRUE 31, FALSE 0, UNVERIFIABLE 3 | killed 16, survived 1 | aab7ea91b15c3546 at 2871659b7d71 |
| US0988 | builder-w2a | 2026-11-06 | TRUE 25, FALSE 0, UNVERIFIABLE 2 | killed 23, survived 4 | 3d801d220653458e at 2871659b7d71 |
| US1128 | builder-US1128 | 2026-11-06 | TRUE 33, FALSE 0, UNVERIFIABLE 2 | killed 17, survived 1 | ed0320b1fbc4a26c at 992b6e5de003 |
| US1126 | builder-w2b | 2026-11-06 | TRUE 33, FALSE 0, UNVERIFIABLE 4 | killed 23, survived 0 | 762e94599d26e4ec at 2c8d0c40dc25 |
| US1124 | builder-w2b | 2026-11-06 | TRUE 26, FALSE 0, UNVERIFIABLE 1 | killed 17, survived 5 | bab824cd245ea822 at 2c8d0c40dc25 |
| US0988 | builder-US0988-repair | 2026-11-06 | TRUE 35, FALSE 0, UNVERIFIABLE 3 | killed 30, survived 5 | 55e614b9cbba741f at 7272875aae8f |
| US1128 | builder-US1128-repair | 2026-11-06 | TRUE 53, FALSE 0, UNVERIFIABLE 7 | killed 33, survived 2 | 33fbb69817626393 at b75acbcb980e |
| US1123 | builder-US1123 | 2026-11-06 | TRUE 42, FALSE 0, UNVERIFIABLE 3 | killed 14, survived 2 | 8ef20f2d429a3b16 at 61e9afe3491d |
| US1126 | builder-US1126-repair | 2026-11-06 | TRUE 50, FALSE 0, UNVERIFIABLE 5 | killed 31, survived 0 | 3cb9edcec5b6e3c9 at 4950f9681d01 |
| US1123 | builder-US1123-repair2 | 2026-11-06 | TRUE 50, FALSE 0, UNVERIFIABLE 4 | killed 25, survived 2 | 112f80bc0b75d85c at a9b13121e943 |
| BG1238 | builder-BG1238 | 2026-11-06 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 1 | c89295e3c6d96019 at a5df01de5a3f |
| BG1238 | orchestrator-BG1238-repair | 2026-11-06 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 1 | f68770a7b1c4700e at 822afd5b1f47 |
| BG1255 | orchestrator-BG1255 | 2026-11-06 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | 8a9272e4ada47100 at 4abb10c02f97 |
| BG1240 | builder-r8w1a | 2026-11-06 | TRUE 21, FALSE 0, UNVERIFIABLE 1 | killed 11, survived 2 | bcc6c8d8160a72b9 at c985273fbb2b |
| US1131 | builder-r8w1a | 2026-11-06 | TRUE 24, FALSE 0, UNVERIFIABLE 4 | killed 17, survived 3 | 0cf532cf05573ccf at c985273fbb2b |
| BG1246 | builder-r8w1a | 2026-11-06 | TRUE 22, FALSE 0, UNVERIFIABLE 2 | killed 11, survived 4 | 1e824beec9d71f4a at c985273fbb2b |
| BG1244 | builder-r8w1a | 2026-11-06 | TRUE 23, FALSE 0, UNVERIFIABLE 4 | killed 26, survived 3 | d5a3a1db42ddb793 at c985273fbb2b |
| BG1242 | builder-r8w1b | 2026-11-06 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 7c4af4be94b91214 at df67539ad024 |
| US1130 | builder-r8w1b | 2026-11-06 | TRUE 15, FALSE 0, UNVERIFIABLE 2 | killed 19, survived 0 | 1b1e26e3790c0cfb at df67539ad024 |
| BG1257 | builder-r8w1b | 2026-11-06 | TRUE 1, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | fb70ea77ba9563b1 at df67539ad024 |
| BG1245 | builder-r8w1b | 2026-11-06 | TRUE 26, FALSE 0, UNVERIFIABLE 4 | killed 19, survived 2 | bfe25faee2751b0a at df67539ad024 |
| US1129 | builder-US1129 | 2026-11-06 | TRUE 22, FALSE 0, UNVERIFIABLE 3 | killed 17, survived 0 | 762494d61a2e3771 at c0bfc07931a0 |
| BG1252 | builder-r8w2 | 2026-11-06 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 1 | d9302e3b42edf628 at 71120f122366 |
| BG1254 | builder-r8w2 | 2026-11-06 | TRUE 27, FALSE 0, UNVERIFIABLE 1 | killed 14, survived 1 | 418325307624ea46 at 71120f122366 |
| US1135 | builder-r8w2 | 2026-11-06 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 2 | 59fe52a8e2ab9a09 at 71120f122366 |
| US1133 | builder-r8w2 | 2026-11-06 | TRUE 15, FALSE 0, UNVERIFIABLE 1 | killed 9, survived 0 | 4f8948453fc3d5f4 at 71120f122366 |
| US1130 | builder-r8w2 | 2026-11-06 | TRUE 16, FALSE 0, UNVERIFIABLE 2 | killed 19, survived 0 | 6a5e17e20216ec03 at 71120f122366 |
| US1132 | builder-r8w2b | 2026-11-06 | TRUE 14, FALSE 0, UNVERIFIABLE 2 | killed 16, survived 0 | 6b2868c6f3b58ff4 at 88f180ac916a |
| US1129 | builder-r8w2b | 2026-11-06 | TRUE 24, FALSE 0, UNVERIFIABLE 3 | killed 17, survived 0 | 4ad6bde0b23b1e69 at 88f180ac916a |
| BG1258 | orchestrator-BG1258 | 2026-11-06 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | 89cce5c961c00c2e at 880e164a333e |
| US1132 | builder-US1132-repair | 2026-11-06 | TRUE 28, FALSE 0, UNVERIFIABLE 2 | killed 22, survived 0 | 7c8a8f0698e3bb4d at 3e8c5c775e59 |
| US1133 | builder-US1133-repair | 2026-11-06 | TRUE 21, FALSE 0, UNVERIFIABLE 1 | killed 18, survived 1 | ad03186bacb5a977 at 0506bdb81d7a |
| BG1259 | orchestrator-BG1259 | 2026-11-06 | TRUE 2, FALSE 0, UNVERIFIABLE 0 | killed 0, survived 1 | 790dad60967cbf84 at e0a060bcea91 |
| BG1259 | builder-BG1259-repair | 2026-11-06 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 1 | 65024c934ecc7267 at a06cd64b861a |
| BG1273 | orchestrator-BG1273 | 2026-11-06 | TRUE 1, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | 6b32bf3925b31a3f at 7a6bbb987d04 |
| BG1274 | builder-BG1274 | 2026-11-06 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | a08c77653d09b5d3 at ffe55071fc17 |
| BG1274 | orchestrator-BG1274-repair | 2026-11-06 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 078900b732cda17f at f0a276aaf814 |
| BG1278 | orchestrator-BG1278 | 2026-11-06 | TRUE 2, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 0 | e2b57430a322b8fd at eb647a98bd76 |
| BG1248 | builder-BG1248 | 2026-11-08 | TRUE 27, FALSE 0, UNVERIFIABLE 13 | killed 14, survived 2 | 28a17c7f265d627f at 1db97ef24deb |
| BG1249 | builder-BG1249 | 2026-11-08 | TRUE 27, FALSE 0, UNVERIFIABLE 9 | killed 14, survived 3 | fba33af7a1cf493c at 5733b936e6e3 |
| BG1289 | builder-BG1289 | 2026-11-08 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | a3d99110bf832f78 at 6d1b61eac72e |
| BG1288 | builder-BG1288 | 2026-11-08 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | 92900c24d150e886 at 4c236fe4d597 |
| BG1280 | builder-BG1288 | 2026-11-08 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 2 | ec7a94c3409e2749 at 4c236fe4d597 |
| US1137 | builder-US1137 | 2026-11-08 | TRUE 25, FALSE 0, UNVERIFIABLE 0 | killed 20, survived 0 | 6b62630f433dae3f at 5f757e0f3564 |
| US1136 | builder-US1136 | 2026-11-08 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 59cff9809128e967 at a459fd6dc652 |
| BG1288 | builder-BG1288-r2 | 2026-11-08 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 1 | b170b281b2e5f1ad at e51dad926285 |
| BG1290 | builder-BG1290 | 2026-11-08 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 1fedf79f0c896871 at b00deeaa8a4e |
| US1136 | builder-US1136-r2 | 2026-11-08 | TRUE 15, FALSE 0, UNVERIFIABLE 1 | killed 7, survived 0 | f4e1e33c22e633dd at 686a7b737046 |
| BG1290 | builder-BG1290-r2 | 2026-11-08 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 63d930f71b5bfb92 at 291547afbc6e |
| US1138 | builder-US1138 | 2026-11-08 | TRUE 18, FALSE 0, UNVERIFIABLE 1 | killed 27, survived 0 | 8bcddd0e159763f3 at d6351a44899c |
| US1138 | builder-US1138-r2 | 2026-11-08 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | 88658d140bc27107 at 7961ea8bea04 |
| US1139 | builder-US1139 | 2026-11-08 | TRUE 17, FALSE 0, UNVERIFIABLE 1 | killed 16, survived 0 | 3e04d451b1cd4f39 at a724f9538c24 |
| US1139 | builder-US1139-r2 | 2026-11-08 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | e1fbf0a45e50291d at f95e02aa2987 |
| US1143 | agent-a9995a17c2ff54714 | 2026-11-09 | TRUE 19, FALSE 0, UNVERIFIABLE 2 | killed 19, survived 1 | 344ef60065b37805 at 7dc73da0164e |
| US0986 | agent-a8b13541d292d694d | 2026-11-09 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 22, survived 0 | 8b79a59224b09107 at 833a9e0c55b4 |
| BG1205 | agent-a8b13541d292d694d | 2026-11-09 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 22, survived 0 | 8b79a59224b09107 at 833a9e0c55b4 |
| US1140 | agent-a2e3b7391cbc88b52 | 2026-11-09 | TRUE 39, FALSE 0, UNVERIFIABLE 0 | killed 27, survived 3 | 2b5f5671ba39dcb0 at c8f961061766 |
| BG1302 | agent-a16ddfb962a271222 | 2026-11-09 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 2 | e1b6fd33a9ecd6da at ab054eb1a003 |
| BG1303 | agent-a16ddfb962a271222 | 2026-11-09 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 2 | 48478cc637d08af8 at ab054eb1a003 |
| US1146 | agent-a87db08ba19908b9d | 2026-11-09 | TRUE 33, FALSE 0, UNVERIFIABLE 0 | killed 34, survived 4 | 33a4f9bd0c9f2022 at 4975eb19428d |
| US1143 | agent-a86886b1310758718 | 2026-11-09 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | fa32add835c7f392 at 3b6df6951479 |
| BG1312 | agent-a5e961724fb473d0a | 2026-11-09 | TRUE 31, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 2 | 6d2e6200b541ddbf at 15020d9c9119 |
| US1130 | agent-ab3ddf10b0c79df6d | 2026-11-09 | TRUE 28, FALSE 0, UNVERIFIABLE 0 | killed 26, survived 1 | 225af9ee42045a68 at 75325b85b131 |
| US1141 | agent-a5b509ecd103c0a2c | 2026-11-09 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 18, survived 0 | a884ce0ea470151f at 35344523e730 |
| US1144 | agent-ab9b2e779b44d00bc | 2026-11-09 | TRUE 27, FALSE 0, UNVERIFIABLE 0 | killed 16, survived 0 | 06147cdf5612633b at 19d129a86f8c |
| US1147 | agent-ac99e8de368a8b328 | 2026-11-09 | TRUE 25, FALSE 0, UNVERIFIABLE 1 | killed 38, survived 0 | 6036b8e3b7a39306 at a5156b7e9125 |
| US1147 | agent-aa633b3a4c9348cba | 2026-11-09 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 93ec3ad227e47689 at c4d53913f29b |
| US1133 | agent-ad983c7594ffa6c79 | 2026-11-09 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 1242999014db0d5c at dba831b568d2 |
| BG1264 | agent-ad983c7594ffa6c79 | 2026-11-09 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 5595668f58241fa5 at dba831b568d2 |
| BG1318 | agent-a76bffbbdd6061ddf | 2026-11-09 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 16, survived 1 | e05448ec4398437f at 897b4c63961d |
| US1148 | agent-a738b8cbad3aadd31 | 2026-11-09 | TRUE 34, FALSE 0, UNVERIFIABLE 0 | killed 25, survived 1 | 93758d0d99048635 at 77edb6283f91 |
| BG1320 | agent-a097bf8ee0820df94 | 2026-11-09 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 1 | 5aede75d6381bd68 at c464def52234 |
| US1145 | agent-ae2e44a5ca45735aa | 2026-11-09 | TRUE 19, FALSE 0, UNVERIFIABLE 3 | killed 17, survived 0 | c94333015ca99fae at f4e3a8c5f275 |
| US1142 | agent-a99b480f496e31d57 | 2026-11-09 | TRUE 24, FALSE 0, UNVERIFIABLE 2 | killed 24, survived 0 | 415441519aea71e1 at 22b0974b3a26 |
| BG1329 | agent-ac5a0636b6a711b56 | 2026-11-09 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 1 | 2088d2c67b3bebf0 at 96ac366240a2 |
| BG1010 | agent-abe7ba792a2fe05a1 | 2026-11-12 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 3 | 08f5551a7a3a5d41 at 4f2d4b45b6fd |
| BG1030 | agent-a34e09e23d8fe1a8d | 2026-11-12 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 2 | 77d6dd13e7e30a2e at 39c82080c7bb |
| BG1010 | agent-af5edc354aaae3f9e | 2026-11-12 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 1 | c0ab3d597cef212c at b8dd0085d07f |
| US1149 | agent-acd26dfce191874a5 | 2026-11-12 | TRUE 17, FALSE 0, UNVERIFIABLE 3 | killed 21, survived 0 | 850e0c43ea838a97 at 1b073493b745 |
| US1011 | agent-a645b7de00d9143c2 | 2026-11-12 | TRUE 19, FALSE 0, UNVERIFIABLE 1 | killed 11, survived 2 | 5417ca1e133705e4 at b5b12fd2d1e3 |
| US0997 | agent-a34fbb483d24fe4f7 | 2026-11-12 | TRUE 27, FALSE 0, UNVERIFIABLE 1 | killed 6, survived 0 | e4072389fca7a7a7 at faf4aa846953 |
| US1149 | agent-a02a7e706c7047225 | 2026-11-12 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 7a2fd874bb3a7f8b at dc1b31fadad7 |
| US1012 | agent-a74a825ff80c5119c | 2026-11-12 | TRUE 28, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 0 | 9042b1d6fe3ae927 at ed451273201f |
| US0998 | agent-ada3896a7bd23a761 | 2026-11-12 | TRUE 24, FALSE 0, UNVERIFIABLE 1 | killed 12, survived 2 | 89aeaa68f4160f94 at 509850a10038 |
| US1013 | agent-a368899f978d7061a | 2026-11-12 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 24, survived 2 | 7dffba504fa20df3 at f60b9512ab27 |
| BG1334 | agent-a45df90bb6be1c910 | 2026-11-12 | TRUE 14, FALSE 0, UNVERIFIABLE 1 | killed 9, survived 0 | d03bb5e7949feb32 at a7e4719f53fb |
| US1000 | agent-a285f7da7fb32a4fb | 2026-11-12 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 1 | 966e14cddc2ab8c1 at d57ec9844bf5 |
| US1016 | agent-ad4164fbfdcc8e1a7 | 2026-11-12 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | killed 18, survived 1 | bd3f7350e9f661d1 at cf56d0116981 |
| US1001 | agent-a4a223abb716c121c | 2026-11-12 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 022266a71a13a340 at a0c64e4aede2 |
| US1014 | agent-ac7e43b4d18629b12 | 2026-11-12 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 1 | c75c61b7b1025b57 at 7d1cf5a00cca |
| US1000 | agent-a853fc9204801d1ea | 2026-11-12 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | e6d6b5461bad9a0a at d3f6e3f3c292 |
| US1015 | agent-a8c808ffeaf53ebd3 | 2026-11-12 | TRUE 27, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | 95a05d88fdb55384 at a2ad5d66643e |
| US1134 | agent-afd8f015112a7dd00 | 2026-11-12 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 1 | c126d4cdd50c70f4 at 3d6f4210ef42 |
| BG1300 | a0b533adf0e8595de | 2026-11-12 | TRUE 21, FALSE 0, UNVERIFIABLE 2 | killed 9, survived 1 | d68f6e85daaf08d4 at a9596961f6fe |
