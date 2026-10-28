# Provenance manifest

Verified on 2026-10-28.

| Role | Repository | Pinned revision | Use here |
|---|---|---|---|
| Upstream matching prototype | `sharifamlani/hack-for-humanity-team` | `2122f2545e652970f15d865986896f783e9a05e2` | MIT-licensed method and implementation reference |
| Voters Pulse production reference | `a2z2913/voterspulse` | `3f2e95f953198f46f12e205ea8a42960b993b785` | Identifier-level electorate logic and sanitized rule records; no private history, UI, address pipeline, or operations copied |

## Data snapshot inputs

| Input | Pinned state | Public transformation |
|---|---|---|
| `VotersPulse Website Sources+Links.xlsx` | Drive modified `2026-10-28T15:39:55.258Z`; downloaded SHA-256 `3ce56407f1256ed4cbcae050a1c2f94a147332ffcb0cfc91e7f8b0ed980bdccd` | Selected public source/candidate metadata only |
| Production ballot catalog | revision `3f2e95f953198f46f12e205ea8a42960b993b785` | Contest scope and match rules only; candidates, notes, retention, origin, rank, and presentation removed |
| Corrections tracker | modified `2026-10-28T14:36:54.909Z`; latest reviewed row `2026-10-28 10:36 EDT` | Aggregate QA counts and limitations only; no addresses, raw notes, or logs |

The workbook internally reports inventory timestamp
`2026-10-23T12:00:00Z` and generation commit
`f983abb898a38f259b4af6cad046186754dbfee2`. Later source-specific workbook
reviews are preserved by the Drive modified time and downloaded-byte hash; the
internal summary is not presented as a newer full rebuild.

## Upstream files consulted

- `LICENSE`: upstream MIT terms and exact copyright notice.
- `lib/match.ts`: evidence hierarchy, weighting, placement, normalization,
  minimum-evidence, and final score arithmetic.
- `lib/questions.ts`: source categories and placement-source order.
- `lib/raceMatch.ts`: ranking, three-point tie threshold, and thin-evidence
  presentation rule.
- `data/questions.json`: reviewed-status count only; no question text copied.
- `scripts/build-records.mjs`: source-role confirmation only; no records or data
  copied.

## Deliberate transformations

The implementation is expressed as a dependency-free Python library instead of
copying the Next.js application. Names and structures are simplified for
inspection, while the consequential formulas and source order are retained.
In the matching-method fixtures, synthetic values replace every real voter,
party, question, position, and evidence record. The separate candidate-source
registry contains public identity/source metadata only. Model calls and dataset
acquisition are not reproduced; their outputs are accepted only as explicitly
labelled inputs.

For the source export, `scripts/export_research_data.py` reads the workbook as a
ZIP/XML package without executing formulas. It selects only approved columns.
The candidate stable ID is the first 16 hexadecimal characters of SHA-256 over
public identity fields; it prevents accidental collisions and is not an
anonymization technique. Candidate positions are set to `unknown` for every
row. Source records omit internal build-use fields, page/usage counts, follow-up
notes, and unconfirmed candidate URLs.

The electorate export selects contest scope, district metadata, source URLs,
and match rules. It omits candidate arrays and product/presentation fields. The
Python `match_rule` implementation follows the tri-state behavior of
`source/netlify/functions/lib/match-ballot.mjs` at the pinned revision.

## Methodology paper

The separate document titled *VP DeepDive Matching Methodology* was not copied
or relicensed. It is a methodological reference with source-level assertions,
not empirical validation. Publication and content licensing must be resolved
outside this software repository.

