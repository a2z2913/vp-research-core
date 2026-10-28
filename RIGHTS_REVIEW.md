# Rights and release review

Review date: 2026-10-28.

`FILE_INVENTORY.md` lists every intended initial-release path and its
classification. No unlisted file is approved for publication by this review.

## Included-file decision

| Paths | Contents | Rights basis | Public license |
|---|---|---|---|
| `vp_research_core/**`, `scripts/**`, `tests/**` | Reference implementation and tooling | New work plus a derivative of MIT-licensed upstream code | MIT |
| `schemas/**` | Original machine-readable interface descriptions | New work | MIT |
| `README.md`, `SCOPE_AND_LIMITATIONS.md`, `PROVENANCE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `RIGHTS_REVIEW.md`, `THIRD_PARTY_NOTICES.md`, `CITATION.cff` | Original documentation and metadata | New work; upstream facts attributed | MIT |
| `fixtures/synthetic_*.json` | Entirely fabricated examples and expected outputs | New synthetic material; no real people, campaigns, voters, or addresses | CC0-1.0 |
| `.github/workflows/test.yml`, `.gitignore`, `pyproject.toml` | Build and repository configuration | New work | MIT |
| `LICENSE` | MIT text with upstream notice preserved and a contributor notice added | Upstream MIT requirement | MIT |

To the extent legally possible, the contributors dedicate the three
`fixtures/synthetic_*.json` files to the public domain under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
This dedication does not cover source datasets or any real-world record.

## Not included; no blanket relicensing

Real candidate records, question wording, campaign/news material, quotes,
embeddings, donor records, third-party datasets, user information, private
product source, branded assets, partner files, and the methods paper are not
present. They require item-specific provenance and rights review before any
future distribution.

DIME v4 content is governed by ODC-BY 1.0. This repository describes the role of
a CFscore and includes fabricated numeric values only; it does not redistribute
DIME records or apply MIT/CC0 to them.

## Privacy and secret review

The release contains no real voter or household fixtures, addresses, recordings,
logs, sessions, credentials, environment files, private keys, or production
configuration. `scripts/release_check.py` enforces forbidden file types and
scans tracked content for common credential formats before release. It is a
release safeguard, not a substitute for human rights and privacy review.

Review outcome: the listed files are suitable for public release under the
stated boundaries. Any later file must be classified in this table or receive a
separate review before publication.

