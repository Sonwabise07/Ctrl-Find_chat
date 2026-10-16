from .formatting import plural
from .lists import with_limit, with_table
from .models import Answer, Facts


def asset_timeline(facts: Facts) -> Answer:
    if not facts.rows:
        return Answer(
            "I couldn't find an asset with that number among the assets you can view.", facts.source
        )
    first = facts.rows[0]
    if first["event"] is None:
        return Answer(f"**{first['asset_no']}** has no recorded events.", facts.source)
    text = (
        f"**{first['asset_no']}** has **{plural(facts.total, 'recorded event')}**. "
        f"The latest is **{first['event']}** on {first['occurred']}."
    )
    return with_table(facts, with_limit(text, facts))
