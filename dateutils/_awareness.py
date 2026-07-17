from datetime import datetime


def is_aware_datetime(value: datetime) -> bool:
    """Return whether a datetime has a usable UTC offset."""
    return value.tzinfo is not None and value.utcoffset() is not None
