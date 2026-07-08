# CR: Relax duplicate-customer detection

Support reports false negatives in duplicate-customer detection caused
by email case and surrounding-whitespace differences: the same person
signing up as `ada@example.com` and `"Ada@Example.com "` is treated as
two customers.

## Change

Change duplicate detection (SPEC R3) so that the email comparison is
case-insensitive and ignores surrounding whitespace. Name comparison
is unchanged.

Update the spec to match.

## Constraints

All other validation behaviour must be preserved.
