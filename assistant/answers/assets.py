from .formatting import money, plural
from .models import Answer, Details, Facts, Table

HISTORY_COLUMNS = ["changed_on", "event", "employee"]


def asset_lookup(facts: Facts) -> Answer:
    if not facts.rows:
        return Answer(
            "I couldn't find an asset with that number among the assets you can view.", facts.source
        )
    row = facts.rows[0]
    where = f" at {row['location']}" if row["location"] != "-" else ""
    holder = f", held by {row['holder']}" if row["holder"] != "-" else ""
    text = f"**{row['asset_no']}** is a {row['description']}, currently **{row['status']}**{where}{holder}."
    history = [{key: str(event[key]) for key in HISTORY_COLUMNS} for event in row["history"]]
    return Answer(
        text,
        facts.source,
        table=Table(HISTORY_COLUMNS, history) if history else None,
        details=Details(row["asset_no"], _facts_about(row)),
    )


def _facts_about(row: dict) -> list[dict]:
    warranty = row["warranty_end"] or "-"
    if row["warranty_end"]:
        warranty = f"{'Ended' if row['warranty_ended'] else 'Ends'} {warranty}"
    purchased = row["purchased"] or "-"
    if row["purchase_price"] is not None:
        purchased += f" · {money(row['purchase_price'])}"
    facts = [
        ("Status", row["status"]),
        ("Location", row["location"]),
        ("Department", row["department"]),
        ("Assigned to", row["holder"]),
        ("Serial number", row["serial_number"]),
        ("Purchased", purchased),
        ("Warranty", warranty),
        ("Repairs", _repairs(row)),
    ]
    return [{"label": label, "text": text} for label, text in facts]


def _repairs(row: dict) -> str:
    count = int(row["repairs"])
    if count == 0:
        return "None"
    parts = [plural(count, "repair")]
    if row["repair_cost"]:
        parts.append(f"{money(row['repair_cost'])} spent")
    if row["open_repairs"]:
        parts.append(f"{int(row['open_repairs'])} open")
    return ", ".join(parts)
