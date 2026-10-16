from .formatting import age_phrase, asset_noun, location_suffix, money, plural
from .lists import with_limit, with_table
from .models import Answer, Facts


def purchases_in_period(facts: Facts) -> Answer:
    label = facts.slots["date_label"]
    where = location_suffix(facts.slots) + age_phrase(facts.slots)
    if not facts.rows:
        return Answer(f"No {asset_noun(facts, 2)} were bought{where} {label}.", facts.source)
    total = facts.total
    worth = money(facts.rows[0]["total_price"])
    verb = "was" if total == 1 else "were"
    text = f"**{total} {asset_noun(facts, total)}** worth **{worth}** {verb} bought{where} {label}."
    rows = [{**row, "price": money(row["price"])} for row in facts.rows]
    return with_table(facts, with_limit(text, facts), rows)


def repairs_in_period(facts: Facts) -> Answer:
    label = facts.slots["date_label"]
    where = location_suffix(facts.slots)
    if not facts.rows:
        return Answer(f"No repairs were reported{where} {label}.", facts.source)
    total = facts.total
    cost = money(facts.rows[0]["total_cost"])
    verb = "was" if total == 1 else "were"
    text = f"**{plural(total, 'repair')}** {verb} reported{where} {label}, costing **{cost}** in total."
    rows = [{**row, "cost": money(row["cost"])} for row in facts.rows]
    return with_table(facts, with_limit(text, facts), rows)
