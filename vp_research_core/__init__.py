"""Public, deterministic matching primitives."""

from .matching import (
    MatchScore,
    Placement,
    compare,
    match_score,
    place_candidate,
    place_voter,
    position_of,
    rank_candidates,
    tally,
)
from .geography import (
    CrosswalkResult,
    canonical_identifier,
    match_records,
    match_rule,
    resolve_crosswalk,
)

__all__ = [
    "MatchScore",
    "Placement",
    "compare",
    "match_score",
    "place_candidate",
    "place_voter",
    "position_of",
    "rank_candidates",
    "tally",
    "CrosswalkResult",
    "canonical_identifier",
    "match_records",
    "match_rule",
    "resolve_crosswalk",
]

