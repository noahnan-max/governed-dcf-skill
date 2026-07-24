# Governed DCF Valuation Skill

An installable AI skill and transparent reference implementation for building, auditing, and challenging intrinsic-value models.

The core idea is simple: a DCF is not “forecast five years and divide by WACC.” A credible valuation must connect sources → assumptions → operating drivers → financial statements → FCFF → valuation → independent checks → immutable release evidence.

## What this public project includes

- A reusable `dcf-valuation-governance` Skill for Codex-compatible agents.
- Valuation-method routing for FCFF, FCFE, DDM, residual income, fair-PB, NAV, and SOTP.
- A three-scenario FCFF reference CLI with an explicit EV-to-equity bridge.
- WACC × terminal-growth sensitivity and reverse DCF.
- A synthetic case with no real-company or licensed data.
- Governance references for assumption dossiers, a 24-module workbook contract, independent recalculation, run manifests, and fail-closed release gates.
- Automated tests for validation, FCFF, the equity bridge, sensitivity, and reverse DCF.

## What remains private

This is a sanitized public Skill, not a dump of the private production engine. Real company cases, holdings, licensed research, reference models, source documents, generated workbooks, local run logs, machine identity, and credentials are deliberately excluded.

The private production system that inspired this Skill has been validated with:

- 31/31 engine regression checks;
- a 24-sheet golden workbook with 10,358 formulas;
- 24 hard workbook checks;
- independent LibreOffice recalculation;
- formula-error scans, SHA-256 artifacts, run manifests, and guarded `latest` promotion.

Those figures describe the private governed engine’s verified baseline, not a claim that this lightweight public CLI generates the same workbook.

## Quick start

```bash
python3 skill/dcf-valuation-governance/scripts/dcf_cli.py \
  validate --input examples/synthetic-consumer-case.json

python3 skill/dcf-valuation-governance/scripts/dcf_cli.py \
  run --input examples/synthetic-consumer-case.json

python3 skill/dcf-valuation-governance/scripts/dcf_cli.py \
  reverse \
  --input examples/synthetic-consumer-case.json \
  --scenario base \
  --target-price 42
```

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

## Install as a Skill

Copy `skill/dcf-valuation-governance` into your agent’s skills directory, then invoke:

```text
Use $dcf-valuation-governance to build and audit a three-scenario DCF.
```

The Skill defaults to `DRAFT_REVIEW` or `BLOCKED` when evidence or model gates are incomplete. It does not produce a trade instruction.

## Repository map

```text
skill/dcf-valuation-governance/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/dcf_cli.py
examples/
tests/
```

## Disclaimer

Educational and research use only. Nothing in this repository is investment advice, a recommendation, or a promise of returns. Validate data, assumptions, formulas, taxes, currencies, share counts, and legal requirements independently.
