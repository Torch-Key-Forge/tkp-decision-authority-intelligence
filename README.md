# TKP Decision and Authority Intelligence

Evidence-linked extraction and classification of operator decisions, authority, boundaries, and review candidates from normalized AI conversations.

This is an upstream support component for [Project Foreman](https://github.com/Torch-Key-Forge/tkp-project-foreman).

## Trust model

The engine enforces four boundaries:

- only user/operator turns can produce authority records;
- structured operator commands can enter the canonical structured ledger;
- natural-language approvals, holds, prohibitions, and scope statements remain provisional review candidates;
- issuing a command never proves execution or completion.

Assistant statements may be collected as non-authoritative matches for audit, but they are never promoted.

## Outputs

```text
output/
├── ledgers/
│   └── Structured_Authority_Ledger.json
├── review/
│   └── Natural_Language_Authority_Review_Queue.json
├── registers/
│   └── Assistant_Non_Authority_Register.json
└── receipts/
    ├── Extraction_Run_Receipt.json
    └── CHECKSUMS.sha256
```

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q

tkp-authority-extract .\fixtures\sanitized_normalized_conversation.json .\demo-output
```

## Input contract

The public candidate accepts a normalized conversation object containing:

- a stable `conversation_id`;
- ordered turns;
- a stable `turn_id` and ordinal for each turn;
- `role`;
- plain text;
- one or more exact `source_refs`.

See `docs/INPUT_OUTPUT_CONTRACT.md`.

## Public evidence boundary

The included fixture is synthetic and sanitized, but it reproduces the governing distinctions exercised by Project Foreman:

- structured authorizations and acceptances;
- natural-language deferral, prohibition, and scope candidates;
- assistant statements that must remain non-authoritative;
- exact source references;
- no execution inference.

Historic private validation identified 188 structured-command evidence occurrences representing 180 unique direct operator commands. A further 352 natural-language candidates were held for review rather than promoted. No private source corpus is included here.

## Status

`0.1.0-publication-candidate`

Current gate: `PUBLICATION_CANDIDATE_PUBLISHED_WINDOWS_VERIFICATION_REQUIRED`

## License

Source is published for review. No reuse license is granted yet. See `LICENSE`.
