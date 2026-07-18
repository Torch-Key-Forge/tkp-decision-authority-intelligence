from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

STRUCTURED_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){2,}$")

STRUCTURED_PREFIXES = (
    ("AUTHORIZE_", "AUTHORIZATION"),
    ("ACCEPT_", "ACCEPTANCE"),
    ("APPROVE_", "AUTHORIZATION"),
    ("HOLD_", "DEFERRAL"),
    ("DEFER_", "DEFERRAL"),
    ("REJECT_", "REJECTION"),
    ("PROHIBIT_", "PROHIBITION"),
    ("DO_NOT_", "PROHIBITION"),
)

NATURAL_RULES: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    ("NAT-AUTH-001", "AUTHORIZATION", re.compile(r"\b(?:go ahead|proceed|approved?|authorize[sd]?)\b", re.I)),
    ("NAT-ACCEPT-001", "ACCEPTANCE", re.compile(r"\b(?:accept(?:ed)?|agreed|good is enough)\b", re.I)),
    ("NAT-DEFER-001", "DEFERRAL", re.compile(r"\b(?:hold|defer|not part of the .* gate)\b", re.I)),
    ("NAT-PROHIBIT-001", "PROHIBITION", re.compile(r"\b(?:remains? unauthorized|do not|must not|not authorized)\b", re.I)),
    ("NAT-SCOPE-001", "SCOPE", re.compile(r"\b(?:local-only|read-only|scope|boundary|without changing|no cloud)\b", re.I)),
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _structured_class(text: str) -> str | None:
    if not STRUCTURED_RE.fullmatch(text.strip()):
        return None
    for prefix, decision_class in STRUCTURED_PREFIXES:
        if text.startswith(prefix):
            return decision_class
    return "STRUCTURED_COMMAND"


def _natural_matches(text: str) -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    for rule_id, decision_class, pattern in NATURAL_RULES:
        if pattern.search(text):
            matches.append((rule_id, decision_class))
    return matches


def _source_refs(turn: dict[str, Any]) -> list[str]:
    refs = turn.get("source_refs") or []
    return [str(ref) for ref in refs if str(ref).strip()]


def extract_authority(conversation: dict[str, Any]) -> dict[str, Any]:
    conversation_id = str(conversation.get("conversation_id") or "").strip()
    turns = conversation.get("turns")
    if not conversation_id:
        raise ValueError("conversation_id is required")
    if not isinstance(turns, list):
        raise ValueError("turns must be a list")

    structured_entries: list[dict[str, Any]] = []
    review_candidates: list[dict[str, Any]] = []
    assistant_matches: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []

    structured_counter = 0
    review_counter = 0
    assistant_counter = 0

    for index, turn in enumerate(turns, start=1):
        if not isinstance(turn, dict):
            exceptions.append({"index": index, "reason": "TURN_NOT_OBJECT"})
            continue

        turn_id = str(turn.get("turn_id") or "").strip()
        role = str(turn.get("role") or "").strip().lower()
        text = str(turn.get("text") or "").strip()
        refs = _source_refs(turn)
        ordinal = turn.get("ordinal", index)

        if not turn_id or role not in {"user", "assistant", "tool", "system"}:
            exceptions.append({
                "index": index,
                "turn_id": turn_id or None,
                "reason": "MISSING_ID_OR_UNSUPPORTED_ROLE",
            })
            continue
        if not text:
            continue

        base = {
            "conversation_id": conversation_id,
            "turn_id": turn_id,
            "ordinal": ordinal,
            "role": role,
            "statement": text,
            "source_refs": refs,
            "text_sha256": _sha256_text(text),
            "execution_status": "NOT_INFERRED",
        }

        structured_class = _structured_class(text)
        natural_matches = _natural_matches(text)

        if role == "user" and structured_class:
            structured_counter += 1
            structured_entries.append({
                "ledger_id": f"AUTH-{structured_counter:04d}",
                "decision_class": structured_class,
                "owner": "OPERATOR",
                "authority_status": "CANONICAL_STRUCTURED_COMMAND",
                **base,
            })
            continue

        if role == "user" and natural_matches:
            for rule_id, decision_class in natural_matches:
                review_counter += 1
                review_candidates.append({
                    "candidate_id": f"REVIEW-{review_counter:04d}",
                    "decision_class": decision_class,
                    "owner": "OPERATOR",
                    "authority_status": "PROVISIONAL_REVIEW",
                    "rule_id": rule_id,
                    **base,
                })
            continue

        if role != "user" and (structured_class or natural_matches):
            assistant_counter += 1
            classes = [structured_class] if structured_class else [match[1] for match in natural_matches]
            assistant_matches.append({
                "register_id": f"NONAUTH-{assistant_counter:04d}",
                "matched_classes": classes,
                "authority_status": "NON_AUTHORITATIVE_ROLE",
                **base,
            })

    return {
        "schema_version": "0.1.0",
        "conversation_id": conversation_id,
        "structured_authority_ledger": structured_entries,
        "natural_language_review_queue": review_candidates,
        "assistant_non_authority_register": assistant_matches,
        "exception_register": exceptions,
        "authority_boundary": {
            "only_user_role_can_hold_operator_authority": True,
            "assistant_statements_non_authoritative": True,
            "natural_language_candidates_require_review": True,
            "execution_not_inferred_from_command": True,
        },
        "counts": {
            "turns_received": len(turns),
            "structured_authority_entries": len(structured_entries),
            "natural_language_review_candidates": len(review_candidates),
            "assistant_non_authority_matches": len(assistant_matches),
            "exceptions": len(exceptions),
        },
    }


def write_outputs(result: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output = Path(output_dir)
    paths = {
        "ledger": output / "ledgers" / "Structured_Authority_Ledger.json",
        "review": output / "review" / "Natural_Language_Authority_Review_Queue.json",
        "assistant": output / "registers" / "Assistant_Non_Authority_Register.json",
        "exceptions": output / "registers" / "Extraction_Exception_Register.json",
        "receipt": output / "receipts" / "Extraction_Run_Receipt.json",
        "checksums": output / "receipts" / "CHECKSUMS.sha256",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    payloads = {
        "ledger": {
            "schema_version": result["schema_version"],
            "conversation_id": result["conversation_id"],
            "entries": result["structured_authority_ledger"],
            "authority_boundary": result["authority_boundary"],
        },
        "review": {
            "schema_version": result["schema_version"],
            "conversation_id": result["conversation_id"],
            "candidates": result["natural_language_review_queue"],
        },
        "assistant": {
            "schema_version": result["schema_version"],
            "conversation_id": result["conversation_id"],
            "entries": result["assistant_non_authority_register"],
        },
        "exceptions": {
            "schema_version": result["schema_version"],
            "conversation_id": result["conversation_id"],
            "entries": result["exception_register"],
        },
        "receipt": {
            "schema_version": result["schema_version"],
            "conversation_id": result["conversation_id"],
            "status": "PASS" if not result["exception_register"] else "PASS_WITH_EXCEPTIONS",
            "counts": result["counts"],
            "authority_boundary": result["authority_boundary"],
        },
    }
    for key, payload in payloads.items():
        paths[key].write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    checksum_lines = []
    for key in ("ledger", "review", "assistant", "exceptions", "receipt"):
        path = paths[key]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksum_lines.append(f"{digest}  {path.relative_to(output).as_posix()}")
    paths["checksums"].write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    return paths
