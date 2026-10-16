from dataclasses import dataclass
from datetime import date, timedelta

DISPLAY_DATE = "%d %b %Y"
DEFAULT_WINDOW_DAYS = 30


@dataclass(frozen=True)
class Period:
    label: str
    start: date
    end: date  # exclusive


@dataclass(frozen=True)
class Window:
    """Warranty end-date range. `start` is None for assets whose warranty already ended."""

    start: date | None
    end: date
    text: str
    expired: bool = False


def first_of_month(day: date, offset: int = 0) -> date:
    year, month = divmod(day.year * 12 + day.month - 1 + offset, 12)
    return date(year, month + 1, 1)


def comparison_periods(kind: str, today: date) -> tuple[Period, Period]:
    """The previous and the current month or quarter, oldest first."""
    if kind == "quarter":
        current = date(today.year, 3 * ((today.month - 1) // 3) + 1, 1)
        previous, following = first_of_month(current, -3), first_of_month(current, 3)
        return (
            Period(_quarter_label(previous), previous, current),
            Period(_quarter_label(current), current, following),
        )
    current = first_of_month(today)
    previous, following = first_of_month(today, -1), first_of_month(today, 1)
    return (
        Period(previous.strftime("%b %Y"), previous, current),
        Period(current.strftime("%b %Y"), current, following),
    )


def warranty_window(name: str, today: date) -> Window:
    if name == "expired":
        text = f"already out of warranty (ended before {today.strftime(DISPLAY_DATE)})"
        return Window(None, today - timedelta(days=1), text, expired=True)
    if name == "this_month":
        start, end = today, first_of_month(today, 1) - timedelta(days=1)
    elif name == "next_month":
        start, end = first_of_month(today, 1), first_of_month(today, 2) - timedelta(days=1)
    else:
        days = int(name.removeprefix("days:")) if name.startswith("days:") else DEFAULT_WINDOW_DAYS
        start, end = today, today + timedelta(days=days)
    text = f"warranty ending between {start.strftime(DISPLAY_DATE)} and {end.strftime(DISPLAY_DATE)}"
    return Window(start, end, text)


def _quarter_label(first_day: date) -> str:
    return f"Q{(first_day.month - 1) // 3 + 1} {first_day.year}"
