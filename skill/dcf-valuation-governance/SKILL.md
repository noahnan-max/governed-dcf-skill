---
name: dcf-valuation-governance
description: Build, audit, challenge, and explain governed intrinsic-value models. Use for three-scenario FCFF DCFs, WACC and terminal-value review, reverse DCF, valuation-method routing, equity bridges, sensitivity analysis, assumption dossiers, workbook contracts, and fail-closed valuation quality gates. Do not use it to produce a buy/sell recommendation from incomplete evidence.
---

# Governed DCF Valuation

Treat valuation as an auditable research system, not a one-cell formula.

## Non-negotiable output state

Return one of:

- `PASS`: required inputs, explicit assumptions, model checks, sensitivity, and independent recalculation all pass.
- `DRAFT_REVIEW`: the model runs, but one or more evidence or review gates remain open.
- `BLOCKED`: required facts or structural inputs are missing; do not fill them with invented values.

Never turn missing data into zero. Never describe a `DRAFT_REVIEW` model as final.

## Workflow

1. **Route the valuation family.** Read `references/valuation-routing.md`.
   - Ordinary operating company: FCFF DCF.
   - Bank, insurer, or broker: FCFE, DDM, residual income, or fair-PB.
   - Property, resources, or strong segment economics: NAV or SOTP.
2. **Freeze the valuation date and units.**
   - State valuation date, reporting cut-off, model currency, per-share currency, diluted shares, and bridge items.
3. **Build the evidence and assumption dossiers.**
   - Historical facts must trace to primary disclosures.
   - Separate `fact`, `calculation`, and `judgment`.
   - Cover revenue, margin, reinvestment, risk/terminal value, and equity bridge.
   - Give every material assumption a base view, bear/base/bull range, evidence, counter-evidence, and falsifier.
4. **Build integrated operating forecasts before valuation.**
   - Forecast business drivers and complete statements or equivalent schedules.
   - Derive FCFF from operations; do not type a free-standing cash-flow series with no bridge.
5. **Run three scenarios.**
   - Probabilities must be explicit and sum to 100%.
   - Each scenario must carry its own WACC, terminal growth, and forecast path.
6. **Run valuation checks.**
   - Require `WACC > terminal growth`.
   - Reconcile enterprise value to equity value and diluted per-share value.
   - Report terminal-value share of enterprise value.
   - Produce WACC × terminal-growth sensitivity and reverse DCF.
7. **Apply workbook and governance gates.**
   - Read `references/workbook-contract.md` and `references/governance-gates.md`.
   - Recalculate independently, scan formula errors, and bind outputs to a run manifest and hashes.
8. **Communicate uncertainty.**
   - Present a range and the variables that change it.
   - State evidence gaps, falsifiers, and what would move the valuation.
   - Add “educational analysis, not investment advice.”

## Public reference CLI

The bundled CLI runs a synthetic or user-provided three-scenario FCFF case. It is a transparent reference implementation, not a substitute for an integrated production workbook.

```bash
python scripts/dcf_cli.py validate --input ../../../examples/synthetic-consumer-case.json
python scripts/dcf_cli.py run --input ../../../examples/synthetic-consumer-case.json
python scripts/dcf_cli.py reverse \
  --input ../../../examples/synthetic-consumer-case.json \
  --scenario base \
  --target-price 42
```

The `run` output must include:

- enterprise value, equity value, and value per diluted share;
- explicit-period PV and terminal-value PV;
- terminal-value share;
- probability-weighted expected value;
- base-case WACC × terminal-growth sensitivity;
- warnings and a machine-readable status.

## Required answer structure

1. **Conclusion and status** — valuation range, probability-weighted value, `PASS/DRAFT_REVIEW/BLOCKED`.
2. **Method routing** — why this valuation family fits the company.
3. **Source and cut-off** — disclosures, dates, units, currency.
4. **Operating model** — business drivers and statement links.
5. **Assumption dossier** — bear/base/bull plus evidence and falsifiers.
6. **DCF bridge** — FCFF, WACC, terminal value, EV-to-equity, per share.
7. **Sensitivity and reverse DCF** — what the current price implies.
8. **Quality gates and limitations** — checks passed, open gaps, independent recalculation.

## Stop rules

Stop and return `BLOCKED` when:

- the valuation date, share count, or bridge cannot be established;
- a material assumption has no evidence or explicit judgment label;
- `WACC <= terminal growth`;
- probabilities do not sum to 100%;
- formula errors or independent recalculation differences remain;
- the method is structurally wrong for the company.

Keep research and execution separate. A valuation result is not a trade instruction.
