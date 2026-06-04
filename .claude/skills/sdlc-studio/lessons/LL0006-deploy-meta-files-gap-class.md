---
id: LL0006
title: Deploy meta-files gap – a new boot-read file must be added to EVERY deploy path
tags: [deploy, packaging, gap-class]
added: 2026-06-03
origin: a boot-read meta-file missing from a systemd deploy path
---

**Lesson.** When you add any new repo-root (or otherwise out-of-`src`) file that the app **reads at boot/runtime**, every packaging + deploy path needs it added independently – Docker `COPY` (+ `.dockerignore` exception), each host rsync/copy script, every box. Missing one produces a box that boots without the file and fails only in that environment.

**Why / what it cost.** A boot-read meta-file shipped in the image but was absent from a parallel systemd deploy path → that box silently missing it; mixed-version production.

**How to apply.** "Does the running app read this at boot?" → enumerate the deploy paths and add it to each in the same change; a smoke check that asserts the file is present post-deploy.

**Generalises to.** Any service with more than one packaging/deploy path (container + bare host, multiple boxes, multiple CI artifacts).
