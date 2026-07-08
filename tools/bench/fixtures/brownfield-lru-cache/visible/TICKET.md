# Ticket: cache is evicting entries that were just read

Users report that an entry they just looked up (via `get`) a moment ago sometimes gets
evicted from the cache immediately afterward, as if the lookup never happened.

**Fix `LRUCache` in `lru_cache.py`** so that both `get()` and `put()` count as "use" for
recency purposes: when the cache is full and a new key is inserted, the entry evicted must
be the one that was least recently used - by either a read or a write - not simply the one
inserted longest ago.
