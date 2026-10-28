import json
from pathlib import Path
import unittest

from vp_research_core.geography import (
    canonical_identifier,
    match_records,
    match_rule,
    resolve_crosswalk,
)


ROOT = Path(__file__).resolve().parents[1]


class GeographyTests(unittest.TestCase):
    def setUp(self):
        self.geography = json.loads((ROOT / "fixtures/synthetic_geography.json").read_text())
        self.rules = json.loads((ROOT / "fixtures/synthetic_electorate_rules.json").read_text())
        self.crosswalk = json.loads((ROOT / "fixtures/synthetic_crosswalk.json").read_text())

    def test_canonical_municipality_aliases(self):
        self.assertEqual(canonical_identifier("City of Saint Example"), "stexample")

    def test_precinct_split_requires_the_same_source(self):
        rule = dict(self.rules[0]["match"], sourceURL="https://example.invalid/other")
        self.assertIsNone(match_rule(rule, self.geography))

    def test_unknown_split_is_not_a_negative(self):
        geography = {**self.geography, "precinct": {**self.geography["precinct"], "split": "P-999"}}
        self.assertIsNone(match_rule(self.rules[0]["match"], geography))

    def test_exact_split_matches(self):
        self.assertTrue(match_rule(self.rules[0]["match"], self.geography))

    def test_overlapping_districts_are_preserved_when_explicit(self):
        self.assertTrue(match_rule(self.rules[2]["match"], self.geography))

    def test_conflicting_districts_are_unknown_by_default(self):
        rule = {"kind": "community_district", "value": "North"}
        self.assertIsNone(match_rule(rule, self.geography))

    def test_all_and_any_keep_three_valued_logic(self):
        unknown = {"kind": "school_district", "value": "7"}
        self.assertFalse(match_rule({"kind": "all", "rules": [unknown, {"kind": "municipality", "value": "Elsewhere"}]}, self.geography))
        self.assertTrue(match_rule({"kind": "any", "rules": [unknown, {"kind": "sldl", "value": "42"}]}, self.geography))

    def test_city_mismatch_is_a_negative(self):
        self.assertFalse(match_rule({"kind": "sldl", "value": "42", "city": "Elsewhere"}, self.geography))

    def test_record_partition_keeps_unknowns(self):
        result = match_records(self.rules, self.geography)
        self.assertEqual([item["id"] for item in result["unresolved"]], ["synthetic-unknown-boundary"])
        self.assertEqual(len(result["matched"]), 3)

    def test_crosswalk_preserves_one_to_many_rows(self):
        result = resolve_crosswalk(
            self.crosswalk,
            from_kind="precinct_split",
            from_value="P-014.2",
            as_of="2026-10-28",
            election_date="2026-11-03",
        )
        self.assertEqual(result.status, "matched")
        self.assertEqual({item["to_value"] for item in result.records}, {"North", "River"})

    def test_crosswalk_rejects_the_wrong_election(self):
        result = resolve_crosswalk(
            self.crosswalk,
            from_kind="precinct_split",
            from_value="P-014.2",
            as_of="2026-10-28",
            election_date="2028-11-07",
        )
        self.assertEqual(result.status, "out_of_scope")

    def test_crosswalk_does_not_mix_boundary_vintages(self):
        conflicting = self.crosswalk + [{**self.crosswalk[0], "boundary_vintage": "synthetic-2024"}]
        result = resolve_crosswalk(
            conflicting,
            from_kind="precinct_split",
            from_value="P-014.2",
            as_of="2026-10-28",
            election_date="2026-11-03",
        )
        self.assertEqual(result.status, "unresolved")


if __name__ == "__main__":
    unittest.main()
