import re

NUMBER = re.compile(r"\d+(?:\u202f\d{3})*(?:\.\d+)?")
DIGITS = re.compile(r"\d+")


def unexplained_numbers(answer: str, rows: list[dict], *context: str) -> list[str]:
    """Numbers in the answer that appear in neither the query rows nor the question and date window."""
    allowed = {float(len(rows))}
    for text in context:
        allowed |= {float(n) for n in DIGITS.findall(text)}
    for row in rows:
        for value in row.values():
            allowed |= {float(n) for n in DIGITS.findall(str(value))}
            if isinstance(value, (int, float)) or hasattr(value, "as_tuple"):
                allowed.add(float(value))
    shown = (token.replace("\u202f", "") for token in NUMBER.findall(answer.replace("**", "")))
    return [token for token in shown if float(token) not in allowed]
