---
id: LL0003
title: Config-schema vs type alignment – strict validators silently strip unknown fields
tags: [schema, validation, config, bug-class]
added: 2026-06-03
origin: a strict-validator API where newly added fields were silently stripped (hit repeatedly)
---

**Lesson.** When a config/message validator runs `additionalProperties: false` (AJV, JSON-Schema, protobuf-strict, etc.), any field present in the TS type but **absent from the schema is silently stripped on load/reload** – the write succeeds, the read returns nothing, no error. Every field added to a type MUST be added to its validation schema in the same change.

**Why / what it cost.** Three separate live regressions where a feature's field round-tripped in code but vanished after a config reload (PATCH echoed 200 from the pre-reload object, masking it). Durable features silently never persisted.

**How to apply.** Treat schema ⊇ type as an invariant; add a test that the schema accepts every type-producible value AND still rejects a genuinely-unknown field. Consider a type-driven schema generator to kill the class.

**Generalises to.** Any system with a strict-validated wire/config format mirrored by a separate hand-maintained type.
