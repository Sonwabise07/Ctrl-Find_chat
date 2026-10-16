import re

ASSET_NUMBER = re.compile(r"\b([A-Za-z]{2,5}-?\d{3,8})\b")
SERIAL = re.compile(
    r"\bserial(?:\s+(?:number|no\.?))?\s+(?=[A-Za-z0-9-]*\d)([A-Za-z0-9-]{5,})", re.IGNORECASE
)


def find_asset_ref(text: str) -> str | None:
    """An asset number such as AST-0013, or a serial number after the word 'serial', without punctuation."""
    match = SERIAL.search(text) or ASSET_NUMBER.search(text)
    return re.sub(r"[^A-Z0-9]", "", match.group(1).upper()) if match else None
