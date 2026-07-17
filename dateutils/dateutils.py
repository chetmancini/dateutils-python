"""
Date and time utilities for Python applications.

This module provides a comprehensive set of utilities for working with dates, times,
and timezones in Python. It includes functions for:

- UTC date/time operations
- Quarter, month, week, and day operations
- Business day calculations (including basic US federal holiday support)
- Date/time parsing and formatting
- Timezone conversions
- Human-readable date formatting

The utilities aim to simplify common date and time operations while providing
consistent handling of timezone information.

Functions operating on calendar dates normalize `datetime` inputs to their
plain local `date` before doing date arithmetic. Timezone-aware values are not
converted to a different timezone during that normalization.

**Note on Holidays:** Basic support for US federal holidays is included
via `get_us_federal_holidays()`. For comprehensive, region-specific,
or rule-based holiday calculations (e.g., Easter or region-specific bank
holidays), consider using a dedicated library like `holidays`. You can easily
integrate it by generating a list of holiday dates from that library and
passing it to the `holidays` argument of the relevant business day functions
in this module.

Example using the `holidays` library:
```python
# pip install holidays
import holidays
from datetime import date
from dateutils import workdays_between

# Get UK holidays for 2024
uk_holidays_2024 = holidays.country_holidays('GB', subdiv='England', years=2024)
holiday_dates = list(uk_holidays_2024.keys())

start = date(2024, 5, 1)
end = date(2024, 5, 31)
# Calculate workdays excluding UK bank holidays
workdays = workdays_between(start, end, holidays=holiday_dates)
print(workdays)
```
"""

import calendar
import importlib
from collections.abc import Generator, Iterable
from datetime import date, datetime, time, timedelta, timezone
from email.utils import format_datetime as _format_http_datetime
from functools import lru_cache
from typing import Any, NamedTuple, cast

try:
    from . import parsing as _parsing
    from . import timezones as _timezones
    from ._awareness import is_aware_datetime as _is_aware_datetime
except ImportError:  # pragma: no cover
    # Support doctest's direct file import mode (no package context), which
    # relies on the package directory being importable on sys.path.
    _parsing = cast(Any, importlib.import_module("parsing"))
    _timezones = cast(Any, importlib.import_module("timezones"))
    _is_aware_datetime = importlib.import_module("_awareness").is_aware_datetime


##################
# Constants
##################
RECENT_SECONDS = 10
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR
DAYS_IN_YEAR = 365
DAYS_IN_MONTH_APPROX = 30
DAYS_IN_MONTH_MAX = 31
DAYS_IN_WEEK = 7
QUARTERS_IN_YEAR = 4
MONTHS_IN_QUARTER = 3
MONTHS_IN_YEAR = 12
WEEKDAYS_IN_WEEK = 5

# Internal constants for leap year birthday handling
_FEBRUARY = 2
_LEAP_DAY = 29
_FEB_28 = 28
_UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

ParseError = _parsing.ParseError
parse_date = _parsing.parse_date
parse_datetime = _parsing.parse_datetime
parse_iso8601 = _parsing.parse_iso8601
format_date = _parsing.format_date
format_datetime = _parsing.format_datetime
to_iso8601 = _parsing.to_iso8601

_get_available_timezones_cached = _timezones._get_available_timezones_cached
get_available_timezones = _timezones.get_available_timezones
now_in_timezone = _timezones.now_in_timezone
today_in_timezone = _timezones.today_in_timezone
localize_datetime = _timezones.localize_datetime
convert_timezone = _timezones.convert_timezone
datetime_to_utc = _timezones.datetime_to_utc
get_timezone_offset = _timezones.get_timezone_offset
format_timezone_offset = _timezones.format_timezone_offset


def _as_date(value: date) -> date:
    """Return the local calendar date represented by a date or datetime value."""
    return value.date() if isinstance(value, datetime) else value


##################
# UTC
##################
def utc_now_seconds() -> int:
    """
    Get the current time in seconds since epoch in UTC.

    Returns:
        int: Current UTC time as Unix timestamp (seconds since epoch)
    """
    return int(datetime.now(timezone.utc).timestamp())


def utc_today() -> date:
    """
    Get the current date in UTC.

    Returns:
        date: Current UTC date
    """
    return datetime.now(timezone.utc).date()


def utc_truncate_epoch_day(ts: int) -> int:
    """
    Truncate a timestamp to the start of the day in UTC.

    Args:
        ts: Unix timestamp (seconds since epoch)

    Returns:
        int: Timestamp truncated to start of day in UTC

    Raises:
        ValueError: If timestamp is invalid
    """
    try:
        dt = datetime.fromtimestamp(ts, timezone.utc)
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return epoch_s(dt)
    except (ValueError, OSError, OverflowError) as e:
        raise ValueError(f"Invalid timestamp: {ts}") from e


def utc_from_timestamp(ts: int) -> datetime:
    """
    Convert a timestamp to a datetime object in UTC timezone.

    Args:
        ts: Unix timestamp (seconds since epoch)

    Returns:
        datetime: Datetime object in UTC timezone

    Raises:
        ValueError: If timestamp is invalid
    """
    try:
        return datetime.fromtimestamp(ts, timezone.utc)
    except (ValueError, OSError, OverflowError) as e:
        raise ValueError(f"Invalid timestamp: {ts}") from e


def epoch_s(dt: datetime) -> int:
    """
    Convert a datetime object to whole Unix seconds, flooring fractional seconds.

    Note: Datetimes with a usable UTC offset are converted to UTC before
          calculating the timestamp. Other datetimes are assumed to be in UTC.

    Args:
        dt: Datetime object to convert.

    Returns:
        int: Unix timestamp (seconds since epoch).

    Examples:
        >>> from datetime import datetime, timezone, timedelta
        >>> dt_utc = datetime(2023, 10, 26, 12, 0, 0, tzinfo=timezone.utc)
        >>> epoch_s(dt_utc)
        1698321600

        >>> dt_naive = datetime(2023, 10, 26, 12, 0, 0)
        >>> epoch_s(dt_naive) # Assumed UTC
        1698321600

        >>> tz_est = timezone(timedelta(hours=-5))
        >>> dt_est = datetime(2023, 10, 26, 7, 0, 0, tzinfo=tz_est)
        >>> epoch_s(dt_est) # Converted to UTC
        1698321600
    """
    # datetime_to_utc assumes UTC for datetimes without a usable offset and
    # converts aware datetimes to UTC.
    delta = datetime_to_utc(dt) - _UNIX_EPOCH
    return delta.days * SECONDS_IN_DAY + delta.seconds


def datetime_start_of_day(day: date) -> datetime:
    """
    Get the start of the day for a specific date.

    Args:
        day: Date to get start of day for

    Returns:
        datetime: Datetime at midnight (00:00:00)
    """
    return datetime.combine(_as_date(day), datetime.min.time())


def _datetime_at_end_of_day(day: date) -> datetime:
    """Return a datetime at the last representable microsecond of the given day."""
    return datetime.combine(_as_date(day), time.max)


def datetime_end_of_day(day: date) -> datetime:
    """
    Get the end of the day for a specific date.

    Args:
        day: Date to get end of day for

    Returns:
        datetime: Datetime at 23:59:59.999999

    Examples:
        >>> from datetime import date
        >>> datetime_end_of_day(date(2024, 7, 22))
        datetime.datetime(2024, 7, 22, 23, 59, 59, 999999)
    """
    return _datetime_at_end_of_day(day)


##################
# Quarter operations
##################
def _validate_quarter(quarter: int, *, name: str = "Quarter") -> None:
    """Validate that a quarter value is between 1 and 4."""
    if not 1 <= quarter <= QUARTERS_IN_YEAR:
        raise ValueError(f"{name} must be between 1 and 4, got {quarter}")


def date_to_quarter(dt: date) -> int:
    """
    Get the quarter of the year for a specific date

    Args:
        dt: Date to get quarter for

    Returns:
        int: Quarter of the year (1-4)
    """
    dt = _as_date(dt)
    return ((dt.month - 1) // MONTHS_IN_QUARTER) + 1


def date_to_start_of_quarter(dt: date) -> date:
    """
    Get the start of the quarter for a specific date

    Args:
        dt: Date to get start of quarter for

    Returns:
        date: Date at the start of the quarter
    """
    dt = _as_date(dt)
    new_month = (((dt.month - 1) // MONTHS_IN_QUARTER) * MONTHS_IN_QUARTER) + 1
    return dt.replace(day=1, month=new_month)


def start_of_quarter(year: int, q: int) -> datetime:
    """
    Get the start of the quarter

    Args:
        year: Year to get start of quarter for
        q: Quarter to get start of (1-4)

    Returns:
        datetime: Datetime at 00:00:00

    Raises:
        ValueError: If quarter is not between 1 and 4
    """
    _validate_quarter(q)
    return datetime(year, (q - 1) * MONTHS_IN_QUARTER + 1, 1)


def end_of_quarter(year: int, q: int) -> datetime:
    """
    Get the end of the quarter.

    Args:
        year: Year to get end of quarter for
        q: Quarter to get end of (1-4)

    Returns:
        datetime: Datetime at 23:59:59.999999

    Raises:
        ValueError: If quarter is not between 1 and 4
    """
    _validate_quarter(q)
    month = q * MONTHS_IN_QUARTER
    days_in_month = calendar.monthrange(year, month)[1]
    return _datetime_at_end_of_day(date(year, month, days_in_month))


def _walk_inclusive(start: int, target: int) -> Generator[int, None, None]:
    """Yield every integer from start to target, including both endpoints."""
    step = 1 if target >= start else -1
    current = start
    while True:
        yield current
        if current == target:
            return
        current += step


def _quarter_index(year: int, quarter: int) -> int:
    """Return a linear index for a year/quarter pair."""
    return year * QUARTERS_IN_YEAR + (quarter - 1)


def _quarter_from_index(index: int) -> tuple[int, int]:
    """Return a (quarter, year) pair from a linear quarter index."""
    year = index // QUARTERS_IN_YEAR
    quarter = index % QUARTERS_IN_YEAR + 1
    return quarter, year


def generate_quarters(
    until_year: int = 1970,
    until_q: int = 1,
    *,
    start_year: int | None = None,
    start_quarter: int | None = None,
) -> Generator[tuple[int, int], None, None]:
    """
    Generate quarters between a starting quarter and a target quarter (inclusive).

    Args:
        until_year: Target year.
        until_q: Target quarter (1-4).
        start_year: Starting year. Defaults to current year.
        start_quarter: Starting quarter (1-4). Defaults to the current quarter.

    Yields:
        tuple[int, int]: Tuples of (quarter, year) walking toward the target.

    Raises:
        ValueError: If start or until quarters are not between 1 and 4
    """
    _validate_quarter(until_q, name="until_q")

    today = date.today()
    start_y = today.year if start_year is None else start_year
    start_q = date_to_quarter(today) if start_quarter is None else start_quarter

    _validate_quarter(start_q, name="start_quarter")

    for idx in _walk_inclusive(_quarter_index(start_y, start_q), _quarter_index(until_year, until_q)):
        yield _quarter_from_index(idx)


##################
# Year operations
##################


def start_of_year(year: int) -> datetime:
    """
    Get the start of the year

    Args:
        year: Year to get start of year for

    Returns:
        datetime: Datetime at 00:00:00
    """
    return datetime(year, 1, 1, 0, 0, 0)


def end_of_year(year: int) -> datetime:
    """
    Get the end of the year.

    Args:
        year: Year to get end of year for

    Returns:
        datetime: Datetime at 23:59:59.999999
    """
    return _datetime_at_end_of_day(date(year, MONTHS_IN_YEAR, DAYS_IN_MONTH_MAX))


def generate_years(until: int = 1970, *, start_year: int | None = None) -> Generator[int, None, None]:
    """
    Generate years between a start year and a target year (inclusive).

    Args:
        until: Target year to walk toward (inclusive).
        start_year: Year to start from. Defaults to the current year.

    Yields:
        int: Years from the start toward the target, moving forward or backward.
    """
    start = date.today().year if start_year is None else start_year
    yield from _walk_inclusive(start, until)


def is_leap_year(year: int) -> bool:
    """
    Check if a year is a leap year

    Args:
        year: Year to check if it is a leap year

    Returns:
        bool: True if the year is a leap year, False otherwise
    """
    return calendar.isleap(year)


##################
# Month operations
##################
def _validate_year_month(year: int, month: int) -> None:
    """Helper function to validate year and month values."""
    if isinstance(year, bool) or not isinstance(year, int) or year < 1:
        raise ValueError(f"Year must be a positive integer, got {year}")
    if isinstance(month, bool) or not isinstance(month, int) or not 1 <= month <= MONTHS_IN_YEAR:
        raise ValueError(f"Month must be between 1 and 12, got {month}")


def _month_index(year: int, month: int) -> int:
    """Return a linear index for a year/month pair."""
    return year * MONTHS_IN_YEAR + (month - 1)


def _month_from_index(index: int) -> tuple[int, int]:
    """Return a (month, year) pair from a linear month index."""
    year = index // MONTHS_IN_YEAR
    month = index % MONTHS_IN_YEAR + 1
    return month, year


def start_of_month(year: int, month: int) -> datetime:
    """
    Get the start of the month

    Args:
        year: Year to get start of month for
        month: Month to get start of (1-12)

    Returns:
        datetime: Datetime at 00:00:00

    Raises:
        ValueError: If year or month is invalid
    """
    _validate_year_month(year, month)
    return datetime(year, month, 1)


def end_of_month(year: int, month: int) -> datetime:
    """
    Get the end of the month.

    Args:
        year: Year to get end of month for
        month: Month to get end of (1-12)

    Returns:
        datetime: Datetime at 23:59:59.999999

    Raises:
        ValueError: If year or month is invalid
    """
    _validate_year_month(year, month)
    days_in_month = calendar.monthrange(year, month)[1]
    return _datetime_at_end_of_day(date(year, month, days_in_month))


def generate_months(
    until_year: int = 1970,
    until_m: int = 1,
    *,
    start_date: date | None = None,
) -> Generator[tuple[int, int], None, None]:
    """
    Generate months between a start date's month and a target month (inclusive).

    Args:
        until_year: Target year.
        until_m: Target month (1-12).
        start_date: Date providing the starting month/year. Defaults to today.

    Yields:
        tuple[int, int]: Tuples of (month, year) from start toward the target.

    Raises:
        ValueError: If until_m is not between 1 and 12
    """
    if not 1 <= until_m <= MONTHS_IN_YEAR:
        raise ValueError(f"until_m must be between 1 and 12, got {until_m}")

    anchor = _as_date(start_date) if start_date is not None else date.today()
    for idx in _walk_inclusive(_month_index(anchor.year, anchor.month), _month_index(until_year, until_m)):
        yield _month_from_index(idx)


def get_days_in_month(year: int, month: int) -> int:
    """
    Get the number of days in a specific month and year

    Args:
        year: Year to get days in month for
        month: Month to get days in (1-12)

    Returns:
        int: Number of days in the specified month

    Raises:
        ValueError: If year or month is invalid
    """
    _validate_year_month(year, month)
    return calendar.monthrange(year, month)[1]


##################
# Week operations
##################
def generate_weeks(
    count: int = 500,
    until_date: date | None = None,
    *,
    start_on_monday: bool = False,
    start_date: date | None = None,
) -> Generator[tuple[date, date], None, None]:
    """
    Generate weeks starting from a reference week and walking toward a target date.

    Args:
        count: Maximum number of weeks to generate.
        until_date: Target date that determines which direction to walk.
            If the target is before the `start_date`, weeks are generated backwards.
            If the target is after `start_date`, weeks are generated forwards.
            When `until_date` is None, weeks are generated backwards.
            Generation always stops once the week containing `until_date` has been yielded.
        start_on_monday: If True, weeks run Monday→Sunday. Otherwise they run
            Sunday→Saturday (the default).
        start_date: Date whose week should be treated as the starting point.
            Defaults to today.

    Yields:
        tuple[date, date]: Tuples of (week_start, week_end) representing the
        inclusive week range. Weeks at the representable date boundaries are
        clipped at date.min and date.max.

    Raises:
        ValueError: If `count` is negative.
    """
    if count < 0:
        raise ValueError(f"count must be >= 0, got {count}")

    if count == 0:
        return

    anchor = _as_date(start_date) if start_date is not None else date.today()
    target = _as_date(until_date) if until_date is not None else None
    desired_start = calendar.MONDAY if start_on_monday else calendar.SUNDAY
    days_since_start = (anchor.weekday() - desired_start) % 7
    week_start_ordinal = anchor.toordinal() - days_since_start
    min_ordinal = date.min.toordinal()
    max_ordinal = date.max.toordinal()

    if target is None:
        direction = -1
    else:
        direction = int(target > anchor) - int(target < anchor)

    for _ in range(count):
        week_start = date.fromordinal(max(week_start_ordinal, min_ordinal))
        week_end = date.fromordinal(min(week_start_ordinal + DAYS_IN_WEEK - 1, max_ordinal))
        yield week_start, week_end
        if direction == 0 or (target is not None and week_start <= target <= week_end):
            break
        step = -7 if direction < 0 else 7
        next_week_start_ordinal = week_start_ordinal + step
        if next_week_start_ordinal > max_ordinal or next_week_start_ordinal + DAYS_IN_WEEK - 1 < min_ordinal:
            return
        week_start_ordinal = next_week_start_ordinal


##################
# Day operations
##################


def date_range(start_date: date, end_date: date) -> list[date]:
    """
    Generate a list of dates between start_date and end_date inclusive

    Args:
        start_date: The start date (inclusive)
        end_date: The end date (inclusive)

    Returns:
        list[date]: List of dates between start_date and end_date inclusive

    Raises:
        ValueError: If start_date is after end_date or if the range is too large (>10 years)
    """
    start_date = _as_date(start_date)
    end_date = _as_date(end_date)

    if start_date > end_date:
        raise ValueError(f"start_date ({start_date}) must be <= end_date ({end_date})")

    boundary_year = start_date.year + 10
    if boundary_year > date.max.year:
        boundary = date.max
    elif start_date.month == _FEBRUARY and start_date.day == _LEAP_DAY and not calendar.isleap(boundary_year):
        boundary = date(boundary_year, 2, 28)
    else:
        boundary = date(boundary_year, start_date.month, start_date.day)

    days_diff = (end_date - start_date).days + 1
    if end_date > boundary:
        raise ValueError(f"Date range too large ({days_diff} days). Consider using a generator for large ranges.")

    return [start_date + timedelta(days=i) for i in range(days_diff)]


def date_range_generator(start_date: date, end_date: date) -> Generator[date, None, None]:
    """
    Generate dates between start_date and end_date inclusive using a generator.

    This is more memory-efficient for large date ranges than date_range().

    Args:
        start_date: The start date (inclusive)
        end_date: The end date (inclusive)

    Yields:
        date: Each date in the range

    Raises:
        ValueError: If start_date is after end_date
    """
    start_date = _as_date(start_date)
    end_date = _as_date(end_date)

    if start_date > end_date:
        raise ValueError(f"start_date ({start_date}) must be <= end_date ({end_date})")

    current = start_date
    while True:
        yield current
        if current == end_date:
            return
        current += timedelta(days=1)


##################
# Holiday operations
##################
def is_weekend(dt: date) -> bool:
    """
    Check if a date falls on a weekend (Saturday or Sunday)

    Args:
        dt: The date to check

    Returns:
        bool: True if the date falls on a weekend, False otherwise

    Examples:
        >>> from datetime import date
        >>> is_weekend(date(2024, 7, 20)) # Saturday
        True
        >>> is_weekend(date(2024, 7, 21)) # Sunday
        True
        >>> is_weekend(date(2024, 7, 22)) # Monday
        False
    """
    return _as_date(dt).weekday() >= calendar.SATURDAY  # 5 = Saturday, 6 = Sunday


def _normalize_holiday_dates(holidays: Iterable[date | datetime] | None) -> set[date]:
    """Normalize holiday values to plain date objects."""
    if holidays is None:
        return set()

    normalized: set[date] = set()
    for holiday in holidays:
        if isinstance(holiday, datetime):
            normalized.add(holiday.date())
        elif isinstance(holiday, date):
            normalized.add(holiday)
        else:
            raise TypeError(f"holidays must contain date or datetime values, got {type(holiday).__name__}")
    return normalized


def _observed_us_federal_holiday(holiday_date: date) -> date:
    """Shift weekend fixed-date holidays to their observed weekday."""
    if holiday_date.weekday() == calendar.SATURDAY:
        return holiday_date - timedelta(days=1)
    if holiday_date.weekday() == calendar.SUNDAY:
        return holiday_date + timedelta(days=1)
    return holiday_date


_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR = 1971
_MLK_DAY_FIRST_FEDERAL_YEAR = 1986
_JUNETEENTH_FIRST_FEDERAL_YEAR = 2021


class _HolidayRule(NamedTuple):
    holiday_type: str
    month: int
    day: int | None = None
    weekday: int | None = None
    occurrence: int | None = None
    from_end: bool = False
    first_year: int | None = None
    last_year: int | None = None


_US_FEDERAL_HOLIDAY_RULES: tuple[_HolidayRule, ...] = (
    _HolidayRule("NEW_YEARS_DAY", 1, day=1, first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR),
    _HolidayRule("MLK_DAY", 1, weekday=calendar.MONDAY, occurrence=3, first_year=_MLK_DAY_FIRST_FEDERAL_YEAR),
    _HolidayRule(
        "PRESIDENTS_DAY", 2, weekday=calendar.MONDAY, occurrence=3, first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR
    ),
    _HolidayRule(
        "MEMORIAL_DAY",
        5,
        weekday=calendar.MONDAY,
        occurrence=1,
        from_end=True,
        first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR,
    ),
    _HolidayRule("JUNETEENTH", 6, day=19, first_year=_JUNETEENTH_FIRST_FEDERAL_YEAR),
    _HolidayRule("INDEPENDENCE_DAY", 7, day=4, first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR),
    _HolidayRule(
        "LABOR_DAY", 9, weekday=calendar.MONDAY, occurrence=1, first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR
    ),
    _HolidayRule(
        "COLUMBUS_DAY", 10, weekday=calendar.MONDAY, occurrence=2, first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR
    ),
    _HolidayRule(
        "VETERANS_DAY",
        10,
        weekday=calendar.MONDAY,
        occurrence=4,
        first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR,
        last_year=1977,
    ),
    _HolidayRule("VETERANS_DAY", 11, day=11, first_year=1978),
    _HolidayRule(
        "THANKSGIVING", 11, weekday=calendar.THURSDAY, occurrence=4, first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR
    ),
    _HolidayRule("CHRISTMAS", 12, day=25, first_year=_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR),
)
_US_FEDERAL_HOLIDAY_TYPES = frozenset(rule.holiday_type for rule in _US_FEDERAL_HOLIDAY_RULES)


def _nth_weekday_in_month(year: int, month: int, weekday: int, n: int, *, from_end: bool = False) -> date:
    """Find the nth occurrence of a weekday in a month, optionally counting from the end."""
    if from_end:
        current = date(year, month, calendar.monthrange(year, month)[1])
        step = -1
    else:
        current = date(year, month, 1)
        step = 1

    while current.weekday() != weekday:
        current += timedelta(days=step)

    if not from_end:
        current += timedelta(days=DAYS_IN_WEEK * (n - 1))
    return current


def _date_from_holiday_rule(year: int, rule: _HolidayRule, *, observed: bool = False) -> date | None:
    """Resolve a US federal holiday rule for a year, omitting inactive historical rules."""
    if (rule.first_year is not None and year < rule.first_year) or (
        rule.last_year is not None and year > rule.last_year
    ):
        return None

    if rule.day is not None:
        holiday_date = date(year, rule.month, rule.day)
        if observed:
            return _observed_us_federal_holiday(holiday_date)
        return holiday_date

    if rule.weekday is None or rule.occurrence is None:  # pragma: no cover
        raise ValueError(f"Invalid holiday rule for {rule.holiday_type}")
    return _nth_weekday_in_month(year, rule.month, rule.weekday, rule.occurrence, from_end=rule.from_end)


def get_us_federal_holidays(
    year: int, holiday_types: tuple[str, ...] | None = None, observed: bool = False
) -> list[date]:
    """
    Get a list of US federal holidays for a given year.

    Includes:
    Fixed holidays:
    - New Year's Day (Jan 1)
    - Juneteenth National Independence Day (Jun 19; federal holiday since 2021)
    - Independence Day (Jul 4)
    - Veterans Day (Nov 11)
    - Christmas Day (Dec 25)

    Floating holidays:
    - Martin Luther King Jr. Day (3rd Monday of January)
    - Presidents Day (3rd Monday of February)
    - Memorial Day (Last Monday of May)
    - Labor Day (1st Monday of September)
    - Columbus Day (2nd Monday of October)
    - Thanksgiving Day (4th Thursday of November)

    Args:
        year: The year for which to get the holidays.
        holiday_types: Optional tuple of holiday types to include. If None, all holidays are included.
                      Historically inactive holiday types are valid but omitted for years before they existed.
                      Valid values: "NEW_YEARS_DAY", "MLK_DAY", "PRESIDENTS_DAY", "MEMORIAL_DAY",
                      "JUNETEENTH", "INDEPENDENCE_DAY", "LABOR_DAY", "COLUMBUS_DAY",
                      "VETERANS_DAY", "THANKSGIVING", "CHRISTMAS"
        observed: If True, fixed-date holidays that fall on Saturday/Sunday are shifted
            to their federally observed weekday (Friday/Monday).

    Returns:
        List[date]: A list of date objects for the holidays in that year,
        sorted in chronological order.

    Raises:
        ValueError: If `year` is before 1971 or `holiday_types` contains unknown holiday names.

    Examples:
        >>> from datetime import date
        >>> holidays_2024 = get_us_federal_holidays(2024)
        >>> date(2024, 1, 1) in holidays_2024  # New Year's Day
        True
        >>> date(2024, 11, 28) in holidays_2024  # Thanksgiving
        True

        >>> observed_2022 = get_us_federal_holidays(2022, observed=True)
        >>> date(2021, 12, 31) in observed_2022  # Observed New Year's Day 2022
        True

        >>> # Get only fixed holidays
        >>> fixed_holidays = get_us_federal_holidays(2024, ("NEW_YEARS_DAY", "JUNETEENTH",
        ...                                                "INDEPENDENCE_DAY", "VETERANS_DAY", "CHRISTMAS"))
        >>> date(2024, 1, 1) in fixed_holidays
        True
        >>> date(2024, 1, 15) in fixed_holidays  # MLK Day (floating)
        False

        >>> get_us_federal_holidays(2020, ("JUNETEENTH",))
        []

    Note:
        The returned list is a copy of the cached holiday data, so modifying it
        will not affect future calls or pollute the cache.

    Implementation Note:
        Holiday calculations are cached (LRU cache with maxsize=32) for performance.
        This cache holds up to 32 year/holiday_type/observed combinations. For
        applications that query many different years, older entries may be
        evicted. To clear the cache manually:
        ``_get_us_federal_holidays_cached.cache_clear()``

    Thread Safety:
        The LRU cache is thread-safe. Concurrent calls with the same parameters
        safely share cached results.
    """
    return list(_get_us_federal_holidays_cached(year, holiday_types, observed))


@lru_cache(maxsize=32)
def _get_us_federal_holidays_cached(
    year: int, holiday_types: tuple[str, ...] | None = None, observed: bool = False
) -> tuple[date, ...]:
    """Internal helper that stores immutable tuples for caching purposes."""
    if year < _US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR:
        raise ValueError(
            f"US federal holidays are supported from {_US_FEDERAL_HOLIDAY_FIRST_SUPPORTED_YEAR} onward, got {year}"
        )

    all_holiday_types: dict[str, date] = {}
    for rule in _US_FEDERAL_HOLIDAY_RULES:
        holiday_date = _date_from_holiday_rule(year, rule, observed=observed)
        if holiday_date is None:
            continue
        if rule.holiday_type in all_holiday_types:  # pragma: no cover
            raise AssertionError(f"Overlapping US federal holiday rules for {rule.holiday_type} in {year}")
        all_holiday_types[rule.holiday_type] = holiday_date

    # If holiday_types is None, return all holidays in chronological order
    if holiday_types is None:
        return tuple(sorted(all_holiday_types.values()))

    invalid_holiday_types = sorted(
        {holiday_type for holiday_type in holiday_types if holiday_type not in _US_FEDERAL_HOLIDAY_TYPES}
    )
    if invalid_holiday_types:
        invalid_types = ", ".join(invalid_holiday_types)
        valid_types = ", ".join(sorted(_US_FEDERAL_HOLIDAY_TYPES))
        raise ValueError(f"Invalid holiday type(s): {invalid_types}. Valid values: {valid_types}")

    # Deduplicate by date in case duplicate types are requested.
    return tuple(
        sorted({all_holiday_types[holiday_type] for holiday_type in holiday_types if holiday_type in all_holiday_types})
    )


def get_us_federal_holidays_list(
    year: int, holiday_types: list[str] | None = None, observed: bool = False
) -> list[date]:
    """
    Convenience wrapper for get_us_federal_holidays that accepts a list instead of tuple.

    This function converts the list to a tuple and calls the cached version.
    Unknown holiday types raise ValueError.

    Args:
        year: The year for which to get the holidays.
        holiday_types: Optional list of holiday type names to include.
        observed: If True, shift weekend fixed-date holidays to observed weekdays.
    """
    if holiday_types is None:
        return get_us_federal_holidays(year, None, observed)
    return get_us_federal_holidays(year, tuple(holiday_types), observed)


def workdays_between(start_date: date, end_date: date, holidays: Iterable[date | datetime] | None = None) -> int:
    """
    Count workdays (Monday-Friday) between two dates, inclusive.

    Optionally excludes specified holidays. For basic US fixed holidays, you
    can generate them using `get_us_federal_holidays()`.

    This function uses an O(1) algorithm for calculating weekdays, making it
    efficient even for very large date ranges. Holiday exclusion is O(h) where
    h is the number of unique holidays in the range.

    Args:
        start_date: The start date (inclusive).
        end_date: The end date (inclusive).
        holidays: Optional collection of holiday dates/datetimes to exclude
            (list, set, tuple, generator, etc.). Duplicates are automatically
            handled.

    Warning:
        **Generators are consumed on first use.** If you need to call this function
        multiple times with the same holidays, convert to a list first::

            holidays = list(my_holiday_generator())
            workdays_between(start1, end1, holidays)  # Works
            workdays_between(start2, end2, holidays)  # Also works

    Returns:
        int: Number of workdays between the start and end dates.

    Raises:
        ValueError: If start_date is after end_date
        TypeError: If `holidays` contains values that are not date/datetime

    Examples:
        >>> from datetime import date
        >>> start = date(2024, 7, 1)  # Monday
        >>> end = date(2024, 7, 7)    # Sunday
        >>> workdays_between(start, end)  # Mon, Tue, Wed, Thu, Fri
        5

        >>> # Using built-in US fixed holidays for 2024
        >>> us_holidays = get_us_federal_holidays(2024)
        >>> workdays_between(start, end, holidays=us_holidays)  # July 4th is excluded
        4

        >>> start = date(2024, 12, 23)
        >>> end = date(2024, 12, 27)
        >>> workdays_between(start, end, holidays=get_us_federal_holidays(2024))  # Excludes Dec 25
        4

        >>> # Efficient for large ranges
        >>> start = date(2000, 1, 1)
        >>> end = date(2024, 12, 31)
        >>> workdays_between(start, end)  # ~25 years, computed in O(1)
        6522
    """
    start_date = _as_date(start_date)
    end_date = _as_date(end_date)

    if start_date > end_date:
        raise ValueError(f"start_date ({start_date}) must be <= end_date ({end_date})")

    # Calculate total days (inclusive)
    total_days = (end_date - start_date).days + 1

    # Calculate workdays using O(1) formula
    # Full weeks contribute 5 workdays each
    full_weeks = total_days // DAYS_IN_WEEK
    remaining_days = total_days % DAYS_IN_WEEK

    # Count weekdays in the remaining partial week
    # Start from start_date's weekday and count how many of the remaining days are weekdays
    start_weekday = start_date.weekday()  # 0=Monday, 6=Sunday
    partial_weekdays = 0
    for i in range(remaining_days):
        day_of_week = (start_weekday + i) % DAYS_IN_WEEK
        if day_of_week < WEEKDAYS_IN_WEEK:  # Monday-Friday (0-4)
            partial_weekdays += 1

    workdays = full_weeks * WEEKDAYS_IN_WEEK + partial_weekdays

    # Subtract holidays that fall on weekdays within the range
    # Convert to set to handle duplicates and consume generators safely
    if holidays is not None:
        holidays_set = _normalize_holiday_dates(holidays)
        for holiday in holidays_set:
            if start_date <= holiday <= end_date and holiday.weekday() < WEEKDAYS_IN_WEEK:
                workdays -= 1

    return workdays


def add_business_days(dt: date, num_days: int, holidays: Iterable[date | datetime] | None = None) -> date:
    """
    Add business days to a date, skipping weekends and holidays.

    For basic US holidays, you can generate them using
    `get_us_federal_holidays()`.

    Args:
        dt: The starting date.
        num_days: Number of business days to add (can be negative).
        holidays: Optional collection of holiday dates/datetimes to skip (list,
            set, tuple, etc.).
            Using a set provides O(1) lookup performance for large holiday lists.
            **Note:** Generators are consumed on first use.

    Returns:
        A new date with the business days added.

    Raises:
        ValueError: If num_days is extremely large (> 10000 or < -10000)
        TypeError: If `holidays` contains values that are not date/datetime

    Examples:
        >>> from datetime import date
        >>> start_date = date(2024, 7, 1)  # Monday
        >>> add_business_days(start_date, 3)
        datetime.date(2024, 7, 4)

        >>> # Skip July 4th holiday
        >>> us_holidays = get_us_federal_holidays(2024)
        >>> add_business_days(start_date, 3, holidays=us_holidays)
        datetime.date(2024, 7, 5)

        >>> # Add negative days
        >>> end_date = date(2024, 7, 8)  # Monday
        >>> add_business_days(end_date, -2)
        datetime.date(2024, 7, 4)

        >>> # Add negative days skipping holiday
        >>> add_business_days(end_date, -2, holidays=us_holidays)
        datetime.date(2024, 7, 3)
    """
    dt = _as_date(dt)

    if not -10000 <= num_days <= 10000:  # noqa: PLR2004
        raise ValueError(f"num_days must be between -10000 and 10000, got {num_days}")

    if num_days == 0:
        return dt

    if holidays is None or (isinstance(holidays, (set, frozenset, list, tuple)) and len(holidays) == 0):
        return _add_business_days_no_holidays(dt, num_days)

    holidays_set = _normalize_holiday_dates(holidays)
    if not holidays_set:
        return _add_business_days_no_holidays(dt, num_days)

    current = dt
    added = 0
    days_to_add = 1 if num_days >= 0 else -1

    while added < abs(num_days):
        current += timedelta(days=days_to_add)
        if current.weekday() < calendar.SATURDAY and current not in holidays_set:  # Weekday and not a holiday
            added += 1

    return current


def _add_business_days_no_holidays(dt: date, num_days: int) -> date:
    """Fast path for add_business_days when there are no holidays."""
    direction = 1 if num_days > 0 else -1
    remaining = abs(num_days)
    dt, weekday = _normalize_business_day_start(dt, direction)
    days = _business_days_to_calendar_days(weekday, remaining, direction)
    return dt + timedelta(days=days * direction)


def _normalize_business_day_start(dt: date, direction: int) -> tuple[date, int]:
    """Normalize weekend start dates for business-day arithmetic."""
    weekday = dt.weekday()
    if direction > 0:
        if weekday == calendar.SATURDAY:
            dt -= timedelta(days=1)
            weekday = calendar.FRIDAY
        elif weekday == calendar.SUNDAY:
            dt -= timedelta(days=2)
            weekday = calendar.FRIDAY
        return dt, weekday

    if weekday == calendar.SATURDAY:
        dt += timedelta(days=2)
        weekday = calendar.MONDAY
    elif weekday == calendar.SUNDAY:
        dt += timedelta(days=1)
        weekday = calendar.MONDAY
    return dt, weekday


def _business_days_to_calendar_days(weekday: int, remaining: int, direction: int) -> int:
    """Convert a business-day count into calendar days, excluding holidays."""
    weeks, extra = divmod(remaining, WEEKDAYS_IN_WEEK)
    days = weeks * DAYS_IN_WEEK
    if extra:
        if direction > 0:
            days += extra + 2 if weekday + extra >= WEEKDAYS_IN_WEEK else extra
        else:
            days += extra + 2 if weekday - extra < 0 else extra
    return days


def next_business_day(dt: date, holidays: Iterable[date | datetime] | None = None) -> date:
    """
    Find the next business day from a given date, skipping weekends and holidays.

    For basic US fixed holidays, you can generate them using
    `get_us_federal_holidays()`.

    Args:
        dt: The starting date.
        holidays: Optional collection of holiday dates to skip (list, set, tuple, etc.).
            Using a set provides O(1) lookup performance for large holiday lists.

    Returns:
        The next business day.

    Examples:
        >>> from datetime import date
        >>> friday = date(2024, 7, 5)
        >>> next_business_day(friday)  # Monday
        datetime.date(2024, 7, 8)

        >>> wednesday = date(2024, 7, 3)
        >>> # July 4th is a holiday
        >>> us_holidays = get_us_federal_holidays(2024)
        >>> next_business_day(wednesday, holidays=us_holidays)  # Friday
        datetime.date(2024, 7, 5)
    """
    return add_business_days(dt, 1, holidays)


def previous_business_day(dt: date, holidays: Iterable[date | datetime] | None = None) -> date:
    """
    Find the previous business day from a given date, skipping weekends and holidays.

    For basic US fixed holidays, you can generate them using
    `get_us_federal_holidays()`.

    Args:
        dt: The starting date.
        holidays: Optional collection of holiday dates to skip (list, set, tuple, etc.).
            Using a set provides O(1) lookup performance for large holiday lists.

    Returns:
        The previous business day.

    Examples:
        >>> from datetime import date
        >>> monday = date(2024, 7, 8)
        >>> previous_business_day(monday)  # Friday
        datetime.date(2024, 7, 5)

        >>> friday = date(2024, 7, 5)
        >>> # July 4th is a holiday
        >>> us_holidays = get_us_federal_holidays(2024)
        >>> previous_business_day(friday, holidays=us_holidays)  # Wednesday
        datetime.date(2024, 7, 3)
    """
    return add_business_days(dt, -1, holidays)


def _ts_difference(timestamp: int | datetime | None = None, now_override: int | None = None) -> timedelta:
    """Helper function to calculate time difference for pretty_date."""
    if now_override is not None:
        try:
            now = datetime.fromtimestamp(now_override, tz=timezone.utc)
        except (ValueError, OSError, OverflowError) as e:
            raise ValueError(f"Invalid now_override timestamp: {now_override}") from e
    else:
        now = datetime.now(timezone.utc)

    if timestamp is None:
        return timedelta(0)
    if isinstance(timestamp, int):
        try:
            ts_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, OSError, OverflowError) as e:
            raise ValueError(f"Invalid timestamp: {timestamp}") from e
        return now - ts_dt
    if isinstance(timestamp, datetime):
        # Assume UTC for datetimes without a usable offset (matches epoch_s).
        return now - datetime_to_utc(timestamp)
    # Runtime callers may still violate type hints.
    raise TypeError(f"timestamp must be int, datetime, or None; got {type(timestamp).__name__}")  # pragma: no cover


def _format_relative_count(count: int, unit: str, *, future: bool) -> str:
    """Format relative count/unit text for future or past expressions."""
    unit_label = unit if count == 1 else f"{unit}s"
    if future:
        return f"in {count} {unit_label}"
    return f"{count} {unit_label} ago"


def _format_relative_within_day(second_diff: int, *, future: bool) -> str:
    """Format relative text for differences smaller than one day."""
    if second_diff < RECENT_SECONDS:
        return "just now"
    if second_diff < SECONDS_IN_MINUTE:
        return _format_relative_count(second_diff, "second", future=future)
    if second_diff < 2 * SECONDS_IN_MINUTE:
        return "in a minute" if future else "a minute ago"
    if second_diff < SECONDS_IN_HOUR:
        return _format_relative_count(second_diff // SECONDS_IN_MINUTE, "minute", future=future)
    if second_diff < 2 * SECONDS_IN_HOUR:
        return "in an hour" if future else "an hour ago"
    # second_diff is < 1 day in this helper.
    return _format_relative_count(second_diff // SECONDS_IN_HOUR, "hour", future=future)


def _format_relative_day_or_longer(day_diff: int, *, future: bool) -> str:
    """Format relative text for differences of one day or longer."""
    if day_diff == 1:
        return "Tomorrow" if future else "Yesterday"
    if day_diff < DAYS_IN_WEEK:
        return _format_relative_count(day_diff, "day", future=future)
    if day_diff < DAYS_IN_MONTH_MAX:
        return _format_relative_count(day_diff // DAYS_IN_WEEK, "week", future=future)
    if day_diff < DAYS_IN_YEAR:
        return _format_relative_count(day_diff // DAYS_IN_MONTH_APPROX, "month", future=future)
    return _format_relative_count(day_diff // DAYS_IN_YEAR, "year", future=future)


def pretty_date(timestamp: int | datetime | None = None, now_override: int | None = None) -> str:
    """
    Format a timestamp as a human-readable relative time string.

    Supports both past times ("2 hours ago", "Yesterday") and future times
    ("in 2 hours", "Tomorrow"). The output is designed to be user-friendly
    and uses natural language approximations.

    Args:
        timestamp: The time to format. Accepts three types:
            - int: Unix timestamp (seconds since epoch). Interpreted as UTC.
            - datetime: A datetime object. If it has no usable UTC offset, it is
              assumed to be UTC. Otherwise it is converted to UTC for comparison.
            - None: Returns "just now".
        now_override: Optional Unix timestamp to use as the reference "now" time.
            Primarily useful for testing to ensure deterministic output.

    Returns:
        str: Human-readable relative time string. Possible formats include:
            - "just now" (within 10 seconds)
            - "X seconds ago" / "in X seconds"
            - "a minute ago" / "in a minute"
            - "X minutes ago" / "in X minutes"
            - "an hour ago" / "in an hour"
            - "X hours ago" / "in X hours"
            - "Yesterday" / "Tomorrow"
            - "X days ago" / "in X days"
            - "X weeks ago" / "in X weeks"
            - "X months ago" / "in X months"
            - "X years ago" / "in X years"

    Raises:
        ValueError: If `timestamp` or `now_override` is an invalid Unix timestamp.
        TypeError: If `timestamp` is not an int, datetime, or None.

    Examples:
        >>> from datetime import datetime, timezone
        >>> # Use now_override for deterministic testing
        >>> now_ts = 1711540800  # 2024-03-27 12:00:00 UTC

        >>> # Using a datetime object (timezone-aware)
        >>> pretty_date(datetime(2024, 3, 27, 11, 59, 30, tzinfo=timezone.utc), now_ts)
        '30 seconds ago'
        >>> pretty_date(datetime(2024, 3, 27, 10, 0, 0, tzinfo=timezone.utc), now_ts)
        '2 hours ago'

        >>> # Future dates
        >>> pretty_date(datetime(2024, 3, 27, 14, 0, 0, tzinfo=timezone.utc), now_ts)
        'in 2 hours'
        >>> pretty_date(datetime(2024, 3, 28, 12, 0, 0, tzinfo=timezone.utc), now_ts)
        'Tomorrow'

        >>> # Using a Unix timestamp (int)
        >>> pretty_date(1711540770, now_ts)  # 30 seconds before now_ts
        '30 seconds ago'

        >>> # Using None returns "just now"
        >>> pretty_date(None, now_ts)
        'just now'

    Note:
        The function uses **approximate values** for longer periods:

        - 1 month = 30 days (actual months vary 28-31 days)
        - 1 year = 365 days (ignores leap years)

        This means "2 months ago" represents exactly 60 days ago, regardless of
        which calendar months were involved. This is intentional for human-readable
        output where precision is less important than readability.
    """
    diff = _ts_difference(timestamp, now_override)
    total_seconds = diff.total_seconds()

    future = total_seconds < 0
    if future:
        total_seconds = abs(total_seconds)
        day_diff = int(total_seconds // SECONDS_IN_DAY)
        second_diff = int(total_seconds % SECONDS_IN_DAY)
    else:
        day_diff = diff.days
        second_diff = diff.seconds

    if day_diff == 0:
        return _format_relative_within_day(second_diff, future=future)
    return _format_relative_day_or_longer(day_diff, future=future)


def httpdate(date_time: datetime) -> str:
    """
    Convert a datetime object to an HTTP date string (RFC 7231 compliant).

    The output is always in GMT/UTC as required by RFC 7231. Datetimes with a
    usable UTC offset are converted to UTC before formatting. Other datetimes
    are assumed to already be in UTC. The formatting uses
    `email.utils.format_datetime` to avoid locale-dependent weekday/month names.

    Args:
        date_time: The datetime to format. If it has no usable UTC offset,
            assumed to be UTC.

    Returns:
        str: HTTP date string in format "Day, DD Mon YYYY HH:MM:SS GMT"

    Examples:
        >>> from datetime import datetime, timezone
        >>> dt_utc = datetime(2024, 7, 22, 14, 30, 0, tzinfo=timezone.utc)
        >>> httpdate(dt_utc)
        'Mon, 22 Jul 2024 14:30:00 GMT'

        >>> # Non-UTC timezone is converted to UTC
        >>> from zoneinfo import ZoneInfo
        >>> dt_ny = datetime(2024, 7, 22, 10, 30, 0, tzinfo=ZoneInfo("America/New_York"))
        >>> httpdate(dt_ny)  # 10:30 EDT = 14:30 UTC
        'Mon, 22 Jul 2024 14:30:00 GMT'
    """
    # Assume UTC for datetimes without a usable offset; convert aware values so
    # the GMT output is consistent.
    return _format_http_datetime(datetime_to_utc(date_time), usegmt=True)


##################
# Parsing, formatting, and timezone operations were moved into
# dedicated modules and are re-exported near the constants section.
##################


##################
# Additional utility functions
##################
def is_business_day(dt: date, holidays: Iterable[date | datetime] | None = None) -> bool:
    """
    Check if a date is a business day (not weekend or holiday).

    Args:
        dt: Date to check
        holidays: Optional collection of holiday dates/datetimes (list, set,
            tuple, generator, etc.). Generators will be consumed. Internally
            converted to a set for O(1) lookup.

    Returns:
        bool: True if the date is a business day, False otherwise

    Examples:
        >>> from datetime import date
        >>> is_business_day(date(2024, 7, 22))  # Monday
        True
        >>> is_business_day(date(2024, 7, 27))  # Saturday
        False
        >>> # Using a set for efficient lookup
        >>> holiday_set = {date(2024, 7, 4), date(2024, 12, 25)}
        >>> is_business_day(date(2024, 7, 4), holidays=holiday_set)
        False
    """
    dt = _as_date(dt)
    if dt.weekday() >= calendar.SATURDAY:
        return False
    if holidays is None:
        return True
    # Convert to set to handle generators and ensure O(1) lookup
    holidays_set = _normalize_holiday_dates(holidays)
    return dt not in holidays_set


def days_until_weekend(dt: date) -> int:
    """
    Get the number of days until the next weekend.

    Args:
        dt: Date to check from

    Returns:
        int: Number of days until Saturday (0 if already weekend)
    """
    dt = _as_date(dt)
    if dt.weekday() >= calendar.SATURDAY:  # Already weekend
        return 0
    return calendar.SATURDAY - dt.weekday()


def days_since_weekend(dt: date) -> int:
    """
    Get the number of days since the last weekend ended.

    Args:
        dt: Date to check from

    Returns:
        int: Number of days since Sunday (0 if currently weekend)
    """
    dt = _as_date(dt)
    if dt.weekday() >= calendar.SATURDAY:  # Currently weekend
        return 0
    return dt.weekday() + 1  # Monday = 1 day since Sunday


def get_week_number(dt: date) -> int:
    """
    Get the ISO week number for a date.

    Args:
        dt: Date to get week number for

    Returns:
        int: ISO week number (1-53)
    """
    return _as_date(dt).isocalendar()[1]


def get_quarter_start_end(year: int, quarter: int) -> tuple[date, date]:
    """
    Get the start and end dates for a quarter.

    Args:
        year: Year
        quarter: Quarter (1-4)

    Returns:
        tuple[date, date]: Start and end dates of the quarter

    Raises:
        ValueError: If quarter is not between 1 and 4
    """
    _validate_quarter(quarter)

    start = start_of_quarter(year, quarter).date()
    end = end_of_quarter(year, quarter).date()
    return start, end


def age_in_years(birth_date: date, as_of_date: date | None = None) -> int:
    """
    Calculate age in years.

    For leap year birthdays (Feb 29), the birthday is considered to fall on
    Feb 28 in non-leap years.

    Args:
        birth_date: Date of birth
        as_of_date: Date to calculate age as of (defaults to today)

    Returns:
        int: Age in years

    Raises:
        ValueError: If birth_date is in the future
    """
    birth_date = _as_date(birth_date)
    if as_of_date is None:
        as_of_date = date.today()
    else:
        as_of_date = _as_date(as_of_date)

    if birth_date > as_of_date:
        raise ValueError("Birth date cannot be in the future")

    years = as_of_date.year - birth_date.year

    # Handle leap year birthday edge case
    birth_month, birth_day = birth_date.month, birth_date.day
    if birth_month == _FEBRUARY and birth_day == _LEAP_DAY and not calendar.isleap(as_of_date.year):
        # In non-leap years, treat Feb 29 birthday as Feb 28
        birth_day = _FEB_28

    # Adjust if birthday hasn't occurred yet this year
    if (as_of_date.month, as_of_date.day) < (birth_month, birth_day):
        years -= 1

    return years


def _round_trip_through_utc(occurrence: datetime) -> datetime:
    """Normalize an aware local datetime by converting through the UTC timeline."""
    return occurrence.astimezone(timezone.utc).astimezone(occurrence.tzinfo)


def _matches_requested_occurrence(normalized: datetime, local_date: date, target_time_of_day: time) -> bool:
    """Return whether normalization preserved the requested local date and time-of-day."""
    return (
        normalized.date() == local_date
        and normalized.hour == target_time_of_day.hour
        and normalized.minute == target_time_of_day.minute
        and normalized.second == target_time_of_day.second
        and normalized.microsecond == target_time_of_day.microsecond
    )


def _aware_occurrence_on_date(local_date: date, target_time_of_day: time) -> datetime:
    """
    Build the aware occurrence for a local date, applying the library's DST policy.

    Nonexistent spring-forward target times roll forward to the next valid local
    time. Ambiguous fall-back target times honor `target_time_of_day.fold`.
    """
    candidate = datetime.combine(local_date, target_time_of_day)
    normalized = _round_trip_through_utc(candidate)

    if not _matches_requested_occurrence(normalized, local_date, target_time_of_day):
        normalized = _round_trip_through_utc(candidate.replace(fold=0))

    return normalized


def _normalized_target_time_of_day(target_time: datetime | time, reference_date: date) -> time:
    """Return a target time whose timezone is usable on the reference date."""
    target_time_of_day = target_time.timetz() if isinstance(target_time, datetime) else target_time
    if isinstance(target_time, datetime) and not _is_aware_datetime(target_time):
        target_time_of_day = target_time_of_day.replace(tzinfo=None)
    if target_time_of_day.tzinfo is not None and not _is_aware_datetime(
        datetime.combine(reference_date, target_time_of_day)
    ):
        return target_time_of_day.replace(tzinfo=None)
    return target_time_of_day


def _next_occurrence_details(target_time: datetime | time, from_time: datetime | None) -> tuple[datetime, datetime]:
    """Return the next occurrence and its reference point on the UTC timeline when aware."""
    if from_time is not None and not _is_aware_datetime(from_time):
        from_time = from_time.replace(tzinfo=None)

    reference_date = from_time.date() if from_time is not None else datetime.now().date()
    target_time_of_day = _normalized_target_time_of_day(target_time, reference_date)

    if from_time is None:
        if target_time_of_day.tzinfo is not None:
            from_time = datetime.now(target_time_of_day.tzinfo)
        else:
            from_time = datetime.now()

    # Ensure both have the same timezone handling.
    if target_time_of_day.tzinfo is None and from_time.tzinfo is not None:
        target_time_of_day = target_time_of_day.replace(tzinfo=from_time.tzinfo)
    elif target_time_of_day.tzinfo is not None and from_time.tzinfo is None:
        from_time = from_time.replace(tzinfo=target_time_of_day.tzinfo)

    from_time_in_target_tz = (
        from_time.astimezone(target_time_of_day.tzinfo) if target_time_of_day.tzinfo is not None else from_time
    )

    if target_time_of_day.tzinfo is not None:
        from_time_utc = from_time_in_target_tz.astimezone(timezone.utc)
        candidate_date = from_time_in_target_tz.date()
        occurrence = _aware_occurrence_on_date(candidate_date, target_time_of_day)

        if occurrence.astimezone(timezone.utc) <= from_time_utc:
            occurrence = _aware_occurrence_on_date(candidate_date + timedelta(days=1), target_time_of_day)

        return occurrence, from_time_utc

    occurrence = datetime.combine(from_time_in_target_tz.date(), target_time_of_day)
    if occurrence <= from_time_in_target_tz:
        occurrence += timedelta(days=1)

    return occurrence, from_time_in_target_tz


def next_occurrence(target_time: datetime | time, from_time: datetime | None = None) -> datetime:
    """
    Return the next daily occurrence of a specific time-of-day.

    The date portion of a datetime target is ignored. The returned datetime is
    strictly after `from_time` (or the current time when omitted). Naive inputs
    produce a naive result; aware inputs produce an occurrence in the target
    timezone. When only one input is aware, the naive input is interpreted in
    the aware input's timezone.

    For aware times, nonexistent spring-forward times roll forward to the next
    valid local time. Ambiguous fall-back times honor `target_time.fold`.

    Args:
        target_time: A datetime or time whose time-of-day represents the target.
        from_time: The reference datetime. Defaults to the current time in the
            target timezone, or local time for naive targets.

    Returns:
        datetime: The next occurrence of the target time-of-day.
    """
    occurrence, _ = _next_occurrence_details(target_time, from_time)
    return occurrence


def time_until_next_occurrence(target_time: datetime | time, from_time: datetime | None = None) -> timedelta:
    """
    Calculate the time remaining until the next daily occurrence of a specific time-of-day.

    This function extracts the time-of-day (hour, minute, second, microsecond) from
    `target_time` and calculates how long until that time occurs next, relative to
    `from_time`. If `target_time` is a datetime, its date portion is ignored - only
    the time-of-day matters.

    This is useful for scheduling scenarios like "how long until 3:00 PM?" or
    "time remaining until the daily backup at 02:00".

    Args:
        target_time: A datetime or time whose time-of-day (HH:MM:SS) represents
            the target. If a datetime is provided, the date portion is ignored. Can
            be timezone-aware or naive.
        from_time: The reference datetime to calculate from. Defaults to the current
            time in `target_time`'s timezone (or local time if `target_time` is naive).

    Returns:
        timedelta: Duration until the next occurrence of the target time-of-day.
            Always positive (0 < result <= 24 hours).

    Timezone Handling:
        - If both datetimes have the same timezone handling (both aware or both naive),
          they are compared directly.
        - If only one has timezone info, the naive datetime is treated as being in
          the same timezone as the aware datetime (using `replace`, not `astimezone`).
          This means no conversion is performed - the naive time is assumed to already
          represent that timezone.
        - For timezone-aware datetimes, DST transitions are normalized before
          comparison. Spring-forward gap times roll forward to the next valid
          local time, and fall-back ambiguous times honor `target_time.fold`
          (`fold=0` for the first occurrence, `fold=1` for the second).

    Examples:
        >>> from datetime import datetime, timezone, timedelta

        >>> # How long until 3:00 PM UTC from 2:30 PM UTC?
        >>> target = datetime(2024, 1, 1, 15, 0, 0, tzinfo=timezone.utc)  # 3:00 PM
        >>> from_dt = datetime(2024, 1, 1, 14, 30, 0, tzinfo=timezone.utc)  # 2:30 PM
        >>> time_until_next_occurrence(target, from_dt)
        datetime.timedelta(seconds=1800)

        >>> # If the target time has already passed today, returns time until tomorrow
        >>> from_dt = datetime(2024, 1, 1, 16, 0, 0, tzinfo=timezone.utc)  # 4:00 PM
        >>> delta = time_until_next_occurrence(target, from_dt)  # Next 3:00 PM is tomorrow
        >>> delta.total_seconds()
        82800.0

        >>> # Useful for scheduling: "How long until the daily 2 AM job runs?"
        >>> job_time = datetime(2024, 1, 1, 2, 0, 0, tzinfo=timezone.utc)
        >>> delta = time_until_next_occurrence(job_time)  # Uses current time as reference
    """
    occurrence, reference_time = _next_occurrence_details(target_time, from_time)
    if occurrence.tzinfo is not None:
        return occurrence.astimezone(timezone.utc) - reference_time
    return occurrence - reference_time
