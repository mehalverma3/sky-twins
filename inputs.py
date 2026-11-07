from datetime import date

MIN_D = date(1900, 1, 1)
MAX_D = date(2050, 12, 31)


def parse_date(text: str):
    """Return a date within range, or None if the input is invalid."""
    try:
        d = date.fromisoformat(text.strip())
    except (ValueError, AttributeError):
        return None
    return d if MIN_D <= d <= MAX_D else None