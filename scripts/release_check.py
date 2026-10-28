#!/usr/bin/env python3
"""Fail on common secret formats, private-data artifacts, or oversized files."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv"}
FORBIDDEN_SUFFIXES = {
    ".env", ".pem", ".key", ".p12", ".pfx", ".wav", ".mp3", ".m4a",
    ".mp4", ".mov", ".sqlite", ".db", ".log",
}
FORBIDDEN_NAMES = {"credentials.json", "secrets.json", "session.json"}
EXPECTED_LARGE_FILES = {
    Path("data/electorate_rules.jsonl"): 2_000_000,
}
REVIEWED_PUBLIC_ADDRESS_STRINGS = {
    # Official ballot-measure title for a public commercial-property lease;
    # not a user, voter, household, fixture, or lookup input.
    "1691 Michigan Avenue",
}
PATTERNS = {
    "private-key header": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile("gh" + r"[pousr]_[A-Za-z0-9]{30,}"),
    "OpenAI-style token": re.compile("sk" + r"-[A-Za-z0-9_-]{20,}"),
    "AWS access key": re.compile("AK" + r"IA[0-9A-Z]{16}"),
    "assigned credential": re.compile(
        r"(?i)(?:api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+-]{16,}"
    ),
    "precise coordinate pair": re.compile(
        r"(?<![A-Za-z0-9])[-+]?\d{1,3}\.\d{5,}\s*,\s*[-+]?\d{1,3}\.\d{5,}(?![A-Za-z0-9])"
    ),
    "address query parameter": re.compile(
        r"(?i)[?&](?:address|street|latitude|longitude|lat|lon)=[^&#\s]+"
    ),
    "street address": re.compile(
        r"(?i)\b\d{1,6}\s+(?:[NSEW]\s+)?[A-Z][A-Za-z0-9 .'-]{1,45}\s(?:St|Street|Rd|Road|Ave|Avenue|Blvd|Boulevard|Ln|Lane|Dr|Drive|Ct|Court|Way|Trail|Trl|Pkwy|Parkway)\b"
    ),
}


def main() -> None:
    problems: list[str] = []
    checked = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        rel = path.relative_to(ROOT)
        checked += 1
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            problems.append(f"forbidden artifact: {rel}")
            continue
        allowed_size = EXPECTED_LARGE_FILES.get(rel, 1_000_000)
        if path.stat().st_size > allowed_size:
            problems.append(f"file exceeds 1 MB: {rel}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"unexpected binary file: {rel}")
            continue
        for label, pattern in PATTERNS.items():
            matches = list(pattern.finditer(text))
            if label == "street address":
                matches = [
                    match
                    for match in matches
                    if match.group(0) not in REVIEWED_PUBLIC_ADDRESS_STRINGS
                    and "district court" not in match.group(0).lower()
                    and "superior court" not in match.group(0).lower()
                ]
            if matches:
                problems.append(f"{label}: {rel}")
    if problems:
        raise SystemExit("release check failed:\n- " + "\n- ".join(problems))
    print(f"release check passed: {checked} text files; no blocked artifacts or token patterns")


if __name__ == "__main__":
    main()

