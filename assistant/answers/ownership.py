from ..filters import FILTER_SLOTS
from .formatting import age_phrase, asset_noun, location_suffix
from .lists import with_limit, with_table
from .models import Answer, Facts

TEAM_NOTE = " Your team is taken as your department, because the database has no manager link yet."


def my_assets(facts: Facts) -> Answer:
    if not facts.rows:
        matching = "matching " if any(key in facts.slots for key in FILTER_SLOTS) else ""
        return with_table(facts, f"You have no {matching}assets assigned to you.")
    total = facts.total
    where = location_suffix(facts.slots) + age_phrase(facts.slots)
    text = f"You have **{total} {asset_noun(facts, total)}** assigned to you{where}."
    return with_table(facts, with_limit(text, facts))


def team_assets(facts: Facts) -> Answer:
    if not facts.rows:
        answer = with_table(facts, "You can see no matching assets in your department.")
    else:
        total, department = facts.total, facts.rows[0]["department"]
        where = location_suffix(facts.slots) + age_phrase(facts.slots)
        text = (
            f"You can see **{total} {asset_noun(facts, total)}** in your department, **{department}**{where}."
        )
        answer = with_table(facts, with_limit(text, facts))
    answer.source += TEAM_NOTE
    return answer
