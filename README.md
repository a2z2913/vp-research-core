# VP Research Core

`vp-research-core` is a small, credential-free reference implementation of the
matching arithmetic used by the pinned Voters Pulse prototype. It exists so the
method can be inspected, tested, and discussed without publishing the Voters
Pulse product, its private data, or its operating systems.

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
- schemas, synthetic fixtures, regression tests, and a no-network evaluator.

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

Only the code and documentation identified in
[`RIGHTS_REVIEW.md`](RIGHTS_REVIEW.md) and the complete
[`FILE_INVENTORY.md`](FILE_INVENTORY.md) are offered under MIT. The synthetic
fixtures are separately dedicated under CC0 1.0. No rights are granted to the
Voters Pulse name, logos, private product, or excluded data.

The repository intentionally excludes real candidate records, real question
text, campaign/news passages, donor rows, third-party datasets, voter answers,
addresses, recordings, logs, sessions, personal analytics, secrets, internal
strategy, partner material, deployment configuration, and the branded UI. See
[`SCOPE_AND_LIMITATIONS.md`](SCOPE_AND_LIMITATIONS.md) for the full boundary.

## Provenance

The reference method is derived from Sharif Amlani's MIT-licensed prototype at
commit [`2122f2545e652970f15d865986896f783e9a05e2`](https://github.com/sharifamlani/hack-for-humanity-team/commit/2122f2545e652970f15d865986896f783e9a05e2),
especially `lib/match.ts` and `lib/questions.ts`. The exact upstream copyright
notice is preserved in `LICENSE` and `THIRD_PARTY_NOTICES.md`.

The private Voters Pulse production repository is referenced only by its
verified revision `3f2e95f953198f46f12e205ea8a42960b993b785`; none of its private
history is copied here. See [`PROVENANCE.md`](PROVENANCE.md).

## Contributing

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md). Contributions must remain
reproducible with synthetic data, disclose provenance, and keep method changes
separate from claims of validation.

