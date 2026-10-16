from .formatting import is_are, money, plural
from .lists import with_limit, with_table
from .models import Answer, Facts

LEAVERS_NOTE = (
    " The database has no exit dates or offboarding cases yet,"
    " so this shows assets held by people marked as no longer active."
)


def unrecovered_assets(facts: Facts) -> Answer:
    if not facts.rows:
        return Answer(
            "No assets are assigned to people who are no longer active.", facts.source + LEAVERS_NOTE
        )
    total, laptops = facts.total, int(facts.rows[0]["laptops"])
    text = f"**{plural(total, 'asset')}** {is_are(total)} still assigned to people who are no longer active"
    text += f", including **{plural(laptops, 'laptop')}**." if laptops else "."
    answer = with_table(facts, with_limit(text, facts))
    answer.source += LEAVERS_NOTE
    return answer


def open_loss_cases(facts: Facts) -> Answer:
    if not facts.rows:
        return Answer("There are no open loss or theft cases.", facts.source)
    first = facts.rows[0]
    text = (
        f"**{plural(facts.total, 'open case')}**: **{first['lost']}** lost and **{first['stolen']}** stolen, "
        f"**{first['negligent']}** marked negligent."
    )
    return with_table(facts, with_limit(text, facts))


def aod_cases(facts: Facts) -> Answer:
    if not facts.rows:
        return Answer("There are no open AOD cases.", facts.source)
    worth = money(facts.rows[0]["total_amount"])
    text = f"**{plural(facts.total, 'open AOD case')}** worth **{worth}** in total."
    rows = [{**row, "amount": money(row["amount"])} for row in facts.rows]
    return with_table(facts, with_limit(text, facts), rows)
