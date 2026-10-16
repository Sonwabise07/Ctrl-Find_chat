import re
from datetime import date

from ..data.lookups import Lookups
from ..vocabulary import Vocabulary
from .dates import COUNT, count_value, parse_range
from .ranking import parse_ranking
from .references import find_asset_ref

NEXT_DAYS = re.compile(r"next (\d{1,3}) days")
MAX_WINDOW_DAYS = 365
OLDER_THAN = re.compile(
    rf"\bolder than\s+{COUNT}\s+(year|month)s?\b"
    rf"|\b(?:over|more than|at least)\s+{COUNT}\s+(year|month)s?\s+old\b"
)


class SlotExtractor:
    """Finds filter values in a question by matching it against values that exist in the database."""

    def __init__(self, vocab: Vocabulary, dashboards: dict[str, str] | None = None):
        self.vocab = vocab
        self.dashboards = dashboards or {}  # id -> title

    def extract(self, text: str, lookups: Lookups, today: date | None = None) -> dict:
        lowered = text.lower()
        found = {
            "asset_type": self._asset_type(lowered, lookups),
            "status": self._status(lowered, lookups),
            "location": self._location(lowered, lookups),
            "department": self._department(text, lowered, lookups),
            "make": self._make(lowered, lookups),
            "person": self._person(lowered, lookups),
            "window": self._window(lowered),
            "group_by": self._group_by(lowered),
            "dashboard": self._dashboard(lowered),
        }
        slots = {key: value for key, value in found.items() if value is not None}
        slots["period"] = "quarter" if "quarter" in lowered else "month"
        slots.update(parse_ranking(lowered, self.vocab) or {})
        if ref := find_asset_ref(text):
            slots["asset_ref"] = ref
        if span := parse_range(lowered, today or date.today()):
            slots.update(
                date_from=span.start.isoformat(), date_to=span.end.isoformat(), date_label=span.label
            )
        if months := self._older_than(lowered):
            slots["older_than"] = months
        return slots

    def _asset_type(self, text, lookups):
        for name, pattern in self.vocab.type_patterns.items():
            if name in lookups.asset_types and pattern.search(text):
                return name

    def _status(self, text, lookups):
        for name, pattern in self.vocab.status_patterns.items():
            if name in lookups.statuses and pattern.search(text):
                return name

    @staticmethod
    def _location(text, lookups):
        for name in lookups.locations:
            first_word = name.split()[0].lower()
            if name.lower() in text or (
                len(first_word) > 4 and re.search(rf"\b{re.escape(first_word)}\b", text)
            ):
                return name

    @staticmethod
    def _department(original, lowered, lookups):
        for name in lookups.departments:
            if name.isupper():  # short codes such as IT are matched case-sensitively
                if len(name) <= 3 and re.search(rf"\b{re.escape(name)}\b", original):
                    return name
            elif re.search(rf"\b{re.escape(name.lower())}\b", lowered):
                return name

    def _make(self, text, lookups):
        found = None
        for make in lookups.makes:
            key = make.lower()
            if key in self.vocab.makes and re.search(rf"\b{re.escape(key)}s?\b", text):
                found = make
                break
        if "macbook" in text:
            found = next((m for m in lookups.makes if m.lower() == "macbook"), found)
        return found

    @staticmethod
    def _person(text, lookups):
        for person in lookups.people:
            if person.full_name.lower() in text:
                return person.id
        matches = [p for p in lookups.people if re.search(rf"\b{re.escape(p.first_name.lower())}\b", text)]
        return matches[0].id if len(matches) == 1 else None

    def _window(self, text):
        if match := NEXT_DAYS.search(text):
            return f"days:{min(int(match.group(1)), MAX_WINDOW_DAYS)}"
        for pattern, value in self.vocab.warranty_windows:
            if pattern.search(text):
                return value

    @staticmethod
    def _older_than(text):
        """An age in months, from 'older than 3 years' or 'over 18 months old'."""
        match = OLDER_THAN.search(text)
        if not match:
            return None
        raw, unit = (match.group(1), match.group(2)) if match.group(1) else (match.group(3), match.group(4))
        return count_value(raw) * (12 if unit == "year" else 1)

    def _dashboard(self, text):
        if "dashboard" not in text:
            return None
        return next((key for key, title in self.dashboards.items() if title.lower() in text), None)

    def _group_by(self, text):
        for pattern, value in self.vocab.group_by:
            if pattern.search(text):
                return value
