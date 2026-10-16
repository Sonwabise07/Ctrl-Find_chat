import re
from dataclasses import dataclass
from datetime import date, timedelta

from ..queries.periods import first_of_month

MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]  # fmt: skip
MONTH_NUMBER = {name[:3]: number for number, name in enumerate(MONTHS, start=1)}
NUMBER_WORDS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}  # fmt: skip

_MONTH = "(" + "|".join(sorted([*MONTHS, *(m[:3] for m in MONTHS), "sept"], key=len, reverse=True)) + ")"
_YEAR = r"(?:\s+(\d{4}))?"
COUNT = r"(\d+|" + "|".join(NUMBER_WORDS) + ")"

LAST_N = re.compile(rf"\b(?:last|past|previous)\s+{COUNT}\s+(day|week|month|year)s?\b")
BETWEEN = re.compile(rf"\b(?:between|from)\s+{_MONTH}{_YEAR}\s+(?:and|to|until|till)\s+{_MONTH}{_YEAR}\b")
SINCE = re.compile(rf"\bsince\s+{_MONTH}{_YEAR}\b")
IN_MONTH = re.compile(rf"\b(?:in|during|for|of)\s+{_MONTH}{_YEAR}\b")


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date  # inclusive

    @property
    def label(self) -> str:
        return f"between {self.start:%d %b %Y} and {self.end:%d %b %Y}"


def parse_range(text: str, today: date) -> DateRange | None:
    """Reads a period such as 'last 90 days', 'last month' or 'between March and May' from a question."""
    lowered = text.lower()
    for parser in (_last_n, _named, _between, _since, _in_month):
        found = parser(lowered, today)
        if found:
            end = min(found.end, today)
            return DateRange(found.start, end) if found.start <= end else None
    return None


def count_value(raw: str) -> int:
    """Reads '90' or a number word such as 'three' or 'a'."""
    return int(raw) if raw.isdigit() else NUMBER_WORDS[raw]


def add_months(day: date, months: int) -> date:
    first = first_of_month(day, months)
    last_day = first_of_month(first, 1) - timedelta(days=1)
    return first.replace(day=min(day.day, last_day.day))


def _last_n(text, today):
    if not (match := LAST_N.search(text)):
        return None
    count = count_value(match.group(1))
    unit = match.group(2)
    if unit == "day":
        start = today - timedelta(days=count)
    elif unit == "week":
        start = today - timedelta(weeks=count)
    else:
        start = add_months(today, -count * (12 if unit == "year" else 1))
    return DateRange(start, today)


def _named(text, today):
    quarter_start = date(today.year, 3 * ((today.month - 1) // 3) + 1, 1)
    named = {
        "this month": DateRange(first_of_month(today), today),
        "last month": DateRange(first_of_month(today, -1), first_of_month(today) - timedelta(days=1)),
        "this quarter": DateRange(quarter_start, today),
        "last quarter": DateRange(first_of_month(quarter_start, -3), quarter_start - timedelta(days=1)),
        "this year": DateRange(date(today.year, 1, 1), today),
        "year to date": DateRange(date(today.year, 1, 1), today),
        "ytd": DateRange(date(today.year, 1, 1), today),
        "last year": DateRange(date(today.year - 1, 1, 1), date(today.year - 1, 12, 31)),
    }
    return next((rng for phrase, rng in named.items() if re.search(rf"\b{phrase}\b", text)), None)


def _between(text, today):
    if not (match := BETWEEN.search(text)):
        return None
    first, first_year, second, second_year = match.groups()
    start = _month_start(first, first_year, today)
    second_number = MONTH_NUMBER[second[:3]]
    year = int(second_year) if second_year else start.year + (second_number < start.month)
    return DateRange(start, first_of_month(date(year, second_number, 1), 1) - timedelta(days=1))


def _since(text, today):
    match = SINCE.search(text)
    return DateRange(_month_start(match.group(1), match.group(2), today), today) if match else None


def _in_month(text, today):
    if not (match := IN_MONTH.search(text)):
        return None
    start = _month_start(match.group(1), match.group(2), today)
    return DateRange(start, first_of_month(start, 1) - timedelta(days=1))


def _month_start(name: str, year: str | None, today: date) -> date:
    """A month named without a year means its most recent occurrence."""
    number = MONTH_NUMBER[name[:3]]
    return date(int(year) if year else today.year - (number > today.month), number, 1)
