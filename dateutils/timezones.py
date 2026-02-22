"""
Timezone utilities.
"""

from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

_SECONDS_IN_MINUTE = 60
_SECONDS_IN_HOUR = 60 * _SECONDS_IN_MINUTE


@lru_cache(maxsize=1)
def _get_available_timezones_cached() -> tuple[str, ...]:
    """Cache timezone names to avoid repeated full-database sorting."""
    return tuple(sorted(available_timezones()))


def get_available_timezones() -> list[str]:
    """
    Get a list of available timezone names

    Returns:
        List of timezone names (e.g. "America/New_York", "Europe/London", etc.)
    """
    # Return a new list so callers can mutate safely without affecting cache.
    return list(_get_available_timezones_cached())


def now_in_timezone(tz_name: str) -> datetime:
    """
    Get the current datetime in the specified timezone

    Args:
        tz_name: Timezone name (e.g. "America/New_York", "Europe/London")

    Returns:
        Current datetime in the specified timezone

    Raises:
        zoneinfo.ZoneInfoNotFoundError: If timezone name is invalid
    """
    tz = ZoneInfo(tz_name)
    return datetime.now(tz)


def today_in_timezone(tz_name: str) -> date:
    """
    Get the current date in the specified timezone

    Args:
        tz_name: Timezone name (e.g. "America/New_York", "Europe/London")

    Returns:
        Current date in the specified timezone

    Raises:
        zoneinfo.ZoneInfoNotFoundError: If timezone name is invalid
    """
    return now_in_timezone(tz_name).date()


def convert_timezone(dt: datetime, to_tz: str) -> datetime:
    """
    Convert a timezone-aware datetime object to another timezone.

    Args:
        dt: The datetime object to convert. Must have tzinfo set.
        to_tz: Target timezone name (e.g., "America/New_York", "Europe/London").
               See `get_available_timezones()` for options.

    Returns:
        datetime: A new datetime object representing the same point in time
                  in the target timezone.

    Raises:
        ValueError: If the input datetime `dt` is naive (tzinfo is None) or if
                   the timezone name is invalid.

    Note on DST Transitions:
        During DST fall-back (e.g., Nov 3, 2024 at 2:00 AM in US Eastern),
        local times like 1:30 AM occur twice. Python's ZoneInfo uses the
        `fold` attribute to disambiguate: fold=0 (default) is the first
        occurrence (DST side), fold=1 is the second (standard time side).

        During DST spring-forward (e.g., Mar 10, 2024 at 2:00 AM in US Eastern),
        times like 2:30 AM do not exist. ZoneInfo normalizes these forward
        to the valid time (e.g., 2:30 AM becomes 3:30 AM EDT).

    Examples:
        >>> from datetime import datetime, timezone, timedelta
        >>> utc_time = datetime(2024, 7, 22, 14, 30, 0, tzinfo=timezone.utc)
        >>> local_time = convert_timezone(utc_time, "America/Los_Angeles")
        >>> print(local_time)
        2024-07-22 07:30:00-07:00

        >>> # Convert from one specific zone to another
        >>> ny_tz = ZoneInfo("America/New_York")
        >>> ny_time = datetime(2024, 7, 22, 10, 30, 0, tzinfo=ny_tz)
        >>> london_time = convert_timezone(ny_time, "Europe/London")
        >>> print(london_time)
        2024-07-22 15:30:00+01:00

        >>> # Example of error for naive datetime
        >>> naive_time = datetime(2024, 7, 22, 14, 30, 0)
        >>> try:
        ...     convert_timezone(naive_time, "America/New_York")
        ... except ValueError as e:
        ...     print(e)
        Input datetime must include timezone information
    """
    if dt.tzinfo is None:
        raise ValueError("Input datetime must include timezone information")

    try:
        target_tz = ZoneInfo(to_tz)
        return dt.astimezone(target_tz)
    except ZoneInfoNotFoundError as e:
        raise ValueError(f"Invalid timezone name '{to_tz}'. Use get_available_timezones() to see valid options.") from e


def datetime_to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC.

    Note: Naive datetimes are assumed to be in UTC (consistent with epoch_s()).
    If you need to convert a naive datetime that represents local time, first
    attach the appropriate timezone using datetime.replace(tzinfo=...) or
    datetime.astimezone().

    DST Ambiguity:
        During DST fall-back transitions (e.g., Nov 3, 2024 in US Eastern),
        times like 1:30 AM occur twice. When converting such ambiguous times:
        - fold=0 (default): First 1:30 AM (EDT, UTC-4) → 5:30 AM UTC
        - fold=1: Second 1:30 AM (EST, UTC-5) → 6:30 AM UTC

        To explicitly specify which occurrence, set the `fold` attribute:
        ``dt.replace(fold=1)`` for the second occurrence.

    Args:
        dt: The datetime to convert. If naive, assumed to be UTC.

    Returns:
        datetime: The datetime in UTC timezone.

    Examples:
        >>> from datetime import datetime, timezone
        >>> from zoneinfo import ZoneInfo
        >>> # Timezone-aware datetime is converted
        >>> ny_dt = datetime(2024, 7, 22, 10, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        >>> utc_dt = datetime_to_utc(ny_dt)
        >>> utc_dt.hour  # 10 EDT = 14 UTC
        14

        >>> # Naive datetime is assumed UTC
        >>> naive_dt = datetime(2024, 7, 22, 12, 0, 0)
        >>> result = datetime_to_utc(naive_dt)
        >>> result.hour
        12
        >>> result.tzinfo == timezone.utc
        True
    """
    if dt.tzinfo is None:
        # Assume UTC for naive datetimes (consistent with epoch_s)
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def get_timezone_offset(tz_name: str) -> timedelta:
    """
    Get the current offset from UTC for a timezone

    Args:
        tz_name: Timezone name

    Returns:
        Timedelta representing the offset from UTC

    Raises:
        ValueError: If timezone name is invalid
    """
    try:
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
        return now.utcoffset() or timedelta(0)
    except ZoneInfoNotFoundError as e:
        raise ValueError(
            f"Invalid timezone name '{tz_name}'. Use get_available_timezones() to see valid options."
        ) from e


def format_timezone_offset(tz_name: str) -> str:
    """
    Get the current offset from UTC for a timezone as a formatted string.

    Args:
        tz_name: Timezone name

    Returns:
        String in format "+HH:MM" or "-HH:MM"

    Raises:
        ValueError: If timezone name is invalid

    Note:
        Returns the offset at the **current moment**. For DST zones, this varies
        throughout the year. For example, "America/New_York" returns "-05:00" in
        winter (EST) and "-04:00" in summer (EDT).

        To get the offset at a specific time, use::

            dt = datetime(2024, 7, 15, tzinfo=ZoneInfo(tz_name))
            offset = dt.utcoffset()
    """
    offset = get_timezone_offset(tz_name)

    # Convert timedelta to hours and minutes
    total_seconds = int(offset.total_seconds())
    hours, remainder = divmod(abs(total_seconds), _SECONDS_IN_HOUR)
    minutes, _ = divmod(remainder, _SECONDS_IN_MINUTE)

    sign = "-" if total_seconds < 0 else "+"
    return f"{sign}{hours:02d}:{minutes:02d}"
