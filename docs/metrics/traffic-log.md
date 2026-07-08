# GitHub traffic log - DarrenBenson/sdlc-studio

Manual snapshots of GitHub repository traffic. **GitHub only retains traffic for a
rolling 14-day window**, so this log is the only durable record - capture it before the
window rolls off. Newest snapshot first.

Pull the numbers with:

```bash
gh api repos/DarrenBenson/sdlc-studio/traffic/views
gh api repos/DarrenBenson/sdlc-studio/traffic/clones
gh api repos/DarrenBenson/sdlc-studio/traffic/popular/referrers
gh api repos/DarrenBenson/sdlc-studio/traffic/popular/paths
gh repo view DarrenBenson/sdlc-studio --json stargazerCount,forkCount,watchers
```

**Reading the numbers:** clones are dominated by automated traffic (CI, agent-skill
installers, mirrors) and routinely exceed views - treat them as a soft signal, not
"downloads". Git has no true download counter, and no GitHub Releases have been cut
(the v4 freeze means the first release is still ahead), so there are zero release-asset
downloads to report. Views (especially uniques) are the cleaner human signal.

---

## 2026-07-08 snapshot (window 2026-06-24 -> 2026-07-07)

| Metric | Total | Unique |
| --- | --- | --- |
| Views | 437 | 105 |
| Clones | 1,072 | 264 |

**All-time:** 16 stars, 3 forks, 2 watchers. Repo public; created 2026-01-17.

**Top referrers (14d):** Google 146, Bing 18, github.com 15, claude.ai 15,
chatgpt.com 14, Brave 13, DuckDuckGo 8.

**Top paths (14d):** Overview 169; skill source trees (`/sdlc-studio`,
`/.claude/skills/sdlc-studio`) 14 each; `docs/INSTALL.md` 12; `docs/` tree 9.

**Notes:**

- Clones (1,072 / 264 unique) far exceed views (437 / 105 unique) - unique cloners >
  unique visitors, the signature of automated rather than human traffic. Clone batches:
  296 on 06-24, then ~160-175/day across 07-04 -> 07-06.
- One bot-ish view spike: 07-03 logged 121 views from only 12 uniques.
- LLM referrers present: claude.ai (15) + chatgpt.com (14) sent ~29 views between them,
  consistent with the agent-discoverability surface (`llms.txt`, For-agents README block).
