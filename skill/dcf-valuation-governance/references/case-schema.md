# Public case schema

The reference CLI consumes one JSON object:

```json
{
  "case_id": "stable-slug",
  "company_name": "Synthetic Company",
  "valuation_date": "2026-06-30",
  "currency": "CNY",
  "per_share_currency": "CNY",
  "bridge": {
    "net_debt": 250,
    "minority_interest": 0,
    "non_operating_investments": 50,
    "diluted_shares": 100
  },
  "scenarios": {
    "bear": {
      "probability": 0.25,
      "wacc": 0.105,
      "terminal_growth": 0.02,
      "revenue": [1000, 1060, 1113],
      "ebit_margin": [0.12, 0.115, 0.11],
      "tax_rate": [0.25, 0.25, 0.25],
      "da_pct_revenue": [0.03, 0.03, 0.03],
      "capex_pct_revenue": [0.04, 0.04, 0.04],
      "nwc_pct_revenue": [0.12, 0.12, 0.12],
      "opening_nwc": 112
    }
  }
}
```

All scenario arrays must have the same non-zero length. Rates are decimal fractions. Money fields must use one model currency. The public CLI does not perform FX conversion or fetch market data.
