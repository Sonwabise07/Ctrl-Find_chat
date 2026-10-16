from ..dashboards.catalog import ChartTopic
from .formatting import is_are, plural
from .models import Answer, Chart

DASHBOARD_SOURCE = "Dashboards use the same data and the same access rules as the assistant."
FILTER_NOTE = " Filters named in your question are not applied to this chart."


def list_answer(dashboards: list[dict]) -> Answer:
    count = len(dashboards)
    text = f"**{plural(count, 'dashboard')}** {is_are(count)} available to you. Pick one to open it."
    return Answer(text, DASHBOARD_SOURCE)


def open_answer(dashboard: dict) -> Answer:
    return Answer(f"Here is the **{dashboard['title']}** dashboard.", DASHBOARD_SOURCE)


def chart_answer(widget: dict, topic: ChartTopic, filtered: bool) -> Answer:
    rows, title = widget["data"]["rows"], widget["title"]
    source = f"Based on {topic.source} as of today." + (FILTER_NOTE if filtered else "")
    if widget["type"] == "columns":
        peak = max(rows, key=lambda row: row["value"])
        text = f"Here is the trend for **{title}**."
        text += (
            f" The highest month is {peak['label']} at **{peak['text']}**."
            if peak["value"]
            else " Nothing is recorded in these months."
        )
        kind = "columns"
    else:
        text = f"**{rows[0]['label']}** is highest in {title.lower()} with **{rows[0]['text']}**."
        kind = "bars"
    chart_rows = [{"label": r["label"], "value": r["value"], "text": r["text"]} for r in rows]
    return Answer(text, source, chart=Chart(chart_rows, title, kind))
