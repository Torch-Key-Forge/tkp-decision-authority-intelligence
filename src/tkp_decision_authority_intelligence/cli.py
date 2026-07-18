from __future__ import annotations

import argparse
import json
from pathlib import Path

from .extractor import extract_authority, write_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tkp-authority-extract",
        description="Extract evidence-linked structured authority and provisional review candidates.",
    )
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = json.loads(args.input_json.read_text(encoding="utf-8"))
        result = extract_authority(payload)
        write_outputs(result, args.output_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    counts = result["counts"]
    print(
        "PASS: "
        f"{counts['structured_authority_entries']} structured, "
        f"{counts['natural_language_review_candidates']} review candidates, "
        f"{counts['assistant_non_authority_matches']} assistant non-authority matches, "
        f"{counts['exceptions']} exceptions"
    )
    return 0
