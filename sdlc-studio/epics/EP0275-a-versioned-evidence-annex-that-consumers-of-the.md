# EP0275: A versioned evidence annex that consumers of the committed sprint records can parse against

> **Status:** Draft
> **Derived Point Total:** 15
> **Parent:** CR0609
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0609. Delivers the work CR0609 requested.

## Story Breakdown

- [ ] [US0992: A consumer parses the report of record against a published, versioned annex](../stories/US0992-a-consumer-parses-the-report-of-record-against.md)
- [ ] [US0993: A consumer recomputes a report's fingerprint from the annex alone](../stories/US0993-a-consumer-recomputes-a-report-s-fingerprint-from.md)
- [ ] [US0994: A consumer reads the committed run record, awaiting signature, sealed or stopped, against the annex](../stories/US0994-a-consumer-reads-the-committed-run-record-awaiting.md)
- [ ] [US0995: A consumer reads the lesson class store, the evidence logs and the four ledgers against the annex](../stories/US0995-a-consumer-reads-the-lesson-class-store-the.md)
- [ ] [US0996: Each committed report and run record states the evidence-schema version it was written under](../stories/US0996-each-committed-report-and-run-record-states-the.md)

## Acceptance Criteria (Epic Level)

- [ ] A `reference-evidence-schema.md` documents RPT schema 1 and 2 with a section catalogue marking each section required or optional, the RUN record, `lessons.jsonl`, the evidence JSONL lines and the four table layouts
- [ ] The fingerprint algorithm is stated canonically enough that a consumer can recompute it, and a test recomputes it from the annex text against a filed report
- [ ] An `evidence_schema` version is stamped where a consumer can read it without running the skill
- [ ] A conformance test fails when an emitted report, run record or lessons line drifts from the annex
- [ ] The annex states a compatibility policy: an added field is minor, a removed or renamed one is major and carries a migration note

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
