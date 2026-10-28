"""Tri-state electorate matching for already-resolved election geography.

This module intentionally does not geocode addresses.  It evaluates public
precinct, split, municipality, and district identifiers after another system
has resolved them, and preserves unknown or conflicting results as ``None``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from typing import Any, Iterable, Mapping, Optional, Sequence


TruthValue = Optional[bool]


def canonical_identifier(value: object) -> str:
    """Normalize a label for comparison without inventing a new identifier."""

    text = str(value or "").lower()
    text = re.sub(r"^(city|town|village) of ", "", text)
    text = re.sub(r"\bsaint\b", "st", text)
    return re.sub(r"[^a-z0-9]", "", text)


def _expected_values(rule: Mapping[str, Any]) -> list[object]:
    values = rule.get("values")
    if isinstance(values, list):
        return values
    return [rule.get("value")]


def match_rule(rule: Mapping[str, Any], geography: Mapping[str, Any]) -> TruthValue:
    """Evaluate an electorate rule with true/false/unknown semantics.

    ``None`` means that the available geography cannot establish eligibility.
    In particular, a missing source, conflicting district result, or unresolved
    municipality is never silently treated as ``False``.
    """

    kind = rule.get("kind")
    if kind in {"all", "any"}:
        rules = rule.get("rules")
        if not isinstance(rules, list) or not rules:
            return None
        answers = [match_rule(child, geography) for child in rules]
        if kind == "all":
            if False in answers:
                return False
            return None if None in answers else True
        if True in answers:
            return True
        return None if None in answers else False

    if kind in {"statewide", "countywide"}:
        return True

    precinct = geography.get("precinct")
    precinct = precinct if isinstance(precinct, Mapping) else {}
    if kind == "precinct_split_set":
        split = precinct.get("split")
        values = rule.get("values")
        if (
            not split
            or precinct.get("sourceURL") != rule.get("sourceURL")
            or not isinstance(values, list)
            or not values
        ):
            return None
        known = rule.get("knownValues")
        if isinstance(known, list) and str(split) not in {str(item) for item in known}:
            return None
        return str(split) in {str(item) for item in values}

    if kind == "precinct_set":
        precinct_id = precinct.get("id")
        values = rule.get("values")
        if (
            not precinct_id
            or precinct.get("sourceURL") != rule.get("sourceURL")
            or not isinstance(values, list)
            or not values
        ):
            return None
        return str(precinct_id) in {str(item) for item in values}

    municipality = geography.get("municipality")
    municipality = municipality if isinstance(municipality, Mapping) else {}
    if kind in {"municipality", "outside_municipality"}:
        if municipality.get("resolved") is not True:
            return None
        inside = canonical_identifier(municipality.get("name")) == canonical_identifier(rule.get("value"))
        return not inside if kind == "outside_municipality" else inside

    if kind == "unresolved":
        city = rule.get("city")
        if (
            city
            and municipality.get("resolved") is True
            and canonical_identifier(city) != canonical_identifier(municipality.get("name"))
        ):
            return False
        return None

    city = rule.get("city")
    if city:
        if municipality.get("resolved") is not True:
            return None
        if canonical_identifier(city) != canonical_identifier(municipality.get("name")):
            return False

    districts = geography.get("mapDistricts")
    if not isinstance(districts, list):
        districts = []
    numbers = {
        canonical_identifier(item.get("number"))
        for item in districts
        if isinstance(item, Mapping)
        and item.get("kind") == kind
        and item.get("matchable") is True
        and canonical_identifier(item.get("number"))
    }
    expected = {
        canonical_identifier(value)
        for value in _expected_values(rule)
        if canonical_identifier(value)
    }
    if rule.get("allowOverlap") is True:
        return bool(numbers & expected) if numbers else None
    if len(numbers) != 1:
        return None
    return next(iter(numbers)) in expected


@dataclass(frozen=True)
class CrosswalkResult:
    """A lossless crosswalk result; ``records`` may contain many targets."""

    status: str
    records: tuple[Mapping[str, Any], ...]
    reason: str


def _iso_date(value: object) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError as error:
        raise ValueError(f"expected ISO date, got {value!r}") from error


def resolve_crosswalk(
    records: Iterable[Mapping[str, Any]],
    *,
    from_kind: str,
    from_value: object,
    as_of: str,
    election_date: str | None = None,
) -> CrosswalkResult:
    """Return every applicable crosswalk row without collapsing splits.

    Records from conflicting boundary vintages are unresolved.  Election-dated
    records require the requested election date to match exactly.  Multiple
    target rows within one vintage are returned together, preserving legitimate
    one-to-many and many-to-many relationships.
    """

    requested_value = canonical_identifier(from_value)
    requested_as_of = _iso_date(as_of)
    requested_election = _iso_date(election_date)
    if not requested_value or requested_as_of is None:
        raise ValueError("from_value and as_of are required")

    candidates: list[Mapping[str, Any]] = []
    for record in records:
        if record.get("from_kind") != from_kind:
            continue
        if canonical_identifier(record.get("from_value")) != requested_value:
            continue
        start = _iso_date(record.get("effective_start"))
        end = _iso_date(record.get("effective_end"))
        if start and requested_as_of < start:
            continue
        if end and requested_as_of > end:
            continue
        record_election = _iso_date(record.get("election_date"))
        if record_election and requested_election != record_election:
            continue
        candidates.append(record)

    if not candidates:
        return CrosswalkResult("out_of_scope", (), "no row applies to the requested date and election")
    vintages = {str(item.get("boundary_vintage") or "") for item in candidates}
    if len(vintages) != 1 or "" in vintages:
        return CrosswalkResult("unresolved", tuple(candidates), "applicable rows do not establish one boundary vintage")
    return CrosswalkResult("matched", tuple(candidates), "all applicable rows from one boundary vintage are retained")


def match_records(
    contests: Sequence[Mapping[str, Any]], geography: Mapping[str, Any]
) -> dict[str, list[Mapping[str, Any]]]:
    """Partition contest records into matched, excluded, and unresolved sets."""

    result: dict[str, list[Mapping[str, Any]]] = {
        "matched": [],
        "excluded": [],
        "unresolved": [],
    }
    for contest in contests:
        answer = match_rule(contest.get("match", {}), geography)
        bucket = "matched" if answer is True else "excluded" if answer is False else "unresolved"
        result[bucket].append(contest)
    return result
