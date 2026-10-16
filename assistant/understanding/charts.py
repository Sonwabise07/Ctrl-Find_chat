from dataclasses import dataclass

from ..dashboards.catalog import ChartTopic
from ..filters import FILTER_SLOTS

BREAKDOWN_FROM = {"count_assets", "list_assets", "breakdown_assets"}
CARRIED_SLOTS = (*FILTER_SLOTS, "group_by")


@dataclass(frozen=True)
class Resolution:
    intent: str  # "show_chart" for a dashboard widget, "breakdown_assets" for a split of the register
    slots: dict
    topic: ChartTopic | None = None
    filtered: bool = False  # the question named filters that the chosen chart cannot apply


class ChartResolver:
    """Decides what a request such as 'show this as a chart' should draw."""

    def __init__(self, topics: tuple[ChartTopic, ...]):
        self.topics = topics

    @property
    def ids(self) -> list[str]:
        return [topic.id for topic in self.topics]

    def resolve(self, text: str, slots: dict, context: dict | None) -> Resolution | None:
        previous = (context or {}).get("intent")
        filters = [key for key in FILTER_SLOTS if key in slots]
        if topic := self._named_topic(text, slots.get("chart")):
            return Resolution("show_chart", {"chart": topic.id}, topic, filtered=bool(filters))
        if filters or "group_by" in slots or previous in BREAKDOWN_FROM:
            return Resolution("breakdown_assets", self._split_slots(slots, context, previous))
        topic = next((t for t in self.topics if previous in t.after), None)
        return Resolution("show_chart", {"chart": topic.id}, topic) if topic else None

    def _named_topic(self, text: str, chosen: str | None) -> ChartTopic | None:
        by_id = next((t for t in self.topics if t.id == chosen), None)
        return by_id or next((t for t in self.topics if t.pattern.search(text)), None)

    @staticmethod
    def _split_slots(slots: dict, context: dict | None, previous: str | None) -> dict:
        earlier = (context or {}).get("slots") or {} if previous in BREAKDOWN_FROM else {}
        merged = {k: v for k, v in earlier.items() if k in CARRIED_SLOTS}
        merged.update({k: v for k, v in slots.items() if k in CARRIED_SLOTS})
        merged.setdefault("group_by", _split_by(merged))
        return merged


def _split_by(filters: dict) -> str:
    """Picks a dimension to split by that the filters have not already fixed."""
    if "asset_type" in filters and "status" in filters:
        return "location"
    if "asset_type" in filters or "make" in filters:
        return "status"
    if any(key in filters for key in ("status", "location", "department")):
        return "type"
    return "status"
