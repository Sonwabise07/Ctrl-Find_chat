import json
import re
from dataclasses import dataclass
from pathlib import Path

from ..catalog import CONFIG_DIR

WIDGET_TYPES = {"kpi", "bars", "columns", "table", "list", "trends", "keyvalue"}


@dataclass(frozen=True)
class Column:
    key: str
    title: str


@dataclass(frozen=True)
class Widget:
    id: str
    type: str
    title: str
    sql: str
    size: str = "medium"
    format: str = "number"
    tone: str = "info"
    requires: tuple[str, ...] = ()
    columns: tuple[Column, ...] = ()


@dataclass(frozen=True)
class Dashboard:
    id: str
    title: str
    widgets: tuple[Widget, ...]

    @property
    def required_tables(self) -> set[str]:
        return {table for widget in self.widgets for table in widget.requires}


def load_dashboards(path: Path = CONFIG_DIR / "dashboards.json") -> dict[str, Dashboard]:
    dashboards = {}
    for raw in json.loads(path.read_text(encoding="utf-8"))["dashboards"]:
        widgets = tuple(_widget(item) for item in raw["widgets"])
        dashboards[raw["id"]] = Dashboard(raw["id"], raw["title"], widgets)
    return dashboards


def _widget(item: dict) -> Widget:
    if item["type"] not in WIDGET_TYPES:
        raise ValueError(f"Unknown widget type {item['type']!r} in widget {item['id']!r}")
    columns = tuple(Column(**column) for column in item.get("columns", ()))
    fields = {key: value for key, value in item.items() if key not in ("columns", "requires")}
    return Widget(**fields, requires=tuple(item.get("requires", ())), columns=columns)


@dataclass(frozen=True)
class ChartTopic:
    """A widget that can be drawn in the chat when someone asks for a chart."""

    id: str  # "<dashboard id>.<widget id>"
    pattern: re.Pattern
    after: tuple[str, ...]  # question types whose answer this chart follows up
    source: str

    @property
    def dashboard_id(self) -> str:
        return self.id.split(".")[0]

    @property
    def widget_id(self) -> str:
        return self.id.split(".")[1]


def load_chart_topics(path: Path = CONFIG_DIR / "dashboards.json") -> tuple[ChartTopic, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))["chart_topics"]
    return tuple(
        ChartTopic(t["id"], re.compile(t["words"], re.IGNORECASE), tuple(t["after"]), t["source"])
        for t in raw
    )
