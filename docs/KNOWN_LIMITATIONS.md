# Known Limitations

1. The public candidate operates on one normalized conversation object at a time.
2. Natural-language rules are deliberately narrow and may produce overlapping candidates.
3. Candidate detection is not semantic adjudication.
4. Structured commands outside recognized prefixes receive the generic `STRUCTURED_COMMAND` class.
5. Supersession, revocation, amendment, dependency, and conflict graphs are not yet resolved.
6. Execution status is never inferred from command text.
7. The private 180-command validation corpus is not included.
