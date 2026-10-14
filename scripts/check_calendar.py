#!/usr/bin/env python3
"""Check a saved LiveOps Event Calendar Planner output.

Checks:
  1. The calendar table has a Type column and every event's type is one of
     the seven labels: tournament, sale, collection, mission, social,
     narrative, always-on.
  2. Cooldown: no event starts within 28 days after the end of the last
     event of the same type, counting the recent events you pass with
     --recent and earlier events in the calendar. Always-on is exempt.
     An event's end is its start plus its duration minus one day.
  3. With --expect-inferred: the output starts with an "Inferred event
     types" section whose table has Event, Type and End date columns and
     only on-list types. With --expect-assumed, at least one end date in
     that table is marked "(assumed ...)". With --expect-inferred-types
     (input gave no types), every type in it is marked "(inferred)".

Days are counted from the plan's first day (Week 1, Day 1 = day 0).
A launch cell is read as, in order of preference:
  - a calendar date ("Oct 15", "Nov 4", "2026-11-04"), if --start-date gives
    the date of Week 1, Day 1;
  - "Week N" / "Wk N" / "WN" plus "Day N" / "DN";
  - "Week N" plus a weekday name, counting weeks from Monday.
Durations are read as "N days", "N-day", "N weeks" or "N-week".

Usage:
    python3 scripts/check_calendar.py OUTPUT.md --recent tournament:-5
    python3 scripts/check_calendar.py OUTPUT.md --recent tournament:0 \\
        --expect-inferred --expect-assumed --start-date 2026-10-14

--recent TYPE:END_DAY gives a recent event's end, in days relative to
Week 1, Day 1 (negative = before the plan). Exits 0 if every check passes.
Standard library only.
"""

import argparse
import datetime as dt
import re
import sys

TYPES = {"tournament", "sale", "collection", "mission", "social", "narrative", "always-on"}
COOLDOWN_DAYS = 28
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def clean(cell):
    return re.sub(r"[*_`]", "", cell).strip()


def split_row(line):
    return [clean(c) for c in line.strip().strip("|").split("|")]


def is_separator(line):
    return set(line.replace("|", "").strip()) <= set("-: ")


def tables(text):
    """Yield (heading_before, header, rows) for each markdown table."""
    lines = text.splitlines()
    heading = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lstrip().startswith("#") or (line.strip().startswith("**") and line.strip().endswith("**")):
            heading = clean(line.lstrip("#"))
        if line.strip().startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            header = [h.lower() for h in split_row(line)]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            yield heading, header, rows, i
            i = j
            continue
        i += 1


def find_col(header, *needles, exclude=()):
    for k, h in enumerate(header):
        if any(n in h for n in needles) and not any(x in h for x in exclude):
            return k
    return None


def parse_date(cell, start):
    if start is None:
        return None
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", cell)
    if m:
        return (dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3))) - start).days
    m = re.search(r"\b(" + "|".join(MONTHS) + r")[a-z]*\.?\s+(\d{1,2})\b", cell, re.I)
    if m:
        month = MONTHS.index(m.group(1).lower()[:3]) + 1
        year = start.year + (1 if month < start.month - 6 else 0)
        return (dt.date(year, month, int(m.group(2))) - start).days
    return None


def parse_start(cell, start):
    d = parse_date(cell, start)
    if d is not None:
        return d
    week = re.search(r"\b(?:week|wk|w)\s*(\d+)", cell, re.I) or re.match(r"\s*(\d+)\b", cell)
    if not week:
        return None
    base = (int(week.group(1)) - 1) * 7
    day = re.search(r"\b(?:day|d)\s*(\d+)", cell[week.end():], re.I)
    if day:
        return base + int(day.group(1)) - 1
    for k, name in enumerate(WEEKDAYS):
        if re.search(r"\b" + name, cell, re.I):
            return base + k
    return base


def parse_duration(cell):
    m = re.search(r"(\d+)\s*-?\s*(day|week)", cell, re.I)
    if not m:
        return 1
    n = int(m.group(1))
    return n * 7 if m.group(2).lower() == "week" else n


def check(text, recent, start=None, expect_inferred=False, expect_assumed=False, expect_inferred_types=False):
    problems, events = [], []
    all_tables = list(tables(text))

    calendar = None
    for heading, header, rows, pos in all_tables:
        type_col = find_col(header, "type", exclude=("inferred",))
        when_col = find_col(header, "week", "wk", "launch", "day", "date", exclude=("end date", "duration"))
        if type_col is not None and when_col is not None and "end date" not in " ".join(header):
            calendar = (header, rows, type_col, when_col)
            break
    if calendar is None:
        return ["no calendar table with a Type column and a week/day column"], []

    header, rows, type_col, when_col = calendar
    event_col = find_col(header, "event")
    dur_col = find_col(header, "duration")
    day_col = find_col(header, "day", exclude=("week", "duration"))
    for row in rows:
        if len(row) <= type_col:
            continue
        label = row[type_col].strip().lower()
        if not label:
            continue  # recovery week or other blank row
        name = row[event_col] if event_col is not None and event_col < len(row) else "?"
        when = row[when_col]
        if day_col is not None and day_col != when_col and day_col < len(row):
            when = f"{when} {'Day ' + row[day_col] if row[day_col].isdigit() else row[day_col]}"
        start_day = parse_start(when, start)
        duration = parse_duration(row[dur_col]) if dur_col is not None and dur_col < len(row) else 1
        if label not in TYPES:
            problems.append(f"off-list type {label!r} on {name!r}")
        if start_day is None:
            problems.append(f"cannot read the launch day {when!r} for {name!r}")
            continue
        events.append({"name": name, "type": label, "start": start_day, "end": start_day + duration - 1})

    history = [(t, end, "recent event") for t, end in recent]
    for e in sorted(events, key=lambda e: e["start"]):
        if e["type"] == "always-on" or e["type"] not in TYPES:
            continue
        for t, end, source in history:
            if t == e["type"] and e["start"] - end < COOLDOWN_DAYS:
                problems.append(
                    f"cooldown: {e['name']!r} ({t}) starts day {e['start']}, "
                    f"{e['start'] - end} days after a {t} ({source}) ended on day {end}")
        history.append((e["type"], e["end"], e["name"]))

    if expect_inferred:
        first_text = next((l for l in text.splitlines() if l.strip()), "")
        if "inferred event types" not in first_text.lower():
            problems.append("output does not start with an 'Inferred event types' section")
        inferred = next(((h, r) for heading, h, r, _ in all_tables if "inferred event types" in heading.lower()), None)
        if inferred is None:
            problems.append("no table under 'Inferred event types'")
        else:
            h, r = inferred
            for col in ("event", "type", "end date"):
                if find_col(h, col) is None:
                    problems.append(f"inferred table has no {col!r} column")
            tcol = find_col(h, "type")
            for row in r:
                if tcol is not None and tcol < len(row):
                    label = re.sub(r"\(.*?\)", "", row[tcol]).strip().lower()
                    if label not in TYPES:
                        problems.append(f"inferred table: off-list type {row[tcol]!r}")
            if expect_assumed and not re.search(r"\(\s*assumed\b", " ".join(" ".join(row) for row in r), re.I):
                problems.append("inferred table marks no end date '(assumed)'")
            if expect_inferred_types and tcol is not None:
                for row in r:
                    if tcol < len(row) and not re.search(r"\(\s*inferred\b", row[tcol], re.I):
                        problems.append(f"inferred table: type {row[tcol]!r} for {row[0]!r} is not marked '(inferred)'")
    return problems, events


def parse_recent(items):
    out = []
    for item in items or []:
        t, day = item.split(":")
        out.append((t.strip().lower(), int(day)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("output", help="saved model output (markdown)")
    ap.add_argument("--recent", action="append", metavar="TYPE:END_DAY",
                    help="a recent event's type and end day relative to Week 1, Day 1; repeatable")
    ap.add_argument("--start-date", type=dt.date.fromisoformat,
                    help="calendar date of Week 1, Day 1 (YYYY-MM-DD), to read dates in launch cells")
    ap.add_argument("--expect-inferred", action="store_true",
                    help="require an 'Inferred event types' table at the start of the output")
    ap.add_argument("--expect-assumed", action="store_true",
                    help="require at least one end date marked '(assumed)' in that table")
    ap.add_argument("--expect-inferred-types", action="store_true",
                    help="require every type in that table to be marked '(inferred)' (input had no types)")
    args = ap.parse_args(argv)

    text = open(args.output, encoding="utf-8").read()
    problems, events = check(text, parse_recent(args.recent), args.start_date, args.expect_inferred,
                             args.expect_assumed, args.expect_inferred_types)
    print(f"{args.output}: {len(events)} event(s)")
    for e in events:
        print(f"  {e['name'][:40]:40s} {e['type']:11s} days {e['start']} to {e['end']}")
    for p in problems:
        print(f"  FAIL {p}")
    print("RESULT:", "FAIL" if problems else "PASS")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
