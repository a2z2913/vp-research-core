# Provenance manifest

Verified on 2026-10-28.

| Role | Repository | Pinned revision | Use here |
|---|---|---|---|
| Upstream matching prototype | `sharifamlani/hack-for-humanity-team` | `2122f2545e652970f15d865986896f783e9a05e2` | MIT-licensed method and implementation reference |
| Voters Pulse production reference | `a2z2913/voterspulse` | `3f2e95f953198f46f12e205ea8a42960b993b785` | Revision identifier only; no private history or source copied |

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
Synthetic fixtures replace every real candidate, voter, party, question, and
record. Model calls and dataset acquisition are not reproduced; their outputs
are accepted only as explicitly labelled inputs.

## Methodology paper

The separate document titled *VP DeepDive Matching Methodology* was not copied
or relicensed. It is a methodological reference with source-level assertions,
not empirical validation. Publication and content licensing must be resolved
outside this software repository.

