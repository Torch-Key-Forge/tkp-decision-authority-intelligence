# Input and Output Contract

## Input

The extractor accepts one normalized conversation JSON object.

Required fields:

- `conversation_id`
- `turns[]`
- `turn_id`
- `ordinal`
- `role`
- `text`
- `source_refs[]`

Only `role: user` is eligible for operator authority.

## Structured command admission

A structured command must:

1. occur in a user turn;
2. be uppercase underscore-delimited structured text;
3. retain exact source references;
4. be classified without inferring execution.

Recognized prefixes include `AUTHORIZE_`, `ACCEPT_`, `APPROVE_`, `HOLD_`, `DEFER_`, `REJECT_`, `PROHIBIT_`, and `DO_NOT_`.

## Natural-language handling

Natural-language authority-like statements are candidates only. They are emitted to a review queue with candidate identity, proposed decision class, matching rule, exact statement, role, source references, text hash, and `PROVISIONAL_REVIEW` status.

## Assistant handling

Matching assistant, tool, or system statements are never promoted. They may be retained in the non-authority register for audit.

## Outputs

The extractor writes a structured authority ledger, natural-language review queue, assistant non-authority register, exception register, extraction receipt, and SHA-256 checksums.
