# Governance gates

## Gate 1 — source integrity

- Historical facts trace to primary disclosures.
- Market data has a valuation date and source.
- Broker material is counter-evidence, not formula authority.

## Gate 2 — assumption integrity

- Each material assumption is labeled `fact`, `calculation`, or `judgment`.
- Revenue, margin, reinvestment, risk/terminal, and equity bridge are covered.
- Bear/base/bull ranges, counter-evidence, and falsifiers are explicit.

## Gate 3 — model integrity

- Statements or equivalent schedules reconcile.
- FCFF follows `NOPAT + D&A - Capex - ΔNWC`.
- `WACC > g`, probabilities sum to 100%, units are consistent.
- Enterprise-to-equity and diluted-share bridges are explicit.

## Gate 4 — workbook integrity

- Formula cells are formulas where expected.
- No `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, or stale cached errors.
- Checks, sensitivities, and reverse DCF are present.

## Gate 5 — independent recalculation

- Recalculate with an engine independent of the workbook writer.
- Re-run the same contract on the recalculated file.
- Compare key outputs within a declared tolerance.

## Gate 6 — release integrity

- Persist an immutable run id.
- Bind source revision, runtime, checks, artifacts, and SHA-256 in a run manifest.
- Promote `latest` only when every hard gate passes.
- Preserve failed runs for diagnosis; never overwrite a prior run id.

`PASS` requires all six gates. Anything less remains `DRAFT_REVIEW` or `BLOCKED`.
