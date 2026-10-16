from .formatting import age_phrase, asset_noun, has_have, is_are, plural
from .models import Answer, Facts, Table


def with_table(facts: Facts, text: str, rows: list[dict] | None = None) -> Answer:
    """The answer with a table of the rows. Pass `rows` when some values need formatting first."""
    shown = facts.rows if rows is None else rows
    table = None
    if shown:
        table = Table(list(facts.columns), [{c: str(row[c]) for c in facts.columns} for row in shown])
    return Answer(text, facts.source, table=table)


def with_limit(text: str, facts: Facts) -> str:
    """Says so when the table shows only the latest rows of a longer result."""
    shown = len(facts.rows)
    return text + (f" Showing the latest {shown}." if facts.total > shown else "")


def list_assets(facts: Facts) -> Answer:
    if not facts.rows:
        return with_table(facts, "No assets match that filter.")
    text = f"**{plural(facts.total, 'asset')}** match{age_phrase(facts.slots)}."
    if facts.total > len(facts.rows):
        text += f" Showing the first {len(facts.rows)}."
    return with_table(facts, text)


def warranty_assets(facts: Facts) -> Answer:
    window, total = facts.window, facts.total
    if window.expired:
        text = f"**{plural(total, 'asset')}** {is_are(total)} {window.text}."
        empty = f"No assets are {window.text}."
    else:
        text = f"**{plural(total, 'asset')}** {has_have(total)} {window.text}."
        empty = f"No assets have {window.text}."
    return with_table(facts, text if facts.rows else empty)


def maintenance_open(facts: Facts) -> Answer:
    text = (
        f"**{plural(facts.total, 'open repair case')}**." if facts.rows else "There are no open repair cases."
    )
    return with_table(facts, text)


def assets_of_person(facts: Facts) -> Answer:
    name = facts.lookups.person_name(facts.slots.get("person")) or "That person"
    if not facts.rows:
        return with_table(facts, f"{name} has no assets assigned to them that you can view.")
    return with_table(facts, f"**{name}** has **{plural(facts.total, 'asset')}** assigned.")


def unconfirmed_assets(facts: Facts) -> Answer:
    if not facts.rows:
        return with_table(facts, "No confirmations are pending in the active cycle.")
    total = facts.total
    text = (
        f"**{total} {asset_noun(facts, total)}** {is_are(total)} unconfirmed "
        "\u2014 a self-confirmation request was sent and there is no reply yet."
    )
    return with_table(facts, text)


def overdue_confirmations(facts: Facts) -> Answer:
    if not facts.rows:
        return with_table(facts, "No confirmations are overdue.")
    total = facts.total
    count = plural(total, "confirmation")
    text = f"**{count}** {is_are(total)} overdue \u2014 the due date has passed with no reply."
    return with_table(facts, text)


def laptop_ages(facts: Facts) -> Answer:
    if not facts.rows:
        return with_table(facts, "No laptops match that filter.")
    first = facts.rows[0]
    text = (
        f"**{plural(facts.total, 'laptop')}** in use or in stock: **{first['past_warranty']}** past warranty "
        f"and **{first['ending_soon']}** ending within {first['soon_days']} days."
    )
    rows = [{**row, "age": _age(row["age_years"], row["age_months"])} for row in facts.rows]
    return with_table(facts, with_limit(text, facts), rows)


def _age(years: int, months: int) -> str:
    parts = [plural(years, "year")] if years else []
    parts += [plural(months, "month")] if months else []
    return " ".join(parts) or "Under a month"
