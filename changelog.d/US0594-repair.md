<!-- section: Fixed -->
- **The tick check was inert for every story, and reported a pass over nothing.** It read only
  `- [x]` checkboxes - the BUG convention - while a story's claim is a `- **Verified:** yes`
  stamp under an `### ACn` heading. Measured over the corpus: 0 of 651 story files yielded a
  criterion it could see, including the unit whose two false ticks are the rationale this row
  cites. It reads both conventions now (625 of 651), and a run in which it examined NO ticks is
  reported outstanding rather than supported - a pass over an empty set is not a pass, and it is
  how the row read green across a whole batch while understanding one of the two conventions its
  corpus is written in.
