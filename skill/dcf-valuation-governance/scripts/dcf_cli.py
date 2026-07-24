#!/usr/bin/env python3
"""Transparent three-scenario FCFF DCF reference implementation.

This educational CLI deliberately keeps the calculations inspectable. It does
not fetch market data and does not replace an integrated production workbook.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ERROR_TOKENS = ("TBD", "TODO", "N/A?", "#REF!", "#DIV/0!", "#VALUE!", "#NAME?")
REQUIRED_SCENARIOS = ("bear", "base", "bull")
ARRAY_FIELDS = (
    "revenue",
    "ebit_margin",
    "tax_rate",
    "da_pct_revenue",
    "capex_pct_revenue",
    "nwc_pct_revenue",
)


class CaseError(ValueError):
    """Raised when a case fails a hard validation gate."""


def load_case(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CaseError("case root must be an object")
    return data


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CaseError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise CaseError(f"{label} must be finite")
    return number


def validate_case(case: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for field in ("case_id", "company_name", "valuation_date", "currency", "per_share_currency"):
        value = case.get(field)
        if not isinstance(value, str) or not value.strip():
            raise CaseError(f"missing non-empty {field}")
        upper = value.upper()
        if any(token in upper for token in ERROR_TOKENS):
            raise CaseError(f"{field} contains a placeholder or error token")

    bridge = case.get("bridge")
    if not isinstance(bridge, dict):
        raise CaseError("bridge must be an object")
    for field in ("net_debt", "minority_interest", "non_operating_investments"):
        _finite_number(bridge.get(field), f"bridge.{field}")
    diluted_shares = _finite_number(bridge.get("diluted_shares"), "bridge.diluted_shares")
    if diluted_shares <= 0:
        raise CaseError("bridge.diluted_shares must be greater than zero")

    scenarios = case.get("scenarios")
    if not isinstance(scenarios, dict) or tuple(sorted(scenarios)) != tuple(sorted(REQUIRED_SCENARIOS)):
        raise CaseError("scenarios must contain exactly bear, base, and bull")

    probability_total = 0.0
    forecast_years: int | None = None
    for name in REQUIRED_SCENARIOS:
        scenario = scenarios[name]
        if not isinstance(scenario, dict):
            raise CaseError(f"scenarios.{name} must be an object")
        probability = _finite_number(scenario.get("probability"), f"{name}.probability")
        if probability < 0 or probability > 1:
            raise CaseError(f"{name}.probability must be between zero and one")
        probability_total += probability

        wacc = _finite_number(scenario.get("wacc"), f"{name}.wacc")
        terminal_growth = _finite_number(scenario.get("terminal_growth"), f"{name}.terminal_growth")
        if not 0 < wacc < 1:
            raise CaseError(f"{name}.wacc must be between zero and one")
        if not -0.20 < terminal_growth < 0.20:
            raise CaseError(f"{name}.terminal_growth is outside the supported range")
        if wacc <= terminal_growth:
            raise CaseError(f"{name} fails WACC > terminal growth")

        lengths: set[int] = set()
        for field in ARRAY_FIELDS:
            values = scenario.get(field)
            if not isinstance(values, list) or not values:
                raise CaseError(f"{name}.{field} must be a non-empty array")
            lengths.add(len(values))
            for index, value in enumerate(values):
                number = _finite_number(value, f"{name}.{field}[{index}]")
                if field == "revenue" and number <= 0:
                    raise CaseError(f"{name}.{field}[{index}] must be positive")
                if field != "revenue" and not -1 < number < 1:
                    raise CaseError(f"{name}.{field}[{index}] must be a decimal rate")
        if len(lengths) != 1:
            raise CaseError(f"{name} forecast arrays must have the same length")
        years = lengths.pop()
        if forecast_years is None:
            forecast_years = years
        elif years != forecast_years:
            raise CaseError("all scenarios must use the same forecast horizon")

        opening_nwc = _finite_number(scenario.get("opening_nwc"), f"{name}.opening_nwc")
        if opening_nwc < 0:
            warnings.append(f"{name}: opening NWC is negative; confirm the business model")

    if abs(probability_total - 1.0) > 1e-9:
        raise CaseError(f"scenario probabilities sum to {probability_total:.10f}, not 1")
    if forecast_years is not None and forecast_years < 3:
        warnings.append("forecast horizon is shorter than three years")
    if case["currency"] != case["per_share_currency"]:
        warnings.append("model and per-share currencies differ; the public CLI does not perform FX conversion")
    return warnings


def scenario_dcf(case: dict[str, Any], name: str, wacc: float | None = None, terminal_growth: float | None = None) -> dict[str, Any]:
    scenario = case["scenarios"][name]
    rate = float(scenario["wacc"] if wacc is None else wacc)
    growth = float(scenario["terminal_growth"] if terminal_growth is None else terminal_growth)
    if rate <= growth:
        raise CaseError(f"{name} fails WACC > terminal growth")

    rows: list[dict[str, float | int]] = []
    previous_nwc = float(scenario["opening_nwc"])
    pv_explicit = 0.0
    for index, revenue_value in enumerate(scenario["revenue"]):
        year = index + 1
        revenue = float(revenue_value)
        ebit = revenue * float(scenario["ebit_margin"][index])
        nopat = ebit * (1.0 - float(scenario["tax_rate"][index]))
        depreciation = revenue * float(scenario["da_pct_revenue"][index])
        capex = revenue * float(scenario["capex_pct_revenue"][index])
        nwc = revenue * float(scenario["nwc_pct_revenue"][index])
        delta_nwc = nwc - previous_nwc
        fcff = nopat + depreciation - capex - delta_nwc
        discount_factor = (1.0 + rate) ** year
        pv_fcff = fcff / discount_factor
        pv_explicit += pv_fcff
        rows.append(
            {
                "year": year,
                "revenue": revenue,
                "ebit": ebit,
                "nopat": nopat,
                "depreciation": depreciation,
                "capex": capex,
                "delta_nwc": delta_nwc,
                "fcff": fcff,
                "discount_factor": discount_factor,
                "pv_fcff": pv_fcff,
            }
        )
        previous_nwc = nwc

    terminal_fcff = float(rows[-1]["fcff"]) * (1.0 + growth)
    terminal_value = terminal_fcff / (rate - growth)
    terminal_discount_factor = float(rows[-1]["discount_factor"])
    pv_terminal = terminal_value / terminal_discount_factor
    enterprise_value = pv_explicit + pv_terminal

    bridge = case["bridge"]
    equity_value = (
        enterprise_value
        - float(bridge["net_debt"])
        - float(bridge["minority_interest"])
        + float(bridge["non_operating_investments"])
    )
    value_per_share = equity_value / float(bridge["diluted_shares"])
    terminal_share = pv_terminal / enterprise_value if enterprise_value else math.nan
    return {
        "scenario": name,
        "probability": float(scenario["probability"]),
        "wacc": rate,
        "terminal_growth": growth,
        "forecast": rows,
        "pv_explicit_fcff": pv_explicit,
        "terminal_fcff": terminal_fcff,
        "terminal_value_at_horizon": terminal_value,
        "pv_terminal_value": pv_terminal,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "value_per_share": value_per_share,
        "terminal_value_share": terminal_share,
    }


def sensitivity(case: dict[str, Any], wacc_steps: tuple[float, ...] = (-0.01, -0.005, 0.0, 0.005, 0.01), growth_steps: tuple[float, ...] = (-0.01, -0.005, 0.0, 0.005, 0.01)) -> dict[str, Any]:
    base = case["scenarios"]["base"]
    base_wacc = float(base["wacc"])
    base_growth = float(base["terminal_growth"])
    rows: list[dict[str, Any]] = []
    for growth_delta in growth_steps:
        growth = base_growth + growth_delta
        values: list[float | None] = []
        for wacc_delta in wacc_steps:
            wacc = base_wacc + wacc_delta
            if wacc <= growth:
                values.append(None)
            else:
                values.append(scenario_dcf(case, "base", wacc=wacc, terminal_growth=growth)["value_per_share"])
        rows.append({"terminal_growth": growth, "values": values})
    return {
        "wacc_columns": [base_wacc + delta for delta in wacc_steps],
        "rows": rows,
    }


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    warnings = validate_case(case)
    scenarios = {name: scenario_dcf(case, name) for name in REQUIRED_SCENARIOS}
    expected_value = sum(item["probability"] * item["value_per_share"] for item in scenarios.values())
    terminal_shares = [item["terminal_value_share"] for item in scenarios.values()]
    if max(terminal_shares) > 0.80:
        warnings.append("terminal value exceeds 80% of enterprise value in at least one scenario")
    return {
        "schema_version": 1,
        "status": "PASS" if not warnings else "DRAFT_REVIEW",
        "case_id": case["case_id"],
        "company_name": case["company_name"],
        "valuation_date": case["valuation_date"],
        "currency": case["currency"],
        "scenarios": scenarios,
        "probability_weighted_value_per_share": expected_value,
        "base_sensitivity": sensitivity(case),
        "warnings": warnings,
        "disclaimer": "Educational analysis only; not investment advice.",
    }


def implied_terminal_growth(case: dict[str, Any], scenario_name: str, target_price: float) -> dict[str, Any]:
    validate_case(case)
    if scenario_name not in REQUIRED_SCENARIOS:
        raise CaseError("scenario must be bear, base, or bull")
    if not math.isfinite(target_price) or target_price <= 0:
        raise CaseError("target price must be positive and finite")

    scenario = scenario_dcf(case, scenario_name)
    bridge = case["bridge"]
    target_equity = target_price * float(bridge["diluted_shares"])
    target_enterprise = (
        target_equity
        + float(bridge["net_debt"])
        + float(bridge["minority_interest"])
        - float(bridge["non_operating_investments"])
    )
    required_pv_terminal = target_enterprise - float(scenario["pv_explicit_fcff"])
    if required_pv_terminal <= 0:
        raise CaseError("target price is below the value of explicit cash flows after the equity bridge")
    horizon_factor = float(scenario["forecast"][-1]["discount_factor"])
    required_terminal_value = required_pv_terminal * horizon_factor
    terminal_fcff_pre_growth = float(scenario["forecast"][-1]["fcff"])
    wacc = float(scenario["wacc"])
    implied_growth = (required_terminal_value * wacc - terminal_fcff_pre_growth) / (
        required_terminal_value + terminal_fcff_pre_growth
    )
    return {
        "case_id": case["case_id"],
        "scenario": scenario_name,
        "target_price": target_price,
        "implied_terminal_growth": implied_growth,
        "model_terminal_growth": float(case["scenarios"][scenario_name]["terminal_growth"]),
        "wacc": wacc,
        "feasible_under_gordon_growth": implied_growth < wacc,
        "disclaimer": "Educational reverse DCF only; not investment advice.",
    }


def _rounded(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 8)
    if isinstance(value, list):
        return [_rounded(item) for item in value]
    if isinstance(value, dict):
        return {key: _rounded(item) for key, item in value.items()}
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "run"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--input", required=True)
    reverse_parser = subparsers.add_parser("reverse")
    reverse_parser.add_argument("--input", required=True)
    reverse_parser.add_argument("--scenario", choices=REQUIRED_SCENARIOS, default="base")
    reverse_parser.add_argument("--target-price", type=float, required=True)
    args = parser.parse_args()

    try:
        case = load_case(args.input)
        if args.command == "validate":
            output: dict[str, Any] = {"status": "PASS", "warnings": validate_case(case)}
        elif args.command == "run":
            output = run_case(case)
        else:
            output = implied_terminal_growth(case, args.scenario, args.target_price)
    except (CaseError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(_rounded(output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
