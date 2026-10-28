# Scope and limitations

## Included

- Deterministic score and placement functions.
- Explicit source, proxy, missingness, normalization, and minimum-evidence
  rules from the pinned upstream implementation.
- Machine-readable schemas.
- Fabricated questions, parties, candidates, voter answers, and expected
  outputs that do not describe real people or elections.
- Offline tests and evaluation tooling.
- Provenance, rights, contribution, citation, and third-party notices.

## Excluded and protected

The following are outside this repository and outside its MIT grant:

- the Voters Pulse product, brand, logos, UI, hosting and deployment system;
- user answers, addresses, voice recordings, logs, session data, and personal
  analytics;
- API keys, credentials, access controls, private partner material, internal
  strategy, and production configuration;
- real candidate records, real interview questions, candidate/campaign/news
  text, quotes, embeddings, model outputs, donor rows, and polling-place data;
- third-party datasets, including DIME v4 data governed by ODC-BY 1.0;
- the Voters Pulse methods paper, whose publication and content license must be
  decided separately;
- future question or candidate-mapping revisions that Sharif Amlani has not yet
  published and that were not present at the pinned revision.

## What the code does not establish

Passing tests establishes that this implementation follows the documented
arithmetic on synthetic inputs. It does not establish accuracy, fairness,
predictive validity, ideological construct validity, external validity,
candidate completeness, or suitability for an election decision.

At the pinned upstream revision, ten active questions were marked
`reviewed: false`. Their text is omitted here. The project discussion concerned
a Miami-Dade pilot. This repository therefore makes no nationwide-coverage or
validated-questionnaire claim.

Words estimates and party proxies are inputs, not ground truth. A words
estimate can come from a model and a party proxy is explicitly a fallback
guess. Consumers should expose those labels and uncertainty rather than display
all scores as equally supported.

## Method-change policy

Constants, source priority, question orientation, weights, thresholds, and
normalization rules are part of the method. A change to any of them must:

1. be isolated in a reviewable change;
2. update fixtures, regression tests, provenance, and limitations;
3. state whether it is a proposed method or a reproduction of the pinned one;
4. avoid validation claims unless supported by a separately documented study.

