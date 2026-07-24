# Workbook contract

A production DCF workbook should expose a coherent model, not a decorative spreadsheet.

## Minimum modules

1. Cover and navigation
2. Source register and valuation date
3. Assumption dossier
4. Historical income statement
5. Historical balance sheet
6. Historical cash-flow statement
7. Revenue drivers
8. Margin and operating-cost drivers
9. Working-capital schedules
10. Capex and depreciation
11. Debt and interest
12. Tax schedule
13. Forecast income statement
14. Forecast balance sheet
15. Forecast cash-flow statement
16. Statement reconciliation
17. FCFF bridge
18. WACC
19. Terminal value
20. EV-to-equity bridge
21. Bear/base/bull scenarios
22. Sensitivity tables
23. Reverse DCF
24. Checks and release summary

## Hard checks

- The balance sheet balances for every forecast period.
- Cash movement reconciles to the cash-flow statement.
- Debt and interest use the same timing convention.
- FCFF reconciles to the operating schedules.
- Terminal value uses a stable cash-flow definition.
- Per-share value uses diluted, not basic, shares unless explicitly justified.
- All scenario probabilities sum to 100%.
- Every scenario satisfies `WACC > g`.
- No formula error tokens remain after independent recalculation.
- The release summary says `MASTER PASS` only when every hard check is true.
