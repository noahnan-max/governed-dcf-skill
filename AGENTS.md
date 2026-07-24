# Working agreement

- Keep examples synthetic or user-provided.
- Never invent missing financial facts; return `BLOCKED`.
- Keep valuation results separate from trade instructions.
- Preserve the public/private disclosure boundary in `SECURITY.md`.
- Run `python3 -m unittest discover -s tests -v` after calculation changes.
- Do not weaken `WACC > terminal growth`, probability, bridge, or finite-number checks.
