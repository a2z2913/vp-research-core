# VP Research Core

`vp-research-core` is a credential-free research release of the reproducible
parts of Voters Pulse: the pinned matching arithmetic, a tri-state electorate
rule evaluator, and a curated election-source registry. It exists so researchers
can inspect sources and reproduce identifier-level matching without publishing
the Voters Pulse product, branding, private user data, or operating systems.

This repository is research software. It does **not** tell anyone how to vote,
does not claim independent empirical validation, and does not claim that a
Miami-Dade pilot generalizes nationwide.

## What is here

- the position-source hierarchy: recorded vote, candidate statement/lean,
  party proxy, then missing;
- agreement scoring in which candidate-specific evidence has weight `1.0` and
  a clearly labelled party proxy has weight `0.5`;
- voter and candidate placement on a rough `[-1, 1]` ideological line;
- the source order for candidate placement: DW-NOMINATE, transformed CFscore,
  words estimate, then question positions;
- line closeness and the final mean of the available agreement and line parts;
- missingness, minimum-evidence, tie, and thin-evidence rules;
- tri-state precinct, split, municipality, and district rule evaluation;
- lossless one-to-many crosswalk handling with effective dates, election dates,
  and boundary vintages;
- 1,900 election-source records, including a 390-record geographic-source view;
- 3,117 candidate identity/source-review records, including 1,116 records with
  a confirmed campaign site or official candidate profile;
- 2,463 sanitized electorate rules with candidates and presentation content
  removed;
- schemas, synthetic fixtures, sanitized QA counts, regression tests, and a
  no-network evaluator.

The candidate export is a source registry, not a candidate-position dataset.
Every row is explicitly labelled `position_evidence=unknown`; researchers must
not treat a campaign link, party, or identity record as evidence of a position.

The consequential constants are in
[`fixtures/synthetic_method.json`](fixtures/synthetic_method.json), while the
defaults in the code preserve the pinned implementation. Changing those values
creates a different method and must not be described as a validated update.

## Reproduce the synthetic reference run

Python 3.11 or later is sufficient; there are no runtime dependencies and no
credentials are used.

```bash
python3 -m unittest discover -s tests -v
python3 scripts/evaluate.py fixtures/synthetic_input.json
python3 scripts/release_check.py
```

The evaluator emits JSON. The test suite compares its result with
`fixtures/synthetic_expected.json` and separately covers hierarchy,
missingness, party-proxy weighting, CFscore conversion, ranking, and ties.
It also covers precinct-source binding, unknown splits, overlapping districts,
conflicting boundaries, municipality aliases, election dates, boundary
vintages, and one-to-many crosswalks.

## Research data snapshot

| File | Records | What it contains |
|---|---:|---|
| `data/source_registry.csv` | 1,900 | Public election/GIS source metadata and provenance |
| `data/geographic_sources.csv` | 390 | Registry subset relevant to district, precinct, or address matching |
| `data/candidate_sources.csv` | 3,117 | Candidate identity, office/scope, review outcome, official source, and confirmed campaign URL when available |
| `data/electorate_rules.jsonl` | 2,463 | Contest scope and identifier-level match rules, with candidate arrays removed |
| `data/qa_summary.json` | 3 checks | Sanitized pass/fail/unresolved counts and explicit limitations |

Hashes, source revisions, workbook metadata, exclusions, and exact counts are in
[`data/export_manifest.json`](data/export_manifest.json). The export script is
included for auditability, but refreshing the data requires separately
authorized local inputs; ordinary use and all tests require no credentials.

## Geography utility

The public geography code does **not** accept an address, call a geocoder, or
ship boundary polygons. It evaluates identifiers already resolved by a cited
source. `match_rule()` returns `True`, `False`, or `None`; `None` means the
available evidence cannot establish eligibility. Source mismatches, missing
precinct splits, conflicting boundaries, and unresolved municipalities remain
unknown.

`resolve_crosswalk()` keeps every applicable target row from one boundary
vintage. It never selects the first result from a split or many-to-many mapping.
Census voting districts must not be treated as current election precincts
without source-specific verification.

The 2026 rule catalog records the election date and source revision. Its source
records do not consistently carry effective-date or boundary-vintage fields,
so those fields are exported as `null` rather than inferred. Researchers must
resolve that gap from the cited authoritative source before longitudinal or
cross-election use.

See [`GEOGRAPHIC_DATA.md`](GEOGRAPHIC_DATA.md) for the source-download and
crosswalk policy, including why this release links to geographic sources rather
than relicensing their geometry.

## Method in plain language

For each answered question, candidate-specific evidence is preferred to a
party proxy. Missing candidate positions and voter answers of `unsure` or
`skip` are excluded from the agreement denominator. Party-proxy comparisons
enter both the agreement numerator and denominator at half weight.

The rough question index assigns `-1` to a configured left answer and `+1` to
the other answer, averages the answered items, and multiplies by `0.5`. It needs
at least two usable answers. Candidate placement uses the first available source
in this order:

1. first-dimension DW-NOMINATE;
2. CFscore transformed as `clamp(-1, 1, -0.098 + 0.456 * CFscore)`;
3. a separately generated words estimate supplied as data;
4. the same rough question index over candidate positions.

Line closeness is `1 - min(abs(voter_x - candidate_x), 1)`. When both agreement
share and line closeness exist, the final score is their arithmetic mean. When
only one exists, that part is the score. A single comparison without a line
placement is deliberately not reported as a match.

## Important boundaries

Only the code, schemas, and documentation identified in
[`RIGHTS_REVIEW.md`](RIGHTS_REVIEW.md) and the complete
[`FILE_INVENTORY.md`](FILE_INVENTORY.md) are offered under MIT. Synthetic
fixtures are dedicated under CC0 1.0. The original selection, arrangement, and
annotations in the curated `data/` files are offered under CC BY 4.0, subject to
the boundary in [`DATA_LICENSE.md`](DATA_LICENSE.md). Linked third-party
content is not copied or relicensed.

The repository intentionally excludes candidate-position claims, real question
text, campaign/news passages, donor rows, third-party dataset bytes, voter
answers, addresses, coordinates, recordings, logs, sessions, personal
analytics, secrets, internal strategy, partner material, deployment
configuration, and the branded UI. See
[`SCOPE_AND_LIMITATIONS.md`](SCOPE_AND_LIMITATIONS.md) for the full boundary.

## Provenance

The reference method is derived from Sharif Amlani's MIT-licensed prototype at
commit [`2122f2545e652970f15d865986896f783e9a05e2`](https://github.com/sharifamlani/hack-for-humanity-team/commit/2122f2545e652970f15d865986896f783e9a05e2),
especially `lib/match.ts` and `lib/questions.ts`. The exact upstream copyright
notice is preserved in `LICENSE` and `THIRD_PARTY_NOTICES.md`.

The identifier-level electorate logic and sanitized rule export are derived
from the verified Voters Pulse revision
`3f2e95f953198f46f12e205ea8a42960b993b785`. No product UI, address/geocoding
pipeline, deployment configuration, private history, or user record is copied.
See [`PROVENANCE.md`](PROVENANCE.md).

## Contributing

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions must remain
reproducible with synthetic data, disclose provenance, and keep method changes
separate from claims of validation.

