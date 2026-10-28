"""Command-line evaluator for a complete JSON input document."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from .matching import place_voter, rank_candidates


def evaluate_document(document: Mapping[str, Any]) -> dict[str, Any]:
    config = document["config"]
    answers = document["answers"]
    voter = place_voter(answers, config)
    return {
        "method_id": config["method_id"],
        "race_id": document["race_id"],
        "voter_placement": asdict(voter) if voter else None,
        "result": rank_candidates(answers, document["candidates"], config, voter),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON document matching schemas/input.schema.json")
    parser.add_argument("--pretty", action="store_true", help="pretty-print the output")
    args = parser.parse_args()
    document = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(evaluate_document(document), indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()

