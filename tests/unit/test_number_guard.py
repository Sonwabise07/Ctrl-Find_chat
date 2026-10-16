from decimal import Decimal

from assistant.answers.number_guard import unexplained_numbers


def test_flags_a_figure_that_is_not_in_the_data():
    assert unexplained_numbers("**99 assets** exist.", [{"value": 5}], "question") == ["99"]


def test_accepts_figures_from_rows_amounts_and_the_question():
    rows = [{"label": "Q3 2026", "value": Decimal("11600.00"), "items": 4}]
    answer = "**Q3 2026**: R11\u202f600 across 4 records, last 30 days."
    assert unexplained_numbers(answer, rows, "last 30 days") == []


def test_checks_decimal_amounts():
    assert unexplained_numbers("**R1\u202f234.50** open.", [{"value": Decimal("1234.50")}]) == []
