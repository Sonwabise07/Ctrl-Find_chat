"""Turns the rows a widget's SQL returns into the JSON the screen draws."""

from ..answers.formatting import money, number
from .catalog import Widget

TREND_TONES = {"good": ("good", "bad"), "bad": ("bad", "good"), "neutral": ("neutral", "neutral")}


def plain(value):
    """JSON friendly number: whole numbers stay whole, decimals become floats."""
    return int(value) if value == int(value) else float(value)


def text(value, kind: str) -> str:
    return money(value) if kind == "money" else number(value)


def kpi(widget: Widget, rows: list[dict]) -> dict:
    row = rows[0]
    return {"value": plain(row["value"]), "text": text(row["value"], widget.format), "tag": row.get("tag")}


def bars(widget: Widget, rows: list[dict]) -> dict:
    total = sum(plain(row["value"]) for row in rows)
    return {
        "total": total,
        "rows": [
            {
                "label": row["label"],
                "value": plain(row["value"]),
                "text": text(row["value"], widget.format),
                "share": round(100 * plain(row["value"]) / total, 1) if total else 0.0,
            }
            for row in rows
        ],
    }


def columns(widget: Widget, rows: list[dict]) -> dict:
    return {
        "rows": [
            {"label": row["label"], "value": plain(row["value"]), "text": text(row["value"], widget.format)}
            for row in rows
        ]
    }


def table(widget: Widget, rows: list[dict]) -> dict:
    keys = [column.key for column in widget.columns]
    return {
        "columns": [{"key": column.key, "title": column.title} for column in widget.columns],
        "rows": [{key: str(row[key]) for key in keys} for row in rows],
    }


def alerts(widget: Widget, rows: list[dict]) -> dict:
    return {"rows": [{key: row[key] for key in ("title", "subtitle", "tone")} for row in rows]}


def keyvalue(widget: Widget, rows: list[dict]) -> dict:
    return {"rows": [{"label": row["label"], "text": text(row["value"], row["kind"])} for row in rows]}


def trends(widget: Widget, rows: list[dict]) -> dict:
    return {"rows": [_trend(row) for row in rows]}


def _trend(row: dict) -> dict:
    now, before = plain(row["value"]), plain(row["previous"])
    direction = "up" if now > before else "down" if now < before else "flat"
    if direction == "flat":
        change, tone = "no change", "neutral"
    else:
        change = "new this month" if before == 0 else f"{100 * (now - before) / before:+.0f}%"
        tone = TREND_TONES[row["up_is"]][0 if direction == "up" else 1]
    return {
        "label": row["label"],
        "text": text(now, row["kind"]),
        "previous_text": text(before, row["kind"]),
        "direction": direction,
        "change": change,
        "tone": tone,
    }


SHAPERS = {
    "kpi": kpi,
    "bars": bars,
    "columns": columns,
    "table": table,
    "list": alerts,
    "keyvalue": keyvalue,
    "trends": trends,
}


def shape(widget: Widget, rows: list[dict]) -> dict:
    return SHAPERS[widget.type](widget, rows)
