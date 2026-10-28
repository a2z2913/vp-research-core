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
]

