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
| BG1374 | agent-aa149fa9f68473a24 | 2026-11-12 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | b9f0671540873722 at a41ed8029d98 |
| BG1190 | agent-aaaeed3bda6813b60 | 2026-11-12 | TRUE 28, FALSE 0, UNVERIFIABLE 3 | killed 16, survived 2 | 77499584b90fdde5 at 0c9a21c8cef6 |
| BG1228 | agent-aaaeed3bda6813b60 | 2026-11-12 | TRUE 28, FALSE 0, UNVERIFIABLE 3 | killed 16, survived 2 | 77499584b90fdde5 at 0c9a21c8cef6 |
| BG1112 | agent-aaaeed3bda6813b60 | 2026-11-12 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 1 | e89dac4c0ebda4f0 at 0c9a21c8cef6 |
| BG1333 | agent-addaf4981ee134d39 | 2026-11-12 | TRUE 19, FALSE 0, UNVERIFIABLE 1 | killed 11, survived 2 | 8f5c3adae0e0d4a5 at 2c9f5ff5c51f |
| BG1371 | agent-addaf4981ee134d39 | 2026-11-12 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 1 | f1c77d8a296e023b at 2c9f5ff5c51f |
| BG0965 | agent-addaf4981ee134d39 | 2026-11-12 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 2 | 4b9f855f1927d450 at 2c9f5ff5c51f |
| BG1340 | agent-a961d39dae50553a4 | 2026-11-12 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | e1fa48901664e635 at c81e3ec6e549 |
| BG1341 | agent-a961d39dae50553a4 | 2026-11-12 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 8ebf38c0f6fae460 at c81e3ec6e549 |
| BG0990 | agent-a961d39dae50553a4 | 2026-11-12 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | d21edfaa472f8031 at c81e3ec6e549 |
| BG1343 | agent-a961d39dae50553a4 | 2026-11-12 | TRUE 7, FALSE 0, UNVERIFIABLE 2 | killed 5, survived 0 | 263e32792806c0a6 at c81e3ec6e549 |
| BG1279 | agent-adf490d3cbadd4efb | 2026-11-12 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 52798d8962de0e20 at fc48ced8435e |
| BG1331 | agent-adf490d3cbadd4efb | 2026-11-12 | TRUE 11, FALSE 0, UNVERIFIABLE 3 | killed 12, survived 0 | 2956cc163a95fb39 at fc48ced8435e |
| BG1305 | agent-adf490d3cbadd4efb | 2026-11-12 | TRUE 7, FALSE 0, UNVERIFIABLE 2 | killed 6, survived 0 | 16a3d012c8c3d579 at fc48ced8435e |
| BG1336 | agent-a668b032939040db2 | 2026-11-12 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | ea2cb7a32f7883fa at 35b9a7886289 |
| BG1337 | agent-a668b032939040db2 | 2026-11-12 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 9f3b7818ac0c032b at 35b9a7886289 |
| BG1330 | agent-a668b032939040db2 | 2026-11-12 | TRUE 15, FALSE 0, UNVERIFIABLE 1 | killed 18, survived 1 | c2e386c92148af41 at 35b9a7886289 |
| BG1005 | agent-a9fa24d46c9d84862 | 2026-11-13 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 93794866a399c3cf at b1befc660041 |
| BG1009 | agent-a9fa24d46c9d84862 | 2026-11-13 | TRUE 10, FALSE 0, UNVERIFIABLE 1 | killed 9, survived 0 | 418583901643afe5 at b1befc660041 |
| BG0991 | agent-a9fa24d46c9d84862 | 2026-11-13 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | a4554680f02228f0 at b1befc660041 |
| BG1262 | agent-a74f98449efe5cabd | 2026-11-13 | TRUE 17, FALSE 0, UNVERIFIABLE 1 | killed 8, survived 0 | 705a48a350ce1518 at 15e3f9989bf2 |
| BG1261 | agent-a74f98449efe5cabd | 2026-11-13 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | f1dc35b52aaa9a42 at 15e3f9989bf2 |
| BG1279 | agent-ab262b595414727bb | 2026-11-13 | TRUE 6, FALSE 0, UNVERIFIABLE 1 | killed 3, survived 1 | 7aadc7707ccf4d49 at 5b0db1f851f6 |
| BG1331 | agent-ab262b595414727bb | 2026-11-13 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 2 | bfc9a1f668c02dbb at 5b0db1f851f6 |
| BG1339 | agent-a34d2d7b8d5153007 | 2026-11-13 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 1 | d45f68f22ab68880 at d1332bebcc27 |
| BG1344 | agent-a34d2d7b8d5153007 | 2026-11-13 | TRUE 7, FALSE 0, UNVERIFIABLE 1 | killed 4, survived 1 | 22c3f07ad1fab610 at d1332bebcc27 |
| BG1372 | agent-a93ebdfdb0401bab2 | 2026-11-13 | TRUE 11, FALSE 0, UNVERIFIABLE 1 | none - no test declared | 82a1af1eb43c4b3f at 0851f78fba98 |
| BG1009 | agent-a99ce8678309e0a6f | 2026-11-13 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 3 | e9c04f06bb726794 at 62ef7fad4358 |
| BG1005 | agent-a99ce8678309e0a6f | 2026-11-13 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 2 | 39f93d41e2d7f6cc at 62ef7fad4358 |
| BG1420 | agent-adce72e294283f566 | 2026-11-13 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 2 | f8f9109cea096609 at 92c84b1008b8 |
| BG1420 | agent-ae14dd817e5f2d813 | 2026-11-13 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | e843b5f99bf5bd30 at 1caffe6db79e |
| BG1391 | agent-a19d55895069cc955 | 2026-11-14 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 6aa9570f6179c8be at c41f87aca305 |
| BG1393 | agent-a19d55895069cc955 | 2026-11-14 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 1 | 9c85bc923508dfbd at c41f87aca305 |
| US0992 | agent-ac886cc0a898c1f84 | 2026-11-14 | TRUE 20, FALSE 0, UNVERIFIABLE 1 | killed 20, survived 1 | 18bb2f3878e3e106 at 0993241e731f |
| BG1425 | agent-a229c275ee83f4d31 | 2026-11-15 | TRUE 22, FALSE 0, UNVERIFIABLE 1 | killed 19, survived 0 | 7669998386caa2b9 at 5a09e949877f |
| BG1397 | agent-aa781dcb6895f9b7d | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 1 | 04c0ddb7abb78239 at 93db614da828 |
| BG1394 | agent-aa781dcb6895f9b7d | 2026-11-15 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 1 | eae3b7777e6b313d at 93db614da828 |
| US1152 | agent-ae06ac928725de915 | 2026-11-15 | TRUE 23, FALSE 0, UNVERIFIABLE 0 | killed 16, survived 2 | 4f83c7e932424092 at fbacb19b53c4 |
| US0992 | agent-a46bdba1c484ea7f7 | 2026-11-15 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 1 | f34c691450cc19e2 at 9440273fd2e6 |
| US1155 | agent-a6eab1e6fb86c7926 | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | a7f026bff17253c3 at 654f65324b2d |
| US1156 | agent-a6eab1e6fb86c7926 | 2026-11-15 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | c649686795bb9653 at 654f65324b2d |
| BG1019 | agent-a0d83e28ea0110a12 | 2026-11-15 | TRUE 21, FALSE 0, UNVERIFIABLE 1 | killed 10, survived 0 | a319900a213e7462 at da2cbec864d5 |
| BG1268 | agent-a79477da0f30548b4 | 2026-11-15 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 1 | 119d244084992d85 at 8cebc5ae43c1 |
| US0993 | agent-a21379cd20e1a3398 | 2026-11-15 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 1 | 5d745608faa4930f at bc0ada9b4c27 |
| US0996 | agent-a21379cd20e1a3398 | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 3 | ffa14fa80bea3591 at bc0ada9b4c27 |
| US1155 | agent-a96e7a387904d87c8 | 2026-11-15 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 06438fdd83d3792f at bd4604ab6615 |
| US1156 | agent-a96e7a387904d87c8 | 2026-11-15 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 1 | f2b87897f15dc86c at bd4604ab6615 |
| US0994 | agent-a9af9dd8ad4131f9d | 2026-11-15 | TRUE 19, FALSE 0, UNVERIFIABLE 1 | killed 10, survived 0 | c84cf414e2373656 at 02516faf5ce5 |
| US0995 | agent-a9af9dd8ad4131f9d | 2026-11-15 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 1 | 7b5b72478e402ada at 02516faf5ce5 |
| US0999 | agent-a2bf98fa70dee7e3b | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 1 | killed 13, survived 0 | f8e4a8169c7a9c25 at 38f8a800b6bc |
| BG1439 | agent-af8d52d9d612f11e5 | 2026-11-15 | TRUE 22, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 053f30b222d3f3fd at ad308a735031 |
| US0995 | agent-a82f190b246e7d558 | 2026-11-15 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 0aed2005c92c0b12 at 22921fa811ae |
| US1150 | agent-a6db323e515448007 | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | d6dd643e29b33ec9 at 3e0fb411f0e9 |
| US1151 | agent-a6db323e515448007 | 2026-11-15 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | d3437c4472cffe0d at 3e0fb411f0e9 |
| BG1442 | agent-aafa72bb967c418b8 | 2026-11-15 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | e5dab239993bfdfe at f155c529e6b4 |
| BG1441 | agent-aafa72bb967c418b8 | 2026-11-15 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 25db1c0be7651275 at f155c529e6b4 |
| US1153 | agent-ab3e7f9d07c70280f | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 18ad4de370b03352 at 24fb01008edd |
| US1154 | agent-ab3e7f9d07c70280f | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | 34cc2efe3f18445b at 24fb01008edd |
| US1154 | agent-afc49710ee7fa674a | 2026-11-15 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 1 | c08a3a562953ed1f at e657560b35ce |
| BG1437 | agent-aafafd38780b86f62 | 2026-11-15 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 1, survived 1 | 69403fa10e4bfde4 at 2fac2fdfd37d |
| BG1445 | agent-aafafd38780b86f62 | 2026-11-15 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 2 | 3f30d6687736829e at 2fac2fdfd37d |
| US1157 | agent-a01cf57063a7495e1 | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 2 | killed 15, survived 0 | 1d552334651069fb at ef4d25e2c0ae |
| US1158 | agent-a01cf57063a7495e1 | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 2 | 660c05cf5dc7e659 at ef4d25e2c0ae |
| US1061 | agent-a7fec24ddc3b52893 | 2026-11-15 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 1 | bd3d8351ef4b6112 at 01e3aa92b85e |
| US1062 | agent-a7fec24ddc3b52893 | 2026-11-15 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 1 | a96d4827f9d6f4f0 at 01e3aa92b85e |
| US1159 | agent-a07112df881a20581 | 2026-11-15 | TRUE 17, FALSE 0, UNVERIFIABLE 2 | killed 14, survived 0 | a02a9145bde738c1 at a805cec77643 |
| US1058 | agent-a8d7bb2339263220d | 2026-11-15 | TRUE 26, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 0 | 03ead1b0e545ec80 at 2766fda51a6f |
| US1059 | agent-a8d7bb2339263220d | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 1 | killed 10, survived 1 | d60750cfd3ed20c8 at 2766fda51a6f |
| US1064 | agent-ad6b0b9722170a11f | 2026-11-15 | TRUE 25, FALSE 0, UNVERIFIABLE 1 | killed 22, survived 2 | 3dab770acd67ad78 at 3ee13b96c40c |
| US1058 | agent-afbd3d2a94a3f7d31 | 2026-11-15 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 2 | a2848b8de53c1042 at 75ba6de1177f |
| US1067 | agent-ab1d471939efa7584 | 2026-11-15 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 2fbbfc9c18625a58 at 2fc73a9954f8 |
| US1068 | agent-ab1d471939efa7584 | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 1 | 72bf03e282a50f85 at 2fc73a9954f8 |
| US1064 | agent-acb2995c1e1263575 | 2026-11-15 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | d0eca8dae5c0d2b9 at e8e66f8db104 |
| US1065 | agent-abfd6bdd803be5a0c | 2026-11-15 | TRUE 19, FALSE 0, UNVERIFIABLE 1 | killed 10, survived 1 | dee74ebffb71cc41 at fb36836ac8e3 |
| US1066 | agent-abfd6bdd803be5a0c | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 2 | a944520273cf6682 at fb36836ac8e3 |
| BG1459 | agent-abfd6bdd803be5a0c | 2026-11-15 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | none - no test declared | 2be7761112222bae at fb36836ac8e3 |
| BG1460 | agent-a4808b05ebc12143e | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 3 | adaf8e3c644c33ef at 61be40f32179 |
| US1067 | agent-a295af853eb4456e9 | 2026-11-15 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 1 | 924ef78137d95397 at 9ebfb69288a1 |
| US1068 | agent-a295af853eb4456e9 | 2026-11-15 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 278354ee0d016b9c at 9ebfb69288a1 |
| US1065 | agent-adaf7b272447a856c | 2026-11-15 | TRUE 11, FALSE 0, UNVERIFIABLE 1 | killed 7, survived 1 | 7d5cda78c9b0be1c at 8207a961bf65 |
| BG1468 | agent-adaf7b272447a856c | 2026-11-15 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 6ab0e4e9cb5b2f58 at 8207a961bf65 |
| BG1469 | agent-adaf7b272447a856c | 2026-11-15 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | c6e451c9860bb1cd at 8207a961bf65 |
| BG1471 | agent-adaf7b272447a856c | 2026-11-15 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 2 | 6623127d8fb9e957 at 8207a961bf65 |
| BG1471 | agent-a9f0da518ea618ee8 | 2026-11-15 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | bf463cc4f1b3d322 at 7675c0e8f633 |
| BG1396 | agent-a8f2ff5f422f5b5a0 | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 2 | aef1f634a7505d6a at f446773f55fd |
| BG1395 | agent-a8f2ff5f422f5b5a0 | 2026-11-15 | TRUE 10, FALSE 0, UNVERIFIABLE 1 | killed 11, survived 2 | 65fae08a5aa95671 at f446773f55fd |
| BG1474 | agent-a5d16abf808e48075 | 2026-11-15 | TRUE 11, FALSE 0, UNVERIFIABLE 1 | killed 8, survived 2 | 664fc5b717d320b9 at d6ced7681e1b |
| US1162 | agent-ab62d4c7b75ac6a25 | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 1 | killed 12, survived 1 | ccdabdeeb2a5f10f at 42252df76c39 |
| US1163 | agent-ab62d4c7b75ac6a25 | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 94739cbee7fe7518 at 42252df76c39 |
| US1165 | agent-a3931a1ac224b5f44 | 2026-11-15 | TRUE 16, FALSE 0, UNVERIFIABLE 1 | killed 15, survived 1 | 8ffb4abfd6aa9b91 at d8a805f872d5 |
| BG1260 | agent-a3931a1ac224b5f44 | 2026-11-15 | TRUE 7, FALSE 0, UNVERIFIABLE 1 | killed 10, survived 0 | 511f6bdd14c9d677 at d8a805f872d5 |
| US1160 | agent-aaae06d487ff24e50 | 2026-11-15 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 1 | bcca1d2437e7e319 at 1773ef2ae524 |
| US1161 | agent-aaae06d487ff24e50 | 2026-11-15 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 1 | 3a52f5d13f2de591 at 1773ef2ae524 |
| US1160 | agent-a5d45d358c8372b91 | 2026-11-15 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | 5721adffeb4e57c2 at 9bda89a1f921 |
| BG1478 | agent-a69c2039f627b67fe | 2026-11-15 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 5fa03323bc39f733 at 92e59e38c197 |
| BG1480 | agent-a69c2039f627b67fe | 2026-11-15 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | 089b17e73ba9525a at 92e59e38c197 |
| BG1479 | agent-a69c2039f627b67fe | 2026-11-15 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | f22378bb0f8f147a at 92e59e38c197 |
| BG1484 | agent-a69c2039f627b67fe | 2026-11-15 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 14b4c748626220cf at 92e59e38c197 |
| US1166 | agent-a22849a350e755137 | 2026-11-15 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 20, survived 0 | 84366f6d9a4a9483 at d2ea7fd61e44 |
| BG0998 | agent-a22849a350e755137 | 2026-11-15 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 2 | 32bac924c49ce7c1 at d2ea7fd61e44 |
| BG1177 | agent-aa35a6faeaf0dfeae | 2026-11-15 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 1 | 7ab86bc6920a62ff at fdc17fbc4c51 |
| US1164 | agent-aa35a6faeaf0dfeae | 2026-11-15 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 25, survived 1 | e91b76a218056452 at fdc17fbc4c51 |
| US1169 | agent-a5c26d9bf7b31b07e | 2026-11-15 | TRUE 14, FALSE 0, UNVERIFIABLE 1 | killed 20, survived 0 | 5c387379c9f130da at 5f476db7c3a8 |
| BG0947 | agent-a5c26d9bf7b31b07e | 2026-11-15 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 3e803ee8c423eefd at 5f476db7c3a8 |
| US1169 | agent-a7e557204f6fdf70b | 2026-11-16 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | c06417da6f7c1db4 at 75d275c0429e |
| BG1489 | agent-a2158982cc47dbbcb | 2026-11-16 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 04d83bdde8c08f26 at 2cfd66c73d90 |
| US1167 | agent-a0ba5f486e4f11944 | 2026-11-16 | TRUE 17, FALSE 0, UNVERIFIABLE 1 | killed 14, survived 0 | 1ceb15977a5ca108 at c012bc8e8ee8 |
| US1167 | agent-a172c18c7dccb0e5b | 2026-11-16 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 591e070472af206b at e001d1d7af17 |
| BG1494 | agent-a3a1e33594f18b294 | 2026-11-16 | TRUE 7, FALSE 0, UNVERIFIABLE 1 | killed 4, survived 0 | 38ce600299535532 at b80bb0af4d1e |
| BG1487 | agent-a3a1e33594f18b294 | 2026-11-16 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 082024015e9c5039 at b80bb0af4d1e |
| BG1493 | agent-ae0eddb7a4a155326 | 2026-11-16 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | e5f225e5e5ea6e11 at e82e4cb8c651 |
| US1170 | agent-a757c829da0be638c | 2026-11-16 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | f686b2a54f565fea at 88b1fc6f247d |
| US1172 | agent-a363ce8a4aebd626b | 2026-11-16 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 79f01b31e68f8a9c at 549a6ba79ba0 |
| US1171 | agent-ae16b5e59e84e497e | 2026-11-16 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | 1151ee0ec70ea5d8 at 9673d999c7ce |
| US1173 | agent-aec412120a0fd965c | 2026-11-16 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | e5002cdef448753b at 9fa295586fad |
| BG1501 | agent-aec412120a0fd965c | 2026-11-16 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 1 | 786db3eba2bd65a6 at 9fa295586fad |
| BG1501 | agent-a232a9a807062f8c2 | 2026-11-16 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 397cdc13ccdec5df at 2e4aa305b54a |
| US1173 | agent-a232a9a807062f8c2 | 2026-11-16 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 2, survived 0 | c30bfce43c412957 at 2e4aa305b54a |
| BG1498 | agent-a7c71263f42498c21 | 2026-11-16 | TRUE 21, FALSE 0, UNVERIFIABLE 1 | killed 9, survived 0 | 5782819cc8b9699d at 06574db5916b |
| BG1503 | agent-a0ab399d25656cd7f | 2026-11-16 | TRUE 23, FALSE 0, UNVERIFIABLE 2 | killed 10, survived 3 | abf3f88fc349f849 at 2e5c6027c18e |
| BG1506 | orchestrator | 2026-11-16 | TRUE 5, FALSE 0, UNVERIFIABLE 1 | killed 2, survived 1 | 4f623464cfa51479 at aa73db00f7ad |
| US1314 | agent-a0ba62cbe75da8de9 | 2026-11-17 | TRUE 31, FALSE 0, UNVERIFIABLE 2 | killed 14, survived 2 | 4d009ef8c1290047 at 795192279f6f |
| BG1524 | agent-aae6fc6aae5704cc8 | 2026-11-17 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 1 | a6f16a697fb3f666 at cb445223ec26 |
| US1292 | agent-aae6fc6aae5704cc8 | 2026-11-17 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | c496978979111c88 at cb445223ec26 |
| BG1523 | agent-a09a464012414bd6c | 2026-11-18 | TRUE 21, FALSE 0, UNVERIFIABLE 2 | killed 10, survived 1 | ba62919cd5898627 at b10e40aebc95 |
| BG1519 | agent-ae79e79ffece33151 | 2026-11-18 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 2 | 80788497f9fd8660 at 85b797868dd8 |
| BG1521 | agent-ae79e79ffece33151 | 2026-11-18 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 2 | 4d04b13c03132759 at 85b797868dd8 |
| BG1522 | agent-ae79e79ffece33151 | 2026-11-18 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 9dfaf2f2af424a9b at 85b797868dd8 |
| BG1507 | agent-a28646348c63599cf | 2026-11-18 | TRUE 19, FALSE 0, UNVERIFIABLE 1 | killed 13, survived 1 | 88fda4bfc80d8445 at defb29b0c9ef |
| BG1520 | agent-a28646348c63599cf | 2026-11-18 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 350e006fa0aaab9a at defb29b0c9ef |
| US1290 | agent-a28646348c63599cf | 2026-11-18 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 625822d552db0e17 at defb29b0c9ef |
| US1291 | agent-a28646348c63599cf | 2026-11-18 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | cc0e2b98483ff7d2 at defb29b0c9ef |
| BG1518 | agent-ab106154513e30497 | 2026-11-18 | TRUE 22, FALSE 0, UNVERIFIABLE 1 | killed 20, survived 0 | 58047e2a543716b2 at 566cb149b7a4 |
| US1293 | agent-a9092a87259ca0d56 | 2026-11-18 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 21, survived 1 | bf5175c7d3c452b9 at 10690f8a385d |
| BG1519 | agent-acaf624f0b3a41145 | 2026-11-18 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 02bfc6bd8c1c9284 at 3777e27e1c1b |
| US1290 | agent-a5bcccb1676e852ea | 2026-11-18 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 65449da79301431e at af624011cc7d |
| BG1507 | agent-a5bcccb1676e852ea | 2026-11-18 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 0d9d34a615f1f1e6 at af624011cc7d |
| BG1520 | agent-a5bcccb1676e852ea | 2026-11-18 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | ba3ada594edfc560 at af624011cc7d |
| US1293 | agent-a1883eb80cca44314 | 2026-11-18 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 1 | ca934d22a9d0fdc4 at ad6e730e8c70 |
| BG1579 | agent-ae9d2789730bc5c77 | 2026-11-18 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | 0441b9094c94fefd at d45984d26ca5 |
| BG1580 | agent-ae9d2789730bc5c77 | 2026-11-18 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 1 | 1a3390a782ace836 at d45984d26ca5 |
| US1313 | agent-af36c11ffbc879c26 | 2026-11-18 | TRUE 22, FALSE 0, UNVERIFIABLE 1 | killed 11, survived 4 | 8257364d70e2fb0e at 4ed7d225516c |
| BG1586 | agent-a9d7ae4ddac135dd5 | 2026-11-18 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 3 | 89a316a6904427d8 at 9925e144c49e |
| US1321 | Dani Okafor (engineering) | 2026-11-18 | TRUE 26, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 1 | c3c0a276808202f6 at 42fc6eb5dd31 |
| US1316 | agent-a7cf0178c200b9e9b | 2026-11-18 | TRUE 29, FALSE 0, UNVERIFIABLE 0 | killed 20, survived 1 | c705af597cb91a5f at fd0f3357d2e4 |
| US1317 | agent-adf464901f9fa8e86 | 2026-11-18 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 45, survived 1 | 78998838835940d3 at fbdb7b10ea2a |
| US1321 | agent-a8e45ac39c9be34f6 | 2026-11-18 | TRUE 33, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 1 | 3795437481d75113 at f1454a8436c4 |
| US1316 | agent-a77dab0c350fa2fb0 | 2026-11-18 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 21, survived 3 | e556b21a63595994 at 3efaa33a27b5 |
| US1318 | agent-a93e747b84dcf86c1 | 2026-11-18 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | killed 21, survived 1 | a032f2aa09b18f32 at fbcd29836829 |
| US1315 | agent-ada1ca22b1cf79021 | 2026-11-18 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 355bc3a9c5981bfa at 3b7af36260df |
| US1319 | agent-ada1ca22b1cf79021 | 2026-11-18 | TRUE 12, FALSE 0, UNVERIFIABLE 1 | killed 14, survived 0 | b3f3ef45674cba75 at 3b7af36260df |
| US1320 | agent-ada1ca22b1cf79021 | 2026-11-18 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 18, survived 0 | a168833d2dcf7a7d at 3b7af36260df |
| US1320 | agent-a9b3b498ad672b0eb | 2026-11-18 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 27, survived 0 | 3cf5de6688a6f52a at bcf94ac3f1fc |
| BG1599 | agent-a97495638d9589aea | 2026-11-18 | TRUE 24, FALSE 0, UNVERIFIABLE 1 | killed 17, survived 0 | 0b44fd8ea691652e at ae7d826f3f40 |
| US1236 | Dani Okafor (engineering) | 2026-11-19 | TRUE 16, FALSE 0, UNVERIFIABLE 1 | killed 16, survived 2 | 2f54643a461c4cfe at ff6ceac9ed47 |
| US1237 | Dani Okafor (engineering) | 2026-11-19 | TRUE 11, FALSE 0, UNVERIFIABLE 2 | killed 12, survived 0 | 0b221e8f29c6732a at ff6ceac9ed47 |
| US1238 | Dani Okafor (engineering) | 2026-11-19 | TRUE 33, FALSE 0, UNVERIFIABLE 1 | killed 19, survived 0 | c3ccaee2c783ccbd at ff6ceac9ed47 |
| US1200 | Dani Okafor (engineering) | 2026-11-19 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 1 | 12ae345a05fba384 at 401cc46459b1 |
| BG1605 | Dani Okafor (engineering) | 2026-11-19 | TRUE 12, FALSE 0, UNVERIFIABLE 1 | killed 7, survived 1 | c42692bc2d55aecb at 77980b8a365e |
| BG1607 | Dani Okafor (engineering) | 2026-11-19 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | b584bea4b33e8021 at 77980b8a365e |
| US1195 | Dani Okafor (engineering) | 2026-11-19 | TRUE 13, FALSE 0, UNVERIFIABLE 1 | killed 12, survived 0 | 6e398b362db59280 at 77980b8a365e |
| US1192 | Dani Okafor (engineering) | 2026-11-19 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 031ca32e833b9db5 at e61656dac065 |
| US1193 | Dani Okafor (engineering) | 2026-11-19 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 1 | a144d279d397a627 at e61656dac065 |
| US1238 | Dani Okafor (engineering) | 2026-11-19 | TRUE 26, FALSE 0, UNVERIFIABLE 1 | killed 9, survived 4 | 9e72f93a9ae1ebce at 89adc9d56fac |
| US1196 | Dani Okafor (engineering) | 2026-11-19 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | f6d817e8e22eadfd at ca56672c0369 |
| US1197 | Dani Okafor (engineering) | 2026-11-19 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 760bafe8003fe58f at ca56672c0369 |
| US1198 | Dani Okafor (engineering) | 2026-11-19 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 871212997bd0bc59 at ca56672c0369 |
| US1192 | Dani Okafor (engineering) | 2026-11-19 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 3 | b402d1f95fcc7825 at ca56672c0369 |
| US1201 | Dani Okafor (engineering) | 2026-11-19 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | cebdae42721f33dd at 83262e4ec591 |
| US1202 | Dani Okafor (engineering) | 2026-11-19 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 49768f9431910e9d at 83262e4ec591 |
| BG1622 | Dani Okafor (engineering) | 2026-11-19 | TRUE 16, FALSE 0, UNVERIFIABLE 2 | killed 6, survived 2 | d6be251e018f1c40 at 83262e4ec591 |
| US1196 | Dani Okafor (engineering) | 2026-11-19 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | bbca909403497e20 at 181dcb1c47ac |
| US1197 | Dani Okafor (engineering) | 2026-11-19 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 3d31f4c0d201fe8d at 181dcb1c47ac |
| US1198 | Dani Okafor (engineering) | 2026-11-19 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 5bab1af9c4fbe8f0 at 181dcb1c47ac |
| US1201 | Dani Okafor (engineering) | 2026-11-19 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | dc05af0a05b280fe at b77dd50e5bfb |
| US1202 | Dani Okafor (engineering) | 2026-11-19 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 76d6a477c47a1c06 at b77dd50e5bfb |
| BG1525 | Dani Okafor (engineering) | 2026-11-19 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | f1b7454fae8eac7a at 6d3cd7e6d36c |
| BG1526 | Dani Okafor (engineering) | 2026-11-19 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 316324acd87812b8 at 6d3cd7e6d36c |
| BG1516 | Dani Okafor (engineering) | 2026-11-19 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 180eab19ca6decfb at 6d3cd7e6d36c |
| BG1517 | Dani Okafor (engineering) | 2026-11-19 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 9043881656e2780b at 6d3cd7e6d36c |
| BG1529 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | f39ade0aae07b9cc at 6d3cd7e6d36c |
| BG1530 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | d050101ba085ab10 at 6d3cd7e6d36c |
| BG1531 | Dani Okafor (engineering) | 2026-11-19 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 3cb35192241c49d3 at 6d3cd7e6d36c |
| BG1533 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 5aca4c149ef08720 at 6d3cd7e6d36c |
| BG1527 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 30174c6f419afe31 at 6d3cd7e6d36c |
| BG1528 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 09d1d5b7a02eb96b at 6d3cd7e6d36c |
| BG1162 | Dani Okafor (engineering) | 2026-11-19 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | 8af757ddd94c27c1 at 6d3cd7e6d36c |
| BG1168 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 1 | c224eef3366e1642 at 6d3cd7e6d36c |
| BG1180 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | e567f39a7a407ad3 at 6d3cd7e6d36c |
| BG1553 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | e97dd97e101a1d9d at 6d3cd7e6d36c |
| BG1554 | Dani Okafor (engineering) | 2026-11-19 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 4c0482179099a58d at 6d3cd7e6d36c |
| BG1555 | Dani Okafor (engineering) | 2026-11-19 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | cfc62fe85694215a at 6d3cd7e6d36c |
| BG1543 | Dani Okafor (engineering) | 2026-11-19 | TRUE 17, FALSE 0, UNVERIFIABLE 1 | killed 14, survived 0 | 7f08579f46dd93b0 at 2c4dfa8ae9e9 |
| BG1546 | Dani Okafor (engineering) | 2026-11-19 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | 8e393e9d68b398be at 2c4dfa8ae9e9 |
| BG1547 | Dani Okafor (engineering) | 2026-11-19 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 7fa8f78e179e7fc0 at 2c4dfa8ae9e9 |
| US1296 | Dani Okafor (engineering) | 2026-11-19 | TRUE 14, FALSE 0, UNVERIFIABLE 3 | killed 12, survived 0 | 6cdd49e509e6cef7 at 2c4dfa8ae9e9 |
| BG1631 | Dani Okafor (engineering) | 2026-11-19 | TRUE 8, FALSE 0, UNVERIFIABLE 1 | killed 4, survived 1 | 8284971beee08eab at 2c4dfa8ae9e9 |
| BG1632 | Dani Okafor (engineering) | 2026-11-19 | TRUE 9, FALSE 0, UNVERIFIABLE 1 | killed 5, survived 1 | 993e0482c657c4f5 at 2c4dfa8ae9e9 |
| US1297 | Dani Okafor (engineering) | 2026-11-19 | TRUE 46, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 1 | 81de81b7630aa24a at 2c4dfa8ae9e9 |
| US1298 | Dani Okafor (engineering) | 2026-11-19 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 23cc55568d40cf79 at 2c4dfa8ae9e9 |
| BG1633 | Dani Okafor (engineering) | 2026-11-19 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 1 | e0b94b50a064982f at 2c4dfa8ae9e9 |
| BG1525 | Dani Okafor (engineering) | 2026-11-20 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 6c271795c56fab93 at 44d85d3511ce |
| BG1180 | Dani Okafor (engineering) | 2026-11-20 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | 0851a2141da86530 at 44d85d3511ce |
| BG1553 | Dani Okafor (engineering) | 2026-11-20 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | a9ab29a5d606fdf4 at 44d85d3511ce |
| BG1543 | Dani Okafor (engineering) | 2026-11-20 | TRUE 15, FALSE 0, UNVERIFIABLE 2 | killed 9, survived 2 | defaafa572a74c4f at bda739d427f8 |
| BG1634 | Dani Okafor (engineering) | 2026-11-20 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 1 | 4241948cc86f336b at bda739d427f8 |
| BG1516 | Dani Okafor (engineering) | 2026-11-20 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | 331b81653f8d3c30 at 6aee7a425fe7 |
| BG1517 | Dani Okafor (engineering) | 2026-11-20 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 2b7a9d6fd983dbc3 at 6aee7a425fe7 |
| BG1531 | Dani Okafor (engineering) | 2026-11-20 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | d6eb3e9d76b6c547 at 6aee7a425fe7 |
| BG1096 | Dani Okafor (engineering) | 2026-11-20 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | c7c3cb4f30b7d467 at 6aee7a425fe7 |
| BG1556 | Dani Okafor (engineering) | 2026-11-20 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 7ac734e7d233e500 at 6aee7a425fe7 |
| BG1557 | Dani Okafor (engineering) | 2026-11-20 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | d8a5e3255571290e at 6aee7a425fe7 |
| BG1565 | Dani Okafor (engineering) | 2026-11-20 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | d7c2b5bb4e31c5a2 at 6aee7a425fe7 |
| BG1621 | Dani Okafor (engineering) | 2026-11-20 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 0817acc027c4ae1f at 6aee7a425fe7 |
| US1299 | Dani Okafor (engineering) | 2026-11-20 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 64bb20f412e26afd at 6aee7a425fe7 |
| BG1644 | Dani Okafor (engineering) | 2026-11-20 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 1 | 441a9664f73de599 at 682c34696387 |
| US1299 | Dani Okafor (engineering) | 2026-11-20 | TRUE 15, FALSE 0, UNVERIFIABLE 1 | killed 12, survived 0 | ff4292172598729f at 2aa31057067e |
| BG1647 | Dani Okafor (engineering) | 2026-11-20 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 1 | 619c9c755f3085bf at 4571566966d7 |
| BG1015 | Dani Okafor (engineering) | 2026-11-20 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | e41aab3430c908c5 at 475820d79bbd |
| BG1472 | Dani Okafor (engineering) | 2026-11-20 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | d9b349a0de187c34 at 475820d79bbd |
| BG1536 | Dani Okafor (engineering) | 2026-11-20 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 851a5b5d55d18282 at 475820d79bbd |
| US1039 | Dani Okafor (engineering) | 2026-11-20 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | 02ac284d2c34c768 at a011a415bb36 |
| US1046 | Dani Okafor (engineering) | 2026-11-20 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | c07ac0aa33c10e03 at a011a415bb36 |
| BG1535 | Dani Okafor (engineering) | 2026-11-20 | TRUE 5, FALSE 0, UNVERIFIABLE 1 | killed 6, survived 0 | 8a8667e20507b099 at a011a415bb36 |
| BG1002 | Dani Okafor (engineering) | 2026-11-20 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 7336d8faad0ebb68 at a011a415bb36 |
| US1036 | Dani Okafor (engineering) | 2026-11-20 | TRUE 21, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | 1ebd0548497ba370 at b4bd2392c11c |
| US1052 | Dani Okafor (engineering) | 2026-11-20 | TRUE 20, FALSE 0, UNVERIFIABLE 2 | killed 17, survived 0 | ed1b551ad3866656 at ff97be63c73c |
| BG1655 | Dani Okafor (engineering) | 2026-11-20 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 33194c0a9ece2d5e at ff97be63c73c |
| US1040 | Dani Okafor (engineering) | 2026-11-20 | TRUE 20, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 0 | 1a28dc73fc21b617 at 96f53a41ff7a |
| US1054 | Dani Okafor (engineering) | 2026-11-20 | TRUE 22, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 1 | b86d6f012df25132 at c6af0e052df1 |
| US1053 | Dani Okafor (engineering) | 2026-11-20 | TRUE 23, FALSE 0, UNVERIFIABLE 1 | killed 19, survived 0 | 1aaf574951b64b09 at 850b1c4d9ba5 |
| BG1655 | Dani Okafor (engineering) | 2026-11-20 | TRUE 15, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 0e3d600e0794a5d9 at cfb2a4fd028f |
| BG1660 | Dani Okafor (engineering) | 2026-11-20 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 35bb08c56aea9842 at b730b6c7fefa |
| BG1663 | Dani Okafor (engineering) | 2026-11-20 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 5be8757e3fca42c4 at 28b067c9435e |
| US1055 | Dani Okafor (engineering) | 2026-11-20 | TRUE 37, FALSE 0, UNVERIFIABLE 0 | killed 26, survived 0 | 1d85697b740c816e at b30aa99954cb |
| US1055 | Dani Okafor (engineering) | 2026-11-20 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | cbe5a62d7f6f0cc5 at 1f3047e3e65a |
| US1322 | Dani Okafor (engineering) | 2026-11-20 | TRUE 9, FALSE 0, UNVERIFIABLE 1 | killed 14, survived 0 | b60d21a0071716f0 at 63f0e65c51b8 |
| US1056 | Dani Okafor (engineering) | 2026-11-20 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | b2dfb8a45637675b at 63f0e65c51b8 |
| US1057 | Dani Okafor (engineering) | 2026-11-20 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 1 | daf1adf53dc090a1 at 63f0e65c51b8 |
| BG1664 | Dani Okafor (engineering) | 2026-11-20 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 1cdd0af865dce281 at 63f0e65c51b8 |
| US1056 | Dani Okafor (engineering) | 2026-11-20 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 1 | 3dae756577b19995 at 95eb3f92b338 |
| US1057 | Dani Okafor (engineering) | 2026-11-20 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 25, survived 0 | 62c23ef3344f7fe5 at 95eb3f92b338 |
| US1322 | Dani Okafor (engineering) | 2026-11-20 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 8f2f97d89e6c3b53 at 95eb3f92b338 |
| BG0961 | Dani Okafor (engineering) | 2026-11-21 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 62e654e9dacaea66 at a01317169922 |
| BG1023 | Dani Okafor (engineering) | 2026-11-21 | TRUE 16, FALSE 0, UNVERIFIABLE 1 | killed 13, survived 0 | 987045401bf1d626 at a01317169922 |
| BG1534 | Dani Okafor (engineering) | 2026-11-21 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 1 | 5424164a42e931e8 at a01317169922 |
| BG0985 | Dani Okafor (engineering) | 2026-11-21 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | b7e474998f7972e8 at 74436b8b3190 |
| BG1021 | Dani Okafor (engineering) | 2026-11-21 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 881328451ebaf413 at 74436b8b3190 |
| BG1051 | Dani Okafor (engineering) | 2026-11-21 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 965f5b282d569577 at 74436b8b3190 |
| BG1058 | Dani Okafor (engineering) | 2026-11-21 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 2ec2c803d9ac4ad9 at 74436b8b3190 |
| BG1107 | Dani Okafor (engineering) | 2026-11-21 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | 9a6e670655f4201b at 74436b8b3190 |
| BG1582 | Dani Okafor (engineering) | 2026-11-21 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 0b78a22adb71a84d at 74436b8b3190 |
| BG1590 | Dani Okafor (engineering) | 2026-11-21 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 2c7deb5ed3bc893d at 74436b8b3190 |
| BG0954 | Dani Okafor (engineering) | 2026-11-21 | TRUE 19, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 3cf2b370a0dd93bf at 41bdc7b0fe04 |
| BG0956 | Dani Okafor (engineering) | 2026-11-21 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 1 | b9592a588798eb87 at 41bdc7b0fe04 |
| BG1399 | Dani Okafor (engineering) | 2026-11-21 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 9cdec9edc04dc817 at 09cf0766d830 |
| BG1409 | Dani Okafor (engineering) | 2026-11-21 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 1b776c7b68c91878 at 09cf0766d830 |
| BG1413 | Dani Okafor (engineering) | 2026-11-21 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 0a25354548f1ca2f at 09cf0766d830 |
| BG1610 | Dani Okafor (engineering) | 2026-11-21 | TRUE 6, FALSE 0, UNVERIFIABLE 1 | killed 3, survived 0 | 702bedea5d75c9d8 at 09cf0766d830 |
| BG1614 | Dani Okafor (engineering) | 2026-11-21 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 10758bf0acfbf78c at 09cf0766d830 |
| BG1624 | Dani Okafor (engineering) | 2026-11-21 | TRUE 7, FALSE 0, UNVERIFIABLE 1 | killed 5, survived 0 | d2ed73ffc13d74a4 at 09cf0766d830 |
| BG1627 | Dani Okafor (engineering) | 2026-11-21 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | d0dc6cd70d031d5c at 09cf0766d830 |
| BG0961 | Dani Okafor (engineering) | 2026-11-21 | TRUE 16, FALSE 0, UNVERIFIABLE 1 | killed 15, survived 0 | 6eced398b617b329 at 67d57b454cf6 |
| BG1023 | Dani Okafor (engineering) | 2026-11-21 | TRUE 12, FALSE 0, UNVERIFIABLE 2 | killed 11, survived 0 | 1d6ec836a904d608 at 67d57b454cf6 |
| BG1534 | Dani Okafor (engineering) | 2026-11-21 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 30244e87ae217020 at 67d57b454cf6 |
| BG0954 | Dani Okafor (engineering) | 2026-11-21 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 16, survived 0 | da160f19d3d160b2 at ef61967bb60f |
| BG0956 | Dani Okafor (engineering) | 2026-11-21 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 1 | f7fa3cbf801cd1e9 at ef61967bb60f |
| BG0983 | Dani Okafor (engineering) | 2026-11-21 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | d206a3e1357abfbb at ef30c7b14e4d |
| BG0987 | Dani Okafor (engineering) | 2026-11-21 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 9aca0100be9d6593 at ef30c7b14e4d |
| BG1609 | Dani Okafor (engineering) | 2026-11-21 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | c9539ce682c9706b at ef30c7b14e4d |
| BG0981 | Dani Okafor (engineering) | 2026-11-21 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | 3a1e3f1fe4f66ea5 at ef30c7b14e4d |
| BG0961 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 1 | killed 6, survived 0 | 6da42a3fe78ce4fc at f03ef4b45a93 |
| BG1023 | Dani Okafor (engineering) | 2026-11-21 | TRUE 5, FALSE 0, UNVERIFIABLE 1 | killed 4, survived 0 | 8305183fc9776df8 at f03ef4b45a93 |
| BG1534 | Dani Okafor (engineering) | 2026-11-21 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 1 | a87f497acd498058 at f03ef4b45a93 |
| BG0985 | Dani Okafor (engineering) | 2026-11-21 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 3b6f98b3c9ce79f5 at b8839c73d8b0 |
| BG1107 | Dani Okafor (engineering) | 2026-11-21 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 1dfeeaca46821c55 at b8839c73d8b0 |
| BG1582 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 8942ffb7cb0e91e3 at b8839c73d8b0 |
| BG1590 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 1 | killed 6, survived 0 | aefe15be397342ba at b8839c73d8b0 |
| BG1399 | Dani Okafor (engineering) | 2026-11-21 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | d63cedae9777d7fc at 7982a8fd8840 |
| BG1409 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | efa3b8770d248971 at 7982a8fd8840 |
| BG1610 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | f249a53bf4de8a2b at 7982a8fd8840 |
| BG1614 | Dani Okafor (engineering) | 2026-11-21 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 4547f2c80bfb3e29 at 7982a8fd8840 |
| BG1624 | Dani Okafor (engineering) | 2026-11-21 | TRUE 5, FALSE 0, UNVERIFIABLE 1 | killed 4, survived 0 | c4376889141df9d2 at 7982a8fd8840 |
| BG1627 | Dani Okafor (engineering) | 2026-11-21 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 5bb647ed262cfb13 at 7982a8fd8840 |
| BG0954 | Dani Okafor (engineering) | 2026-11-21 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 3152b82fed565267 at ed47dfd49318 |
| BG0956 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 1 | killed 6, survived 1 | dbd9f8286c3c8d9d at ed47dfd49318 |
| BG1470 | Dani Okafor (engineering) | 2026-11-21 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 20, survived 1 | 39a301b81b443ab3 at ed47dfd49318 |
| BG0983 | Dani Okafor (engineering) | 2026-11-21 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 1 | 3bdf6d7d6498db6b at 97530826c479 |
| BG0987 | Dani Okafor (engineering) | 2026-11-21 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 8135a3f500fdff89 at 97530826c479 |
| BG1609 | Dani Okafor (engineering) | 2026-11-21 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | bcc612c87869f627 at 97530826c479 |
| BG0981 | Dani Okafor (engineering) | 2026-11-21 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | 6c06bafb9ca54acc at 97530826c479 |
| BG1107 | Dani Okafor (engineering) | 2026-11-21 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 5029aedebd1a932f at 97530826c479 |
| BG1470 | Dani Okafor (engineering) | 2026-11-21 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 1 | 973614df2d2a2c04 at c70b799ef175 |
| BG1399 | Dani Okafor (engineering) | 2026-11-21 | TRUE 14, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 65dd087828a89019 at d608c8779053 |
| BG1409 | Dani Okafor (engineering) | 2026-11-21 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 5a819fc3d3395eff at d608c8779053 |
| BG1614 | Dani Okafor (engineering) | 2026-11-21 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 1 | a22fe933b9037e64 at d608c8779053 |
| BG1624 | Dani Okafor (engineering) | 2026-11-21 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 0b52653fc82a8dad at d608c8779053 |
| BG1627 | Dani Okafor (engineering) | 2026-11-21 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 2, survived 0 | 49faef8690fa9703 at d608c8779053 |
| BG1609 | Dani Okafor (engineering) | 2026-11-21 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 55cc78cf022fbece at ef108745050d |
| BG1470 | Dani Okafor (engineering) | 2026-11-21 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 1 | e44c5d14076b49dd at cd58d123954e |
| BG1400 | Dani Okafor (engineering) | 2026-11-21 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 2, survived 0 | a6cfbf00caee11ed at b1d2369353ed |
| BG1406 | Dani Okafor (engineering) | 2026-11-21 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 2, survived 0 | 794c4c9d480162ff at b1d2369353ed |
| BG1448 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | f27ee8ddd28eb2ee at b1d2369353ed |
| BG1477 | Dani Okafor (engineering) | 2026-11-21 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 2, survived 0 | 6cee2d80bec35093 at b1d2369353ed |
| BG1491 | Dani Okafor (engineering) | 2026-11-21 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 07ba6431d3a8add9 at b1d2369353ed |
| BG1512 | Dani Okafor (engineering) | 2026-11-21 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 6eb3fac46a7de988 at b1d2369353ed |
| BG1539 | Dani Okafor (engineering) | 2026-11-21 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | 7b4e00a12e1cb10c at b1d2369353ed |
| BG1629 | Dani Okafor (engineering) | 2026-11-21 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 1a3dcdb3ace2612b at b1d2369353ed |
| BG1406 | Dani Okafor (engineering) | 2026-11-21 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 1 | fcf7d0e311d0b7f8 at b12e9b3e84d5 |
| BG1448 | Dani Okafor (engineering) | 2026-11-21 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 17, survived 0 | e0846809b724f062 at b12e9b3e84d5 |
| BG1512 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 0 | d43a7373781545b1 at b12e9b3e84d5 |
| BG1539 | Dani Okafor (engineering) | 2026-11-21 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 16, survived 0 | 9753b7f27fbb0000 at b12e9b3e84d5 |
| BG1477 | Dani Okafor (engineering) | 2026-11-21 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 1 | 95b822c0448f1018 at 77bcc66d0e02 |
| BG1629 | Dani Okafor (engineering) | 2026-11-21 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 1 | 68c9ef76cfae3776 at 77bcc66d0e02 |
| BG1400 | Dani Okafor (engineering) | 2026-11-21 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 1 | c87b975103b32698 at 77bcc66d0e02 |
| BG1491 | Dani Okafor (engineering) | 2026-11-21 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 221958b9a4608421 at 77bcc66d0e02 |
| BG1477 | Dani Okafor (engineering) | 2026-11-22 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | d8a53f2f8cd76cd1 at beaf119a5443 |
| BG1534 | Dani Okafor (engineering) | 2026-11-22 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 30, survived 1 | dbbf0a2f4e98cd01 at 663edcd12fc0 |
| BG1578 | Dani Okafor (engineering) | 2026-11-22 | TRUE 14, FALSE 0, UNVERIFIABLE 1 | killed 26, survived 1 | 814007e8aa76a1d6 at 663edcd12fc0 |
| BG0970 | Dani Okafor (engineering) | 2026-11-22 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 15, survived 0 | 6fd878c1f009b5e8 at b2f83d8b2ece |
| BG0982 | Dani Okafor (engineering) | 2026-11-22 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 9, survived 1 | 4d68f2be308072b5 at b2f83d8b2ece |
| BG0999 | Dani Okafor (engineering) | 2026-11-22 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | bf2c8d64ae6863fa at b2f83d8b2ece |
| BG1050 | Dani Okafor (engineering) | 2026-11-22 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 1 | 582e18b8cf00c9e1 at b2f83d8b2ece |
| BG1108 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 12, survived 0 | 6ce1efeee0776f83 at b2f83d8b2ece |
| BG1120 | Dani Okafor (engineering) | 2026-11-22 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 16b578f8906ba2cb at b2f83d8b2ece |
| BG1124 | Dani Okafor (engineering) | 2026-11-22 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | db2561424f0593c2 at b2f83d8b2ece |
| BG1475 | Dani Okafor (engineering) | 2026-11-22 | TRUE 17, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | 7341319c90e81f00 at 8560c0b0cddf |
| BG1623 | Dani Okafor (engineering) | 2026-11-22 | TRUE 15, FALSE 0, UNVERIFIABLE 1 | killed 18, survived 0 | a6f5c1495e23ae3e at 8560c0b0cddf |
| BG1626 | Dani Okafor (engineering) | 2026-11-22 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 25361458e50557b9 at 8560c0b0cddf |
| BG1059 | Dani Okafor (engineering) | 2026-11-22 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 045f92e719c8149a at 4d46f94e7b20 |
| BG1060 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 00a727ab3d47a27d at 4d46f94e7b20 |
| BG1332 | Dani Okafor (engineering) | 2026-11-22 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 14, survived 0 | c1c3c01d237fe56c at 4d46f94e7b20 |
| BG1436 | Dani Okafor (engineering) | 2026-11-22 | TRUE 9, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 6c68ba58dae24587 at 4d46f94e7b20 |
| BG1463 | Dani Okafor (engineering) | 2026-11-22 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | e9f2fa4caca73156 at 4d46f94e7b20 |
| BG1465 | Dani Okafor (engineering) | 2026-11-22 | TRUE 4, FALSE 0, UNVERIFIABLE 1 | killed 5, survived 0 | 292abce340219385 at 4d46f94e7b20 |
| BG1482 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | 21d6ea4b4b94870c at 4d46f94e7b20 |
| BG1483 | Dani Okafor (engineering) | 2026-11-22 | TRUE 9, FALSE 0, UNVERIFIABLE 1 | killed 13, survived 0 | 62b4a032eca62521 at 4d46f94e7b20 |
| BG1534 | Dani Okafor (engineering) | 2026-11-22 | TRUE 22, FALSE 0, UNVERIFIABLE 0 | killed 19, survived 0 | 5d5c33e6b4dcb435 at 97c0b4ca482f |
| BG1578 | Dani Okafor (engineering) | 2026-11-22 | TRUE 18, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 7a707a08b95bf8f8 at 97c0b4ca482f |
| BG0970 | Dani Okafor (engineering) | 2026-11-22 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 11, survived 0 | 0f8500b38161c5f6 at ac68018d4917 |
| BG0982 | Dani Okafor (engineering) | 2026-11-22 | TRUE 10, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | 8c5071a02dc55a42 at ac68018d4917 |
| BG0999 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 6, survived 0 | 47139e370c7cc2f5 at ac68018d4917 |
| BG1108 | Dani Okafor (engineering) | 2026-11-22 | TRUE 8, FALSE 0, UNVERIFIABLE 0 | killed 5, survived 0 | c9cfb80f7c13dc0e at ac68018d4917 |
| BG1120 | Dani Okafor (engineering) | 2026-11-22 | TRUE 9, FALSE 0, UNVERIFIABLE 1 | killed 10, survived 0 | c685af6e8c5b9130 at ac68018d4917 |
| BG1124 | Dani Okafor (engineering) | 2026-11-22 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 0 | df6bfe49ac452e0d at ac68018d4917 |
| BG1475 | Dani Okafor (engineering) | 2026-11-22 | TRUE 16, FALSE 0, UNVERIFIABLE 0 | killed 23, survived 0 | d1241d48fc863542 at 0bf381f8459b |
| BG1623 | Dani Okafor (engineering) | 2026-11-22 | TRUE 11, FALSE 0, UNVERIFIABLE 0 | killed 20, survived 0 | c0dbf3aec867c887 at 0bf381f8459b |
| BG1626 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | d29065f683f3010d at 0bf381f8459b |
| BG1534 | Dani Okafor (engineering) | 2026-11-22 | TRUE 22, FALSE 0, UNVERIFIABLE 0 | killed 8, survived 0 | 0ae7d1edab9f2f49 at ac5f808c75ac |
| BG1059 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | ead0c03c7038ded6 at 1736835cd317 |
| BG1060 | Dani Okafor (engineering) | 2026-11-22 | TRUE 3, FALSE 0, UNVERIFIABLE 0 | killed 7, survived 0 | 13d23c828693087d at 1736835cd317 |
| BG1332 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 18, survived 0 | 3f48e2a7d9b84e23 at 1736835cd317 |
| BG1436 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | 86ae4afc771f02f6 at 1736835cd317 |
| BG1463 | Dani Okafor (engineering) | 2026-11-22 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 10, survived 0 | a3a32851624941aa at 1736835cd317 |
| BG1465 | Dani Okafor (engineering) | 2026-11-22 | TRUE 6, FALSE 0, UNVERIFIABLE 2 | killed 7, survived 0 | 98f806804c3dfc26 at 1736835cd317 |
| BG1482 | Dani Okafor (engineering) | 2026-11-22 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 5b90e7484bd9a679 at 1736835cd317 |
| BG1483 | Dani Okafor (engineering) | 2026-11-22 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 16, survived 0 | 884516f62f8beb27 at 1736835cd317 |
| BG1475 | Dani Okafor (engineering) | 2026-11-22 | TRUE 24, FALSE 0, UNVERIFIABLE 0 | killed 31, survived 0 | 035e9c245c791708 at 27155e5b4632 |
| BG0999 | Dani Okafor (engineering) | 2026-11-22 | TRUE 5, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 1662acbf9c51ef53 at 249fecd288b0 |
| BG1108 | Dani Okafor (engineering) | 2026-11-22 | TRUE 4, FALSE 0, UNVERIFIABLE 0 | killed 3, survived 1 | cc700bc4f4d2d555 at 249fecd288b0 |
| BG1120 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 1 | killed 6, survived 0 | 19e78ed1c7d227fa at 249fecd288b0 |
| BG1463 | Dani Okafor (engineering) | 2026-11-22 | TRUE 7, FALSE 0, UNVERIFIABLE 0 | killed 4, survived 0 | 4789d2c21a6045ed at dfe94480fc55 |
| BG1482 | Dani Okafor (engineering) | 2026-11-22 | TRUE 6, FALSE 0, UNVERIFIABLE 0 | killed 2, survived 0 | e8932ab3662c168c at dfe94480fc55 |
| BG1483 | Dani Okafor (engineering) | 2026-11-22 | TRUE 6, FALSE 0, UNVERIFIABLE 1 | killed 3, survived 0 | fed332692634baf5 at dfe94480fc55 |
| BG1012 | Dani Okafor (engineering) | 2026-11-22 | TRUE 13, FALSE 0, UNVERIFIABLE 0 | killed 13, survived 0 | ddf73240f41c0fce at e80af2d5d875 |
| BG1532 | Dani Okafor (engineering) | 2026-11-22 | TRUE 12, FALSE 0, UNVERIFIABLE 0 | killed 27, survived 0 | cd33814f6c8f8391 at e80af2d5d875 |
