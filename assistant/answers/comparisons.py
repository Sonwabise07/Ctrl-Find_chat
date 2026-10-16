from .formatting import money, plural
from .models import Answer, Chart, Facts

WHAT_IS_COMPARED = {"spend_by_period": "purchases", "maintenance_cost_by_period": "repair costs"}


def _summary(row: dict) -> str:
    return f"{money(row['value'])} across {plural(int(row['items']), 'record')}"


def period_comparison(intent: str):
    def format_comparison(facts: Facts) -> Answer:
        earlier, later = facts.rows[0], facts.rows[1]
        text = (
            f"**{later['label']}**: {_summary(later)}; "
            f"**{earlier['label']}**: {_summary(earlier)} ({WHAT_IS_COMPARED[intent]})."
        )
        rows = [
            {"label": r["label"], "value": float(r["value"]), "text": money(r["value"])} for r in facts.rows
        ]
        return Answer(text, facts.source, chart=Chart(rows, "Comparison of two periods."))

    return format_comparison


def open_aod_value(facts: Facts) -> Answer:
    row = facts.rows[0]
    records = plural(int(row["items"]), "record")
    text = f"**{money(row['value'])}** in AOD is currently open across **{records}**."
    return Answer(text, facts.source)
