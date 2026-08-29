# TKP Decision and Authority Intelligence

**Recover evidence of what the operator actually decided—without turning assistant suggestions into authority.**

TKP Decision and Authority Intelligence is the second public technical component in the Project Foreman recovery chain. It consumes normalized conversation records and separates structured operator authority, provisional natural-language review candidates, and non-authoritative assistant statements while preserving exact evidence links.

## Where it fits

```text
AI conversation export
        ↓
TKP Conversation Normalizer
        ↓
TKP Decision and Authority Intelligence
        ↓
TKP Conversation-to-Artifact
        ↓
Project Foreman workspace / recovery package
```

Related public components:

- [Project Foreman](https://github.com/Torch-Key-Forge/tkp-project-foreman) — the product-level recovery surface;
- [TKP Conversation Normalizer](https://github.com/Torch-Key-Forge/tkp-conversation-normalizer) — reconstructs and normalizes source conversation structure;
- [TKP Conversation-to-Artifact](https://github.com/Torch-Key-Forge/tkp-conversation-to-artifact) — composes reviewed evidence into portable project artifacts.

## Why it exists

Long AI conversations mix together operator decisions, approvals, prohibitions, assistant proposals, speculative plans, and statements about work that may or may not have happened.

For project recovery, those categories cannot be treated as equivalent. This component preserves the distinction so downstream artifacts can represent authority without silently inventing it.

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

## Fit and limitations

Use this component when the job is **evidence-linked extraction and classification of operator authority and decision candidates from already-normalized conversations**.

It does not:

- acquire conversations;
- normalize raw exports;
- promote assistant statements to operator authority;
- promote natural-language candidates without review;
- infer that an authorized action was executed or completed;
- generate a complete Project Foreman recovery package;
- establish general provider or marketplace portability.

## Fastest first value

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q

tkp-authority-extract .\fixtures\sanitized_normalized_conversation.json .\demo-output
```

## Input contract

The public release accepts a normalized conversation object containing:

- a stable `conversation_id`;
- ordered turns;
- a stable `turn_id` and ordinal for each turn;
- `role`;
- plain text;
- one or more exact `source_refs`.

See `docs/INPUT_OUTPUT_CONTRACT.md`.

## Proof and evidence boundary

The included fixture is synthetic and sanitized, but it reproduces the governing distinctions exercised by Project Foreman:

- structured authorizations and acceptances;
- natural-language deferral, prohibition, and scope candidates;
- assistant statements that must remain non-authoritative;
- exact source references;
- no execution inference.

Historic private validation identified 188 structured-command evidence occurrences representing 180 unique direct operator commands. A further 352 natural-language candidates were held for review rather than promoted. No private source corpus is included here.

## Current release state

Current public release: **v0.1.0**, published July 19, 2026.

- Runnable Python package and CLI: yes
- Synthetic/sanitized public fixture: yes
- Automated tests: yes
- Clean GitHub-hosted Windows verification on the release head: passed
- Assistant authority promotion: no
- Natural-language authority promotion without review: no
- Execution/completion inference: no
- Private conversation corpus included: no

The release verification covered source tests, wheel construction, fresh-environment installation, CLI fixture execution, PASS receipt generation, zero recorded exceptions, and targeted privacy scanning. See [PUBLICATION_READINESS.md](PUBLICATION_READINESS.md) and [WINDOWS_VERIFICATION_GATE.md](WINDOWS_VERIFICATION_GATE.md).

## Trust, support, and security

For ordinary usage questions and non-sensitive defects, see [SUPPORT.md](SUPPORT.md).

For sensitive-data and security-reporting guidance, see [SECURITY.md](SECURITY.md). The repository does not currently claim a dedicated private vulnerability-reporting channel.

## Product and portability boundary

This repository is an upstream **product component** for Project Foreman. It consumes normalized conversation records and produces evidence-linked authority/decision ledgers, review queues, audit registers, and receipts.

It does not provide a general provider/target adapter framework. No broader multi-target portability claim is established by this repository alone.

## License

Released under the MIT License. See `LICENSE`.
