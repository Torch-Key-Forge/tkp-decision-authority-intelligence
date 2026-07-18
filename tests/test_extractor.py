from __future__ import annotations

import json
from pathlib import Path

from tkp_decision_authority_intelligence.extractor import extract_authority, write_outputs

ROOT = Path(__file__).resolve().parents[1]


def load_fixture():
    return json.loads((ROOT / "fixtures" / "sanitized_normalized_conversation.json").read_text(encoding="utf-8"))


def test_structured_user_commands_are_canonical():
    result = extract_authority(load_fixture())
    entries = result["structured_authority_ledger"]
    assert len(entries) == 3
    assert [entry["decision_class"] for entry in entries] == ["AUTHORIZATION", "AUTHORIZATION", "ACCEPTANCE"]
    assert all(entry["owner"] == "OPERATOR" for entry in entries)
    assert all(entry["authority_status"] == "CANONICAL_STRUCTURED_COMMAND" for entry in entries)


def test_assistant_structured_command_is_never_promoted():
    result = extract_authority(load_fixture())
    statements = {entry["statement"] for entry in result["structured_authority_ledger"]}
    assert "ACCEPT_ATLAS_WORKSHOP_FIXTURE_TESTED_LOCAL_BASELINE" not in statements
    assert any(entry["turn_id"] == "TURN-0007" for entry in result["assistant_non_authority_register"])


def test_natural_language_candidates_remain_provisional():
    result = extract_authority(load_fixture())
    candidates = result["natural_language_review_queue"]
    assert candidates
    assert all(entry["authority_status"] == "PROVISIONAL_REVIEW" for entry in candidates)
    assert any(entry["turn_id"] == "TURN-0005" and entry["decision_class"] == "DEFERRAL" for entry in candidates)
    assert any(entry["turn_id"] == "TURN-0009" and entry["decision_class"] == "PROHIBITION" for entry in candidates)
    assert any(entry["turn_id"] == "TURN-0011" and entry["decision_class"] == "PROHIBITION" for entry in candidates)


def test_execution_is_not_inferred():
    result = extract_authority(load_fixture())
    all_entries = result["structured_authority_ledger"] + result["natural_language_review_queue"] + result["assistant_non_authority_register"]
    assert all(entry["execution_status"] == "NOT_INFERRED" for entry in all_entries)


def test_every_record_retains_exact_source_reference_and_hash():
    result = extract_authority(load_fixture())
    all_entries = result["structured_authority_ledger"] + result["natural_language_review_queue"] + result["assistant_non_authority_register"]
    assert all(entry["source_refs"] for entry in all_entries)
    assert all(len(entry["text_sha256"]) == 64 for entry in all_entries)


def test_output_package_and_checksums(tmp_path):
    result = extract_authority(load_fixture())
    paths = write_outputs(result, tmp_path)
    assert all(path.exists() for path in paths.values())
    receipt = json.loads(paths["receipt"].read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS"
    assert len(paths["checksums"].read_text(encoding="utf-8").strip().splitlines()) == 5


def test_missing_conversation_id_fails_closed():
    payload = load_fixture()
    payload["conversation_id"] = ""
    try:
        extract_authority(payload)
    except ValueError as exc:
        assert "conversation_id" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
