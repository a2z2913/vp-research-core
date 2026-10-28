"""Deterministic reference implementation of the pinned matching arithmetic.

This module uses mappings so callers can validate data with the included JSON
schemas without adopting a product-specific model. It performs no network I/O.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence


DEFAULT_METHOD: dict[str, float | int] = {
    "party_proxy_weight": 0.5,
    "index_scale": 0.5,
    "minimum_answers": 2,
    "cfscore_intercept": -0.098,
    "cfscore_slope": 0.456,
    "tie_threshold": 0.03,
    "star_minimum_own_positions": 4,
}

YES_NO = {"yes", "no"}
ANSWER_TO_STANCE = {"yea": "yes", "nay": "no"}


@dataclass(frozen=True)
class Position:
    stance: str | None
    basis: str | None


@dataclass(frozen=True)
class Placement:
    x: float
    source: str
    answers: int
    low: float | None = None
    high: float | None = None
    why: str | None = None
    raw: float | None = None
    cycle: int | None = None


@dataclass(frozen=True)
class MatchScore:
    score: float
    agree_share: float | None
    line_closeness: float | None
    own_positions: int
    proxy_positions: int


def _settings(config: Mapping[str, Any]) -> dict[str, float | int]:
    values = dict(DEFAULT_METHOD)
    values.update(config.get("method", {}))
    if not 0 <= float(values["party_proxy_weight"]) <= 1:
        raise ValueError("party_proxy_weight must be between 0 and 1")
    if int(values["minimum_answers"]) < 1:
        raise ValueError("minimum_answers must be positive")
    return values


def _questions(config: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    questions = {str(q["id"]): q for q in config.get("questions", [])}
    if len(questions) != len(config.get("questions", [])):
        raise ValueError("question ids must be unique")
    return questions


def _tally_questions(config: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    """Mirror upstream: use active questions when any are marked active."""

    questions = _questions(config)
    active = {qid: item for qid, item in questions.items() if item.get("active")}
    return active or questions


def _bounded(value: Any, label: str) -> float:
    number = float(value)
    if not -1 <= number <= 1:
        raise ValueError(f"{label} must be between -1 and 1")
    return number


def position_of(candidate: Mapping[str, Any], question_id: str) -> Position:
    """Return the first available position in the pinned source hierarchy."""

    vote = candidate.get("votes", {}).get(question_id)
    if vote in YES_NO:
        return Position(vote, "voted")

    statement = candidate.get("statements", {}).get(question_id)
    if statement and statement.get("stance") in YES_NO:
        reading = statement.get("reading", "stated")
        if reading not in {"stated", "leans"}:
            raise ValueError(f"invalid statement reading for {question_id}")
        return Position(statement["stance"], reading)

    proxy = candidate.get("party_proxy", {}).get(question_id)
    if proxy in YES_NO:
        return Position(proxy, "party")
    return Position(None, None)


def compare(
    answers: Mapping[str, str], candidate: Mapping[str, Any], question_id: str
) -> dict[str, str | None]:
    mine = ANSWER_TO_STANCE.get(answers.get(question_id, ""))
    theirs = position_of(candidate, question_id)
    if mine is None:
        return {"cell": "skipped", "basis": theirs.basis}
    if theirs.stance is None:
        return {"cell": "none", "basis": None}
    return {
        "cell": "agree" if mine == theirs.stance else "differ",
        "basis": theirs.basis,
    }


def tally(
    answers: Mapping[str, str], candidate: Mapping[str, Any], config: Mapping[str, Any]
) -> dict[str, dict[str, int]]:
    out = {"own": {"agree": 0, "of": 0}, "proxy": {"agree": 0, "of": 0}}
    for question_id in _tally_questions(config):
        result = compare(answers, candidate, question_id)
        if result["cell"] not in {"agree", "differ"}:
            continue
        bucket = out["proxy"] if result["basis"] == "party" else out["own"]
        bucket["of"] += 1
        if result["cell"] == "agree":
            bucket["agree"] += 1
    return out


def _index(
    stances: Mapping[str, str | None], config: Mapping[str, Any]
) -> tuple[float, int] | None:
    settings = _settings(config)
    right = 0
    count = 0
    for question_id, question in _questions(config).items():
        stance = stances.get(question_id)
        left_answer = question.get("left_answer")
        if stance not in YES_NO or left_answer not in YES_NO:
            continue
        count += 1
        right += -1 if stance == left_answer else 1
    if count < int(settings["minimum_answers"]):
        return None
    return (right / count) * float(settings["index_scale"]), count


def place_voter(
    answers: Mapping[str, str], config: Mapping[str, Any]
) -> Placement | None:
    got = _index(
        {question_id: ANSWER_TO_STANCE.get(answer) for question_id, answer in answers.items()},
        config,
    )
    return Placement(got[0], "positions", got[1]) if got else None


def place_candidate(
    candidate: Mapping[str, Any], config: Mapping[str, Any]
) -> Placement | None:
    record = candidate.get("dw_nominate")
    if record is not None:
        return Placement(
            _bounded(record["value"], "DW-NOMINATE value"),
            "record",
            int(record.get("votes_scored", 0)),
        )

    donors = candidate.get("cfscore")
    if donors is not None:
        settings = _settings(config)
        raw = float(donors["value"])
        x = float(settings["cfscore_intercept"]) + float(settings["cfscore_slope"]) * raw
        return Placement(
            max(-1, min(1, x)),
            "donors",
            0,
            raw=raw,
            cycle=int(donors["cycle"]),
        )

    estimate = candidate.get("words_estimate")
    if estimate is not None:
        x = _bounded(estimate["value"], "words estimate")
        low = _bounded(estimate.get("low", x), "words estimate low")
        high = _bounded(estimate.get("high", x), "words estimate high")
        if low > x or high < x:
            raise ValueError("words estimate range must contain its value")
        return Placement(
            x,
            "words",
            int(estimate.get("passages", 0)),
            low=low,
            high=high,
            why=str(estimate.get("why", ""))[:300],
        )

    placement_ids = {
        question_id
        for question_id, question in _questions(config).items()
        if question.get("left_answer") in YES_NO
    }
    positions = {question_id: position_of(candidate, question_id) for question_id in placement_ids}
    got = _index({qid: item.stance for qid, item in positions.items()}, config)
    if not got:
        return None
    proxy_count = sum(item.basis == "party" for item in positions.values())
    source = "guess" if proxy_count > got[1] / 2 else "positions"
    return Placement(got[0], source, got[1])


def match_score(
    answers: Mapping[str, str],
    candidate: Mapping[str, Any],
    config: Mapping[str, Any],
    voter: Placement | None = None,
) -> MatchScore | None:
    settings = _settings(config)
    counts = tally(answers, candidate, config)
    proxy_weight = float(settings["party_proxy_weight"])
    weight = counts["own"]["of"] + proxy_weight * counts["proxy"]["of"]
    agree_share = (
        (counts["own"]["agree"] + proxy_weight * counts["proxy"]["agree"]) / weight
        if weight > 0
        else None
    )

    me = voter or place_voter(answers, config)
    them = place_candidate(candidate, config)
    line_closeness = (
        1 - min(abs(me.x - them.x), 1) if me is not None and them is not None else None
    )

    if line_closeness is None and weight < int(settings["minimum_answers"]):
        return None
    parts = [part for part in (agree_share, line_closeness) if part is not None]
    if not parts:
        return None
    return MatchScore(
        sum(parts) / len(parts),
        agree_share,
        line_closeness,
        counts["own"]["of"],
        counts["proxy"]["of"],
    )


def rank_candidates(
    answers: Mapping[str, str],
    candidates: Sequence[Mapping[str, Any]],
    config: Mapping[str, Any],
    voter: Placement | None = None,
) -> dict[str, Any]:
    settings = _settings(config)
    scored: list[tuple[Mapping[str, Any], MatchScore | None]] = [
        (candidate, match_score(answers, candidate, config, voter))
        for candidate in candidates
    ]
    ranked = sorted(
        ((candidate, score) for candidate, score in scored if score is not None),
        key=lambda item: (-item[1].score, str(item[0]["candidate_id"])),
    )
    tie = (
        len(ranked) > 1
        and ranked[0][1].score - ranked[1][1].score < float(settings["tie_threshold"])
    )
    best = ranked[0] if ranked and not tie else None
    best_own = best[1].own_positions if best else 0
    starred = best is not None and best_own >= int(settings["star_minimum_own_positions"])

    rows = []
    for candidate, score in ranked:
        row: dict[str, Any] = {"candidate_id": candidate["candidate_id"]}
        row.update(asdict(score))
        rows.append(row)
    has_candidate_evidence = any(
        candidate.get("votes")
        or candidate.get("statements")
        or candidate.get("dw_nominate") is not None
        or candidate.get("cfscore") is not None
        or candidate.get("words_estimate") is not None
        for candidate in candidates
    )
    return {
        "scored": bool(has_candidate_evidence),
        "tie": tie,
        "best_candidate_id": best[0]["candidate_id"] if best else None,
        "best_own_positions": best_own,
        "starred": starred,
        "thin": best is not None and not starred,
        "ranking": rows,
        "unscored_candidate_ids": [
            candidate["candidate_id"] for candidate, score in scored if score is None
        ],
    }

