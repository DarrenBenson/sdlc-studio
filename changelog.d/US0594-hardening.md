<!-- section: Fixed -->
- **The diff source behind the tick check is exercised against real git, and a ref cannot make
  git write a file.** `_changed_paths` was mocked in every test that reached it, so four mutants
  survived the whole suite - each turning "cannot look" into "nothing changed", which the row
  reads as every tick contradicted. It is now driven against a real repository, and its failure
  paths answer None rather than an empty set, which are opposite verdicts one layer up. The base
  ref was interpolated into a single argv token: `--output=<path>` was parsed by git as an
  OPTION, wrote that file, exited 0 and returned an empty diff. The ref is verified with
  `rev-parse` first and the diff arguments are terminated with `--`.
- **A checklist row's WINDOW is drift-checked like its command.** The resolvability assertion sat
  behind a guard that was permanently empty, so a window naming a verb nothing exposes passed
  every test. `cycle_drift` walks windows on the same terms as commands now.
