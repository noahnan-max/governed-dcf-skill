from __future__ import annotations

import importlib.util
import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skill" / "dcf-valuation-governance" / "scripts" / "dcf_cli.py"
SPEC = importlib.util.spec_from_file_location("dcf_cli", SCRIPT)
assert SPEC and SPEC.loader
DCF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DCF)


class DcfCliTests(unittest.TestCase):
    def setUp(self) -> None:
        path = ROOT / "examples" / "synthetic-consumer-case.json"
        self.case = json.loads(path.read_text(encoding="utf-8"))

    def test_synthetic_case_passes_validation(self) -> None:
        self.assertEqual(DCF.validate_case(self.case), [])

    def test_run_is_finite_and_probability_weighted(self) -> None:
        result = DCF.run_case(self.case)
        values = result["scenarios"]
        expected = sum(item["probability"] * item["value_per_share"] for item in values.values())
        self.assertAlmostEqual(result["probability_weighted_value_per_share"], expected, places=10)
        self.assertTrue(math.isfinite(expected))
        self.assertGreater(values["bull"]["value_per_share"], values["base"]["value_per_share"])
        self.assertGreater(values["base"]["value_per_share"], values["bear"]["value_per_share"])

    def test_fcff_bridge_reconciles(self) -> None:
        result = DCF.scenario_dcf(self.case, "base")
        for row in result["forecast"]:
            reconstructed = row["nopat"] + row["depreciation"] - row["capex"] - row["delta_nwc"]
            self.assertAlmostEqual(row["fcff"], reconstructed, places=10)

    def test_equity_bridge_reconciles(self) -> None:
        result = DCF.scenario_dcf(self.case, "base")
        bridge = self.case["bridge"]
        expected = (
            result["enterprise_value"]
            - bridge["net_debt"]
            - bridge["minority_interest"]
            + bridge["non_operating_investments"]
        )
        self.assertAlmostEqual(result["equity_value"], expected, places=10)
        self.assertAlmostEqual(result["value_per_share"], expected / bridge["diluted_shares"], places=10)

    def test_wacc_must_exceed_growth(self) -> None:
        broken = json.loads(json.dumps(self.case))
        broken["scenarios"]["base"]["wacc"] = 0.03
        broken["scenarios"]["base"]["terminal_growth"] = 0.03
        with self.assertRaises(DCF.CaseError):
            DCF.validate_case(broken)

    def test_probabilities_must_sum_to_one(self) -> None:
        broken = json.loads(json.dumps(self.case))
        broken["scenarios"]["bull"]["probability"] = 0.20
        with self.assertRaises(DCF.CaseError):
            DCF.validate_case(broken)

    def test_sensitivity_center_matches_base(self) -> None:
        base = DCF.scenario_dcf(self.case, "base")["value_per_share"]
        table = DCF.sensitivity(self.case)
        self.assertAlmostEqual(table["rows"][2]["values"][2], base, places=10)

    def test_reverse_dcf_recovers_model_growth(self) -> None:
        base = DCF.scenario_dcf(self.case, "base")
        reverse = DCF.implied_terminal_growth(self.case, "base", base["value_per_share"])
        self.assertAlmostEqual(
            reverse["implied_terminal_growth"],
            self.case["scenarios"]["base"]["terminal_growth"],
            places=10,
        )


if __name__ == "__main__":
    unittest.main()
