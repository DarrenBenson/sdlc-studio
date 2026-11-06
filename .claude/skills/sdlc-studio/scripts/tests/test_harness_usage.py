"""US1125 (CR0667): each CLI's headless usage output is normalised to one basis.

`lib/harness_usage.parse(harness, text)` reads the headless output of Claude Code, Cursor CLI,
Codex CLI, Copilot CLI and OpenCode into one shape: input without cache, cache read, cache write,
output (reasoning included) and reasoning, with the model and the session id.

Every fixture under `fixtures/harness_usage/` is cut from a real session captured on 2026-11-06,
never written from documentation. Each is the CLI's stdout as captured, scrubbed of the one auth
field it held (Claude Code's `credential_expires_at`). `copilot.jsonl` keeps only the four events
the parser reads, with the tool list, system segments and conversation hashes taken out of the
checkpoint; every count is as captured. `cursor.json` holds four Cursor captures, the run's own
and three more taken to settle whether `inputTokens` holds the cache reads (it does not).

Pinned here:

* each captured session normalises to its own counts, model and session id (AC1);
* Codex's and Copilot's cached input is split out, so input, cache read and cache write sum to
  the CLI's own prompt total once, and a repeated running-total record is not added twice (AC2);
* a non-zero exit, output with no usage and a line that does not parse are unmetered with a
  reason naming which, every count None, never zero (AC3);
* Claude Code's `total_cost_usd`, Copilot's session accounting and OpenCode's own token total
  are checked against the normalised figure, a gap above 5% is named, and a check that cannot
  be made is named as unchecked rather than passed (AC4).

BG1244 adds: a usage container that is not a JSON object is unmetered with a reason naming it,
never an `AttributeError` (AC1); an absent reasoning count is None and unreported, never 0
(AC2); a session that used two models is named for the one that carried the most tokens (AC3);
and the Codex reading of `input_tokens` cites the evidence that decides it (AC4).

BG1252 adds: a session that used two models carries each model's own counts in
`Usage.by_model`, summing to the session's (AC1).

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py -q
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/harness_usage.py
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import harness_usage
from lib.harness_usage import NO_USAGE, NONZERO_EXIT, UNPARSEABLE, parse

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "harness_usage"
COUNTS = ("input", "cache_read", "cache_write", "output", "reasoning")

#: Per-million US dollar rates for claude-haiku-5-5 that reproduce the capture's own
#: `modelUsage.claude-haiku-5-5.costUSD` (0.00355672) exactly. The five-minute write rate is
#: not fixed by the capture, which wrote none, so it never weighs here.
HAIKU = {"input": 0.10, "output": 0.50, "cache_read": 0.01, "cache_write": 0.125,
         "cache_write_1h": 0.20}


def _text(name: str) -> str:
    return (FIXTURES / name).read_text()


def _cursor(index: int) -> str:
    return json.loads(_text("cursor.json"))["captures"][index]["stdout"]


def _lines(name: str) -> list[dict]:
    return [json.loads(raw) for raw in _text(name).splitlines() if raw.strip()]


def _jsonl(events: list[dict]) -> str:
    return "".join(json.dumps(e) + "\n" for e in events)


class HarnessUsageTests(unittest.TestCase):

    def _expect(self, got, **want):
        self.assertTrue(got.metered, got.reason)
        for field, value in want.items():
            self.assertEqual(getattr(got, field), value, field)

    def test_each_captured_session_normalises(self):
        self._expect(parse("claude", _text("claude.json")),
                     input=2, cache_read=11382, cache_write=17126, cache_write_1h=17126,
                     output=35, reasoning=31, model="claude-haiku-5-5", model_source="output",
                     session_id="4052faf6-ae92-4245-a560-c2c9534b3cec", unreported=())
        cursor = parse("cursor", _cursor(0))
        self._expect(cursor, input=9046, cache_read=6016, cache_write=0, output=31,
                     reasoning=None, model=None,
                     session_id="372d681a-bac0-4786-b53b-60fe4399f7a4")
        self.assertEqual(set(cursor.unreported), {"reasoning", "model"})
        # Codex's and OpenCode's streams name no model; the caller's launch model fills it, and
        # these are the models their own stores recorded for the captured sessions.
        self._expect(parse("codex", _text("codex.jsonl"), model="gpt-6.1-sol"),
                     input=2236, cache_read=12288, cache_write=0, output=5, reasoning=0,
                     model="gpt-6.1-sol", model_source="caller",
                     session_id="01a1b08f-6aa6-7db1-93e7-b71b8ab17ef6", unreported=())
        self._expect(parse("copilot", _text("copilot.jsonl")),
                     input=4, cache_read=0, cache_write=27578, output=4, reasoning=0,
                     model="claude-sonnet-5.5", model_source="output",
                     session_id="95be3a2a-b4e1-4265-8d11-fe4bb10bee03")
        self._expect(parse("opencode", _text("opencode.jsonl"),
                           model="opencode/deepseek-v4.1-flash-free"),
                     input=9896, cache_read=1792, cache_write=0, output=3, reasoning=0,
                     model="opencode/deepseek-v4.1-flash-free", model_source="caller",
                     session_id="ses_e4f70696affemjSa99Fu7ITrM9")
        # Claude Code's top-level `usage` reads the same where `modelUsage` is absent.
        flat = json.loads(_text("claude.json"))
        del flat["modelUsage"]
        self._expect(parse("claude", json.dumps(flat)), input=2, cache_read=11382,
                     cache_write=17126, cache_write_1h=17126, output=35, reasoning=31,
                     model=None, unreported=("model",))
        bare = parse("codex", _text("codex.jsonl"))
        self.assertIsNone(bare.model)
        self.assertIn("model", bare.unreported)
        with self.assertRaises(ValueError):
            parse("gemini", "{}")

    def test_cached_input_is_split_and_never_counted_twice(self):
        codex = parse("codex", _text("codex.jsonl"))
        raw = next(e for e in _lines("codex.jsonl") if e["type"] == "turn.completed")["usage"]
        self.assertEqual(codex.input + codex.cache_read + codex.cache_write, raw["input_tokens"])
        self.assertEqual(codex.prompt, raw["input_tokens"])
        self.assertEqual(codex.input, raw["input_tokens"] - raw["cached_input_tokens"])

        events = _lines("copilot.jsonl")
        checkpoint = next(e for e in events if e["type"] == "session.usage_checkpoint")
        metrics = checkpoint["data"]["accountingSnapshot"]["modelMetrics"]["claude-sonnet-5.5"]
        prompt_tokens = (checkpoint["data"]["promptCacheBreakState"][0]["models"]
                         ["claude-sonnet-5.5"]["prompt_tokens"])
        copilot = parse("copilot", _text("copilot.jsonl"))
        self.assertEqual(copilot.prompt, metrics["usage"]["inputTokens"])
        self.assertEqual(copilot.prompt, prompt_tokens)
        self.assertEqual(copilot.input, 4)
        # The checkpoint is a running total: seen twice, it still counts once.
        again = parse("copilot", _text("copilot.jsonl") + json.dumps(checkpoint) + "\n")
        self.assertEqual([getattr(again, c) for c in COUNTS],
                         [getattr(copilot, c) for c in COUNTS])

        # Claude Code and OpenCode already report input without cache: nothing is taken off.
        self.assertEqual(parse("claude", _text("claude.json")).input, 2)
        self.assertEqual(parse("opencode", _text("opencode.jsonl")).input, 9896)

    def test_reasoning_is_counted_inside_output_once(self):
        """Every capture reasoned 0 tokens, so these give the captures some reasoning to pin
        the stated reading: OpenCode reports it beside output (its total adds it), Codex and
        Copilot inside it."""
        opencode = _text("opencode.jsonl").replace('"total":11691', '"total":11698').replace(
            '"reasoning":0', '"reasoning":7')
        got = parse("opencode", opencode)
        self.assertEqual((got.output, got.reasoning), (10, 7))
        self.assertEqual(got.disagreements, ())
        codex = parse("codex", _text("codex.jsonl").replace('"reasoning_output_tokens":0',
                                                             '"reasoning_output_tokens":2'))
        self.assertEqual((codex.output, codex.reasoning), (5, 2))
        copilot = parse("copilot", _text("copilot.jsonl").replace('"reasoningTokens":0',
                                                                  '"reasoningTokens":3'))
        self.assertEqual((copilot.output, copilot.reasoning), (4, 3))

    def test_cursor_input_excludes_its_cache_reads(self):
        """Two directories under one parent, one read cold (23289 input, no cache) and one with
        its prefix cached (17312 input beside 6016 cache read), agree on the prompt only when
        `inputTokens` leaves the cache reads out; read as inside, the second is 6k short."""
        cold, warm = parse("cursor", _cursor(1)), parse("cursor", _cursor(3))
        self.assertEqual(cold.cache_read, 0)
        self.assertGreater(warm.cache_read, 0)
        self.assertAlmostEqual(warm.prompt / cold.prompt, 1.0, delta=0.01)
        self.assertEqual(parse("cursor", _cursor(2)).prompt, cold.prompt)

    def test_unmetered_with_a_reason(self):
        captured = {"claude": _text("claude.json"), "cursor": _cursor(0),
                    "codex": _text("codex.jsonl"), "copilot": _text("copilot.jsonl"),
                    "opencode": _text("opencode.jsonl")}
        no_usage = {"claude": json.dumps({"type": "result", "session_id": "s", "result": "OK"}),
                    "cursor": json.dumps({"type": "result", "session_id": "s"}),
                    "codex": _jsonl([e for e in _lines("codex.jsonl")
                                     if e["type"] != "turn.completed"]),
                    "copilot": _jsonl([e for e in _lines("copilot.jsonl")
                                       if e["type"] != "session.usage_checkpoint"]),
                    "opencode": _jsonl([e for e in _lines("opencode.jsonl")
                                        if e["type"] != "step_finish"])}
        for harness in harness_usage.HARNESSES:
            cases = [(parse(harness, captured[harness], exit_code=1), NONZERO_EXIT, "exit"),
                     (parse(harness, no_usage[harness]), NO_USAGE, "no usage"),
                     (parse(harness, ""), NO_USAGE, "no usage"),
                     (parse(harness, captured[harness] + '{"type": "turn.compl\n'), UNPARSEABLE,
                      "does not parse")]
            for got, kind, words in cases:
                with self.subTest(harness=harness, kind=kind):
                    self.assertFalse(got.metered)
                    self.assertEqual(got.unmetered, kind)
                    self.assertIn(words, got.reason)
                    self.assertEqual([getattr(got, c) for c in COUNTS], [None] * len(COUNTS))
            self.assertTrue(parse(harness, captured[harness], exit_code=0).metered, harness)

        torn = parse("codex", _text("codex.jsonl") + "not json\n")
        self.assertIn("line 5", torn.reason)
        result = [e for e in _lines("copilot.jsonl")]
        result[-1]["exitCode"] = 1
        self.assertEqual(parse("copilot", _jsonl(result)).unmetered, NONZERO_EXIT)
        lots = _text("codex.jsonl").replace('"output_tokens":5', '"output_tokens":"lots"')
        self.assertEqual(parse("codex", lots).unmetered, UNPARSEABLE)
        uncached = _text("codex.jsonl").replace('"input_tokens":14524', '"input_tokens":100')
        self.assertEqual(parse("codex", uncached).unmetered, UNPARSEABLE)

    def test_a_disagreement_with_the_harness_total_is_named(self):
        claude = _text("claude.json")
        right = parse("claude", claude, prices={"claude-haiku-5-5": HAIKU})
        [check] = right.checks
        self.assertEqual((check.against, check.status), ("total_cost_usd", "agrees"))
        self.assertAlmostEqual(check.normalised, 0.00355672, places=10)
        self.assertEqual(right.disagreements, ())

        five_minute = dict(HAIKU, cache_write_1h=HAIKU["cache_write"])
        wrong = parse("claude", claude, prices={"claude-haiku-5-5": five_minute})
        self.assertEqual(wrong.checks[0].status, "disagrees")
        self.assertEqual(len(wrong.disagreements), 1)
        self.assertIn("total_cost_usd", wrong.disagreements[0])
        self.assertTrue(wrong.metered)
        for scale, status in ((1.04, "agrees"), (0.96, "agrees"), (1.06, "disagrees"),
                              (0.94, "disagrees")):
            scaled = {k: v * scale for k, v in HAIKU.items()}
            got = parse("claude", claude, prices={"claude-haiku-5-5": scaled})
            self.assertEqual(got.checks[0].status, status, scale)
            self.assertEqual(bool(got.disagreements), status == "disagrees", scale)

        unpriced = parse("claude", claude)
        self.assertEqual(unpriced.checks[0].status, "unchecked")
        self.assertIn("claude-haiku-5-5", unpriced.checks[0].detail)
        self.assertIsNone(unpriced.checks[0].normalised)

        copilot = parse("copilot", _text("copilot.jsonl"))
        [check] = copilot.checks
        self.assertEqual((check.against, check.status), ("session accounting", "agrees"))
        self.assertEqual(check.harness, 27586)
        events = _lines("copilot.jsonl")
        snapshot = next(e for e in events
                        if e["type"] == "session.usage_checkpoint")["data"]["accountingSnapshot"]
        snapshot["tokenDetails"]["input"]["tokenCount"] = 2004
        off = parse("copilot", _jsonl(events))
        self.assertEqual(off.checks[0].status, "disagrees")
        self.assertIn("session accounting", off.disagreements[0])

        opencode = parse("opencode", _text("opencode.jsonl"))
        self.assertEqual([(c.against, c.status) for c in opencode.checks], [("total", "agrees")])
        bumped = _text("opencode.jsonl").replace('"total":11691', '"total":13691')
        self.assertIn("total", parse("opencode", bumped).disagreements[0])
        # Only a gap above 5% is named: 100 on a total of 2000 is exactly 5%, 101 is above it.
        for uncached, status in ((305, "agrees"), (306, "disagrees")):
            edge = _text("opencode.jsonl").replace('"total":11691', '"total":2000').replace(
                '"input":9896', f'"input":{uncached}')
            self.assertEqual(parse("opencode", edge).checks[0].status, status, uncached)
        self.assertEqual(parse("codex", _text("codex.jsonl")).checks, ())


    def test_a_non_object_usage_container_is_unmetered_not_raised(self):
        """Each shape is a real capture with one container replaced by a JSON value that is not
        an object: the eight BG1244 found raising `AttributeError`, then the four containers
        beside them read the same way."""
        def claude(change):
            doc = json.loads(_text("claude.json"))
            change(doc)
            return json.dumps(doc)

        def flat(change):
            def edit(doc):
                del doc["modelUsage"]
                change(doc["usage"])
            return edit

        def stream(name, kind, change):
            events = _lines(name)
            change([e for e in events if e["type"] == kind][-1])
            return _jsonl(events)

        def snapshot(change):
            return stream("copilot.jsonl", "session.usage_checkpoint",
                          lambda e: change(e["data"]["accountingSnapshot"]))

        sonnet = "claude-sonnet-5.5"
        shapes = [
            ("claude", claude(lambda d: d.update(modelUsage={"m": 5})), "modelUsage.m"),
            ("claude", claude(lambda d: d.update(modelUsage=[1])), "modelUsage"),
            ("claude", claude(lambda d: (d.pop("modelUsage"), d.update(usage="x"))), "usage"),
            ("copilot", snapshot(lambda s: s["modelMetrics"].update({sonnet: "x"})),
             f"modelMetrics.{sonnet}"),
            ("copilot", stream("copilot.jsonl", "session.usage_checkpoint",
                               lambda e: e.update(data=[1])), "session.usage_checkpoint.data"),
            ("copilot", snapshot(lambda s: s["tokenDetails"].update(input=4)),
             "accountingSnapshot.tokenDetails.input"),
            ("opencode", stream("opencode.jsonl", "step_finish", lambda e: e.update(part="x")),
             "step_finish.part"),
            ("opencode", stream("opencode.jsonl", "step_finish",
                                lambda e: e["part"]["tokens"].update(cache=[1])), "tokens.cache"),
            # The four containers beside the eight, which raised the same way, then two that
            # were read as absent: a `modelUsage` array, and `tokenDetails` itself.
            ("claude", claude(flat(lambda u: u.update(cache_creation="x"))),
             "usage.cache_creation"),
            ("claude", claude(flat(lambda u: u.update(output_tokens_details=[1]))),
             "usage.output_tokens_details"),
            ("copilot", stream("copilot.jsonl", "session.usage_checkpoint",
                               lambda e: e["data"].update(accountingSnapshot=[1])),
             "data.accountingSnapshot"),
            ("copilot", snapshot(lambda s: s["modelMetrics"][sonnet].update(usage="x")),
             f"modelMetrics.{sonnet}.usage"),
            ("claude", claude(lambda d: d.update(modelUsage=[])), "modelUsage"),
            ("copilot", snapshot(lambda s: s.update(tokenDetails=[1])),
             "accountingSnapshot.tokenDetails"),
        ]
        for harness, text, container in shapes:
            with self.subTest(harness=harness, container=container):
                got = parse(harness, text)
                self.assertFalse(got.metered)
                self.assertEqual(got.unmetered, NO_USAGE)
                self.assertTrue(got.reason.endswith(f": {container} is not a JSON object"),
                                got.reason)
                self.assertEqual([getattr(got, c) for c in COUNTS], [None] * len(COUNTS))
        # The positive control: each builder with no edit still meters.
        self.assertTrue(parse("claude", claude(lambda d: None)).metered)
        self.assertTrue(parse("copilot", snapshot(lambda s: None)).metered)
        self.assertTrue(parse("opencode", stream("opencode.jsonl", "step_finish",
                                                 lambda e: None)).metered)

    def test_an_absent_reasoning_count_is_unreported_not_zero(self):
        """Each capture with its reasoning field removed: the reasoning is None and named in
        `unreported`, while the output it would sit inside is read as captured."""
        claude = json.loads(_text("claude.json"))
        del claude["modelUsage"]["claude-haiku-5-5"]["thinkingTokens"]
        flat = json.loads(_text("claude.json"))
        del flat["modelUsage"]
        del flat["usage"]["output_tokens_details"]["thinking_tokens"]
        # An absent container reads as empty, so with no details at all it is still unreported.
        bare = json.loads(json.dumps(flat))
        del bare["usage"]["output_tokens_details"]
        codex = _lines("codex.jsonl")
        del next(e for e in codex if e["type"] == "turn.completed")["usage"][
            "reasoning_output_tokens"]
        copilot = _lines("copilot.jsonl")
        del next(e for e in copilot if e["type"] == "session.usage_checkpoint")["data"][
            "accountingSnapshot"]["modelMetrics"]["claude-sonnet-5.5"]["usage"]["reasoningTokens"]
        cases = [("claude", json.dumps(claude), 35), ("claude", json.dumps(flat), 35),
                 ("claude", json.dumps(bare), 35),
                 ("codex", _jsonl(codex), 5), ("copilot", _jsonl(copilot), 4)]
        for harness, text, output in cases:
            with self.subTest(harness=harness):
                got = parse(harness, text, model="m")
                self.assertTrue(got.metered, got.reason)
                self.assertIsNone(got.reasoning)
                self.assertEqual(got.unreported, ("reasoning",))
                self.assertEqual(got.output, output)

    def test_the_session_model_is_the_one_with_most_tokens(self):
        """Two models in one Claude Code session: the second carries more tokens in all, but
        fewer input and output tokens, so a model chosen by order, by input or by output is
        the wrong one. Either order names the same model, and the counts are the two summed."""
        haiku = json.loads(_text("claude.json"))["modelUsage"]["claude-haiku-5-5"]
        opus = dict(haiku, inputTokens=1, outputTokens=1, thinkingTokens=0,
                    cacheReadInputTokens=40000, cacheCreationInputTokens=0,
                    cacheCreationEphemeral1hInputTokens=0)
        for order in (("claude-haiku-5-5", "claude-opus-5-5"),
                      ("claude-opus-5-5", "claude-haiku-5-5")):
            doc = json.loads(_text("claude.json"))
            doc["modelUsage"] = {name: {"claude-haiku-5-5": haiku, "claude-opus-5-5": opus}[name]
                                 for name in order}
            with self.subTest(order=order):
                got = parse("claude", json.dumps(doc))
                self._expect(got, model="claude-opus-5-5", model_source="output",
                             input=3, cache_read=51382, cache_write=17126, output=36,
                             reasoning=31)

    def test_a_two_model_session_carries_its_split(self):
        """BG1252 AC1. Two models in one Claude Code session: the `Usage` carries each model's own
        counts, typed here, and every count of the session is the two summed. MUTANTS: the split
        dropped (`by_model` None) or cut to `_largest`'s model alone; one model's counts booked
        under the other; a model's one-hour write or reasoning left off its counts; Copilot's
        split not carried; a split keyed None for a CLI that names no model."""
        haiku = json.loads(_text("claude.json"))["modelUsage"]["claude-haiku-5-5"]
        opus = dict(haiku, inputTokens=1000, outputTokens=2000, thinkingTokens=0,
                    cacheReadInputTokens=0, cacheCreationInputTokens=500,
                    cacheCreationEphemeral1hInputTokens=0)
        doc = json.loads(_text("claude.json"))
        doc["modelUsage"] = {"claude-haiku-5-5": haiku, "claude-opus-5-5": opus}
        got = parse("claude", json.dumps(doc))
        self.assertEqual({
            "claude-haiku-5-5": {"input": 2, "cache_read": 11382, "cache_write": 17126,
                                 "cache_write_1h": 17126, "output": 35, "reasoning": 31},
            "claude-opus-5-5": {"input": 1000, "cache_read": 0, "cache_write": 500,
                                "cache_write_1h": 0, "output": 2000, "reasoning": 0}},
            got.by_model)
        self.assertEqual("claude-haiku-5-5", got.model)
        for k in COUNTS + ("cache_write_1h",):
            self.assertEqual(getattr(got, k), sum(m[k] for m in got.by_model.values()), k)
        # a single-model session carries its one model, Copilot's as Claude Code's
        for harness, name in (("claude", "claude.json"), ("copilot", "copilot.jsonl")):
            with self.subTest(harness=harness):
                one = parse(harness, _text(name))
                self.assertEqual([one.model], list(one.by_model))
                self.assertEqual({k: getattr(one, k) for k in COUNTS + ("cache_write_1h",)},
                                 one.by_model[one.model])
        # a CLI that names no model, or a Claude Code result with no modelUsage, carries none
        self.assertIsNone(parse("cursor", _cursor(0), model="m").by_model)
        bare = json.loads(_text("claude.json"))
        del bare["modelUsage"]
        self.assertIsNone(parse("claude", json.dumps(bare), model="m").by_model)

    def test_the_codex_docstring_names_the_total_tokens_evidence(self):
        """14524 input beside 12288 cached fits either reading; the rollout's `total_tokens`,
        input plus output, decides it, and the docstring must cite that."""
        doc = harness_usage.__doc__
        codex = doc[doc.index("* Codex CLI:"):doc.index("* Copilot CLI:")]
        self.assertIn("total_tokens", codex)
        self.assertIn("14529", codex)
        raw = next(e for e in _lines("codex.jsonl") if e["type"] == "turn.completed")["usage"]
        self.assertEqual(raw["input_tokens"] + raw["output_tokens"], 14529)
        self.assertIn(str(raw["input_tokens"] + raw["cached_input_tokens"]
                          + raw["output_tokens"]), codex)

if __name__ == "__main__":
    unittest.main()
