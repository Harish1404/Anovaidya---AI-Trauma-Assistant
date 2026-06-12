import re
from typing import Optional

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

SKIP_KEYWORDS = ["no", "skip", "later", "not now", "nope", "don't"]


def extract_email(text: str) -> Optional[str]:
    """Extract an email address from user text."""
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_doctor_name(text: str, doctors: list) -> Optional[str]:
    """Match a doctor name from user text against the recommended list."""
    text_lower = text.lower()

    # 1. Direct full name match
    for doc in doctors:
        name = doc.get("full_name", "")
        if name.lower() in text_lower:
            return name

    # 2. Match by first name or last name
    for doc in doctors:
        name = doc.get("full_name", "")
        clean_name = name.replace("Dr.", "").replace("dr.", "").strip()
        parts = clean_name.split()
        if parts:
            first_name = parts[0]
            last_name = parts[-1]
            if len(first_name) > 2 and first_name.lower() in text_lower:
                return name
            if len(last_name) > 2 and last_name.lower() in text_lower:
                return name

    # 3. Match by number or ordinal
    tokens = re.findall(r"\b\w+\b", text_lower)
    ordinals = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]

    for idx, doc in enumerate(doctors):
        name = doc.get("full_name", "")

        # Check for digit (1-based index)
        digit_str = str(idx + 1)
        if digit_str in tokens:
            return name

        # Check for ordinal word
        if idx < len(ordinals):
            ordinal_word = ordinals[idx]
            if ordinal_word in tokens:
                return name

    return None


def is_email_skip_message(text: str) -> bool:
    """Return True if the user wants to skip providing an email."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in SKIP_KEYWORDS)
