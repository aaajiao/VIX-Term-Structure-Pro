"""Regression scenarios for alert dispatch; these do not compile or execute Pine.

The small state model exercises send/observe bookkeeping with synthetic events.
Source wiring checks keep the Pine dispatch guards connected to that contract.
TradingView is still required to validate realtime ticks and session alignment.
"""

from dataclasses import dataclass, field
from pathlib import Path
import re
import unittest


@dataclass
class AlertDispatch:
    once_per_bar: bool = True
    bar: int = 100
    day: int = 20260910
    dispatched_this_bar: bool = False
    last_sent: dict = field(default_factory=lambda: {"buy": 0, "sell": 0})
    day_latch: dict = field(default_factory=lambda: {"buy": 0, "sell": 0})
    observed: dict = field(default_factory=lambda: {"buy": 0, "sell": 0})
    confirmed_day_sent: dict = field(default_factory=lambda: {"buy": 0, "sell": 0})

    def next_bar(self, bar, day=None):
        self.bar = bar
        self.dispatched_this_bar = False
        self.observed = {"buy": 0, "sell": 0}
        if day is not None and day != self.day:
            self.day = day
            self.day_latch = {"buy": 0, "sell": 0}

    def preview(self, side, level, *, edge=True, allowed=True, extended=False, cooldown=5):
        # edge comes from the signal layer; a discarded event is never queued.
        new_event = edge and level > self.observed[side]
        upgrade = level > self.day_latch[side]
        eligible = allowed and new_event and upgrade and self.bar - self.last_sent[side] > cooldown
        dispatched = eligible and (not self.once_per_bar or not self.dispatched_this_bar)
        if dispatched:
            self.dispatched_this_bar = True
            self.last_sent[side] = self.bar
            self.day_latch[side] = level
        if extended and new_event and upgrade:
            self.day_latch[side] = level
        if new_event:
            self.observed[side] = level
        return dispatched

    def confirmed(self, side, structure_day, *, intraday=True, regular=True, bar_closed=False):
        timing_ok = regular if intraday else bar_closed
        eligible = timing_ok and structure_day != self.confirmed_day_sent[side]
        dispatched = eligible and (not self.once_per_bar or not self.dispatched_this_bar)
        if dispatched:
            self.dispatched_this_bar = True
            self.confirmed_day_sent[side] = structure_day
        return dispatched


class AlertTransitionTests(unittest.TestCase):
    def test_once_per_bar_opposite_side_does_not_claim_a_send(self):
        state = AlertDispatch()
        self.assertTrue(state.preview("buy", 2))
        self.assertFalse(state.preview("sell", 3))
        self.assertEqual(state.last_sent["sell"], 0)
        self.assertEqual(state.day_latch["sell"], 0)
        self.assertEqual(state.observed["sell"], 3)
        # Repeated ticks cannot retry the discarded sell event.
        self.assertFalse(state.preview("sell", 3))
        state.next_bar(101)
        self.assertFalse(state.preview("sell", 3, edge=False))
        # A genuinely new crossing is still eligible: the lost call did not send.
        state.next_bar(102)
        self.assertTrue(state.preview("sell", 3))

    def test_realtime_allows_opposite_sides_in_one_bar(self):
        state = AlertDispatch(once_per_bar=False)
        self.assertTrue(state.preview("buy", 2))
        self.assertTrue(state.preview("sell", 3))
        self.assertEqual(state.last_sent, {"buy": 100, "sell": 100})

    def test_once_per_bar_quota_resets_without_resetting_day_latch(self):
        state = AlertDispatch()
        self.assertTrue(state.preview("buy", 1))
        state.next_bar(106)
        self.assertFalse(state.preview("buy", 1))
        self.assertTrue(state.preview("sell", 2))

    def test_cooldown_blocked_upgrade_is_observed_and_never_queued(self):
        state = AlertDispatch(once_per_bar=False)
        self.assertTrue(state.preview("buy", 1))
        state.next_bar(102)
        self.assertFalse(state.preview("buy", 2))
        self.assertEqual(state.last_sent["buy"], 100)
        self.assertEqual(state.day_latch["buy"], 1)
        self.assertEqual(state.observed["buy"], 2)
        state.next_bar(106)
        self.assertFalse(state.preview("buy", 2, edge=False))
        state.next_bar(107)
        self.assertTrue(state.preview("buy", 3))

    def test_cooldown_boundary_remains_strict(self):
        state = AlertDispatch()
        self.assertTrue(state.preview("buy", 1))
        state.next_bar(105)
        self.assertFalse(state.preview("buy", 2))
        state.next_bar(106)
        self.assertTrue(state.preview("buy", 3))

    def test_extended_session_discard_still_consumes_day_latch(self):
        state = AlertDispatch()
        self.assertFalse(state.preview("buy", 2, allowed=False, extended=True))
        self.assertEqual(state.last_sent["buy"], 0)
        self.assertEqual(state.day_latch["buy"], 2)
        state.next_bar(120)
        self.assertFalse(state.preview("buy", 2))
        self.assertTrue(state.preview("buy", 3))

    def test_confirmed_emits_on_first_regular_bar_after_premarket(self):
        state = AlertDispatch(day=20260911)
        # The chart day changed during premarket, before the new SPX snapshot.
        self.assertFalse(state.confirmed("buy", 20260910, regular=False))
        state.next_bar(111)
        self.assertTrue(state.confirmed("buy", 20260910, regular=True))
        self.assertFalse(state.confirmed("buy", 20260910, regular=True))
        state.next_bar(112)
        self.assertFalse(state.confirmed("buy", 20260910, regular=True))

    def test_confirmed_regular_only_chart_uses_same_first_bar(self):
        state = AlertDispatch(day=20260910)
        state.next_bar(111, day=20260911)
        self.assertTrue(state.confirmed("buy", 20260910))

    def test_daily_confirmed_still_waits_for_close(self):
        state = AlertDispatch()
        self.assertFalse(state.confirmed("sell", 20260910, intraday=False))
        self.assertTrue(state.confirmed("sell", 20260910, intraday=False, bar_closed=True))
        self.assertFalse(state.confirmed("sell", 20260910, intraday=False, bar_closed=True))


class PineAlertWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (Path(__file__).resolve().parents[1] / "vix.pine").read_text()
        cls.alerts = cls.source.split("// ========== 10. SMART ALERT", 1)[1]

    def test_confirmed_timing_has_no_chart_date_delay(self):
        self.assertIn(
            "confirmed_emit_now = timeframe.isintraday ? regular_session_bar : barstate.isconfirmed",
            self.source,
        )

    def test_transport_is_unthrottled_inside_explicit_guards(self):
        calls = re.findall(r"\balert\(msg,\s*([^)]*)\)", self.alerts)
        self.assertEqual(calls, ["alert.freq_all", "alert.freq_all"])
        for side in ("buy", "sell"):
            self.assertIn(
                f'if should_emit_{side} and (alert_freq_mode == "Real-time" or not alert_dispatched_this_bar)',
                self.alerts,
            )
        self.assertEqual(self.alerts.count("alert_dispatched_this_bar := true"), 2)

    def test_dispatch_quota_is_rollback_safe_and_reset_per_bar(self):
        self.assertIn("varip bool alert_dispatched_this_bar = false", self.alerts)
        bar_reset = self.alerts.split("if barstate.isnew", 1)[1].split("if has_new_chart_day", 1)[0]
        self.assertIn("alert_dispatched_this_bar := false", bar_reset)

    def test_rejected_preview_events_keep_observation_bookkeeping(self):
        for side in ("buy", "sell"):
            self.assertIn(f"if is_new_{side}\n        {side}_alert_level_sent :=", self.alerts)
            self.assertIn(f"if should_latch_extended_{side}\n        {side}_day_latch_level :=", self.alerts)


if __name__ == "__main__":
    unittest.main()
