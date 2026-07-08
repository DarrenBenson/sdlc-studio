# Ticket: last page of results is sometimes wrong

Users report that the last page of a paginated results list sometimes shows an item
they already saw on the previous page, and other times seems to be missing an item
entirely. It depends on how many total results there are.

**Fix `paginate(items, page, page_size)` in `paginate.py`** so that:

- Pages are 1-indexed (the first page is `page=1`).
- Every item in `items` appears on exactly one page, across all pages, in original order.
- Requesting a page number beyond the last page returns an empty list.

Please also make sure the fix holds regardless of whether the total item count happens to
divide evenly by the page size.
