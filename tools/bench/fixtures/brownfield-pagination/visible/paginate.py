"""Pagination helper used by the results list view."""
from __future__ import annotations


def paginate(items: list, page: int, page_size: int) -> list:
    """Return the 1-indexed `page` of `items`, `page_size` items per page."""
    total_pages = (len(items) + page_size - 1) // page_size if items else 0
    start = (page - 1) * page_size
    end = start + page_size
    if page == total_pages:
        # last-page special case: clamp to the true end of the list
        end = len(items)
        start = end - page_size
    return items[start:end]
