"""Tests for scripts/check_calendar.py. Run: python3 -m unittest discover tests"""

import datetime as dt
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import check_calendar as cc  # noqa: E402


def check(text, recent=(), **kw):
    return cc.check(text, list(recent), **kw)


GOOD = """### Calendar

| Week | Day | Event | Type | Duration |
|---|---|---|---|---|
| 1 | Mon | Master Album | collection | 7 days |
| 2 |  | (recovery week) |  |  |
| 3 | Wed | Comeback Chapter | narrative | 4 days |
| 4 | Mon | Squad Push | social | 7 days |
"""


class TestParsing(unittest.TestCase):
    def test_separate_week_and_day_columns(self):
        problems, events = check(GOOD)
        self.assertEqual(problems, [])
        self.assertEqual([(e["type"], e["start"], e["end"]) for e in events],
                         [("collection", 0, 6), ("narrative", 16, 19), ("social", 21, 27)])

    def test_combined_week_day_headers(self):
        for header, cell in [("Week / Launch Day", "Week 3, Day 2"), ("Week/Day", "Wk3, Day2"),
                             ("Week / Day", "W3 D2"), ("Week / Launch", "Week 3, Tue")]:
            text = f"| {header} | Event | Type | Duration |\n|---|---|---|---|\n| {cell} | X | sale | 2 weeks |\n"
            problems, events = check(text)
            self.assertEqual(problems, [], header)
            self.assertEqual((events[0]["start"], events[0]["end"]), (15, 28), header)

    def test_dates_with_start_date(self):
        text = "| Week / Launch Day | Event | Type | Duration |\n|---|---|---|---|\n| Week 4, Wed Nov 4 | X | tournament | 5 days |\n"
        _, events = check(text, start=dt.date(2026, 10, 14))
        self.assertEqual((events[0]["start"], events[0]["end"]), (21, 25))

    def test_no_calendar_table(self):
        problems, _ = check("No table here.")
        self.assertTrue(problems)


class TestRules(unittest.TestCase):
    def test_off_list_type_fails(self):
        problems, _ = check(GOOD.replace("| narrative |", "| collection + mission |"))
        self.assertTrue(any("off-list" in p for p in problems))

    def test_cooldown_from_recent_event_end(self):
        tournament_week4 = GOOD.replace("| 4 | Mon | Squad Push | social |", "| 4 | Mon | Cup | tournament |")
        # Day 21 start: blocked if the last tournament ended on day -6 (27 days), allowed at day -7 (28 days).
        self.assertTrue(check(tournament_week4, [("tournament", -6)])[0])
        self.assertEqual(check(tournament_week4, [("tournament", -7)])[0], [])

    def test_cooldown_counts_from_end_within_calendar(self):
        text = ("| Week | Day | Event | Type | Duration |\n|---|---|---|---|---|\n"
                "| 1 | Mon | A | mission | 14 days |\n| 4 | Mon | B | mission | 7 days |\n")
        problems, _ = check(text)  # A ends day 13, B starts day 21: 8 days later
        self.assertTrue(any("cooldown" in p for p in problems))

    def test_always_on_is_exempt(self):
        text = ("| Week | Day | Event | Type | Duration |\n|---|---|---|---|---|\n"
                "| 1 | Mon | Streak | always-on | 28 days |\n| 2 | Mon | Pass | always-on | 21 days |\n")
        self.assertEqual(check(text, [("always-on", 0)])[0], [])


INFERRED = """## Inferred event types

| Event | Type | End date | Why |
|---|---|---|---|
| Weekend tournament | tournament (inferred) | Week 1, Day 1 (assumed) | No end date or duration given |
| Daily login streak | always-on (inferred) | ongoing | Runs continuously |

""" + GOOD


class TestInferredTable(unittest.TestCase):
    def test_inferred_table_passes(self):
        self.assertEqual(check(INFERRED, [("tournament", 0)], expect_inferred=True, expect_assumed=True)[0], [])

    def test_inferred_table_must_come_first(self):
        moved = GOOD + "\n" + INFERRED.split(GOOD)[0]
        self.assertTrue(check(moved, expect_inferred=True)[0])

    def test_assumed_marker_may_carry_detail(self):
        detail = INFERRED.replace("(assumed)", "(assumed: plan start)")
        self.assertEqual(check(detail, [("tournament", 0)], expect_inferred=True, expect_assumed=True)[0], [])

    def test_untyped_input_needs_every_type_marked_inferred(self):
        self.assertEqual(check(INFERRED, expect_inferred=True, expect_inferred_types=True)[0], [])
        unmarked = INFERRED.replace("tournament (inferred)", "tournament")
        self.assertTrue(check(unmarked, expect_inferred=True, expect_inferred_types=True)[0])

    def test_inferred_table_needs_end_date_and_assumed_marker(self):
        no_end = INFERRED.replace("| Event | Type | End date | Why |", "| Event | Type | When | Why |")
        self.assertTrue(check(no_end, expect_inferred=True)[0])
        no_mark = INFERRED.replace("(assumed)", "")
        self.assertTrue(check(no_mark, expect_inferred=True, expect_assumed=True)[0])


class TestCommandLine(unittest.TestCase):
    def test_worked_example_passes(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_calendar.py"),
                            os.path.join(ROOT, "examples", "sample-input-output.md"), "--recent", "tournament:-5"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_exit_code_on_failure(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(GOOD.replace("| narrative |", "| live event |"))
        try:
            r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_calendar.py"), f.name],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
