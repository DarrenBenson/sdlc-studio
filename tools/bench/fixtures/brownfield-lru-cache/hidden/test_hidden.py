"""Held-back acceptance suite for the brownfield-lru-cache fixture. The agent under test
never sees this file - it is copied in only for scoring, after the arm declares done.
"""
from __future__ import annotations

import sys


class TestLRUCache:
    def test_get_protects_an_entry_from_eviction(self, lru_cache_cls) -> None:
        c = lru_cache_cls(3)
        c.put("a", 1)
        c.put("b", 2)
        c.put("c", 3)
        c.get("a")          # "a" is now the most recently used
        c.put("d", 4)       # cache full -> must evict the true LRU entry, which is "b"
        assert c.get("a") == 1, "a was just read - it must not be evicted"
        assert c.get("b") is None, "b is the true least-recently-used entry and must be evicted"
        assert c.get("c") == 3
        assert c.get("d") == 4

    def test_put_on_existing_key_also_counts_as_recent_use(self, lru_cache_cls) -> None:
        c = lru_cache_cls(2)
        c.put("a", 1)
        c.put("b", 2)
        c.put("a", 10)      # re-put "a" - it is now most recently used
        c.put("c", 3)       # must evict "b", not "a"
        assert c.get("a") == 10
        assert c.get("b") is None
        assert c.get("c") == 3

    def test_plain_insertion_order_eviction_without_any_reads(self, lru_cache_cls) -> None:
        c = lru_cache_cls(2)
        c.put("x", 1)
        c.put("y", 2)
        c.put("z", 3)       # no gets at all - "x" is oldest, must be evicted
        assert c.get("x") is None
        assert c.get("y") == 2
        assert c.get("z") == 3

    def test_get_on_missing_key_returns_none_without_side_effects(self, lru_cache_cls) -> None:
        c = lru_cache_cls(2)
        c.put("a", 1)
        assert c.get("missing") is None
        c.put("b", 2)
        c.put("c", 3)       # cache full: "a" (never touched again) should be evicted
        assert c.get("a") is None
        assert c.get("b") == 2
        assert c.get("c") == 3


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__]))
