from __future__ import annotations

import json
import unittest
from pathlib import Path

from vp_research_core.evaluate import evaluate_document
from vp_research_core.matching import (
    compare,
    match_score,
    place_candidate,
    place_voter,
    position_of,
    rank_candidates,
    tally,
)


ROOT = Path(__file__).resolve().parents[1]


class MatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((ROOT / "fixtures/synthetic_input.json").read_text())
        cls.config = cls.document["config"]
        cls.answers = cls.document["answers"]

    def test_reference_fixture(self) -> None:
        expected = json.loads((ROOT / "fixtures/synthetic_expected.json").read_text())
        self.assertEqual(evaluate_document(self.document), expected)

    def test_source_hierarchy(self) -> None:
        candidate = {
            "votes": {"synthetic_a": "no"},
            "statements": {"synthetic_a": {"stance": "yes", "reading": "stated"}},
            "party_proxy": {"synthetic_a": "yes"},
        }
        self.assertEqual(position_of(candidate, "synthetic_a").basis, "voted")
        self.assertEqual(position_of(candidate, "synthetic_a").stance, "no")
        self.assertEqual(compare(self.answers, candidate, "synthetic_a")["cell"], "differ")

    def test_party_proxy_is_half_weighted(self) -> None:
        alpha = self.document["candidates"][0]
        counts = tally(self.answers, alpha, self.config)
        self.assertEqual(counts, {"own": {"agree": 2, "of": 3}, "proxy": {"agree": 1, "of": 1}})
        score = match_score(self.answers, alpha, self.config)
        self.assertAlmostEqual(score.agree_share, 2.5 / 3.5)

    def test_single_comparison_without_line_is_not_a_match(self) -> None:
        gamma = self.document["candidates"][2]
        self.assertIsNone(place_candidate(gamma, self.config))
        self.assertIsNone(match_score(self.answers, gamma, self.config))

    def test_voter_index_uses_answer_orientation(self) -> None:
        placement = place_voter(self.answers, self.config)
        self.assertIsNotNone(placement)
        self.assertEqual(placement.x, 0.0)
        self.assertEqual(placement.answers, 4)

    def test_candidate_placement_source_order(self) -> None:
        all_sources = {
            "candidate_id": "synthetic-order",
            "party": "SYN",
            "votes": {"synthetic_a": "yes", "synthetic_b": "no"},
            "dw_nominate": {"value": 0.4, "votes_scored": 20},
            "cfscore": {"value": -1.0, "cycle": 2098},
            "words_estimate": {"value": -0.2, "low": -0.4, "high": 0.1, "passages": 3},
        }
        self.assertEqual(place_candidate(all_sources, self.config).source, "record")
        del all_sources["dw_nominate"]
        donors = place_candidate(all_sources, self.config)
        self.assertEqual(donors.source, "donors")
        self.assertAlmostEqual(donors.x, -0.554)
        del all_sources["cfscore"]
        self.assertEqual(place_candidate(all_sources, self.config).source, "words")
        del all_sources["words_estimate"]
        self.assertEqual(place_candidate(all_sources, self.config).source, "positions")

    def test_equal_scores_are_a_tie_with_no_best(self) -> None:
        first = self.document["candidates"][0]
        second = json.loads(json.dumps(first))
        second["candidate_id"] = "synthetic-alpha-copy"
        result = rank_candidates(self.answers, [first, second], self.config)
        self.assertTrue(result["tie"])
        self.assertIsNone(result["best_candidate_id"])
        self.assertFalse(result["starred"])


if __name__ == "__main__":
    unittest.main()

