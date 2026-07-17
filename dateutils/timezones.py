"""
Timezone utilities.
"""

import importlib
from datetime import date, datetime, timedelta, timezone, tzinfo
from functools import lru_cache
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

try:
    from ._awareness import is_aware_datetime as _is_aware_datetime
except ImportError:  # pragma: no cover
    # Support doctest's direct file import mode (no package context), which
    # relies on the package directory being importable on sys.path.
    _is_aware_datetime = importlib.import_module("_awareness").is_aware_datetime


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


def _resolve_timezone(tz: str | tzinfo) -> tzinfo:
    """Return a timezone object for a name or a supplied tzinfo instance."""
    if isinstance(tz, str):
        try:
            return ZoneInfo(tz)
        except ZoneInfoNotFoundError as e:
            raise ValueError(
                f"Invalid timezone name '{tz}'. Use get_available_timezones() to see valid options."
            ) from e
    if isinstance(tz, tzinfo):
        return tz
    raise TypeError("tz must be a timezone name or datetime.tzinfo instance")


def now_in_timezone(tz: str | tzinfo) -> datetime:
    """
    Get the current datetime in the specified timezone

    Args:
        tz: IANA timezone name (e.g. "America/New_York") or a ``tzinfo``
            instance.

    Returns:
        Current datetime in the specified timezone

    Raises:
        zoneinfo.ZoneInfoNotFoundError: If the timezone name is invalid.
        TypeError: If ``tz`` is neither a timezone name nor a ``tzinfo`` instance.
    """
    return datetime.now(ZoneInfo(tz) if isinstance(tz, str) else _resolve_timezone(tz))


def today_in_timezone(tz: str | tzinfo) -> date:
    """
    Get the current date in the specified timezone

    Args:
        tz: IANA timezone name (e.g. "America/New_York") or a ``tzinfo``
            instance.

    Returns:
        Current date in the specified timezone

    Raises:
        zoneinfo.ZoneInfoNotFoundError: If the timezone name is invalid.
        TypeError: If ``tz`` is neither a timezone name nor a ``tzinfo`` instance.
    """
    return now_in_timezone(tz).date()


def localize_datetime(
    dt: datetime,
    tz: str | tzinfo,
    *,
    ambiguous: Literal["raise", "earliest", "latest"] = "raise",
    nonexistent: Literal["raise", "shift_forward"] = "raise",
) -> datetime:
    """Attach a timezone to a datetime without a usable UTC offset.

    Use this when a value is a local wall time whose timezone is known.
    :meth:`datetime.astimezone` instead converts an already-aware datetime that
    represents a specific instant. Direct ``replace(tzinfo=...)`` skips DST
    validation, so it can silently choose one occurrence of a repeated time or
    create a nonexistent one.

    Args:
        dt: The local datetime to localize. It must not have a usable UTC offset.
        tz: An IANA timezone name (for example, ``"America/New_York"``) or a
            :class:`datetime.tzinfo` instance such as :data:`datetime.timezone.utc`.
        ambiguous: How to resolve a repeated wall time during a DST fall-back.
            ``"earliest"`` selects the first occurrence (``fold=0``),
            ``"latest"`` selects the second (``fold=1``), and ``"raise"``
            rejects the ambiguous time.
        nonexistent: How to resolve a missing wall time during a DST
            spring-forward. ``"shift_forward"`` applies the same forward
            normalization as :func:`convert_timezone`; ``"raise"`` rejects
            the nonexistent time.

    Returns:
        An aware datetime in ``tz``.

    Raises:
        ValueError: If ``dt`` already has a usable UTC offset, the timezone name
            or a policy is invalid, or a DST transition requires a policy that
            was not selected.
        TypeError: If ``tz`` is neither a timezone name nor a
            :class:`datetime.tzinfo` instance.

    Examples:
        >>> from datetime import datetime
        >>> localize_datetime(datetime(2024, 7, 22, 10, 30), "America/New_York")
        datetime.datetime(2024, 7, 22, 10, 30, tzinfo=zoneinfo.ZoneInfo(key='America/New_York'))

        >>> localize_datetime(
        ...     datetime(2024, 11, 3, 1, 30), "America/New_York", ambiguous="latest"
        ... ).fold
        1
    """
    if _is_aware_datetime(dt):
        raise ValueError("Input datetime must be naive")
    dt = dt.replace(tzinfo=None)
    if ambiguous not in {"raise", "earliest", "latest"}:
        raise ValueError("ambiguous must be one of: 'raise', 'earliest', 'latest'")
    if nonexistent not in {"raise", "shift_forward"}:
        raise ValueError("nonexistent must be one of: 'raise', 'shift_forward'")

    target_tz = _resolve_timezone(tz)

    first = dt.replace(tzinfo=target_tz, fold=0)
    second = dt.replace(tzinfo=target_tz, fold=1)
    first_round_trip = first.astimezone(timezone.utc).astimezone(target_tz).replace(tzinfo=None)
    second_round_trip = second.astimezone(timezone.utc).astimezone(target_tz).replace(tzinfo=None)

    if dt not in (first_round_trip, second_round_trip):
        if nonexistent == "raise":
            raise ValueError(f"Local time {dt!s} does not exist in timezone {tz!r}")
        return first.astimezone(timezone.utc).astimezone(target_tz)

    if first.utcoffset() != second.utcoffset():
        if ambiguous == "raise":
            raise ValueError(f"Local time {dt!s} is ambiguous in timezone {tz!r}")
        return first if ambiguous == "earliest" else second

    return first


def convert_timezone(dt: datetime, to_tz: str | tzinfo) -> datetime:
    """
    Convert a timezone-aware datetime object to another timezone.

    Args:
        dt: The datetime object to convert. Must have a usable UTC offset.
        to_tz: Target IANA timezone name (e.g., "America/New_York") or a
            ``tzinfo`` instance. See `get_available_timezones()` for names.

    Returns:
        datetime: A new datetime object representing the same point in time
                  in the target timezone.

    Raises:
        ValueError: If the input datetime `dt` has no usable UTC offset or if
            the timezone name is invalid.
        TypeError: If ``to_tz`` is neither a timezone name nor a ``tzinfo``
            instance.

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
    if not _is_aware_datetime(dt):
        raise ValueError("Input datetime must include timezone information")

    target_tz = _resolve_timezone(to_tz)
    source_utc = dt.astimezone(timezone.utc)
    source_round_trip = source_utc.astimezone(dt.tzinfo)

    # A mismatched wall time means the source was inside a spring-forward
    # gap. Normalize with fold=0 so inherited fold state cannot move the
    # nonexistent time backward.
    if source_round_trip.replace(tzinfo=None) != dt.replace(tzinfo=None):
        source_utc = dt.replace(fold=0).astimezone(timezone.utc)

    return source_utc.astimezone(target_tz)


def datetime_to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC.

    Note: Datetimes without a usable UTC offset are assumed to be in UTC
    (consistent with epoch_s()). If you need to convert a local wall time,
    first attach the appropriate timezone using datetime.replace(tzinfo=...) or
    datetime.astimezone().

    DST Ambiguity:
        During DST fall-back transitions (e.g., Nov 3, 2024 in US Eastern),
        times like 1:30 AM occur twice. When converting such ambiguous times:
        - fold=0 (default): First 1:30 AM (EDT, UTC-4) → 5:30 AM UTC
        - fold=1: Second 1:30 AM (EST, UTC-5) → 6:30 AM UTC

        To explicitly specify which occurrence, set the `fold` attribute:
        ``dt.replace(fold=1)`` for the second occurrence.

    Args:
        dt: The datetime to convert. If it has no usable UTC offset, assumed to
            be UTC.

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
    if not _is_aware_datetime(dt):
        # Assume UTC for datetimes without a usable offset (consistent with epoch_s).
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def get_timezone_offset(tz: str | tzinfo) -> timedelta:
    """
    Get the current offset from UTC for a timezone

    Args:
        tz: IANA timezone name or a ``tzinfo`` instance.

    Returns:
        Timedelta representing the offset from UTC

    Raises:
        ValueError: If timezone name is invalid
        TypeError: If ``tz`` is neither a timezone name nor a ``tzinfo`` instance.
    """
    now = datetime.now(_resolve_timezone(tz))
    return now.utcoffset() or timedelta(0)


def format_timezone_offset(tz: str | tzinfo) -> str:
    """
    Get the current offset from UTC for a timezone as a formatted string.

    Args:
        tz: IANA timezone name or a ``tzinfo`` instance.

    Returns:
        String in format "+HH:MM" or "-HH:MM"

    Raises:
        ValueError: If timezone name is invalid
        TypeError: If ``tz`` is neither a timezone name nor a ``tzinfo`` instance.

    Note:
        Returns the offset at the **current moment**. For DST zones, this varies
        throughout the year. For example, "America/New_York" returns "-05:00" in
        winter (EST) and "-04:00" in summer (EDT).

        To get the offset at a specific time, use::

            dt = datetime(2024, 7, 15, tzinfo=ZoneInfo(tz_name))
            offset = dt.utcoffset()
    """
    offset = get_timezone_offset(tz)

    # Convert timedelta to hours and minutes
    total_seconds = int(offset.total_seconds())
    hours, remainder = divmod(abs(total_seconds), _SECONDS_IN_HOUR)
    minutes, _ = divmod(remainder, _SECONDS_IN_MINUTE)

    sign = "-" if total_seconds < 0 else "+"
    return f"{sign}{hours:02d}:{minutes:02d}"
