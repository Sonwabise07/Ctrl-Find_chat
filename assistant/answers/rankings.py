from .formatting import age_phrase, asset_noun, has_have, location_suffix, money
from .models import Answer, Chart, Facts

MOST_NOUN = {
    "count": ("the most", "the fewest"),
    "value": ("the highest purchase value", "the lowest purchase value"),
}


def ranking(facts: Facts) -> Answer:
    if not facts.rows:
        return Answer("No assets match that filter.", facts.source)
    slots, rows = facts.slots, facts.rows
    is_value = slots.get("rank_metric") == "value"
    descending = slots.get("rank_order", "desc") == "desc"
    show = money if is_value else (lambda value: str(int(value)))

    tied = [r for r in rows if r["value"] == rows[0]["value"]]
    names = " and ".join(f"**{r['label']}**" for r in tied)
    behind = " and ".join(f"{r['label']} ({show(r['value'])})" for r in rows[len(tied) : len(tied) + 2])
    measure = MOST_NOUN[slots.get("rank_metric", "count")][0 if descending else 1]
    subject = _subject(facts, is_value)
    each = "each " if len(tied) > 1 else ""
    text = f"{names} {has_have(len(tied))} {measure}{subject}, {each}with **{show(rows[0]['value'])}**"
    text += f", {'ahead of' if descending else 'followed by'} {behind}." if behind else "."

    group = slots.get("group_by", "status")
    measured = "purchase value" if is_value else "asset count"
    note = f"{'Highest' if descending else 'Lowest'} {measured} by {group}"
    chart_rows = [{"label": r["label"], "value": float(r["value"]), "text": show(r["value"])} for r in rows]
    return Answer(text, facts.source, chart=Chart(chart_rows, note))


def _subject(facts: Facts, is_value: bool) -> str:
    """What is being ranked, with any filters from the question."""
    filtered_type = facts.slots.get("asset_type") or facts.slots.get("make")
    noun = asset_noun(facts, 2)
    base = (f" among {noun}" if filtered_type else "") if is_value else f" {noun}"
    return base + location_suffix(facts.slots) + age_phrase(facts.slots)
