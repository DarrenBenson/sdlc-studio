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


class CloseOwedFieldsFileTests(unittest.TestCase):
    """US0391: the baseline note reaches the file through the shared fields-file loader, so prose
    carrying shell metacharacters is stored verbatim rather than swallowed by a shell."""

    def test_fields_file_baseline_note_is_stored_verbatim(self) -> None:
        import json
        d = Path(tempfile.mkdtemp(prefix="close_owed_ff_"))
        (d / "sdlc-studio").mkdir(parents=True)
        hazard = "grandfathered before `git log` and $(date) were run"
        (d / "fields.json").write_text(json.dumps({"note": hazard}))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = close_owed.main(["--root", str(d), "baseline",
                                  "--fields-file", str(d / "fields.json")])
        self.assertEqual(rc, 0)
        data = json.loads((d / close_owed.BASELINE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(data["note"], hazard)        # byte-for-byte - it crossed no shell


class DecisionTerminalTests(unittest.TestCase):
    """BG0382. The terminal set mixes two different things: `Done`/`Fixed` are reached by
    BUILDING, `Won't Fix`/`Superseded`/`Duplicate` by RULING. A close-down accounts for what a
    sprint delivered, so only the first kind can owe one - and an advisory no correct action
    can discharge is one an operator learns to scroll past."""

    def _unit(self, root: Path, ident: str, status: str) -> None:
        d = root / "sdlc-studio" / ("bugs" if ident.startswith("BG") else "stories")
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{ident}-x.md").write_text(
            f"# {ident}: x\n\n> **Status:** {status}\n\n"
            f"## Acceptance Criteria\n\n- [ ] it behaves\n", encoding="utf-8")

    def test_a_unit_ruled_rather_than_built_owes_no_close(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "Won't Implement")
            close_owed.stamp_baseline(root)
            self._unit(root, "US0002", "Won't Implement")
            owed = [cid for cid, _ in close_owed.owed(root)["owed"]]
            self.assertNotIn("US0002", owed)

    def test_a_delivered_unit_still_does(self) -> None:
        """The other half, so the carve-out cannot widen into a blanket exemption."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "Ready")
            close_owed.stamp_baseline(root)
            self._unit(root, "US0002", "Done")
            owed = [cid for cid, _ in close_owed.owed(root)["owed"]]
            self.assertIn("US0002", owed)

    def test_the_split_is_shared_with_the_criteria_floor(self) -> None:
        """One authority, not two lists of statuses. The transition verb's criteria floor asks
        the same question, and a second copy here would drift from it."""
        self.assertTrue(close_owed.sdlc_md.is_delivered_terminal("story", "Done"))
        self.assertTrue(close_owed.sdlc_md.is_delivered_terminal("bug", "Fixed"))
        for ruled in ("Won't Implement", "Won't Fix", "Superseded"):
            with self.subTest(status=ruled):
                self.assertTrue(close_owed.sdlc_md.is_decision_terminal(ruled))
                self.assertFalse(close_owed.sdlc_md.is_delivered_terminal("story", ruled)
                                 or close_owed.sdlc_md.is_delivered_terminal("bug", ruled))




def _actuals(root: Path, day: str, ids: list) -> None:
    """The close telemetry `transition.py` writes: one row per unit reaching terminal, in a file
    named for the day. That filename IS the terminal date - derived, never declared."""
    import json as _json
    p = root / "sdlc-studio" / "retros" / "evidence" / f"actuals-{day}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(_json.dumps({"id": i, "type": "bug", "project": "x"}) + "\n"
                         for i in ids), encoding="utf-8")


def _run_state(root: Path, outcome: str) -> None:
    import json as _json
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_json.dumps({"schema": 1, "run_id": "RUN-T", "outcome": outcome}),
                 encoding="utf-8")


class CloseTimeRepairTests(CloseOwedBase):
    """US0617 / CR0527: a unit fixed DURING a close is not a unit nobody accounted for.

    A close writes a retro accounting for its batch, then stamps the baseline. Anything reaching
    terminal after that stamp is uncovered - and a repair made during the close is exactly such a
    unit, so the ledger re-opened the moment a careful close did its job. Observed twice in one
    close of RUN-01KYZKY5. The operator's reading was that the sprint was never being closed; the
    mechanism was worse - it WAS closed, repeatedly, and each close was undone by the next repair.

    Both states are still REPORTED. The split is about wording and countability, never about
    forgiving anything, so every test here also asserts the unit stays in `owed`.
    """

    def _tree(self, *, terminal_day: str, retro_day: str, outcome: str) -> dict:
        """The retro carries a recorded velocity override on purpose.

        The close has TWO halves and each holds the exit code on its own account. Without the
        override the fixture also owes a velocity row, so an exit-code assertion here would pass
        or fail for a reason that has nothing to do with the unit split under test - which it did
        on the first run of these tests.
        """
        _bug(self.root, "BG0001", "Fixed")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _bug(self.root, "BG0005", "Fixed")
        _dated_retro(self.root, "RETRO0002", "BG0001", retro_day,
                     override="no plan-time forecast for this fixture")
        _actuals(self.root, terminal_day, ["BG0005"])
        _run_state(self.root, outcome)
        return close_owed.owed(self.root)

    def test_a_unit_terminal_after_the_retro_is_reported_as_a_close_time_repair(self) -> None:
        """MUTANT: classify every uncovered unit as unaccounted (drop the date comparison)."""
        r = self._tree(terminal_day="2026-02-02", retro_day="2026-02-01", outcome="stopped")
        self.assertEqual([cid for cid, _ in r["close_time_repairs"]], ["BG0005"])
        self.assertEqual(r["unaccounted"], [])
        self.assertEqual({cid for cid, _ in r["owed"]}, {"BG0005"},
                         "the split must not forgive the unit - it is still owed")

    def test_an_unaccounted_unit_is_still_reported_as_unaccounted(self) -> None:
        """The control. MUTANT: classify every uncovered unit as a close-time repair.

        That would empty the unaccounted set and turn the ledger into a rubber stamp.
        """
        r = self._tree(terminal_day="2026-01-15", retro_day="2026-02-01", outcome="stopped")
        self.assertEqual(r["close_time_repairs"], [])
        self.assertEqual([cid for cid, _ in r["unaccounted"]], ["BG0005"])

    def test_work_delivered_into_an_OPEN_run_is_not_a_close_time_repair(self) -> None:
        """MUTANT: test `outcome` for truthiness instead of comparing it to `running`.

        `outcome` is the string "running" while a run is live, so a truthiness test reads an
        open run as a closed one - and then every unit delivered into the current sprint is
        excused as a repair made during a close that has not started. Caught on this repo's own
        tree, where four units of an open batch were all reported as close-time repairs.
        """
        r = self._tree(terminal_day="2026-02-02", retro_day="2026-02-01", outcome="running")
        self.assertEqual(r["close_time_repairs"], [],
                         "ordinary delivery into an open run was excused as a close-time repair")
        self.assertEqual([cid for cid, _ in r["unaccounted"]], ["BG0005"])

    def test_the_classification_is_derived_not_declared(self) -> None:
        """MUTANT: read the terminal date from a field on the artefact instead.

        No unit declares when it closed, and a field somebody must remember to set records the
        honest case and misses the careless one - which is the whole population this ledger
        exists for. With no telemetry row, nothing is classified a repair.
        """
        _bug(self.root, "BG0001", "Fixed")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _bug(self.root, "BG0005", "Fixed")
        _dated_retro(self.root, "RETRO0002", "BG0001", "2026-02-01")
        _run_state(self.root, "stopped")
        r = close_owed.owed(self.root)         # no actuals file at all
        self.assertEqual(r["close_time_repairs"], [])
        self.assertEqual([cid for cid, _ in r["unaccounted"]], ["BG0005"])
        self.assertEqual(close_owed.terminal_dates(self.root), {})

    def test_the_earliest_close_is_the_one_that_counts(self) -> None:
        """MUTANT: keep the LATEST date per unit.

        A unit reopened and re-closed owes its account from the first close; taking the later
        date would let a re-close move a unit out of the owed set it was already in.
        """
        _actuals(self.root, "2026-03-01", ["BG0009"])
        _actuals(self.root, "2026-01-09", ["BG0009"])
        self.assertEqual(close_owed.terminal_dates(self.root)["BG0009"], "2026-01-09")

    def test_a_malformed_telemetry_row_is_not_a_date(self) -> None:
        """MUTANT: let a bad row raise, or count it as a unit.

        The scan must survive a truncated write - the file is appended to on every transition,
        and a crash mid-append must not make the whole ledger unreadable.
        """
        p = self.root / "sdlc-studio" / "retros" / "evidence" / "actuals-2026-02-02.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"id": "BG0007", "type": "bug"}\n{"id": "BG00\n\n', encoding="utf-8")
        self.assertEqual(close_owed.terminal_dates(self.root), {"BG0007": "2026-02-02"})

    def test_the_report_names_the_two_states_apart(self) -> None:
        """MUTANT: print one combined list.

        One number cannot carry two states, and the failure being repaired is an advisory that
        fires on a run which did account for itself - which is how it comes to be stepped over.
        """
        r = self._tree(terminal_day="2026-02-02", retro_day="2026-02-01", outcome="stopped")
        text = close_owed.render(r)
        self.assertIn("CLOSE-TIME REPAIR", text)
        self.assertIn("BG0005", text)
        self.assertIn("FILED and deferred", text,
                      "the report does not state the rule the split exists to serve")

    def test_close_time_repairs_alone_do_not_hold_the_exit_code(self) -> None:
        """MUTANT: keep gating the exit code on `owed` rather than on `unaccounted`.

        Driven through `main(["detect"])`, not through `owed()`: the exit code IS the interface
        a gate branches on, and a library-level assertion cannot see which field the command
        actually reads. Gating on a close-time repair would refuse the ceremony precisely
        because the close had done its job carefully - the unconvergeable close from the other
        side.
        """
        self._tree(terminal_day="2026-02-02", retro_day="2026-02-01", outcome="stopped")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = close_owed.main(["--root", str(self.root), "detect"])
        self.assertEqual(rc, 0, f"a close-time repair alone held the gate:\n{out.getvalue()}")
        self.assertIn("CLOSE-TIME REPAIR", out.getvalue(), "...and it was not even reported")

    def test_an_unaccounted_unit_still_holds_the_exit_code(self) -> None:
        """The positive control. MUTANT: always exit 0.

        The ledger's whole value is refusing a run nobody accounted for; a detector that never
        holds the gate reports into a void.
        """
        self._tree(terminal_day="2026-01-15", retro_day="2026-02-01", outcome="stopped")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = close_owed.main(["--root", str(self.root), "detect"])
        self.assertEqual(rc, 1, "an unaccounted unit did not hold the gate")




class CloseRepairOverrideTests(CloseOwedBase):
    """US0618 / CR0527: the deliberate way through, for a repair that genuinely could not wait.

    US0616 refuses the inline repair and US0617 makes the residue readable. This is the recorded
    exception - and it has to cost something to use and be countable afterwards, or it becomes
    the routine the rule was written against.
    """

    def _tree(self, override: str = "") -> dict:
        _bug(self.root, "BG0001", "Fixed")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _bug(self.root, "BG0005", "Fixed")
        lines = ["# RETRO-0002: a sprint", "", "> **Date:** 2026-02-01",
                 "> **Batch:** BG0001",
                 "> **Velocity-override:** no plan-time forecast for this fixture"]
        if override:
            lines.append(f"> **Close-repair-override:** {override}")
        lines += ["", "## Delivered", "- shipped", ""]
        _write(self.root / "sdlc-studio" / "retros" / "RETRO0002-r.md",
               "\n".join(lines) + "\n")
        _actuals(self.root, "2026-02-02", ["BG0005"])
        _run_state(self.root, "stopped")
        return close_owed.owed(self.root)

    def test_a_bare_override_is_refused_and_a_reasoned_one_is_accepted(self) -> None:
        """MUTANT: accept the marker's presence rather than a reason after it.

        The velocity override beside it already holds this rule: a bare marker is not an
        override. An escape that costs nothing to write is one that gets written every time.
        """
        bare = self._tree(override="BG0005")
        self.assertEqual(bare["close_repair_overrides"], [],
                         "a bare marker with no reason was honoured as an override")
        self.assertEqual([c for c, _ in bare["close_time_repairs"]], ["BG0005"])

        self.setUp()
        reasoned = self._tree(override="BG0005 - the close itself was wrong without it")
        self.assertEqual([c for c, _t, _w in reasoned["close_repair_overrides"]], ["BG0005"])
        self.assertEqual(reasoned["close_time_repairs"], [])

    def test_an_override_covers_only_the_unit_it_names(self) -> None:
        """MUTANT: treat any recorded override as covering the whole run.

        One exception must not license the next, which is the difference between a recorded
        exception and a blanket exemption.
        """
        _bug(self.root, "BG0001", "Fixed")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        for bid in ("BG0005", "BG0006"):
            _bug(self.root, bid, "Fixed")
        _write(self.root / "sdlc-studio" / "retros" / "RETRO0002-r.md",
               "# RETRO-0002: a sprint\n\n> **Date:** 2026-02-01\n> **Batch:** BG0001\n"
               "> **Velocity-override:** none needed\n"
               "> **Close-repair-override:** BG0005 - unavoidable\n\n## Delivered\n- x\n")
        _actuals(self.root, "2026-02-02", ["BG0005", "BG0006"])
        _run_state(self.root, "stopped")
        r = close_owed.owed(self.root)
        self.assertEqual([c for c, _t, _w in r["close_repair_overrides"]], ["BG0005"])
        self.assertEqual([c for c, _ in r["close_time_repairs"]], ["BG0006"],
                         "one unit's override covered another unit's repair")

    def test_an_override_naming_no_unit_forgives_nothing(self) -> None:
        """MUTANT: allow an override with a reason but no unit id.

        That would forgive every close-time repair in the run at once - the blanket exemption
        this is specifically not.
        """
        r = self._tree(override="it was all unavoidable, honestly")
        self.assertEqual(r["close_repair_overrides"], [])
        self.assertEqual([c for c, _ in r["close_time_repairs"]], ["BG0005"])

    def test_the_close_reports_the_override_count_and_reasons(self) -> None:
        """MUTANT: store the override without reporting it.

        An override nobody sees is indistinguishable from the inline repair the rule forbids,
        so it is surfaced on every run rather than filed away.
        """
        r = self._tree(override="BG0005 - the close itself was wrong without it")
        text = close_owed.render(r)
        self.assertIn("BG0005", text)
        self.assertIn("recorded override", text)
        self.assertIn("the close itself was wrong without it", text,
                      "the reason is stored but never shown, so nobody can question it")


class HeadlineAndExitCodeAgreeTests(CloseRepairOverrideTests):
    """BG0518: the first line contradicted the verdict on the one state that matters.

    The exit code was computed from `unaccounted`, the headline from `owed`. `owed` keeps every
    uncovered terminal unit - including the ones an override fully accounts for, deliberately,
    because visible and countable is the point. So on a fully-overridden set the tool printed
    "a sprint close is owed (run the retro, then `gate --require-retro RETROxxxx`)" and exited
    0. A gate reading the code was right; every human and agent reading the line was told the
    opposite, and told to do work that was not owed and could not honestly be done - there is
    no batch left for that retro to account for.

    Inherits the override fixture rather than rebuilding it: this is a claim about how that
    exact state is REPORTED.
    """

    OVERRIDE = "BG0005 - the defect was in the close loop that was running this close"

    def test_a_fully_overridden_set_makes_no_claim_that_a_close_is_owed(self) -> None:
        """MUTANT: compose the headline from `owed` again (restore `n` in the head branches).

        Asserts the CLAIM is absent, not that some word is present, because the units are still
        named further down and a substring test for "BG0005" passes either way.
        """
        r = self._tree(override=self.OVERRIDE)
        self.assertEqual(r["unaccounted"], [], "the fixture is not a fully-overridden set")
        head = close_owed.render(r).splitlines()[0]
        self.assertNotIn("a sprint close is owed", head,
                         f"the headline claims a close is owed while exiting 0: {head}")
        self.assertNotIn("--require-retro", head,
                         f"the headline names a discharge command for an empty ledger: {head}")
        self.assertFalse(close_owed.is_owed(r), "nothing is owed, so the predicate must be False")

    def test_the_overridden_units_are_still_named(self) -> None:
        """The control. MUTANT: fix the headline by suppressing the report.

        An override nobody can see is indistinguishable from the inline repair the rule forbids.
        Quietening the tool is not the fix; agreeing with itself is.
        """
        text = close_owed.render(self._tree(override=self.OVERRIDE))
        self.assertIn("BG0005", text, "the overridden unit is no longer reported at all")
        self.assertIn("recorded override", text)

    def _unaccounted_tree(self) -> dict:
        """A unit nobody accounted for: terminal BEFORE the retro was written, so it is not a
        close-time repair and no override applies to it.

        Dropping the override from `_tree` is NOT this state - the unit there is still a
        close-time repair, which by CR0527 is reported and deliberately does not hold the exit
        code. Writing that control first and watching it fail is what showed the difference.
        """
        _bug(self.root, "BG0001", "Fixed")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _bug(self.root, "BG0005", "Fixed")
        _dated_retro(self.root, "RETRO0002", "BG0001", "2026-02-01",
                     override="no plan-time forecast for this fixture")
        _actuals(self.root, "2026-01-15", ["BG0005"])       # BEFORE the retro
        _run_state(self.root, "stopped")
        return close_owed.owed(self.root)

    def test_an_unaccounted_unit_still_refuses_and_still_exits_non_zero(self) -> None:
        """The other control. MUTANT: make `is_owed` return False unconditionally.

        This fix must not buy a quiet tool by silencing a real refusal.
        """
        r = self._unaccounted_tree()
        self.assertEqual([c for c, _ in r["unaccounted"]], ["BG0005"], "the fixture is wrong")
        self.assertTrue(close_owed.is_owed(r))
        self.assertIn("a sprint close is owed", close_owed.render(r).splitlines()[0])

    def test_the_headline_and_the_verdict_cannot_disagree(self) -> None:
        """The property, over both states. MUTANT: derive either one from its own expression.

        One predicate, two consumers. A future branch that reports a debt without holding the
        exit code - or holds it without saying so - fails here rather than in somebody's
        session.
        """
        for label, build in (("overridden", lambda: self._tree(override=self.OVERRIDE)),
                             ("repair-only", lambda: self._tree()),
                             ("unaccounted", self._unaccounted_tree)):
            with self.subTest(state=label):
                r = build()
                claims = "a sprint close is owed" in close_owed.render(r)
                self.assertEqual(claims, close_owed.is_owed(r),
                                 "the headline and the exit code disagree about this report")

    def test_the_shipped_command_agrees_too(self) -> None:
        """MUTANT: fix `render` and leave `cmd_detect` computing its own answer.

        The library functions agreeing proves nothing about the CLI, which is what an operator
        and a gate actually run - a library test is not a lane test (LL0040). This drives
        `cmd_detect` itself and reads the exit code it returns, never a pipe's.
        """
        import argparse
        self._tree(override=self.OVERRIDE)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = close_owed.cmd_detect(argparse.Namespace(root=str(self.root), format="text"))
        head = buf.getvalue().splitlines()[0]
        self.assertEqual(rc, 0, f"the command refuses a fully-overridden set: {head}")
        self.assertNotIn("a sprint close is owed", head,
                         f"the command exits 0 and still claims a close is owed: {head}")


if __name__ == "__main__":
    unittest.main()
