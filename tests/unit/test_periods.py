from datetime import date

from assistant.queries.periods import comparison_periods, first_of_month, warranty_window


def test_first_of_month_moves_across_years():
    assert first_of_month(date(2026, 1, 15), -1) == date(2025, 12, 1)
    assert first_of_month(date(2026, 12, 15), 1) == date(2027, 1, 1)


def test_month_comparison_runs_oldest_first():
    earlier, later = comparison_periods("month", date(2026, 10, 7))
    assert (earlier.label, later.label) == ("Sep 2026", "Oct 2026")
    assert earlier.end == later.start == date(2026, 10, 1)


def test_quarter_comparison():
    earlier, later = comparison_periods("quarter", date(2026, 10, 7))
    assert (earlier.label, later.label) == ("Q3 2026", "Q4 2026")
    assert later.end == date(2027, 1, 1)


def test_next_month_window():
    window = warranty_window("next_month", date(2026, 10, 7))
    assert (window.start, window.end) == (date(2026, 11, 1), date(2026, 11, 30))


def test_expired_window_has_no_start():
    window = warranty_window("expired", date(2026, 10, 7))
    assert window.start is None and window.end == date(2026, 10, 6) and window.expired
