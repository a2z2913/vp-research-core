#!/usr/bin/env python3
"""Create the rights-reviewed public research export from pinned local inputs.

The source workbook and production checkout stay outside the repository.  This
script copies only the fields listed below and deliberately omits internal use
notes, failed URL guesses, usage metrics, private QA logs, candidates' contact
information, and all address-level inputs.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
import zipfile


SHEET_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_NS = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}

SOURCE_FIELDS = [
    "source_id",
    "state",
    "jurisdiction",
    "content_areas",
    "organization",
    "description",
    "url",
    "authority",
    "source_checked_at",
    "hostname",
]
CANDIDATE_FIELDS = [
    "candidate_source_id",
    "state",
    "candidate_name",
    "office",
    "geographic_scope",
    "review_outcome",
    "campaign_url",
    "reviewed_on",
    "official_election_record",
    "source_id",
    "evidence_class",
    "position_evidence",
]


def clean(value: object) -> str:
    return str(value or "").strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def column_number(reference: str) -> int:
    match = re.match(r"[A-Z]+", reference)
    if not match:
        raise ValueError(f"invalid cell reference: {reference}")
    result = 0
    for letter in match.group(0):
        result = result * 26 + ord(letter) - 64
    return result


def read_workbook(path: Path) -> dict[str, list[list[object]]]:
    """Read cell values without executing formulas or macros."""

    with zipfile.ZipFile(path) as book:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in book.namelist():
            root = ET.fromstring(book.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", SHEET_NS):
                shared.append("".join(node.text or "" for node in item.iterfind(".//m:t", SHEET_NS)))

        workbook = ET.fromstring(book.read("xl/workbook.xml"))
        relationships = ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))
        targets = {
            item.attrib["Id"]: item.attrib["Target"]
            for item in relationships.findall("p:Relationship", PACKAGE_NS)
        }
        result: dict[str, list[list[object]]] = {}
        for sheet in workbook.find("m:sheets", SHEET_NS):
            relationship_id = sheet.attrib[f"{{{OFFICE_REL_NS}}}id"]
            target = targets[relationship_id].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            root = ET.fromstring(book.read(target))
            rows: list[list[object]] = []
            for row in root.findall(".//m:sheetData/m:row", SHEET_NS):
                values: dict[int, object] = {}
                for cell in row.findall("m:c", SHEET_NS):
                    index = column_number(cell.attrib["r"])
                    cell_type = cell.attrib.get("t")
                    raw = cell.find("m:v", SHEET_NS)
                    if cell_type == "inlineStr":
                        values[index] = "".join(node.text or "" for node in cell.iterfind(".//m:t", SHEET_NS))
                    elif raw is None:
                        values[index] = ""
                    elif cell_type == "s":
                        values[index] = shared[int(raw.text)]
                    else:
                        values[index] = raw.text or ""
                width = max(values, default=0)
                rows.append([values.get(index, "") for index in range(1, width + 1)])
            result[sheet.attrib["name"]] = rows
        return result


def records_after_header(rows: list[list[object]], first_header: str) -> list[dict[str, object]]:
    for index, row in enumerate(rows):
        if row and clean(row[0]) == first_header:
            headers = [clean(item) for item in row]
            return [
                {header: record[position] if position < len(record) else "" for position, header in enumerate(headers) if header}
                for record in rows[index + 1 :]
                if any(clean(item) for item in record)
            ]
    raise ValueError(f"header {first_header!r} was not found")


def excel_date(value: object) -> str:
    text = clean(value)
    if not text:
        return ""
    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        return (datetime(1899, 12, 30) + timedelta(days=float(text))).date().isoformat()
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError as error:
        raise ValueError(f"unrecognized workbook date {text!r}") from error


def public_url(value: object, *, allow_many: bool = False) -> str:
    text = clean(value)
    if not text:
        return ""
    values = [part.strip() for part in text.split(";")] if allow_many else [text]
    for item in values:
        parts = urlsplit(item)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError(f"non-public URL in reviewed export: {item!r}")
        lowered = item.lower()
        if re.search(r"(?:^|[?&])(?:address|street|latitude|longitude|lat|lon)=", lowered):
            raise ValueError(f"address or coordinate query is not exportable: {item!r}")
    return "; ".join(values)


def public_description(value: object) -> str:
    """Remove operational QA prose while retaining the source's public label."""

    text = clean(value)
    marker = re.search(
        r"(?i)\b(?:production|preview|daily review|deploy|timeout|timed out|fallback|live[- ]check|voterspulse|vp|site change)\b",
        text,
    )
    if not marker:
        return text
    prefix = text[: marker.start()].strip(" ;:,.")
    public_label = re.split(r"[;:]", prefix, maxsplit=1)[0].strip()
    return public_label or "Public source"


def write_csv(path: Path, fields: list[str], records: Iterable[dict[str, object]]) -> int:
    rows = list(records)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def export_workbook(book: dict[str, list[list[object]]], output: Path) -> dict[str, int]:
    source_records = records_after_header(book["Source Registry"], "Source ID")
    sources: list[dict[str, object]] = []
    for record in source_records:
        source_id = clean(record.get("Source ID"))
        if not source_id:
            continue
        if clean(record.get("Content area(s)")) == "Privacy and data use":
            continue
        sources.append(
            {
                "source_id": source_id,
                "state": clean(record.get("State")),
                "jurisdiction": clean(record.get("Jurisdiction")),
                "content_areas": clean(record.get("Content area(s)")),
                "organization": clean(record.get("Source organization")),
                "description": public_description(record.get("Link label / description")),
                "url": public_url(record.get("URL")),
                "authority": clean(record.get("Authority")),
                "source_checked_at": excel_date(record.get("Recorded source check")),
                "hostname": clean(record.get("Hostname (www omitted)")),
            }
        )
    if len({record["source_id"] for record in sources}) != len(sources):
        raise ValueError("Source Registry contains duplicate Source IDs")
    sources.sort(key=lambda record: str(record["source_id"]))

    geography_sources = [
        record for record in sources if "District, precinct, and address matching" in str(record["content_areas"])
    ]

    candidate_records = records_after_header(book["Campaign Link Review"], "State")
    candidates: list[dict[str, object]] = []
    for record in candidate_records:
        state = clean(record.get("State"))
        name = clean(record.get("Candidate name"))
        office = clean(record.get("Office(s)"))
        scope = clean(record.get("Counties / scope"))
        official_record = public_url(record.get("Official election record"), allow_many=True)
        if not (state and name and office and scope):
            continue
        identity = "|".join([state, name.casefold(), office.casefold(), scope.casefold(), official_record])
        candidate_id = "candidate-source-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
        candidates.append(
            {
                "candidate_source_id": candidate_id,
                "state": state,
                "candidate_name": name,
                "office": office,
                "geographic_scope": scope,
                "review_outcome": clean(record.get("Recorded review outcome")),
                "campaign_url": public_url(record.get("Confirmed campaign URL")),
                "reviewed_on": excel_date(record.get("Reviewed on")),
                "official_election_record": official_record,
                "source_id": clean(record.get("Source ID")),
                "evidence_class": "candidate_identity_and_source_review",
                "position_evidence": "unknown",
            }
        )
    if len({record["candidate_source_id"] for record in candidates}) != len(candidates):
        raise ValueError("candidate stable ID collision or duplicate review record")
    candidates.sort(key=lambda record: str(record["candidate_source_id"]))

    return {
        "source_registry": write_csv(output / "source_registry.csv", SOURCE_FIELDS, sources),
        "geographic_sources": write_csv(output / "geographic_sources.csv", SOURCE_FIELDS, geography_sources),
        "candidate_sources": write_csv(output / "candidate_sources.csv", CANDIDATE_FIELDS, candidates),
    }


def clean_rule(rule: object) -> object:
    if not isinstance(rule, dict):
        return {}
    permitted = {"kind", "sourceURL", "values", "knownValues", "value", "city", "allowOverlap", "rules"}
    result: dict[str, object] = {}
    for key in permitted:
        if key not in rule:
            continue
        value = rule[key]
        if key == "rules":
            result[key] = [clean_rule(child) for child in value] if isinstance(value, list) else []
        elif key == "sourceURL":
            result[key] = public_url(value)
        else:
            result[key] = value
    return result


def source_urls(record: dict[str, Any]) -> list[str]:
    found: set[str] = set()

    def visit(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"url", "sourceURL"} and isinstance(child, str) and child:
                    try:
                        found.add(public_url(child))
                    except ValueError:
                        pass
                else:
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(record.get("sources", []))
    visit(record.get("match", {}))
    return sorted(found)


def export_catalog(path: Path, output: Path, revision: str) -> int:
    text = path.read_text(encoding="utf-8").strip()
    prefix = "export default "
    marker = text.find(prefix)
    if marker < 0:
        raise ValueError("ballot catalog is not the expected static export")
    data = json.loads(text[marker + len(prefix) :].removesuffix(";"))
    records: list[dict[str, object]] = []
    for contest in data.get("contests", []):
        identity = "|".join(
            [
                clean(contest.get("state")),
                clean(contest.get("id")),
                clean(contest.get("office")),
                json.dumps(contest.get("counties", []), sort_keys=True),
                json.dumps(contest.get("match", {}), sort_keys=True),
            ]
        )
        rule_id = clean(contest.get("id")) or "electorate-rule-" + hashlib.sha256(identity.encode()).hexdigest()[:16]
        records.append(
            {
                "rule_id": rule_id,
                "state": clean(contest.get("state") or "FL"),
                "contest_type": clean(contest.get("type")),
                "office": clean(contest.get("office")),
                "jurisdiction": clean(contest.get("jurisdiction")),
                "counties": contest.get("counties", []),
                "district": contest.get("district", {}),
                "electorate": clean(contest.get("electorate")),
                "levels": contest.get("levels", []),
                "match": clean_rule(contest.get("match", {})),
                "source_urls": source_urls(contest),
                "checked": clean(contest.get("checked") or data.get("checked")),
                "election_date": clean(data.get("electionDay")),
                "boundary_vintage": contest.get("boundaryVintage") or None,
                "effective_start": contest.get("effectiveStart") or None,
                "effective_end": contest.get("effectiveEnd") or None,
                "source_revision": revision,
            }
        )
    records.sort(key=lambda record: str(record["rule_id"]))
    destination = output / "electorate_rules.jsonl"
    with destination.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    return len(records)


def summary_values(book: dict[str, list[list[object]]]) -> dict[str, str]:
    values: dict[str, str] = {}
    for row in book.get("Summary", []):
        if len(row) >= 2 and clean(row[0]) in {"Inventory date (UTC)", "Version audited", "Branch / commit"}:
            values[clean(row[0])] = clean(row[1])
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--workbook-modified", required=True)
    parser.add_argument("--generated-at", required=True)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    book = read_workbook(args.workbook)
    counts = export_workbook(book, args.output)
    counts["electorate_rules"] = export_catalog(args.catalog, args.output, args.source_revision)
    exported = [
        args.output / "source_registry.csv",
        args.output / "geographic_sources.csv",
        args.output / "candidate_sources.csv",
        args.output / "electorate_rules.jsonl",
    ]
    qa_summary = args.output / "qa_summary.json"
    if qa_summary.exists():
        exported.append(qa_summary)
    manifest = {
        "generated_at": args.generated_at,
        "workbook": {
            "title": "VotersPulse Website Sources+Links.xlsx",
            "modified_at": args.workbook_modified,
            "download_sha256": sha256(args.workbook),
            "reported_summary": summary_values(book),
        },
        "production_source_revision": args.source_revision,
        "record_counts": counts,
        "file_sha256": {path.name: sha256(path) for path in exported},
        "exclusions": [
            "internal build-use fields and page-usage counts",
            "evidence and follow-up notes",
            "unconfirmed candidate URLs",
            "candidate position claims",
            "addresses, coordinates, user records, and QA inputs",
            "candidate arrays and presentation content from the production catalog",
        ],
    }
    (args.output / "export_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"record_counts": counts, "manifest": str(args.output / "export_manifest.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
