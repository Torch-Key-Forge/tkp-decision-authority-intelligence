# Security

## Data sensitivity

Normalized conversation records and authority-review outputs can contain private, personal, client, organizational, or credential-bearing material. Use synthetic or sanitized fixtures for public reproduction and debugging.

Do not commit or post private conversation records, access tokens, credentials, local private paths, client data, or sensitive authority material.

## Reporting

This repository does not currently publish a dedicated private vulnerability-reporting contact or claim a verified private security-reporting channel.

Do **not** disclose secrets, private source data, sensitive authority records, or exploit details in a public GitHub issue. Public issues may be used only for sanitized, non-sensitive security hardening questions that are safe to discuss openly.

A dedicated private reporting route remains a public-governance gap rather than a capability claimed by this repository.

## Trust-boundary safety

Security defects include any behavior that could incorrectly promote assistant language, unreviewed natural-language candidates, or unsupported execution/completion claims into authoritative output.

The current public contract requires:

- operator authority originates only from user/operator evidence;
- assistant statements remain non-authoritative;
- natural-language candidates remain provisional until review;
- a command is not proof of execution or completion.

## Current supported state

The current public release observed during the August 29, 2026 GitHub Estate Reconciliation is `v0.1.0` under the MIT License. GitHub-hosted Windows verification exists for the release head.

That verification is not a claim of penetration testing, security certification, or suitability for processing secrets without appropriate operator controls.
