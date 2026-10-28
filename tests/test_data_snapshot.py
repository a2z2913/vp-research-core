import csv
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


class DataSnapshotTests(unittest.TestCase):
    def test_manifest_hashes_and_record_counts(self):
        manifest = json.loads((DATA / "export_manifest.json").read_text())
        for name, expected in manifest["file_sha256"].items():
            actual = hashlib.sha256((DATA / name).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, name)

        with (DATA / "candidate_sources.csv").open(newline="") as handle:
            candidates = list(csv.DictReader(handle))
        with (DATA / "source_registry.csv").open(newline="") as handle:
            sources = list(csv.DictReader(handle))
        with (DATA / "geographic_sources.csv").open(newline="") as handle:
            geography_sources = list(csv.DictReader(handle))
        electorate = [json.loads(line) for line in (DATA / "electorate_rules.jsonl").read_text().splitlines()]
        self.assertEqual(len(candidates), manifest["record_counts"]["candidate_sources"])
        self.assertEqual(len(sources), manifest["record_counts"]["source_registry"])
        self.assertEqual(len(geography_sources), manifest["record_counts"]["geographic_sources"])
        self.assertEqual(len(electorate), manifest["record_counts"]["electorate_rules"])

    def test_candidate_rows_do_not_claim_positions(self):
        with (DATA / "candidate_sources.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertTrue(rows)
        self.assertEqual({row["position_evidence"] for row in rows}, {"unknown"})
        for row in rows:
            if row["review_outcome"].startswith("No confirmed"):
                self.assertEqual(row["campaign_url"], "")

    def test_electorate_export_excludes_candidates_and_exposes_version_gaps(self):
        rows = [json.loads(line) for line in (DATA / "electorate_rules.jsonl").read_text().splitlines()]
        self.assertEqual(len({row["rule_id"] for row in rows}), len(rows))
        for row in rows:
            self.assertNotIn("candidates", row)
            self.assertNotIn("presentation", row)
            self.assertIn("boundary_vintage", row)
            self.assertIn("effective_start", row)
            self.assertIn("effective_end", row)

    def test_qa_snapshot_includes_open_denominators(self):
        qa = json.loads((DATA / "qa_summary.json").read_text())
        tracker = qa["tracker"]
        self.assertEqual(sum(tracker["active_issues_by_tracker_area"].values()), tracker["active_issue_denominator"])
        gaps = next(check for check in qa["checks"] if check["id"] == "current-open-style-gaps")
        self.assertEqual(gaps["collier_exact_splits"]["unresolved"], gaps["collier_exact_splits"]["denominator"])
        self.assertEqual(gaps["okeechobee_exact_splits"]["unresolved"], gaps["okeechobee_exact_splits"]["denominator"])


if __name__ == "__main__":
    unittest.main()
