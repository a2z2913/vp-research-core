# Geographic data and crosswalk policy

`data/geographic_sources.csv` is a 390-record view of the public source
registry. It points to government election/GIS pages and services used for
district, precinct, or address matching. It does not copy their geometry,
address indexes, voter records, or provider responses.

## Why the repository links instead of redistributing geometry

Source availability is not the same as redistribution permission. Each
publisher may impose different attribution, access, currency, or reuse terms.
Until a source-specific review establishes compatible rights, researchers
should retrieve the source directly and retain its own terms rather than place
its bytes under MIT or CC BY.

For every downloaded source, record at minimum:

- registry `source_id`, canonical URL, publisher, and retrieval timestamp;
- response checksum, format, coordinate reference system, and layer/table ID;
- boundary vintage and effective start/end dates;
- election date or cycle when the source is election-specific;
- provider license/terms and required attribution;
- whether the identifiers are election precincts, precinct splits, Census
  voting districts, legislative districts, or another geography.

Census voting districts are not assumed to be current election precincts.
Similarly, a precinct number without its publisher/source URL and election
scope is not a portable identifier.

## Crosswalk behavior

The schema in `schemas/crosswalk.schema.json` models a single edge from one
published identifier to another. Repeated rows are intentional: a split may map
to multiple districts and a district may receive multiple splits.
`resolve_crosswalk()` returns every applicable row from one boundary vintage.
It returns `unresolved` when applicable rows mix vintages and `out_of_scope`
when dates or election scope do not match.

Only synthetic crosswalk rows are included in this release. No real crosswalk
bytes were published because their source-specific redistribution terms and
complete vintage metadata were not established file by file. This is an
explicit omission, not an empty-data or universal-coverage claim.
