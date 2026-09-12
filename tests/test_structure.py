"""Regression checks for pure signal gates and daily-structure wiring.

Run with: python3 -m unittest discover -s tests -v

The helper adapter executes the small, pure gate bodies read from vix.pine.
It does not compile Pine or emulate request.security, history, or realtime
rollback. TradingView compilation and chart/reload checks remain required.
"""

from __future__ import annotations

import ast
import math
from pathlib import Path
import re
from types import SimpleNamespace
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "vix.pine"


def _assignment(name: str) -> str:
    match = re.search(rf"^(?:(?:float|int|bool|string) )?{name}\s*=\s*(.+)$", SOURCE.read_text(), re.M)
    if match is None:
        raise AssertionError(f"Missing assignment: {name}")
    return match[1].split("//", 1)[0].strip()


def _value(name: str, **bindings):
    """Evaluate an actual scalar production predicate with fixture inputs."""
    expression = _expression(_assignment(name))
    namespace = {"__builtins__": {}, "na": lambda value: value is None or isinstance(value, float) and math.isnan(value)}
    return eval(expression, namespace, bindings)


def _split_arguments(text: str) -> list[str]:
    parts, start, depth, quoted = [], 0, 0, False
    for index, char in enumerate(text):
        if char == '"' and (index == 0 or text[index - 1] != "\\"):
            quoted = not quoted
        elif not quoted:
            if char in "([":
                depth += 1
            elif char in ")]":
                depth -= 1
            elif char == "," and depth == 0:
                parts.append(text[start:index].strip())
                start = index + 1
    return parts + [text[start:].strip()]


def _request_tuple(first_output: str):
    match = re.search(rf"^\[({first_output},[^\n]+)\] = request\.security\(([^\n]+)\)$", SOURCE.read_text(), re.M)
    if match is None:
        raise AssertionError(f"Missing tuple request: {first_output}")
    arguments = _split_arguments(match[2])
    outputs = _split_arguments(match[1])
    expressions = _split_arguments(arguments[2][1:-1])
    if len(outputs) != len(expressions):
        raise AssertionError("Mismatched tuple output/expression arity")
    return arguments, dict(zip(outputs, expressions))


def _expression(expression: str) -> str:
    """Translate the top-level, right-associative Pine ternaries in our gates."""
    depth = 0
    question = None
    nested = 0
    for index, char in enumerate(expression):
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif depth == 0 and char == "?":
            if question is None:
                question = index
            else:
                nested += 1
        elif depth == 0 and char == ":" and question is not None:
            if nested:
                nested -= 1
            else:
                condition = _expression(expression[:question].strip())
                yes = _expression(expression[question + 1:index].strip())
                no = _expression(expression[index + 1:].strip())
                return f"({yes} if {condition} else {no})"
    if "?" in expression:
        raise AssertionError("Unsupported nested-parenthesis ternary in gate adapter")
    return re.sub(r"\b(false|true)\b", lambda m: m[0].title(), expression)


def _load_helper(name: str):
    """Load only the supported pure syntax; fail if a gate becomes stateful."""
    source = SOURCE.read_text()
    match = re.search(rf"^{name}\(([^\n]*)\) =>\n((?:[ \t]+[^\n]*\n)+)", source, re.M)
    if match is None:
        raise AssertionError(f"Missing pure helper: {name}")
    arguments, body = match.groups()
    translated = [f"def {name}({arguments}):"]
    lines = [line for line in body.splitlines() if line.strip() and not line.lstrip().startswith("//")]
    for index, line in enumerate(lines):
        indentation = line[:len(line) - len(line.lstrip())]
        value = line.strip().split("//", 1)[0].strip()
        if value.startswith("else if "):
            value = "elif " + _expression(value[8:]) + ":"
        elif value.startswith("if "):
            value = "if " + _expression(value[3:]) + ":"
        elif value == "else":
            value = "else:"
        elif ":=" in value or re.match(r"(?:(?:int|float|bool) )?\w+ = ", value):
            value = re.sub(r"^(int|float|bool) ", "", value)
            lhs, rhs = re.split(r"\s*(?::=|=)\s*", value, maxsplit=1)
            value = lhs + " = " + _expression(rhs)
        elif index == len(lines) - 1:
            value = "return " + _expression(value)
        else:
            raise AssertionError(f"Unsupported gate statement: {value}")
        translated.append(indentation + value)
    tree = ast.parse("\n".join(translated))
    allowed = (
        ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Assign, ast.Name,
        ast.Load, ast.Store, ast.Constant, ast.If, ast.IfExp, ast.Return, ast.List,
        ast.Call, ast.UnaryOp, ast.Not, ast.USub, ast.BoolOp, ast.And, ast.Or,
        ast.Compare, ast.Eq, ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise AssertionError(f"Unsupported gate syntax: {type(node).__name__}")
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id == "na"):
            raise AssertionError("Pure gate adapter only supports na() calls")
    namespace = {"__builtins__": {}, "na": lambda value: value is None or isinstance(value, float) and math.isnan(value)}
    exec(compile(tree, str(SOURCE), "exec"), namespace)
    return namespace[name]


class SignalSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setup_gate = staticmethod(_load_helper("f_signal_setup"))
        cls.buy_transition = staticmethod(_load_helper("f_buy_transition"))
        cls.sell_transition = staticmethod(_load_helper("f_sell_transition"))

    def setup(self, **changes):
        values = dict(s=4, ready=True, regime=2, mom_buy=True, mom_sell=True,
                      z_val=-1.8, mid=1.5, min_buy=4, core_buy=True,
                      core_sell=True, strict_sell=False, filter_trend=True,
                      trend_ready=True, trend_bull=True)
        values.update(changes)
        return self.setup_gate(**values)

    def test_missing_core_blocks_extreme_and_normal_setups(self):
        # The regression included a synthetic -5 from SKEW(-3) + PCR(-2)
        # even when the VIX/futures source itself was unavailable.
        for score in (-6, -5, -2, 0, 4, 5, 6):
            with self.subTest(score=score):
                self.assertEqual(self.setup(s=score, ready=False), [0, 0, 1])
        self.assertEqual(self.setup(s=math.nan), [0, 0, 1])

    def test_buy_dip_gate_reasons_are_specific(self):
        self.assertEqual(self.setup(), [1, 0, 0])
        for changes, reason in ((dict(regime=3), 2), (dict(mom_buy=False), 3),
                                (dict(z_val=-1.5), 4), (dict(core_buy=False), 5),
                                (dict(trend_ready=False), 6), (dict(trend_bull=False), 7)):
            with self.subTest(changes=changes):
                self.assertEqual(self.setup(**changes), [0, 0, reason])

    def test_trend_availability_only_gates_trend_filtered_dips(self):
        self.assertEqual(self.setup(trend_ready=False, filter_trend=False), [1, 0, 0])
        self.assertEqual(self.setup(s=5, trend_ready=False, trend_bull=False), [2, 0, 0])
        self.assertEqual(self.setup(s=6, trend_ready=False, trend_bull=False), [3, 0, 0])

    def test_balanced_and_strict_sells_preserve_their_contract(self):
        self.assertEqual(self.setup(s=-5, core_sell=False), [0, 2, 0])
        self.assertEqual(self.setup(s=-5, core_sell=False, strict_sell=True), [0, 0, 5])
        self.assertEqual(self.setup(s=-6, core_sell=False, strict_sell=True), [0, 3, 0])
        self.assertEqual(self.setup(s=-2, regime=1), [0, 0, 2])
        self.assertEqual(self.setup(s=-2, mom_sell=False), [0, 0, 3])

    def test_only_threshold_entries_and_upgrades_create_events(self):
        for score, previous, expected in ((4, 3, 1), (5, 4, 2), (6, 5, 3),
                                           (4, 4, 0), (5, 6, 0), (6, 6, 0)):
            with self.subTest(score=score, previous=previous):
                self.assertEqual(self.buy_transition(score, previous, 4), expected)
        for score, previous, expected in ((-2, -1, 1), (-5, -4, 2), (-6, -5, 3),
                                           (-2, -2, 0), (-5, -6, 0), (-6, -6, 0)):
            with self.subTest(score=score, previous=previous):
                self.assertEqual(self.sell_transition(score, previous), expected)

    def test_unknown_previous_snapshot_cannot_manufacture_crossing(self):
        self.assertEqual(self.buy_transition(6, math.nan, 4), 0)
        self.assertEqual(self.sell_transition(-6, math.nan), 0)
        self.assertEqual(self.buy_transition(math.nan, 0, 4), 0)
        self.assertEqual(self.sell_transition(math.nan, 0), 0)

    def test_changed_sensitivity_moves_only_the_dip_boundary(self):
        self.assertEqual(self.setup(s=2, min_buy=2), [1, 0, 0])
        self.assertEqual(self.setup(s=2, min_buy=3), [0, 0, 0])
        self.assertEqual(self.setup(s=3, min_buy=3), [1, 0, 0])
        self.assertEqual(self.setup(s=3, min_buy=4), [0, 0, 0])

    def test_rejected_crossing_does_not_suppress_the_next_valid_recross(self):
        last_signal, previous_score = 90, 3
        emitted = []
        for bar, score, bullish in ((100, 4, False), (101, 3, True), (103, 4, True)):
            setup_level = self.setup(s=score, trend_bull=bullish)[0]
            crossing = self.buy_transition(score, previous_score, 4)
            cooldown = _value("is_buy_dip_cooldown_ok", last_buy_dip_bar=last_signal,
                              bar_index=bar, signal_display_cooldown=5)
            final = _value("final_buy_dip", chart_signal_confirmed=True,
                           buy_transition_level=crossing, buy_setup_level=setup_level,
                           is_buy_dip_cooldown_ok=cooldown)
            if final:
                last_signal = bar
                emitted.append(bar)
            if bar == 100:
                self.assertEqual(last_signal, 90)
            previous_score = score
        self.assertEqual(emitted, [103])
        self.assertEqual(last_signal, 103)


class DataAndSymbolTests(unittest.TestCase):
    def test_missing_nonpositive_core_quotes_never_validate(self):
        self.assertTrue(_value("valid_data", vix=20, vx1=21, vx2=22))
        for field in ("vix", "vx1", "vx2"):
            for bad in (math.nan, 0.0, -1.0):
                quotes = dict(vix=20, vx1=21, vx2=22)
                quotes[field] = bad
                with self.subTest(field=field, bad=bad):
                    self.assertFalse(_value("valid_data", **quotes))

    def test_each_enabled_structure_factor_must_be_ready(self):
        factors = dict.fromkeys(("valid_data", "is_z_ready", "is_skew_ready", "is_pcr_ready",
                                 "is_basis_ready", "is_volume_ready", "is_vvix_ready"), True)
        self.assertTrue(_value("data_ready_chart", **factors))
        for factor in factors:
            with self.subTest(factor=factor):
                self.assertFalse(_value("data_ready_chart", **(factors | {factor: False})))
        self.assertNotRegex(_assignment("data_ready_chart"), r"trend|syminfo|bar_index")

    def test_warmup_requires_actual_observations(self):
        for count, expected in ((math.nan, False), (0, False), (251, False), (252, True)):
            with self.subTest(count=count):
                self.assertEqual(_value("has_sufficient_data", core_observations=count, adapt_lookback=252), expected)
        self.assertFalse(_value("is_z_ready", has_z_history=True, z_ready_observations=10, smooth_dyn=8, momentum_bars=3))
        self.assertTrue(_value("is_z_ready", has_z_history=True, z_ready_observations=11, smooth_dyn=8, momentum_bars=3))
        self.assertFalse(_value("is_z_ready", has_z_history=False, z_ready_observations=11, smooth_dyn=8, momentum_bars=3))

    def test_enabled_weekly_factor_requires_its_own_completed_feed(self):
        for enabled, weekly, expected in ((False, math.nan, True), (True, math.nan, False), (True, -2, True)):
            with self.subTest(enabled=enabled, weekly=weekly):
                self.assertEqual(_value("data_ready_live_chart", data_ready_chart=True,
                                        use_mtf_confirm=enabled, z_weekly=weekly), expected)
                self.assertEqual(_value("data_ready_confirmed_chart", data_ready_chart=True,
                                        use_mtf_confirm=enabled, z_weekly_confirmed=weekly), expected)

    def test_daily_volume_spike_is_not_twenty_carried_intraday_values(self):
        daily = [100.0] * 19 + [300.0]
        daily_ma = sum(daily) / 20
        self.assertAlmostEqual(300 / daily_ma, 30 / 11)
        self.assertTrue(_value("is_vol_spike", is_volume_ready=True, vx1_vol=300, vol_ma=daily_ma))
        # This was the old chart-context value after a daily quote was repeated
        # for twenty intraday bars, which erased the daily spike classification.
        carried_intraday_ma = sum([300.0] * 20) / 20
        self.assertEqual(300 / carried_intraday_ma, 1)
        self.assertFalse(_value("is_vol_spike", is_volume_ready=True, vx1_vol=300, vol_ma=carried_intraday_ma))
        self.assertFalse(_value("is_vol_spike", is_volume_ready=False, vx1_vol=300, vol_ma=daily_ma))

    def test_exact_index_family_detection_avoids_cnq_false_match(self):
        for ticker, root, kind, nasdaq, russell in (
            ("CNQ", "CNQ", "stock", False, False),
            ("QQQM", "QQQM", "fund", True, False),
            ("TQQQ", "TQQQ", "fund", True, False),
            ("MNQU2026", "MNQ", "futures", True, False),
            ("NQ", "NQ", "stock", False, False),
            ("IWM", "IWM", "fund", False, True),
            ("M2KU2026", "M2K", "futures", False, True),
            ("BRUT", "BRUT", "stock", False, False),
        ):
            bindings = dict(chart_ticker=ticker, chart_root=root, syminfo=SimpleNamespace(type=kind))
            with self.subTest(ticker=ticker):
                self.assertEqual(_value("is_nasdaq_chart", **bindings), nasdaq)
                self.assertEqual(_value("is_russell_chart", **bindings), russell)


class PineStructureWiringTests(unittest.TestCase):
    def test_confirmed_snapshot_keeps_all_fields_offset(self):
        arguments, fields = _request_tuple("confirmed_day_id_d")
        self.assertEqual(arguments[:2], ['"SP:SPX"', '"D"'])
        self.assertIn("lookahead=barmerge.lookahead_on", arguments)
        self.assertTrue(all(expression.endswith("[1]") for expression in fields.values()))
        self.assertEqual(fields["data_ready_confirmed_d"], "data_ready_confirmed_chart[1]")

    def test_daily_volume_and_readiness_travel_with_score(self):
        arguments, fields = _request_tuple("score_live")
        self.assertEqual(arguments[:2], ['"SP:SPX"', '"D"'])
        for output, expression in (("data_ready_live", "data_ready_live_chart"),
                                   ("vol_ratio_live", "vol_ratio_chart"),
                                   ("vol_spike_live", "is_vol_spike"),
                                   ("vol_high_live", "is_vol_high"),
                                   ("scaled_vol_live", "scaled_vol_chart")):
            with self.subTest(output=output):
                self.assertEqual(fields[output], expression)

    def test_volume_plot_and_panel_consume_the_selected_daily_feed(self):
        source = SOURCE.read_text()
        self.assertRegex(source, r"plot\(show_volume \? scaled_vol_daily : na, color=daily_vol_color,")
        self.assertRegex(source, r"(?m)^\s+vol_ratio = vol_ratio_daily$")
        self.assertIn("is_vol_spike_daily", _assignment("daily_vol_color"))
        self.assertIn("is_vol_high_daily", _assignment("daily_vol_color"))

    def test_intraday_strict_mode_selects_completed_score_and_volume(self):
        for enabled, intraday, expected in ((False, True, False), (True, True, True),
                                            (False, False, False), (True, False, False)):
            with self.subTest(enabled=enabled, intraday=intraday):
                self.assertEqual(_value("use_completed_chart_source", use_confirmed_signals=enabled,
                                        timeframe=SimpleNamespace(isintraday=intraday)), expected)
        for strict in (False, True):
            self.assertEqual(_value("score", use_completed_chart_source=strict,
                                    confirmed_score_d=4, score_live=-6), 4 if strict else -6)
            self.assertEqual(_value("vol_ratio_daily", use_completed_chart_source=strict,
                                    vol_ratio_confirmed_d=2.75, vol_ratio_live=1), 2.75 if strict else 1)

    def test_strict_trend_and_readiness_do_not_read_live_values(self):
        self.assertFalse(_value("data_ready", use_completed_chart_source=True,
                                data_ready_confirmed_d=False, data_ready_live=True))
        self.assertFalse(_value("signal_trend_ready", use_completed_chart_source=True,
                                confirmed_primary_ready_d=False, is_primary_trend_ready=True))
        self.assertFalse(_value("signal_trend_bull", use_completed_chart_source=True,
                                confirmed_primary_bull_d=False, is_primary_bull=True))
        self.assertEqual(_value("signal_vix", use_completed_chart_source=True,
                                confirmed_vix_d=20, vix=40), 20)

    def test_only_final_events_write_display_cooldown(self):
        source = SOURCE.read_text()
        for side in ("buy_dip", "sell_hedge"):
            assignments = re.findall(rf"(?m)^\s*last_{side}_bar := .+$", source)
            self.assertEqual(len(assignments), 1)
            self.assertRegex(source, rf"(?m)^if final_{side}\n    last_{side}_bar := bar_index$")

    def test_missing_prices_are_not_written_as_neutral_history(self):
        for name in ("term_spread", "contango_pct", "vix_basis", "raw_z"):
            with self.subTest(name=name):
                self.assertRegex(_assignment(name), r": na$")
        self.assertNotIn("bar_index", _assignment("has_sufficient_data"))
        self.assertIn("math.sum(valid_data ? 1 : 0,", _assignment("core_observations"))

    def test_no_new_security_sites_and_all_invalid_symbols_are_guarded(self):
        # This is a narrow source regression guard, NOT an expanded request
        # budget proof. TradingView must check nested unique calls at runtime.
        requests = [line for line in SOURCE.read_text().splitlines()
                    if not line.lstrip().startswith("//") and "request.security(" in line]
        self.assertLessEqual(len(requests), 15)
        self.assertTrue(all("ignore_invalid_symbol=true" in line for line in requests))


if __name__ == "__main__":
    unittest.main()
