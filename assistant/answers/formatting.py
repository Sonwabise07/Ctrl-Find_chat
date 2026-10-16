from .models import Chart, Facts


def money(value) -> str:
    amount = float(value)
    digits = f"{amount:,.0f}" if amount == int(amount) else f"{amount:,.2f}"
    return "R" + digits.replace(",", "\u202f")


def number(value) -> str:
    return f"{int(value):,}".replace(",", "\u202f")


def plural(count: int, word: str) -> str:
    return f"{count} {word}" + ("" if count == 1 else "s")


def is_are(count: int) -> str:
    return "is" if count == 1 else "are"


def has_have(count: int) -> str:
    return "has" if count == 1 else "have"


def asset_noun(facts: Facts, count: int) -> str:
    noun = facts.vocab.type_nouns.get(facts.slots.get("asset_type"), "asset")
    make = facts.slots.get("make")
    return (f"{make} " if make else "") + noun + ("" if count == 1 else "s")


def location_suffix(slots: dict) -> str:
    location = f" at {slots['location']}" if slots.get("location") else ""
    department = f" in the {slots['department']} department" if slots.get("department") else ""
    return location + department


def age_phrase(slots: dict) -> str:
    months = slots.get("older_than")
    if not months:
        return ""
    return ", older than " + (plural(months // 12, "year") if months % 12 == 0 else plural(months, "month"))


def ranked_chart(rows: list[dict], note: str) -> Chart:
    return Chart(
        [{"label": r["label"], "value": int(r["value"]), "text": str(r["value"])} for r in rows], note
    )
