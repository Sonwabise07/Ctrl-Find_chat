from .formatting import age_phrase, asset_noun, is_are, location_suffix, plural, ranked_chart
from .models import Answer, Facts


def count_assets(facts: Facts) -> Answer:
    count = int(facts.rows[0]["value"])
    status = facts.slots.get("status")
    state = facts.vocab.status_phrases[status] if status else "registered"
    suffix = location_suffix(facts.slots) + age_phrase(facts.slots)
    text = f"**{count} {asset_noun(facts, count)}** {is_are(count)} {state}{suffix}."
    source = facts.source
    if facts.slots.get("make"):
        source += " Make is matched on the asset description."
    return Answer(text, source)


def breakdown_assets(facts: Facts) -> Answer:
    if not facts.rows:
        return Answer("No assets match that filter.", facts.source)
    group = facts.slots.get("group_by", "status")
    rows = facts.rows
    leader = f"**{rows[0]['label']}** is highest"
    if len(rows) > 1 and rows[1]["value"] == rows[0]["value"]:
        leader = f"**{rows[0]['label']}** and **{rows[1]['label']}** are joint highest"
    text = (
        f"Here is the split of **{facts.total} {asset_noun(facts, facts.total)}** by {group}"
        f"{age_phrase(facts.slots)}. "
        f"{leader} with **{rows[0]['value']}**."
    )
    return Answer(
        text, facts.source, chart=ranked_chart(rows, f"Comparison across {len(rows)} {group} values.")
    )


def audit_exceptions_by_location(facts: Facts) -> Answer:
    rows = facts.rows
    if not rows:
        return Answer("No audit exceptions are recorded in the active cycle.", facts.source)
    tied = [r for r in rows if r["value"] == rows[0]["value"]]
    names = " and ".join(f"**{r['label']}**" for r in tied)
    behind = " and ".join(f"{r['label']} ({r['value']})" for r in rows[len(tied) : len(tied) + 2])
    flagged = plural(int(rows[0]["value"]), "flagged asset")
    verb, each = ("have", "each ") if len(tied) > 1 else ("has", "")
    text = f"{names} {verb} the most open exceptions this cycle, {each}with **{flagged}**"
    text += f", ahead of {behind}." if behind else "."
    return Answer(text, facts.source, chart=ranked_chart(rows, f"Comparison across {len(rows)} locations."))
