# Scope and limitations

## Included

- Deterministic score and placement functions.
- Explicit source, proxy, missingness, normalization, and minimum-evidence
  rules from the pinned upstream implementation.
- Machine-readable schemas.
- Fabricated questions, parties, candidates, voter answers, and expected
  outputs that do not describe real people or elections.
- Public election-source metadata with stable source IDs, official URLs,
  jurisdictions, authority classes, and recorded check dates.
- Candidate identity/source-review metadata: public name, office/scope, review
  outcome, official election record, and a confirmed campaign URL when one was
  independently reviewed.
- Sanitized electorate rules and reusable tri-state matching for already
  resolved precinct, split, municipality, and district identifiers.
- Sanitized QA counts with denominators, failures/unresolved cases, source
  versions, code revisions, and explicit limitations.
- Offline tests and evaluation tooling.
- Provenance, rights, contribution, citation, and third-party notices.

## Excluded and protected

The following are outside this repository and outside its MIT grant:

- the Voters Pulse product, brand, logos, UI, hosting and deployment system;
- user answers, addresses, voice recordings, logs, session data, and personal
  analytics;
- API keys, credentials, access controls, private partner material, internal
  strategy, and production configuration;
- candidate positions, endorsements, party-proxy claims, real interview
  questions, campaign/news text, quotes, embeddings, model outputs, donor rows,
  and polling-place/address records;
- third-party datasets, including DIME v4 data governed by ODC-BY 1.0;
- the Voters Pulse methods paper, whose publication and content license must be
  decided separately;
- future question or candidate-mapping revisions that Sharif Amlani has not yet
  published and that were not present at the pinned revision.

The public mapping utility is not an address-to-district service. It does not
geocode, query voter files, redistribute GIS geometry, or promise that a Census
voting district is the current election precinct. It evaluates identifiers
that a caller obtained from a documented source. Crosswalk rows must retain
effective dates, election dates, and boundary vintages; split and many-to-many
results must not be collapsed.

The current production rule catalog does not consistently encode boundary
vintage or effective-start/end fields. The public export carries those fields
as `null`, not as guessed values. Election-date and source-revision fields are
present, but they do not cure the missing boundary metadata.

## What the code does not establish

Passing tests establishes that this implementation follows the documented
arithmetic and tri-state rule behavior on synthetic inputs. It does not establish accuracy, fairness,
predictive validity, ideological construct validity, external validity,
candidate completeness, or suitability for an election decision.

The real source registry is an inventory, not a complete audit. A URL's presence
does not prove availability, currentness, ballot completeness, campaign
ownership, or geographic coverage. The candidate records establish identity
and source-review status only; `position_evidence=unknown` is intentional.

The October 28 QA snapshot was partial. Seven tracker issues remained active
(four Florida, two Texas, one Southeast), including unresolved exact-split
evidence and public-source availability. The snapshot includes failures and
unresolved denominators and must not be generalized beyond its stated controls.

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

