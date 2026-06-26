"""
RegIntel AI — Requirement Search Engine  (TASK 4)
==================================================
Lightweight, fully-offline keyword search over requirements_taxonomy.json.

Usage:
    python search_requirements.py "suspicious transaction monitoring"
    python search_requirements.py "KYC AML" --limit 20

Returns JSON to stdout.  No external dependencies, no API calls.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TAXONOMY_PATH = Path(__file__).parent / "data" / "requirements" / "requirements_taxonomy.json"

SEARCH_FIELDS = [
    ("requirement_text", 3),  # (field_name, weight)
    ("domain",           2),
    ("subdomain",        2),
    ("source_document",  1),
]


def load_taxonomy(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def score_record(tokens: list[str], record: dict) -> int:
    """Return a weighted hit-count score; 0 means no match."""
    score = 0
    for field, weight in SEARCH_FIELDS:
        field_tokens = tokenize(record.get(field, "") or "")
        hits = sum(1 for t in tokens if t in field_tokens)
        score += hits * weight
    return score


def search(query: str, taxonomy: list[dict], limit: int = 50) -> list[dict]:
    """Case-insensitive multi-token search; results sorted by relevance."""
    tokens = tokenize(query)
    if not tokens:
        return []

    scored = []
    for rec in taxonomy:
        s = score_record(tokens, rec)
        if s > 0:
            scored.append((s, rec))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [
        {
            "requirement_id":  r["requirement_id"],
            "domain":          r.get("domain", ""),
            "subdomain":       r.get("subdomain", ""),
            "source_document": r.get("source_document", ""),
            "text":            r.get("requirement_text", ""),
            "obligation_type": r.get("obligation_type", ""),
            "effective_status":r.get("effective_status", ""),
            "_score":          s,
        }
        for s, r in scored[:limit]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="RegIntel offline requirement search")
    parser.add_argument("query",  help="Search query string")
    parser.add_argument("--limit", type=int, default=50,
                        help="Maximum results to return (default: 50)")
    parser.add_argument("--taxonomy", default=str(TAXONOMY_PATH),
                        help="Path to requirements_taxonomy.json")
    args = parser.parse_args()

    taxonomy_path = Path(args.taxonomy)
    if not taxonomy_path.exists():
        sys.exit(f"ERROR: taxonomy file not found at {taxonomy_path}")

    taxonomy = load_taxonomy(taxonomy_path)
    results  = search(args.query, taxonomy, limit=args.limit)

    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.stderr.write(f"Found {len(results)} results for query: {args.query!r}\n")


if __name__ == "__main__":
    main()
