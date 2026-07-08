"""Held-back acceptance suite for the brownfield-pagination fixture. The agent under
test never sees this file - it is copied in only for scoring, after the arm declares done.
"""
from __future__ import annotations

import sys

import pytest


class TestPaginate:
    @pytest.mark.parametrize("count,page_size", [
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
        (9, 3), (10, 3), (11, 3), (1, 1), (7, 7), (7, 4),
    ])
    def test_every_item_appears_exactly_once_in_order(self, paginate, count, page_size) -> None:
        items = list(range(count))
        total_pages = (count + page_size - 1) // page_size if count else 0
        collected: list = []
        for page in range(1, total_pages + 1):
            collected.extend(paginate(items, page, page_size))
        assert collected == items, (
            f"count={count} page_size={page_size}: expected {items}, got {collected}")

    def test_page_beyond_last_is_empty(self, paginate) -> None:
        items = list(range(10))
        assert paginate(items, 5, 3) == []

    def test_empty_items_any_page_is_empty(self, paginate) -> None:
        assert paginate([], 1, 3) == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
