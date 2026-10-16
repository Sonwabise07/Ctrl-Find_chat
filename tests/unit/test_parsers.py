from datetime import date

import pytest

from assistant.understanding.dates import add_months, parse_range
from assistant.understanding.ranking import parse_ranking
from assistant.understanding.references import find_asset_ref
from assistant.understanding.slots import SlotExtractor
from assistant.vocabulary import load_vocabulary

TODAY = date(2026, 10, 12)
VOCAB = load_vocabulary()


@pytest.mark.parametrize(
    ("question", "start", "end"),
    [
        ("last 90 days", date(2026, 7, 14), TODAY),
        ("in the last three months", date(2026, 7, 12), TODAY),
        ("over the past 2 weeks", date(2026, 9, 28), TODAY),
        ("last month", date(2026, 9, 1), date(2026, 9, 30)),
        ("this quarter", date(2026, 10, 1), TODAY),
        ("last quarter", date(2026, 7, 1), date(2026, 9, 30)),
        ("this year", date(2026, 1, 1), TODAY),
        ("year to date", date(2026, 1, 1), TODAY),
        ("last year", date(2025, 1, 1), date(2025, 12, 31)),
        ("between March and May", date(2026, 3, 1), date(2026, 5, 31)),
        ("from July 2025 to September 2025", date(2025, 7, 1), date(2025, 9, 30)),
        ("between November and February", date(2025, 11, 1), date(2026, 2, 28)),
        ("since July", date(2026, 7, 1), TODAY),
        ("in March 2025", date(2025, 3, 1), date(2025, 3, 31)),
        ("in October", date(2026, 10, 1), TODAY),
        ("in December", date(2025, 12, 1), date(2025, 12, 31)),
    ],
)
def test_reads_periods_from_a_question(question, start, end):
    found = parse_range(f"What did we buy {question}?", TODAY)
    assert (found.start, found.end) == (start, end)


def test_a_question_with_no_period_has_no_range():
    assert parse_range("How many laptops do we have?", TODAY) is None


def test_the_label_states_both_dates():
    assert parse_range("last month", TODAY).label == "between 01 Sep 2026 and 30 Sep 2026"


def test_adding_months_stays_inside_the_month():
    assert add_months(date(2026, 3, 31), -1) == date(2026, 2, 28)
    assert add_months(date(2026, 1, 15), -2) == date(2025, 11, 15)


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        (
            "Which location has the most laptops?",
            {"group_by": "location", "rank_order": "desc", "rank_metric": "count", "rank_limit": 5},
        ),
        (
            "Top 3 departments by asset value",
            {"group_by": "department", "rank_order": "desc", "rank_metric": "value", "rank_limit": 3},
        ),
        (
            "Which type has the fewest assets?",
            {"group_by": "type", "rank_order": "asc", "rank_metric": "count", "rank_limit": 5},
        ),
        (
            "bottom two statuses",
            {"group_by": "status", "rank_order": "asc", "rank_metric": "count", "rank_limit": 2},
        ),
        (
            "Which office is the most expensive?",
            {"group_by": "location", "rank_order": "desc", "rank_metric": "value", "rank_limit": 5},
        ),
    ],
)
def test_reads_a_ranking_request(question, expected):
    assert parse_ranking(question.lower(), VOCAB) == expected


@pytest.mark.parametrize(
    "question",
    [
        "which office has the most audit exceptions?",
        "show assets by status",
        "the most recent purchases",
        "top repairs",
    ],
)
def test_other_questions_are_not_rankings(question):
    assert parse_ranking(question, VOCAB) is None


@pytest.mark.parametrize(
    ("question", "ref"),
    [
        ("Tell me about AST-0013", "AST0013"),
        ("where is ast0013?", "AST0013"),
        ("show me EXT-100002", "EXT100002"),
        ("serial number ab12-cd34", "AB12CD34"),
        ("serial no. 7QK2M9XT4B please", "7QK2M9XT4B"),
        ("serial numbers are useful", None),
        ("Dell Latitude 5440", None),
        ("the P2423 monitor", None),
        ("Q4 2026", None),
    ],
)
def test_finds_an_asset_number_or_serial_only_when_there_is_one(question, ref):
    assert find_asset_ref(question) == ref


@pytest.mark.parametrize(
    ("question", "months"),
    [
        ("laptops older than 3 years", 36),
        ("monitors older than two years", 24),
        ("assets over 18 months old", 18),
        ("laptops that are 3 years old", None),
    ],
)
def test_reads_an_age_in_months(question, months):
    assert SlotExtractor._older_than(question) == months
