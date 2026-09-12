"""Numerical contract tests for VIX's fixed-horizon statistics.

The Python model enumerates entry dates directly; it does not compile or execute
Pine. Narrow source checks connect the regression cases to Pine's eligibility,
price-validity, and rolling-window guards. TradingView validation is still needed.
"""

from dataclasses import dataclass
from pathlib import Path
import re
import unittest


PINE_PATH = Path(__file__).resolve().parents[1] / "vix.pine"


@dataclass(frozen=True)
class Stats:
    count: int
    wins: int
    average: float | None


def entry_date_reference(prices, signals, *, current, lookback, hold,
                         sell=False, current_closed=True, eligible=True):
    """Oracle: select signal dates first, then evaluate mature valid returns."""
    returns = []
    last_closed = current if current_closed else current - 1
    if eligible:
        for entry in signals:
            exit_bar = entry + hold
            if not current - lookback + 1 <= entry <= current:
                continue
            if exit_bar > last_closed:
                continue
            entry_price, exit_price = prices[entry], prices[exit_bar]
            if entry_price is None or exit_price is None:
                continue
            if entry_price <= 0 or exit_price <= 0:
                continue
            returns.append((exit_price / entry_price - 1) * 100)
    wins = sum(value <= 0 if sell else value > 0 for value in returns)
    return Stats(len(returns), wins, sum(returns) / len(returns) if returns else None)


class NumericalStatsContractTests(unittest.TestCase):
    def test_open_exit_is_not_a_completed_sample(self):
        prices = [100, 102, 105, 110]
        options = dict(current=3, lookback=4, hold=3)
        self.assertEqual(
            entry_date_reference(prices, [0], current_closed=False, **options),
            Stats(0, 0, None),
        )
        closed = entry_date_reference(prices, [0], **options)
        self.assertEqual((closed.count, closed.wins), (1, 1))
        self.assertAlmostEqual(closed.average, 10)

    def test_existing_completed_sample_survives_an_open_exit_day(self):
        # Entry 0 is mature; entry 1 has its exit on the still-open day 3.
        result = entry_date_reference(
            [100, 100, 110, 80], [0, 1], current=3,
            lookback=4, hold=2, current_closed=False,
        )
        self.assertEqual((result.count, result.wins), (1, 1))
        self.assertAlmostEqual(result.average, 10)

    def test_manual_source_inception_does_not_mix_in_spx(self):
        # A missing manual entry must not become an SPX 5,000 -> manual 50 return.
        result = entry_date_reference(
            [None, None, 50, 55], [0, 2], current=3,
            lookback=4, hold=1, sell=True,
        )
        self.assertEqual((result.count, result.wins), (1, 0))
        self.assertAlmostEqual(result.average, 10)
        crossed_inception = entry_date_reference(
            [None, None, 50, 55], [0], current=3,
            lookback=4, hold=2, sell=True,
        )
        self.assertEqual(crossed_inception, Stats(0, 0, None))

    def test_invalid_endpoints_are_neither_samples_nor_sell_wins(self):
        for endpoint in (None, 0, -1):
            for prices in ([endpoint, 100], [100, endpoint]):
                with self.subTest(prices=prices):
                    result = entry_date_reference(
                        prices, [0], current=1, lookback=2, hold=1, sell=True,
                    )
                    self.assertEqual(result, Stats(0, 0, None))

    def test_real_zero_return_remains_a_sell_win_only(self):
        args = dict(current=1, lookback=2, hold=1)
        self.assertEqual(entry_date_reference([100, 100], [0], **args), Stats(1, 0, 0))
        self.assertEqual(
            entry_date_reference([100, 100], [0], sell=True, **args),
            Stats(1, 1, 0),
        )

    def test_window_excludes_old_entries_even_when_exit_is_recent(self):
        # At day 7, L=6 includes entries 2..7. Entry 1 exits at day 4 but is old.
        prices = [100, 100, 100, 100, 200, 100, 120, 100, 100]
        result = entry_date_reference(
            prices, [1, 3, 5], current=7, lookback=6, hold=3,
        )
        self.assertEqual((result.count, result.wins), (1, 1))
        self.assertAlmostEqual(result.average, 20)

    def test_rolling_exit_windows_match_entry_date_boundaries(self):
        # Verify the L-H rolling length over minimum/default/maximum settings.
        for lookback, hold in ((252, 5), (756, 20), (252, 60), (4788, 60)):
            with self.subTest(lookback=lookback, hold=hold):
                current = 6000
                eligible_entries = set(range(current - lookback + 1, current - hold + 1))
                evaluation_window = range(current - (lookback - hold) + 1, current + 1)
                shifted_entries = {exit_bar - hold for exit_bar in evaluation_window}
                self.assertEqual(shifted_entries, eligible_entries)
                self.assertNotIn(current - lookback, shifted_entries)
                self.assertIn(current - lookback + 1, shifted_entries)

    def test_incompatible_calendar_excludes_apparent_winners(self):
        result = entry_date_reference(
            [100, 150], [0], current=1, lookback=2, hold=1, eligible=False,
        )
        self.assertEqual(result, Stats(0, 0, None))


class PineSourceStatsGuardTests(unittest.TestCase):
    """Guard high-risk wiring without asserting formatting or the whole source."""

    @classmethod
    def setUpClass(cls):
        cls.source = PINE_PATH.read_text()

    def assignment(self, name):
        match = re.search(rf"^{re.escape(name)}\s*=\s*(.+)$", self.source, re.MULTILINE)
        self.assertIsNotNone(match, f"Missing Pine assignment: {name}")
        return match.group(1)

    def test_manual_reference_has_no_per_bar_fallback(self):
        self.assertRegex(
            self.assignment("ref_close"),
            r"^auto_detect_index\s*\?\s*auto_ref_close\s*:\s*manual_close$",
        )

    def test_calendar_gate_preserves_us_equity_family(self):
        gate = self.assignment("is_stats_compatible_calendar")
        self.assertIn('syminfo.timezone == "America/New_York"', gate)
        for instrument_type in ("stock", "fund", "index"):
            self.assertIn(f'syminfo.type == "{instrument_type}"', gate)
        self.assertIn("is_stats_daily_chart", self.assignment("is_stats_eligible_chart"))
        self.assertIn("is_stats_compatible_calendar", self.assignment("is_stats_eligible_chart"))

    def test_all_evaluation_tiers_share_closed_validity_gates(self):
        self.assertIn("barstate.isconfirmed", self.assignment("stats_exit_confirmed"))
        self.assertIn("is_stats_eligible_chart", self.assignment("stats_exit_confirmed"))
        tier_holds = {
            "crash": "crash", "strong": "strong", "dip": "dip",
            "euphoria": "crash", "strong_sell": "strong", "sell_hedge": "dip",
        }
        for tier, hold in tier_holds.items():
            with self.subTest(tier=tier):
                evaluation = self.assignment(f"{tier}_eval_num")
                self.assertIn("stats_exit_confirmed", evaluation)
                self.assertIn(f"{hold}_return_valid", evaluation)
                self.assertIn(f"[{hold}_return_bars]", evaluation)
                for suffix in ("win_num", "return_contrib"):
                    self.assertIn(f"{tier}_eval_num == 1", self.assignment(f"{tier}_{suffix}"))

    def test_return_endpoints_require_positive_prices(self):
        for tier in ("crash", "strong", "dip"):
            validity = self.assignment(f"{tier}_return_valid")
            self.assertIn("not na(ref_close)", validity)
            self.assertIn("ref_close > 0", validity)
            self.assertIn(f"not na(ref_close[{tier}_return_bars])", validity)
            self.assertIn(f"ref_close[{tier}_return_bars] > 0", validity)
            self.assertRegex(self.assignment(f"{tier}_ref_return"), r":\s*na$")

    def test_each_rolling_aggregate_uses_its_signal_date_window(self):
        for tier in ("crash", "strong", "dip"):
            self.assertEqual(
                self.assignment(f"{tier}_stats_window"),
                f"stats_lookback_bars - {tier}_return_bars",
            )
        aggregation_tiers = {
            "crash_buy": "crash", "strong_buy": "strong", "buy_dip": "dip",
            "euphoria_sell": "crash", "strong_sell": "strong", "sell_hedge": "dip",
        }
        for prefix, tier in aggregation_tiers.items():
            for suffix in ("return_sum", "evaluated_count", "win_count"):
                expression = self.assignment(f"{prefix}_{suffix}")
                self.assertIn(f", {tier}_stats_window)", expression)

    def test_readiness_counts_executed_closed_bars(self):
        ready = self.assignment("stats_ready")
        self.assertNotIn("bar_index", ready)
        self.assertIn("is_stats_eligible_chart", ready)
        self.assertIn("stats_closed_bars >= stats_lookback_bars", ready)
        self.assertRegex(
            self.source,
            r"var int stats_closed_bars = 0\s+if barstate\.isconfirmed\s+stats_closed_bars \+= 1",
        )

    def test_empty_statistics_render_na(self):
        function = re.search(
            r"f_stats_cell\([^\n]+\) =>\s*([^\n]+)", self.source,
        )
        self.assertIsNotNone(function)
        self.assertIn("evaluated_count > 0", function.group(1))
        self.assertIn('"N/A"', function.group(1))


if __name__ == "__main__":
    unittest.main()
