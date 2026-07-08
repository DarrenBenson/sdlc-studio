"""A small in-memory LRU cache."""
from __future__ import annotations


class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._data: dict = {}

    def get(self, key):
        if key not in self._data:
            return None
        return self._data[key]

    def put(self, key, value) -> None:
        if key in self._data:
            del self._data[key]
        self._data[key] = value
        if len(self._data) > self.capacity:
            oldest = next(iter(self._data))
            del self._data[oldest]
