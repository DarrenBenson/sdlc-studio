# RETRO-0135: Rowan's push is judged on a configured gate host, and the gate's documents and weekly run tell the truth

> **Date:** 2026-10-20
> **Run:** RUN-01M59TRM
> **Batch:** US1079, BG1066, US1075, US1077, US1078, BG1061, US1084, US1085, BG1054

## Keep

- The gate host carried every push: each was judged on devserver1 against exactly the commit pushed, in about ten minutes, and the three it refused (US1076's interrupt regression, US1084's bare hook call and its unattributed module) were real defects stopped before main.
- `tools/run-suite.sh all` ran on the host live, against the working tree: GREEN with 8157 passed, `--check` accepted it, and the waiting line named the push holding the lock (US1076, US1078).
- QA seats mutated the author's tests, not only the code, with paraphrases, swapped clauses and a negation elsewhere in a sentence. Every survivor they found was a real gap the author's own mutants could not show.
- Building in a side worktree while a push held the main tree kept delivery moving without writing a tracked file under a running hook.

## Stop

- Briefing a review before running the reviewer's own pass: first-review approval fell to 1 of 10 units, against 9 of 19 the run before, and two units hit the cap (US1076 as BG1078, US1086 as BG1095).
- Repairing the instances a reviewer names instead of the class: US1086's fall-back check grew its phrase list and failed round 2 on the same class, and US1084, BG1061 and US1085 each widened a pattern only to the examples quoted.
- Calling a failure a load flake before reproducing it: BG1077 was US1076's background launch ignoring SIGINT.
- Pushing without the full tools suite: US1084's first push went red on two guards a local run would have shown.

## Try

- [LC-018] Before every brief, run a claim inventory of the commit message and changelog against the code, and drop any absolute that no test proves ("however worded", "each closed").
- Before every brief, mutate my own tests as the QA seat does, with paraphrases, swapped clauses and a negation elsewhere in the sentence, and repair a finding by testing its class with wordings the reviewer did not give (CR0650).
- Write a documentation unit's criteria against structured content a test can compare exactly, such as a table cell's set read from the source, never as a negative claim about prose.

## Known issues carried

| id | ruling | ruled by | date |
| --- | --- | --- | --- |
| BG1070 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1071 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1072 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1073 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1074 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1075 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1076 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1078 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1079 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1080 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1081 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1082 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1083 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1084 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1085 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1086 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1087 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1088 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1089 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1090 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1091 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1092 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1093 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1094 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1095 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1096 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1097 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1098 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| CR0650 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1100 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1101 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
| BG1102 | not-stop-ship | Darren Benson (operator) | 2026-10-20 |
