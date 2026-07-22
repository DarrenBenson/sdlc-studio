"""The close-owed detector: is a sprint close owed right now?

The load-bearing cases are not "no retros at all" - they are the partial ones a real project
hits: a terminal unit some retro DID account for (covered, not owed), the historical tail a
baseline forgives (grandfathered, not owed), and the one that matters - a unit closed AFTER
adoption that no retro names (owed, and must be caught). A detector that only fired on an empty
project would never fire in practice, because the failure mode is shipping Done work and skipping
the retro, not omitting the work.
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import close_owed  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _story(root: Path, sid: str, status: str) -> None:
    _write(root / "sdlc-studio" / "stories" / f"{sid}-s.md",
           f"# {sid}: A story\n\n> **Status:** {status}\n> **Epic:** EP0100\n> **Points:** 2\n")


def _bug(root: Path, bid: str, status: str) -> None:
    _write(root / "sdlc-studio" / "bugs" / f"{bid}-b.md",
           f"# {bid}: A bug\n\n> **Status:** {status}\n> **Points:** 2\n")


def _retro(root: Path, rid: str, batch: str) -> None:
    _write(root / "sdlc-studio" / "retros" / f"{rid}-r.md",
           f"# RETRO-{rid[5:]}: a sprint\n\n> **Batch:** {batch}\n\n## Delivered\n- shipped\n")


class CloseOwedBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)


class UnbaselinedTests(CloseOwedBase):
    def test_unbaselined_reports_every_uncovered_terminal_unit(self) -> None:
        _story(self.root, "US0001", "Done")
        _bug(self.root, "BG0001", "Fixed")
        report = close_owed.owed(self.root)
        self.assertFalse(report["baselined"])
        ids = {cid for cid, _ in report["owed"]}
        self.assertEqual(ids, {"US0001", "BG0001"})

    def test_non_terminal_units_are_never_owed(self) -> None:
        _story(self.root, "US0001", "In Progress")
        _story(self.root, "US0002", "Draft")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])

    def test_detect_exit_zero_when_unbaselined_even_with_uncovered(self) -> None:
        _story(self.root, "US0001", "Done")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = close_owed.main(["--root", str(self.root), "detect", "--format", "json"])
        self.assertEqual(rc, 0)  # unbaselined is a soft state, not a gate failure


def _epic(root: Path, eid: str, status: str) -> None:
    _write(root / "sdlc-studio" / "epics" / f"{eid}-e.md",
           f"# {eid}: An epic\n\n> **Status:** {status}\n> **Derived Point Total:** 4\n")


def _story_in(root: Path, sid: str, status: str, epic: str) -> None:
    _write(root / "sdlc-studio" / "stories" / f"{sid}-s.md",
           f"# {sid}: A story\n\n> **Status:** {status}\n> **Epic:** {epic}\n> **Points:** 2\n")


class CoverageTests(CloseOwedBase):
    def test_a_retro_that_names_the_unit_makes_it_covered(self) -> None:
        _story(self.root, "US0001", "Done")
        _retro(self.root, "RETRO0001", "US0001")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])
        self.assertEqual(close_owed.owed(self.root)["covered"], 1)


class DerivedEpicCoverageTests(CloseOwedBase):
    """BG0210: a clean close manufactured its own close-owed debt, unclearably.

    An epic reaches terminal by DERIVATION - `apply-signoff` closes it once every child is
    terminal, after the retro is written - and nothing adds it to any `Batch`. So the moment a
    sprint closed cleanly, the epics that close had just derived were reported as terminal with
    no retro accounting for them. Closing again could not clear it, because the next close
    derives its own epics in turn. About 38 epics in this repo were in that state, most of the
    reported total, so the headline number was largely false - and a detector reporting a
    permanent, growing, unclearable debt is one people learn to skim past, which is the failure
    it exists to prevent.

    An epic is not accounted for by being NAMED in a batch; it is accounted for when the retro
    accounted for the children whose closure derived it. Adding epics to the `Batch` instead
    would have been the obvious fix and is wrong: `retro accuracy` sums points over the batch,
    and an epic's Derived Point Total is the sum of its stories, so it would double-count every
    sprint's velocity.
    """

    def test_an_epic_whose_children_a_retro_covered_is_covered(self) -> None:
        _epic(self.root, "EP0100", "Done")
        _story_in(self.root, "US0001", "Done", "EP0100")
        _story_in(self.root, "US0002", "Done", "EP0100")
        _retro(self.root, "RETRO0001", "US0001, US0002")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])

    def test_an_epic_with_an_uncovered_child_is_still_owed(self) -> None:
        """The relaxation must not become a blanket exemption for epics."""
        _epic(self.root, "EP0100", "Done")
        _story_in(self.root, "US0001", "Done", "EP0100")
        _story_in(self.root, "US0002", "Done", "EP0100")
        _retro(self.root, "RETRO0001", "US0001")          # US0002 never accounted for
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertIn("EP0100", ids)
        self.assertIn("US0002", ids)

    def test_only_an_epic_inherits_coverage_from_children(self) -> None:
        """The `type_ != "epic"` guard was unpinned by the ENTIRE suite.

        Removing it left all 3,180 tests green, so the one check keeping this relaxation
        from becoming a blanket exemption had no evidence behind it - while the commit
        claimed every branch was mutation-killed by its own test. A story or bug can carry
        children too (a story naming a parent epic is the same shape inverted), and nothing
        asserted they stay owed on their own account.
        """
        # The non-epic must actually HAVE children, all covered - otherwise the childless
        # guard catches it first and the test passes with `type_` removed, which is what
        # the first version of this test did.
        _write(self.root / "sdlc-studio" / "bugs" / "BG0002-p.md",
               "# BG0002: a bug that something calls its parent\n\n"
               "> **Status:** Fixed\n> **Points:** 2\n")
        _story_in(self.root, "US0001", "Done", "BG0002")   # names the BUG as its parent
        _retro(self.root, "RETRO0001", "US0001")           # ...and that child IS covered
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertIn("BG0002", ids,
                      "a bug must be owed on its own account, never by inheriting coverage")

    def test_an_epic_is_owed_when_its_DECLARED_breakdown_holds_an_uncovered_id(self) -> None:
        """Coverage must read children the way the DERIVATION does, or the two disagree.

        `apply-signoff` derives an epic terminal from its declared Story Breakdown; this
        rule read `children_of` (anything naming the epic as parent). An id declared in the
        breakdown but not backed by a file naming that parent was therefore invisible here,
        so the epic could be forgiven off a strict subset of the children its own closure
        was derived from. Both id sets must be covered.
        """
        _write(self.root / "sdlc-studio" / "epics" / "EP0100-e.md",
               "# EP0100: An epic\n\n> **Status:** Done\n> **Derived Point Total:** 4\n\n"
               "## Story Breakdown\n\n- [x] US0001 first\n- [x] US0002 second\n")
        _story_in(self.root, "US0001", "Done", "EP0100")
        # US0002 is declared in the breakdown but does not name EP0100 as its parent.
        _write(self.root / "sdlc-studio" / "stories" / "US0002-s.md",
               "# US0002: A story\n\n> **Status:** Done\n> **Points:** 2\n")
        _retro(self.root, "RETRO0001", "US0001")       # US0002 never accounted for
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertIn("EP0100", ids)

    def test_a_childless_terminal_epic_is_still_owed(self) -> None:
        """No children means nothing derived it, so there is nothing to inherit coverage from.

        Without this an epic with no stories would be silently forgiven by a rule about its
        children - a vacuous pass, the shape this repo keeps filing.
        """
        _epic(self.root, "EP0100", "Done")
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertIn("EP0100", ids)


class DeadBreakdownIdTests(CloseOwedBase):
    """BG0211: an epic owed a close that no close can give.

    The union of `children_of` and the declared Story Breakdown is deliberately strict - it
    cannot forgive more than the narrower rule. But an id in the breakdown with no backing
    file (split, renamed, deleted) or naming a non-delivery artefact (a CR, an RFC) can never
    appear in a retro `Batch`, because a `Batch` names delivery units. So the epic is reported
    as owing a close forever, and every close leaves it owed.

    A permanent unclearable debt is the exact failure BG0210 was filed for. Forgiving it is
    not enough on its own: the dead id is a real defect in the breakdown, so it is REPORTED
    rather than silently dropped. Forgive the unsatisfiable demand, surface the cause.
    """

    def _epic_with_breakdown(self, *ids: str) -> None:
        boxes = "".join(f"- [x] {i} thing\n" for i in ids)
        _write(self.root / "sdlc-studio" / "epics" / "EP0100-e.md",
               "# EP0100: An epic\n\n> **Status:** Done\n> **Derived Point Total:** 4\n\n"
               f"## Story Breakdown\n\n{boxes}")

    def test_a_ghost_id_in_the_breakdown_does_not_owe_forever(self) -> None:
        self._epic_with_breakdown("US0001", "US9999")     # US9999 has no backing file
        _story_in(self.root, "US0001", "Done", "EP0100")
        _retro(self.root, "RETRO0001", "US0001")
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertNotIn("EP0100", ids,
                         "no retro can ever name US9999, so the demand is unsatisfiable")

    def test_a_cr_id_in_the_breakdown_does_not_owe_forever(self) -> None:
        self._epic_with_breakdown("US0001", "CR0001")
        _write(self.root / "sdlc-studio" / "change-requests" / "CR0001-c.md",
               "# CR0001: a request\n\n> **Status:** Complete\n> **Size:** S\n")
        _story_in(self.root, "US0001", "Done", "EP0100")
        _retro(self.root, "RETRO0001", "US0001")
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertNotIn("EP0100", ids, "a CR is a discovery item and never appears in a Batch")

    def test_an_rfc_id_in_the_breakdown_does_not_owe_forever(self) -> None:
        self._epic_with_breakdown("US0001", "RFC0001")
        _write(self.root / "sdlc-studio" / "rfcs" / "RFC0001-r.md",
               "# RFC0001: a design\n\n> **Status:** Accepted\n")
        _story_in(self.root, "US0001", "Done", "EP0100")
        _retro(self.root, "RETRO0001", "US0001")
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertNotIn("EP0100", ids, "an RFC is a discovery item and never appears in a Batch")

    def test_the_dead_id_is_reported_not_silently_forgiven(self) -> None:
        """Forgiving without surfacing would trade a false debt for a hidden defect."""
        self._epic_with_breakdown("US0001", "US9999")
        _story_in(self.root, "US0001", "Done", "EP0100")
        _retro(self.root, "RETRO0001", "US0001")
        report = close_owed.owed(self.root)
        self.assertEqual(report["dead_breakdown_ids"], [["EP0100", "US9999"]])
        self.assertIn("US9999", close_owed.render(report))

    def test_a_LIVE_uncovered_child_still_owes_even_beside_a_dead_id(self) -> None:
        """The relaxation must not become a blanket exemption for any epic with one bad id.

        Without this, adding a single ghost id to a breakdown would forgive an epic whose
        real children are genuinely unaccounted for - a self-service exemption.
        """
        self._epic_with_breakdown("US0001", "US0002", "US9999")
        _story_in(self.root, "US0001", "Done", "EP0100")
        _story_in(self.root, "US0002", "Done", "EP0100")
        _retro(self.root, "RETRO0001", "US0001")          # US0002 is live and uncovered
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertIn("EP0100", ids)
        self.assertIn("US0002", ids)


class BaselineTests(CloseOwedBase):
    def test_baseline_grandfathers_the_existing_tail(self) -> None:
        _story(self.root, "US0001", "Done")
        _bug(self.root, "BG0001", "Fixed")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        report = close_owed.owed(self.root)
        self.assertTrue(report["baselined"])
        self.assertEqual(report["owed"], [])
        self.assertEqual(report["grandfathered"], 2)

    def test_a_higher_id_closed_after_the_baseline_is_owed(self) -> None:
        _story(self.root, "US0001", "Done")  # pre-adoption tail
        close_owed.stamp_baseline(self.root, date="2026-01-01")  # cutoff US=1
        _story(self.root, "US0005", "Done")  # later work, no retro
        report = close_owed.owed(self.root)
        self.assertEqual({cid for cid, _ in report["owed"]}, {"US0005"})
        self.assertEqual(report["grandfathered"], 1)

    def test_later_work_covered_by_a_retro_is_not_owed(self) -> None:
        _story(self.root, "US0001", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _story(self.root, "US0005", "Done")
        _retro(self.root, "RETRO0002", "US0005")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])

    def test_detect_exits_nonzero_when_a_close_is_owed(self) -> None:
        _story(self.root, "US0001", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _story(self.root, "US0005", "Done")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = close_owed.main(["--root", str(self.root), "detect", "--format", "json"])
        self.assertEqual(rc, 1)

    def test_lower_id_in_flight_at_baseline_owes_when_it_later_closes(self) -> None:
        # The BLOCKER the set model fixes: a unit NON-terminal at baseline (a lower id) that closes
        # later must be owed, never silently forgiven. A highest-id cutoff would grandfather it.
        _story(self.root, "US0100", "Done")   # high id, terminal at baseline
        _story(self.root, "US0050", "Draft")  # in flight, lower id, NOT terminal at baseline
        close_owed.stamp_baseline(self.root, date="2026-01-01")  # forgives only {US0100}
        _story(self.root, "US0050", "Done")   # closes later, no retro -> must be owed
        report = close_owed.owed(self.root)
        self.assertEqual({cid for cid, _ in report["owed"]}, {"US0050"})

    def test_ulid_ids_are_grandfathered_by_set_membership(self) -> None:
        # Schema-v3 ULID ids have no numeric value; a highest-id cutoff broke entirely on them
        # (baseline empty -> everything owed forever). Set membership forgives them correctly.
        _story(self.root, "US-01JQK3F8AAZ8QK", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        report = close_owed.owed(self.root)
        self.assertEqual(report["owed"], [])
        self.assertEqual(report["grandfathered"], 1)

    def test_exclude_holds_named_ids_to_a_close_at_stamp_time(self) -> None:
        _story(self.root, "US0001", "Done")
        _story(self.root, "US0002", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01", exclude={"US0002"})
        report = close_owed.owed(self.root)
        self.assertEqual({cid for cid, _ in report["owed"]}, {"US0002"})


class CorruptBaselineTests(CloseOwedBase):
    """BG0155: a present-but-corrupt .close-owed-baseline.json must be a loud BLOCKING state,
    distinguishable from 'never baselined' - never a silent pass, never a re-stamp nudge (which
    would grandfather the very units that owe a close)."""

    def _baseline_path(self) -> Path:
        return self.root / close_owed.BASELINE_FILE

    def _corrupt(self, text: str) -> None:
        fp = self._baseline_path()
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(text, encoding="utf-8")

    def test_truncated_baseline_is_corrupt_not_absent(self) -> None:
        self._corrupt('{"grandfathered": ["US0001"')  # truncated JSON
        with self.assertRaises(close_owed.BaselineCorrupt):
            close_owed.load_baseline(self.root)

    def test_merge_conflict_marker_is_corrupt(self) -> None:
        self._corrupt('<<<<<<< HEAD\n{"grandfathered": []}\n=======\n{}\n>>>>>>> other\n')
        with self.assertRaises(close_owed.BaselineCorrupt):
            close_owed.load_baseline(self.root)

    def test_json_array_baseline_is_corrupt_not_a_crash(self) -> None:
        # the AttributeError path: a JSON array has no .get - it must be a clean corrupt signal
        self._corrupt('["US0001", "US0002"]')
        with self.assertRaises(close_owed.BaselineCorrupt):
            close_owed.load_baseline(self.root)

    def test_wrong_shape_grandfathered_is_corrupt(self) -> None:
        self._corrupt('{"grandfathered": "US0001"}')  # a string, not a list
        with self.assertRaises(close_owed.BaselineCorrupt):
            close_owed.load_baseline(self.root)

    def test_owed_reports_corrupt_and_owes_nothing_by_default(self) -> None:
        _story(self.root, "US0001", "Done")
        self._corrupt('["US0001"]')
        report = close_owed.owed(self.root)
        self.assertTrue(report["corrupt"])
        self.assertFalse(report["baselined"])
        self.assertEqual(report["owed"], [])  # never enumerates an amnesty target

    def test_detect_exits_nonzero_on_a_corrupt_baseline(self) -> None:
        self._corrupt('{"grandfathered": ')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = close_owed.main(["--root", str(self.root), "detect"])
        self.assertEqual(rc, 1)  # blocking failure, not a soft-state exit 0

    def test_render_directs_repair_not_a_restamp(self) -> None:
        self._corrupt('["US0001"]')
        text = close_owed.render(close_owed.owed(self.root))
        self.assertIn("CORRUPT", text)
        self.assertIn("repair", text.lower())
        self.assertNotIn("Run `close_owed baseline`", text)


class BatchLineCoverageTests(CloseOwedBase):
    """BG0225: a unit written inside parentheses on the `Batch` line went unseen.

    Coverage was read through `retro.batch_ids`, which STRIPS every `(...)` before matching -
    correct for `retro accuracy`, where a parenthetical is provenance (`(from CR0139)`) and
    would pad the forecast with non-units, but wrong for "did a retro account for this?". A
    Batch reading `BG0219, EP0090 (US0276)` - the natural way to write a story delivered under
    its epic - left US0276 reported as owed by a retro that plainly names it. A false alarm is
    the same failure as a miss: the operator reworded the line to silence the detector, which
    is how a detector stops being read.

    Coverage is therefore matched with the CANONICAL unanchored id matcher
    (`sdlc_md.ID_SEARCH_RE`), the one the rest of the codebase already uses, rather than a
    third hand-rolled regex - `retro.ARTEFACT_ID_RE` pins the digit run at exactly four, so a
    five-digit id matched nothing at all.
    """

    def test_a_leaf_unit_in_parentheses_is_covered(self) -> None:
        _story(self.root, "US0001", "Done")
        _bug(self.root, "BG0001", "Fixed")
        _retro(self.root, "RETRO0001", "BG0001, EP0090 (US0001)")
        report = close_owed.owed(self.root)
        self.assertEqual(report["owed"], [])
        # ...and the REPORT is what the operator reads, so assert on the rendered text too.
        self.assertNotIn("US0001", close_owed.render(report))

    def test_a_bare_unit_is_still_covered(self) -> None:
        _story(self.root, "US0001", "Done")
        _bug(self.root, "BG0001", "Fixed")
        _retro(self.root, "RETRO0001", "US0001, BG0001")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])

    def test_a_unit_adjacent_to_punctuation_is_covered(self) -> None:
        _story(self.root, "US0001", "Done")
        _bug(self.root, "BG0001", "Fixed")
        _retro(self.root, "RETRO0001", "[US0001] and *BG0001*.")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])

    def test_a_five_digit_id_is_matched_whole_and_credits_only_itself(self) -> None:
        """The trailing-boundary lesson: `\\d{4}` truncated or dropped a five-digit id."""
        _story(self.root, "US01010", "Done")
        _story(self.root, "US0101", "Done")
        _retro(self.root, "RETRO0001", "US01010")
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertNotIn("US01010", ids, "the id the retro names must be covered")
        self.assertIn("US0101", ids, "a shorter id must not be credited by a longer one")

    def test_a_lookalike_token_does_not_count_as_coverage(self) -> None:
        """Wider matching must not manufacture coverage out of prose."""
        _story(self.root, "US0001", "Done")
        _bug(self.root, "BG0001", "Fixed")
        _retro(self.root, "RETRO0001", "SUS0001 (BUS0001, BG00012) - a CR0001/RFC0001 follow-up")
        ids = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertEqual(ids, {"US0001", "BG0001"})

    def test_an_epic_in_a_provenance_parenthetical_earns_no_coverage(self) -> None:
        """A parenthetical names WHICH epic decomposed the batch, not a delivered epic.

        So only a LEAF unit (story or bug) earns coverage from inside `(...)`. A childless
        epic has no derivation to inherit from, and must stay owed rather than be forgiven by
        being mentioned as provenance.
        """
        _epic(self.root, "EP0001", "Done")                 # childless: nothing derived it
        _bug(self.root, "BG0001", "Fixed")
        _retro(self.root, "RETRO0001", "BG0001 (from EP0001)")
        report = close_owed.owed(self.root)
        ids = {cid for cid, _ in report["owed"]}
        self.assertEqual(ids, {"EP0001"})
        self.assertIn("EP0001", close_owed.render(report))


def _dated_retro(root: Path, rid: str, batch: str, date: str, override: str = "") -> None:
    """A retro carrying the Date the baseline doctrine is applied to, and optionally the
    recorded override that says why it can have no velocity row."""
    lines = [f"# RETRO-{rid[5:]}: a sprint", "", f"> **Date:** {date}",
             f"> **Batch:** {batch}"]
    if override:
        lines.append(f"> **Velocity-override:** {override}")
    lines += ["", "## Delivered", "- shipped", ""]
    _write(root / "sdlc-studio" / "retros" / f"{rid}-r.md", "\n".join(lines))


def _velocity_row(root: Path, rid: str) -> None:
    """A row for `rid` in the velocity record, as `accuracy --write` appends one."""
    p = root / "sdlc-studio" / "retros" / "VELOCITY.md"
    header = ("| Retro | Date | Units | Measured | Forecast | Points | "
              "Estimate (tokens, plan-time) | Actual (tokens) | Ratio (est/actual) | "
              "Tokens/pt | Oversized | Wall (s) | Constants | Sample | Model | Note | Source |\n"
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | "
              "--- | --- | --- | --- |\n")
    text = p.read_text(encoding="utf-8") if p.is_file() else "# Velocity history\n\n" + header
    _write(p, text + f"| {rid} | 2026-07-20 | 1 | 0 | 0 | 2 | - | - | - | - | 0 | - | - | "
                     f"unforecast | - | not attributable: interactive sprint | - |\n")


class AVelocityRowIsPartOfTheClose(CloseOwedBase):
    """US0288 (CR0284): `covered_ids` asked one question - does some retro's Batch name this
    unit - and nothing anywhere asked whether the accuracy and velocity write ran. So
    `accuracy --tokens N --write` shipped and RETRO0039 onwards still closed with no row in
    VELOCITY.md, and the rate every plan quotes was never re-measured against them.

    The demand is for the ROW, not for a token total: a row with a blank Actual and a recorded
    reason is a complete close - it states that the sprint's cost was not recoverable, which is
    a fact the record holds. No row at all states nothing, and is indistinguishable from an
    oversight.
    """

    def _baselined(self, stamp: str = "2026-07-16") -> None:
        _story(self.root, "US0001", "Done")
        close_owed.stamp_baseline(self.root, date=stamp)

    def test_a_retro_with_no_velocity_row_is_owed(self) -> None:
        self._baselined()
        _story(self.root, "US0005", "Done")
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20")
        report = close_owed.owed(self.root)
        self.assertEqual(report["owed"], [], "the unit half is clean")
        self.assertEqual([r for r, _d in report["velocity_owed"]], ["RETRO0002"])
        self.assertIn("RETRO0002", close_owed.render(report))
        self.assertIn("VELOCITY", close_owed.render(report).upper())

    def test_a_retro_that_has_a_row_is_not_owed(self) -> None:
        """The positive control: a close that DID write its row must not be demanded again, or
        the signal would be permanently red and read as noise."""
        self._baselined()
        _story(self.root, "US0005", "Done")
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20")
        _velocity_row(self.root, "RETRO0002")
        report = close_owed.owed(self.root)
        self.assertEqual(report["velocity_owed"], [])

    def test_a_blank_actual_with_a_reason_is_a_complete_close(self) -> None:
        """The row `_velocity_row` writes carries no token total at all - a blank Actual and the
        reason it is blank. That is the record saying the cost was not recoverable, and the
        demand is satisfied: the story asks for the ROW, never for a number."""
        self._baselined()
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20")
        _velocity_row(self.root, "RETRO0002")
        self.assertEqual(close_owed.owed(self.root)["velocity_owed"], [])

    def test_detect_exits_non_zero_on_a_missing_velocity_row(self) -> None:
        self._baselined()
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc = close_owed.main(["--root", str(self.root), "detect"])
        self.assertEqual(rc, 1, buf.getvalue())
        self.assertIn("RETRO0002", buf.getvalue())

    def test_retros_before_the_baseline_stamp_owe_no_velocity_row(self) -> None:
        # the unclearable-debt failure the baseline exists to prevent: 65 retros on disk, and
        # adopting the check must not hand the project a tail no close can ever clear
        self._baselined(stamp="2026-07-16")
        _dated_retro(self.root, "RETRO0001", "US0001", "2026-07-15")
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-16")   # the stamp day counts
        report = close_owed.owed(self.root)
        self.assertEqual([r for r, _d in report["velocity_owed"]], ["RETRO0002"])

    def test_an_undated_retro_is_not_demanded_but_is_named(self) -> None:
        """The baseline is applied to the retro's DATE, so a retro carrying none cannot be
        placed either side of the stamp. It is not demanded - guessing would recreate the
        unclearable tail - and it is REPORTED, so the escape is visible rather than silent."""
        self._baselined()
        _write(self.root / "sdlc-studio" / "retros" / "RETRO0002-r.md",
               "# RETRO-0002: a sprint\n\n> **Batch:** US0005\n\n## Delivered\n- shipped\n")
        report = close_owed.owed(self.root)
        self.assertEqual(report["velocity_owed"], [])
        self.assertEqual(report["velocity_undated"], ["RETRO0002"])
        self.assertIn("RETRO0002", close_owed.render(report))

    def test_a_recorded_velocity_override_is_named_not_owed(self) -> None:
        self._baselined()
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20",
                     override="the run predates the harness baseline and its telemetry is gone")
        report = close_owed.owed(self.root)
        self.assertEqual(report["velocity_owed"], [])
        self.assertEqual([r for r, _why in report["velocity_overrides"]], ["RETRO0002"])
        rendered = close_owed.render(report)
        self.assertIn("predates the harness baseline", rendered,
                      "an escape nobody can read is a silent pass")

    def test_a_bare_override_with_no_reason_is_not_an_override(self) -> None:
        """The escape is the RECORDED REASON. A bare marker is the dodge the whole ceremony
        exists to refuse - the same rule the retro's own `declined:` disposition obeys."""
        self._baselined()
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20", override="   ")
        report = close_owed.owed(self.root)
        self.assertEqual([r for r, _d in report["velocity_owed"]], ["RETRO0002"])

    def test_an_unfilled_placeholder_is_not_a_reason(self) -> None:
        self._baselined()
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20", override="{{why}}")
        self.assertEqual([r for r, _d in close_owed.owed(self.root)["velocity_owed"]],
                         ["RETRO0002"])

    def test_a_blank_override_does_not_borrow_the_next_line_as_its_reason(self) -> None:
        """`extract_field` falls through an empty value to the next non-blank line, which would
        let a bare marker be 'reasoned' by whatever prose followed it - the dodge wearing the
        ceremony's own clothes."""
        self._baselined()
        _write(self.root / "sdlc-studio" / "retros" / "RETRO0002-r.md",
               "# RETRO-0002: a sprint\n\n> **Date:** 2026-07-20\n> **Batch:** US0005\n"
               "> **Velocity-override:**\n\n## Delivered\n- shipped\n")
        report = close_owed.owed(self.root)
        self.assertEqual([r for r, _d in report["velocity_owed"]], ["RETRO0002"])
        self.assertEqual(report["velocity_overrides"], [])

    def test_an_unbaselined_project_demands_no_row(self) -> None:
        """Without a stamp there is no date to scope the demand to, and reporting every retro
        on disk would be the unclearable tail again. The baseline nudge stands on its own."""
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20")
        report = close_owed.owed(self.root)
        self.assertFalse(report["baselined"])
        self.assertEqual(report["velocity_owed"], [])

    def test_a_corrupt_baseline_still_reports_nothing_but_the_corruption(self) -> None:
        _dated_retro(self.root, "RETRO0002", "US0005", "2026-07-20")
        _write(self.root / close_owed.BASELINE_FILE, '["US0005"]')
        report = close_owed.owed(self.root)
        self.assertTrue(report["corrupt"])
        self.assertEqual(report["velocity_owed"], [])


if __name__ == "__main__":
    unittest.main()
