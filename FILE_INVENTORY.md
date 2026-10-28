# Public release file inventory

Reviewed on 2026-10-28. This is the complete intended public tree for release
0.2.0. Generated caches and local Git metadata are not release files.

| Path | Purpose | License/classification |
|---|---|---|
| `.github/workflows/test.yml` | Offline CI | MIT code/config |
| `.gitignore` | Local exclusion rules | MIT config |
| `CITATION.cff` | Citation metadata | MIT documentation |
| `CONTRIBUTING.md` | Contribution and data-boundary rules | MIT documentation |
| `DATA_LICENSE.md` | CC BY 4.0 data boundary and attribution | MIT documentation/licensing notice |
| `FILE_INVENTORY.md` | This release inventory | MIT documentation |
| `GEOGRAPHIC_DATA.md` | Source-download, licensing, vintage, and crosswalk policy | MIT documentation |
| `LICENSE` | MIT grant and preserved notices | MIT license text |
| `PROVENANCE.md` | Pinned sources and transformations | MIT documentation |
| `README.md` | Scope, method, and usage | MIT documentation |
| `RIGHTS_REVIEW.md` | File-class rights decision | MIT documentation |
| `SCOPE_AND_LIMITATIONS.md` | Included/excluded boundary and non-claims | MIT documentation |
| `SECURITY.md` | Security and privacy reporting policy | MIT documentation |
| `THIRD_PARTY_NOTICES.md` | Attribution and non-redistribution notices | MIT documentation |
| `data/candidate_sources.csv` | 3,117 public candidate identity/source-review records; no positions or internal notes | CC BY 4.0 curated data |
| `data/electorate_rules.jsonl` | 2,463 sanitized identifier-level electorate rules; no candidate arrays | CC BY 4.0 curated data |
| `data/export_manifest.json` | Input versions, exclusions, counts, and file hashes | CC BY 4.0 data metadata |
| `data/geographic_sources.csv` | 390-record geographic-source view of the registry | CC BY 4.0 curated data |
| `data/qa_summary.json` | Sanitized QA denominators, results, sources, and limitations | CC BY 4.0 data metadata |
| `data/source_registry.csv` | 1,900 public election/GIS source records | CC BY 4.0 curated data |
| `fixtures/synthetic_crosswalk.json` | Fabricated split-to-district one-to-many rows | CC0-1.0 synthetic data |
| `fixtures/synthetic_electorate_rules.json` | Fabricated electorate rules | CC0-1.0 synthetic data |
| `fixtures/synthetic_expected.json` | Fabricated regression output | CC0-1.0 synthetic data |
| `fixtures/synthetic_geography.json` | Fabricated resolved identifiers; no address or coordinates | CC0-1.0 synthetic data |
| `fixtures/synthetic_input.json` | Fabricated race/evidence/voter input | CC0-1.0 synthetic data |
| `fixtures/synthetic_method.json` | Fabricated question identifiers plus pinned constants | CC0-1.0 synthetic data |
| `pyproject.toml` | Python package metadata | MIT code/config |
| `schemas/candidate.schema.json` | Candidate-evidence interface | MIT code/schema |
| `schemas/candidate_source.schema.json` | Candidate source-review interface | MIT code/schema |
| `schemas/crosswalk.schema.json` | Dated, versioned crosswalk interface | MIT code/schema |
| `schemas/electorate_record.schema.json` | Sanitized electorate-record wrapper and provenance fields | MIT code/schema |
| `schemas/electorate_rule.schema.json` | Tri-state electorate rule interface | MIT code/schema |
| `schemas/geography.schema.json` | Already-resolved election-geography interface | MIT code/schema |
| `schemas/input.schema.json` | Evaluation-input interface | MIT code/schema |
| `schemas/method.schema.json` | Method-configuration interface | MIT code/schema |
| `schemas/source_registry.schema.json` | Election-source registry interface | MIT code/schema |
| `scripts/evaluate.py` | Source-checkout CLI wrapper | MIT code |
| `scripts/export_research_data.py` | Deterministic, field-limited local export tool | MIT code |
| `scripts/release_check.py` | Secret/privacy artifact safeguard | MIT code |
| `tests/test_geography.py` | Tri-state, split, overlap, and crosswalk tests | MIT code |
| `tests/test_data_snapshot.py` | Snapshot hashes, counts, data-boundary, and QA-denominator tests | MIT code |
| `tests/test_matching.py` | Offline regression and rule tests | MIT code |
| `vp_research_core/__init__.py` | Public Python exports | MIT code |
| `vp_research_core/evaluate.py` | JSON evaluator | MIT code |
| `vp_research_core/geography.py` | Identifier-level electorate and crosswalk logic | MIT code |
| `vp_research_core/matching.py` | Deterministic reference implementation | MIT code |

No binary dataset, geometry, paper, user/address record, product UI, deployment
file, credential, private workbook, raw QA log, or private Voters Pulse history
is in this inventory. The public factual registries contain no linked-source
content and are licensed only within the boundary in `DATA_LICENSE.md`.

