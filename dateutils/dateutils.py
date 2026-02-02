"""
Date and time utilities for Python applications.

This module provides a comprehensive set of utilities for working with dates, times,
and timezones in Python. It includes functions for:

- UTC date/time operations
- Quarter, month, week, and day operations
- Business day calculations (including basic US fixed holiday support)
- Date/time parsing and formatting
- Timezone conversions
- Human-readable date formatting

The utilities aim to simplify common date and time operations while providing
consistent handling of timezone information.

**Note on Holidays:** Basic support for fixed US federal holidays is included
via `get_us_federal_holidays()`. For comprehensive, region-specific,
or rule-based holiday calculations (e.g., floating holidays like Easter,
observed holidays falling on weekends), consider using a dedicated library
like `holidays`. You can easily integrate it by generating a list of holiday
dates from that library and passing it to the `holidays` argument of the
relevant business day functions in this module.

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
import re
from collections.abc import Generator, Iterable
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime as _format_http_datetime
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

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

# Compiled regex for ISO 8601 parsing (verbose mode for readability)
_ISO8601_PATTERN = re.compile(
    r"""
    ^
    (\d{4}-\d{2}-\d{2})           # Date part: YYYY-MM-DD (required)
    (?:
        T(\d{2}:\d{2}:\d{2})      # Time part: THH:MM:SS (optional)
    )?
    (\.\d+)?                       # Fractional seconds: .123456 (optional)
    (Z | [+-]\d{2}:?\d{2})?        # Timezone: Z or ±HH:MM or ±HHMM (optional)
    $
    """,
    re.VERBOSE,
)


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
    Convert a datetime object to a Unix timestamp (seconds since epoch).

    Note: Timezone-aware datetimes are converted to UTC before calculating
          the timestamp. Naive datetimes are assumed to be in UTC.

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
    if dt.tzinfo is None:
        # Assume naive datetime is in UTC (documented behavior)
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def datetime_start_of_day(day: date) -> datetime:
    """
    Get the start of the day for a specific date.

    Args:
        day: Date to get start of day for

    Returns:
        datetime: Datetime at midnight (00:00:00)
    """
    return datetime.combine(day, datetime.min.time())


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
    return datetime_start_of_day(day) + timedelta(days=1) - timedelta(microseconds=1)


##################
# Quarter operations
##################
def date_to_quarter(dt: date) -> int:
    """
    Get the quarter of the year for a specific date

    Args:
        dt: Date to get quarter for

    Returns:
        int: Quarter of the year (1-4)
    """
    return ((dt.month - 1) // 3) + 1


def date_to_start_of_quarter(dt: date) -> date:
    """
    Get the start of the quarter for a specific date

    Args:
        dt: Date to get start of quarter for

    Returns:
        date: Date at the start of the quarter
    """
    new_month = (((dt.month - 1) // 3) * 3) + 1
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
    if not 1 <= q <= QUARTERS_IN_YEAR:
        raise ValueError(f"Quarter must be between 1 and 4, got {q}")
    return datetime(year, (q - 1) * 3 + 1, 1)


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
    if not 1 <= q <= QUARTERS_IN_YEAR:
        raise ValueError(f"Quarter must be between 1 and 4, got {q}")
    # Calculate the month at the end of the quarter
    month = q * 3
    # Get the last day of that month
    days_in_month = calendar.monthrange(year, month)[1]
    return datetime(year, month, days_in_month, 23, 59, 59, 999999)


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
    if not 1 <= until_q <= QUARTERS_IN_YEAR:
        raise ValueError(f"until_q must be between 1 and 4, got {until_q}")

    today = date.today()
    start_y = start_year or today.year
    start_q = start_quarter or date_to_quarter(today)

    if not 1 <= start_q <= QUARTERS_IN_YEAR:
        raise ValueError(f"start_quarter must be between 1 and 4, got {start_q}")

    start_idx = start_y * QUARTERS_IN_YEAR + (start_q - 1)
    target_idx = until_year * QUARTERS_IN_YEAR + (until_q - 1)

    def _idx_to_tuple(idx: int) -> tuple[int, int]:
        year = idx // QUARTERS_IN_YEAR
        quarter = idx % QUARTERS_IN_YEAR + 1
        return quarter, year

    direction = 0
    if target_idx > start_idx:
        direction = 1
    elif target_idx < start_idx:
        direction = -1

    idx = start_idx
    yield _idx_to_tuple(idx)
    if idx == target_idx:
        return

    step = 1 if direction > 0 else -1
    while idx != target_idx:
        idx += step
        yield _idx_to_tuple(idx)


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
    return datetime(year, 12, 31, 23, 59, 59, 999999)


def generate_years(until: int = 1970, *, start_year: int | None = None) -> Generator[int, None, None]:
    """
    Generate years between a start year and a target year (inclusive).

    Args:
        until: Target year to walk toward (inclusive).
        start_year: Year to start from. Defaults to the current year.

    Yields:
        int: Years from the start toward the target, moving forward or backward.
    """
    start = start_year or date.today().year
    current = start
    yield current
    if current == until:
        return

    step = 1 if until > start else -1
    while current != until:
        current += step
        yield current


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
    if not isinstance(year, int) or year < 1:
        raise ValueError(f"Year must be a positive integer, got {year}")
    if not isinstance(month, int) or not 1 <= month <= MONTHS_IN_YEAR:
        raise ValueError(f"Month must be between 1 and 12, got {month}")


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
    return datetime(year, month, days_in_month, 23, 59, 59, 999999)


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

    anchor = start_date or date.today()
    current_idx = anchor.year * 12 + (anchor.month - 1)
    target_idx = until_year * 12 + (until_m - 1)

    def _idx_to_tuple(idx: int) -> tuple[int, int]:
        year = idx // 12
        month = idx % 12 + 1
        return month, year

    direction = 0
    if target_idx > current_idx:
        direction = 1
    elif target_idx < current_idx:
        direction = -1

    yield _idx_to_tuple(current_idx)
    if current_idx == target_idx:
        return

    step = 1 if direction > 0 else -1
    while current_idx != target_idx:
        current_idx += step
        yield _idx_to_tuple(current_idx)


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
        inclusive week range.
    """

    def _week_start(today: date) -> date:
        desired_start = calendar.MONDAY if start_on_monday else calendar.SUNDAY
        days_since_start = (today.weekday() - desired_start) % 7
        return today - timedelta(days=days_since_start)

    anchor = start_date or date.today()
    week_start = _week_start(anchor)

    if until_date is None:
        direction = -1
    elif until_date > anchor:
        direction = 1
    elif until_date < anchor:
        direction = -1
    else:
        direction = 0

    for _ in range(count):
        week_end = week_start + timedelta(days=6)
        if until_date is not None:
            if direction > 0 and week_start > until_date:
                break
            if direction < 0 and week_end < until_date:
                break
        yield week_start, week_end
        if direction == 0:
            break
        step = -7 if direction < 0 else 7
        week_start += timedelta(days=step)


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
    if start_date > end_date:
        raise ValueError(f"start_date ({start_date}) must be <= end_date ({end_date})")

    days_diff = (end_date - start_date).days + 1
    if days_diff > (10 * DAYS_IN_YEAR):
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
    if start_date > end_date:
        raise ValueError(f"start_date ({start_date}) must be <= end_date ({end_date})")

    current = start_date
    while current <= end_date:
        yield current
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
    return dt.weekday() >= calendar.SATURDAY  # 5 = Saturday, 6 = Sunday


def get_us_federal_holidays(year: int, holiday_types: tuple[str, ...] | None = None) -> list[date]:
    """
    Get a list of US federal holidays for a given year.

    Includes:
    Fixed holidays:
    - New Year's Day (Jan 1)
    - Juneteenth National Independence Day (Jun 19)
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

    Note: This function returns the *actual* date of the holiday. It does *not*
    account for the observed date when the holiday falls on a weekend
    (e.g., observed on Mon/Fri). For observed holiday calculation, use a dedicated
    library like `holidays`.

    Args:
        year: The year for which to get the holidays.
        holiday_types: Optional tuple of holiday types to include. If None, all holidays are included.
                      Valid values: "NEW_YEARS_DAY", "MLK_DAY", "PRESIDENTS_DAY", "MEMORIAL_DAY",
                      "JUNETEENTH", "INDEPENDENCE_DAY", "LABOR_DAY", "COLUMBUS_DAY",
                      "VETERANS_DAY", "THANKSGIVING", "CHRISTMAS"

    Returns:
        List[date]: A list of date objects for the holidays in that year,
        sorted in chronological order.

    Examples:
        >>> from datetime import date
        >>> holidays_2024 = get_us_federal_holidays(2024)
        >>> date(2024, 1, 1) in holidays_2024  # New Year's Day
        True
        >>> date(2024, 11, 28) in holidays_2024  # Thanksgiving
        True

        >>> # Get only fixed holidays
        >>> fixed_holidays = get_us_federal_holidays(2024, ("NEW_YEARS_DAY", "JUNETEENTH",
        ...                                                "INDEPENDENCE_DAY", "VETERANS_DAY", "CHRISTMAS"))
        >>> date(2024, 1, 1) in fixed_holidays
        True
        >>> date(2024, 1, 15) in fixed_holidays  # MLK Day (floating)
        False
    Note:
        The returned list is a copy of the cached holiday data, so modifying it
        will not affect future calls or pollute the cache.

    Implementation Note:
        Holiday calculations are cached (LRU cache with maxsize=32) for performance.
        This cache holds up to 32 year/holiday_type combinations. For applications
        that query many different years, older entries may be evicted. To clear the
        cache manually: ``_get_us_federal_holidays_cached.cache_clear()``

    Thread Safety:
        The LRU cache is thread-safe. Concurrent calls with the same parameters
        safely share cached results.
    """
    return list(_get_us_federal_holidays_cached(year, holiday_types))


@lru_cache(maxsize=32)
def _get_us_federal_holidays_cached(year: int, holiday_types: tuple[str, ...] | None = None) -> tuple[date, ...]:
    """Internal helper that stores immutable tuples for caching purposes."""
    # Define all possible holiday types
    all_holiday_types: dict[str, date] = {
        # Fixed holidays
        "NEW_YEARS_DAY": date(year, 1, 1),
        "JUNETEENTH": date(year, 6, 19),
        "INDEPENDENCE_DAY": date(year, 7, 4),
        "VETERANS_DAY": date(year, 11, 11),
        "CHRISTMAS": date(year, 12, 25),
    }

    # Calculate floating holidays more efficiently
    def find_nth_weekday(year: int, month: int, weekday: int, n: int, from_end: bool = False) -> date:
        """Find the nth occurrence of a weekday in a month."""
        if from_end:
            # Start from the last day of the month
            last_day = calendar.monthrange(year, month)[1]
            d = date(year, month, last_day)
            while d.weekday() != weekday:
                d -= timedelta(days=1)
            return d
        else:
            # Start from the first day of the month
            d = date(year, month, 1)
            while d.weekday() != weekday:
                d += timedelta(days=1)
            # Move to the nth occurrence
            d += timedelta(days=7 * (n - 1))
            return d

    # 3rd Monday in January (Martin Luther King Jr. Day)
    all_holiday_types["MLK_DAY"] = find_nth_weekday(year, 1, 0, 3)  # Monday = 0

    # 3rd Monday in February (Presidents Day)
    all_holiday_types["PRESIDENTS_DAY"] = find_nth_weekday(year, 2, 0, 3)

    # Last Monday in May (Memorial Day)
    all_holiday_types["MEMORIAL_DAY"] = find_nth_weekday(year, 5, 0, 1, from_end=True)

    # 1st Monday in September (Labor Day)
    all_holiday_types["LABOR_DAY"] = find_nth_weekday(year, 9, 0, 1)

    # 2nd Monday in October (Columbus Day)
    all_holiday_types["COLUMBUS_DAY"] = find_nth_weekday(year, 10, 0, 2)

    # 4th Thursday in November (Thanksgiving Day)
    all_holiday_types["THANKSGIVING"] = find_nth_weekday(year, 11, 3, 4)  # Thursday = 3

    # If holiday_types is None, return all holidays in chronological order
    if holiday_types is None:
        return tuple(sorted(all_holiday_types.values()))

    # Otherwise, return only the specified holiday types
    result = []
    for holiday_type in holiday_types:
        if holiday_type in all_holiday_types:
            result.append(all_holiday_types[holiday_type])

    return tuple(sorted(result))


def get_us_federal_holidays_list(year: int, holiday_types: list[str] | None = None) -> list[date]:
    """
    Convenience wrapper for get_us_federal_holidays that accepts a list instead of tuple.

    This function converts the list to a tuple and calls the cached version.
    """
    if holiday_types is None:
        return get_us_federal_holidays(year, None)
    return get_us_federal_holidays(year, tuple(holiday_types))


def workdays_between(start_date: date, end_date: date, holidays: Iterable[date] | None = None) -> int:
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
        holidays: Optional collection of holiday dates to exclude (list, set, tuple,
            generator, etc.). Duplicates are automatically handled.

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
        holidays_set = set(holidays)
        for holiday in holidays_set:
            if start_date <= holiday <= end_date and holiday.weekday() < WEEKDAYS_IN_WEEK:
                workdays -= 1

    return workdays


def add_business_days(dt: date, num_days: int, holidays: Iterable[date] | None = None) -> date:
    """
    Add business days to a date, skipping weekends and holidays.

    For basic US holidays, you can generate them using
    `get_us_federal_holidays()`.

    Args:
        dt: The starting date.
        num_days: Number of business days to add (can be negative).
        holidays: Optional collection of holiday dates to skip (list, set, tuple, etc.).
            Using a set provides O(1) lookup performance for large holiday lists.
            **Note:** Generators are consumed on first use.

    Returns:
        A new date with the business days added.

    Raises:
        ValueError: If num_days is extremely large (> 10000 or < -10000)

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
    if not -10000 <= num_days <= 10000:  # noqa: PLR2004
        raise ValueError(f"num_days must be between -10000 and 10000, got {num_days}")

    if num_days == 0:
        return dt

    if holidays is None or (
        isinstance(holidays, (set, frozenset, list, tuple)) and len(holidays) == 0
    ):
        return _add_business_days_no_holidays(dt, num_days)

    holidays_set: set[date] = set(holidays) if holidays is not None else set()
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
    if num_days == 0:
        return dt

    direction = 1 if num_days > 0 else -1
    remaining = abs(num_days)
    weekday = dt.weekday()

    if direction > 0:
        if weekday == calendar.SATURDAY:
            dt -= timedelta(days=1)
            weekday = calendar.FRIDAY
        elif weekday == calendar.SUNDAY:
            dt -= timedelta(days=2)
            weekday = calendar.FRIDAY

        weeks, extra = divmod(remaining, WEEKDAYS_IN_WEEK)
        days = weeks * DAYS_IN_WEEK
        if extra:
            if weekday + extra >= WEEKDAYS_IN_WEEK:
                days += extra + 2
            else:
                days += extra
        return dt + timedelta(days=days)

    if weekday == calendar.SATURDAY:
        dt += timedelta(days=2)
        weekday = calendar.MONDAY
    elif weekday == calendar.SUNDAY:
        dt += timedelta(days=1)
        weekday = calendar.MONDAY

    weeks, extra = divmod(remaining, WEEKDAYS_IN_WEEK)
    days = weeks * DAYS_IN_WEEK
    if extra:
        if weekday - extra < 0:
            days += extra + 2
        else:
            days += extra
    return dt - timedelta(days=days)


def next_business_day(dt: date, holidays: Iterable[date] | None = None) -> date:
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


def previous_business_day(dt: date, holidays: Iterable[date] | None = None) -> date:
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
        now = datetime.fromtimestamp(now_override, tz=timezone.utc)
    else:
        now = datetime.now(timezone.utc)

    if timestamp is None:
        return timedelta(0)
    elif isinstance(timestamp, int):
        try:
            ts_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, OSError, OverflowError):
            return timedelta(0)  # Return zero diff for invalid timestamps
        return now - ts_dt
    elif isinstance(timestamp, datetime):
        # Handle naive datetimes by assuming UTC
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return now - timestamp
    # Type system guarantees we never reach here (timestamp is int | datetime | None)
    return timedelta(0)  # pragma: no cover


def pretty_date(timestamp: int | datetime | None = None, now_override: int | None = None) -> str:  # noqa: C901, PLR0911, PLR0912
    """
    Format a timestamp as a human-readable relative time string.

    Supports both past times ("2 hours ago", "Yesterday") and future times
    ("in 2 hours", "Tomorrow"). The output is designed to be user-friendly
    and uses natural language approximations.

    Args:
        timestamp: The time to format. Accepts three types:
            - int: Unix timestamp (seconds since epoch). Interpreted as UTC.
            - datetime: A datetime object. If naive (no tzinfo), assumed to be UTC.
              If timezone-aware, converted to UTC for comparison.
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

    # Future dates (negative diff means timestamp is in the future)
    if total_seconds < 0:
        total_seconds = abs(total_seconds)
        day_diff = int(total_seconds // SECONDS_IN_DAY)
        second_diff = int(total_seconds % SECONDS_IN_DAY)

        if day_diff == 0:
            if second_diff < RECENT_SECONDS:
                return "just now"
            if second_diff < SECONDS_IN_MINUTE:
                return "in " + str(second_diff) + " seconds"
            if second_diff < 2 * SECONDS_IN_MINUTE:
                return "in a minute"
            if second_diff < SECONDS_IN_HOUR:
                return "in " + str(int(second_diff / SECONDS_IN_MINUTE)) + " minutes"
            if second_diff < 2 * SECONDS_IN_HOUR:
                return "in an hour"
            return "in " + str(int(second_diff / SECONDS_IN_HOUR)) + " hours"
        elif day_diff == 1:
            return "Tomorrow"
        elif day_diff < DAYS_IN_WEEK:
            return "in " + str(day_diff) + " days"
        elif day_diff < DAYS_IN_MONTH_MAX:
            return "in " + str(int(day_diff / DAYS_IN_WEEK)) + " weeks"
        elif day_diff < DAYS_IN_YEAR:
            return "in " + str(int(day_diff / DAYS_IN_MONTH_APPROX)) + " months"
        return "in " + str(int(day_diff / DAYS_IN_YEAR)) + " years"

    # Past dates
    day_diff = diff.days
    second_diff = diff.seconds

    if day_diff == 0:
        if second_diff < RECENT_SECONDS:
            return "just now"
        if second_diff < SECONDS_IN_MINUTE:
            return str(second_diff) + " seconds ago"
        if second_diff < 2 * SECONDS_IN_MINUTE:
            return "a minute ago"
        if second_diff < SECONDS_IN_HOUR:
            return str(int(second_diff / SECONDS_IN_MINUTE)) + " minutes ago"
        if second_diff < 2 * SECONDS_IN_HOUR:
            return "an hour ago"
        # timedelta.seconds is always < 86400, so this is the final case for day_diff == 0
        return str(int(second_diff / SECONDS_IN_HOUR)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    elif day_diff < DAYS_IN_WEEK:
        return str(day_diff) + " days ago"
    elif day_diff < DAYS_IN_MONTH_MAX:
        return str(int(day_diff / DAYS_IN_WEEK)) + " weeks ago"
    elif day_diff < DAYS_IN_YEAR:
        return str(int(day_diff / DAYS_IN_MONTH_APPROX)) + " months ago"
    return str(int(day_diff / DAYS_IN_YEAR)) + " years ago"


def httpdate(date_time: datetime) -> str:
    """
    Convert a datetime object to an HTTP date string (RFC 7231 compliant).

    The output is always in GMT/UTC as required by RFC 7231. Timezone-aware
    datetimes are converted to UTC before formatting. Naive datetimes are
    assumed to already be in UTC. The formatting uses `email.utils.format_datetime`
    to avoid locale-dependent weekday/month names.

    Args:
        date_time: The datetime to format. If naive, assumed to be UTC.

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
    if date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC for consistent GMT output
        date_time = date_time.astimezone(timezone.utc)
    return _format_http_datetime(date_time, usegmt=True)


##################
# Parsing and formatting
##################
def parse_date(
    date_str: str,
    formats: list[str] | None = None,
    *,
    dayfirst: bool = False,
) -> date | None:
    """
    Parse a date string using multiple possible formats.

    Tries a list of common formats if `formats` is not provided.
    For ambiguous dates like "03/04/2024", the `dayfirst` parameter controls
    interpretation: False (default) treats it as March 4th (US style),
    True treats it as April 3rd (European style).

    Args:
        date_str: The date string to parse.
        formats: Optional list of format strings (e.g., "%Y/%m/%d") to try.
            If provided, `dayfirst` is ignored.
        dayfirst: If True, ambiguous dates are parsed as day/month/year (European).
            If False (default), ambiguous dates are parsed as month/day/year (US).
            Only applies when `formats` is None.

    Returns:
        A date object if parsing was successful, None otherwise. Returns None
        for both unparseable strings and invalid calendar dates (e.g., Feb 29
        in a non-leap year, April 31, etc.).

    Examples:
        >>> from datetime import date
        >>> parse_date("2024-07-22")
        datetime.date(2024, 7, 22)

        >>> parse_date("07/22/2024")  # US format (default)
        datetime.date(2024, 7, 22)

        >>> parse_date("22/07/2024", dayfirst=True)  # European format
        datetime.date(2024, 7, 22)

        >>> # Ambiguous date: 03/04/2024
        >>> parse_date("03/04/2024")  # Default: March 4th
        datetime.date(2024, 3, 4)

        >>> parse_date("03/04/2024", dayfirst=True)  # European: April 3rd
        datetime.date(2024, 4, 3)

        >>> parse_date("22 Jul 2024")
        datetime.date(2024, 7, 22)

        >>> parse_date("July 22, 2024")
        datetime.date(2024, 7, 22)

        >>> # Using a custom format
        >>> parse_date("20242207", formats=["%Y%d%m"])
        datetime.date(2024, 7, 22)

        >>> # Parsing fails
        >>> parse_date("invalid date string")

        >>> parse_date("2024-20-80")

    """
    if formats is None:
        if dayfirst:
            # European/international style: day before month
            formats = [
                "%Y-%m-%d",  # 2023-01-31 (ISO - unambiguous)
                "%d/%m/%Y",  # 31/01/2023
                "%m/%d/%Y",  # 01/31/2023 (fallback for US)
                "%d-%m-%Y",  # 31-01-2023
                "%m-%d-%Y",  # 01-31-2023 (fallback for US)
                "%d.%m.%Y",  # 31.01.2023
                "%Y/%m/%d",  # 2023/01/31
                "%B %d, %Y",  # January 31, 2023
                "%d %B %Y",  # 31 January 2023
                "%b %d, %Y",  # Jan 31, 2023
                "%d %b %Y",  # 31 Jan 2023
            ]
        else:
            # US style (default): month before day
            formats = [
                "%Y-%m-%d",  # 2023-01-31 (ISO - unambiguous)
                "%m/%d/%Y",  # 01/31/2023
                "%d/%m/%Y",  # 31/01/2023 (fallback for European)
                "%m-%d-%Y",  # 01-31-2023
                "%d-%m-%Y",  # 31-01-2023 (fallback for European)
                "%d.%m.%Y",  # 31.01.2023
                "%Y/%m/%d",  # 2023/01/31
                "%B %d, %Y",  # January 31, 2023
                "%d %B %Y",  # 31 January 2023
                "%b %d, %Y",  # Jan 31, 2023
                "%d %b %Y",  # 31 Jan 2023
            ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None


def parse_datetime(datetime_str: str, formats: list[str] | None = None) -> datetime | None:
    """
    Parse a datetime string using multiple possible formats

    Args:
        datetime_str: The datetime string to parse
        formats: List of format strings to try (if None, uses common formats)

    Returns:
        A datetime object if parsing was successful, None otherwise
    """
    if formats is None:
        formats = [
            "%Y-%m-%d %H:%M:%S",  # 2023-01-31 14:30:45
            "%Y-%m-%dT%H:%M:%S",  # 2023-01-31T14:30:45
            "%Y-%m-%dT%H:%M:%S.%f",  # 2023-01-31T14:30:45.123456
            "%Y-%m-%dT%H:%M:%SZ",  # 2023-01-31T14:30:45Z
            "%Y-%m-%dT%H:%M:%S.%fZ",  # 2023-01-31T14:30:45.123456Z
            "%d/%m/%Y %H:%M:%S",  # 31/01/2023 14:30:45
            "%m/%d/%Y %H:%M:%S",  # 01/31/2023 14:30:45
            "%d-%m-%Y %H:%M:%S",  # 31-01-2023 14:30:45
            "%Y/%m/%d %H:%M:%S",  # 2023/01/31 14:30:45
        ]

    for fmt in formats:
        try:
            dt = datetime.strptime(datetime_str, fmt)
            # Handle ISO 8601 format with timezone designator
            if datetime_str.endswith("Z"):
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return None


def parse_iso8601(iso_str: str) -> datetime | None:
    """
    Parse an ISO 8601 formatted date/time string.

    This handles various ISO 8601 formats including:
    - Date only: 2023-01-31
    - Date and time: 2023-01-31T14:30:45
    - With milliseconds: 2023-01-31T14:30:45.123
    - With timezone: 2023-01-31T14:30:45+02:00

    Note:
        Fractional seconds are limited to microsecond precision (6 digits).
        Any digits beyond 6 are silently truncated. For example,
        ".123456789" (nanoseconds) becomes ".123456" (microseconds).

    Args:
        iso_str: The ISO 8601 string to parse

    Returns:
        A datetime object, or None if parsing failed
    """
    match = _ISO8601_PATTERN.match(iso_str)
    if not match:
        return None

    date_part, time_part, ms_part, tz_part = match.groups()

    if time_part is None:
        # Date only
        return datetime.strptime(date_part, "%Y-%m-%d")

    # Combine date and time
    dt_str = f"{date_part}T{time_part}"
    dt_format = "%Y-%m-%dT%H:%M:%S"

    if ms_part:
        # Truncate to microsecond precision (6 digits max after the decimal point)
        # Python's %f only supports up to 6 digits; anything beyond is silently truncated by strptime
        max_fractional_len = 7  # ".XXXXXX" (1 dot + 6 digits)
        if len(ms_part) > max_fractional_len:
            ms_part = ms_part[:max_fractional_len]
        dt_str += ms_part
        dt_format += ".%f"

    dt = datetime.strptime(dt_str, dt_format)

    # Handle timezone
    if tz_part:
        if tz_part == "Z":
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Convert +HH:MM or +HHMM to ±HHMM for timedelta calculation
            tz_part = tz_part.replace(":", "")
            sign = -1 if tz_part[0] == "-" else 1
            hours = int(tz_part[1:3])
            minutes = int(tz_part[3:5])
            offset = sign * timedelta(hours=hours, minutes=minutes)
            dt = dt.replace(tzinfo=timezone(offset))

    return dt


def format_date(dt: date | datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date or datetime object using the specified format

    Args:
        dt: The date or datetime to format
        format_str: Format string (default ISO format)

    Returns:
        Formatted date string
    """
    if isinstance(dt, datetime):
        dt = dt.date()

    return dt.strftime(format_str)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object using the specified format

    Args:
        dt: The datetime to format
        format_str: Format string (default ISO format without T)

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def to_iso8601(dt: date | datetime) -> str:
    """
    Convert a date or datetime to ISO 8601 format

    Args:
        dt: Date or datetime to convert

    Returns:
        ISO 8601 formatted string
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt.isoformat()

    # It's a datetime
    if dt.tzinfo is None:
        # Assume UTC for naive datetimes
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat()


##################
# Timezone operations
##################
def get_available_timezones() -> list[str]:
    """
    Get a list of available timezone names

    Returns:
        List of timezone names (e.g. "America/New_York", "Europe/London", etc.)
    """
    return sorted(available_timezones())


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
    try:
        tz = ZoneInfo(tz_name)
        return datetime.now(tz)
    except ZoneInfoNotFoundError as e:
        raise ValueError(
            f"Invalid timezone name '{tz_name}'. Use get_available_timezones() to see valid options."
        ) from e


def today_in_timezone(tz_name: str) -> date:
    """
    Get the current date in the specified timezone

    Args:
        tz_name: Timezone name (e.g. "America/New_York", "Europe/London")

    Returns:
        Current date in the specified timezone

    Raises:
        ValueError: If timezone name is invalid
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
    hours, remainder = divmod(abs(total_seconds), SECONDS_IN_HOUR)
    minutes, _ = divmod(remainder, SECONDS_IN_MINUTE)

    sign = "-" if total_seconds < 0 else "+"
    return f"{sign}{hours:02d}:{minutes:02d}"


##################
# Additional utility functions
##################
def is_business_day(dt: date, holidays: Iterable[date] | None = None) -> bool:
    """
    Check if a date is a business day (not weekend or holiday).

    Args:
        dt: Date to check
        holidays: Optional collection of holiday dates (list, set, tuple, generator, etc.).
            Generators will be consumed. Internally converted to a set for O(1) lookup.

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
    if dt.weekday() >= calendar.SATURDAY:
        return False
    if holidays is None:
        return True
    # Convert to set to handle generators and ensure O(1) lookup
    holidays_set = set(holidays) if not isinstance(holidays, (set, frozenset)) else holidays
    return dt not in holidays_set


def days_until_weekend(dt: date) -> int:
    """
    Get the number of days until the next weekend.

    Args:
        dt: Date to check from

    Returns:
        int: Number of days until Saturday (0 if already weekend)
    """
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
    return dt.isocalendar()[1]


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
    if not 1 <= quarter <= QUARTERS_IN_YEAR:
        raise ValueError(f"Quarter must be between 1 and 4, got {quarter}")

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
    if as_of_date is None:
        as_of_date = date.today()

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


def time_until_next_occurrence(target_time: datetime, from_time: datetime | None = None) -> timedelta:
    """
    Calculate the time remaining until the next daily occurrence of a specific time-of-day.

    This function extracts the time-of-day (hour, minute, second, microsecond) from
    `target_time` and calculates how long until that time occurs next, relative to
    `from_time`. The date portion of `target_time` is ignored - only the time-of-day
    matters.

    This is useful for scheduling scenarios like "how long until 3:00 PM?" or
    "time remaining until the daily backup at 02:00".

    Args:
        target_time: A datetime whose time-of-day (HH:MM:SS) represents the target.
            The date portion is ignored. Can be timezone-aware or naive.
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

    Examples:
        >>> from datetime import datetime, timezone, timedelta

        >>> # How long until 3:00 PM UTC from 2:30 PM UTC?
        >>> target = datetime(2024, 1, 1, 15, 0, 0, tzinfo=timezone.utc)  # 3:00 PM
        >>> from_dt = datetime(2024, 1, 1, 14, 30, 0, tzinfo=timezone.utc)  # 2:30 PM
        >>> time_until_next_occurrence(target, from_dt)
        datetime.timedelta(seconds=1800)  # 30 minutes

        >>> # If the target time has already passed today, returns time until tomorrow
        >>> from_dt = datetime(2024, 1, 1, 16, 0, 0, tzinfo=timezone.utc)  # 4:00 PM
        >>> delta = time_until_next_occurrence(target, from_dt)  # Next 3:00 PM is tomorrow
        >>> delta.total_seconds()
        82800.0  # 23 hours

        >>> # Useful for scheduling: "How long until the daily 2 AM job runs?"
        >>> job_time = datetime(2024, 1, 1, 2, 0, 0, tzinfo=timezone.utc)
        >>> delta = time_until_next_occurrence(job_time)  # Uses current time as reference
    """
    if from_time is None:
        if target_time.tzinfo is not None:
            from_time = datetime.now(target_time.tzinfo)
        else:
            from_time = datetime.now()

    # Ensure both have the same timezone handling
    if target_time.tzinfo is None and from_time.tzinfo is not None:
        target_time = target_time.replace(tzinfo=from_time.tzinfo)
    elif target_time.tzinfo is not None and from_time.tzinfo is None:
        from_time = from_time.replace(tzinfo=target_time.tzinfo)

    # Calculate next occurrence
    next_occurrence = target_time.replace(year=from_time.year, month=from_time.month, day=from_time.day)

    if next_occurrence <= from_time:
        # Target time has already passed today, move to next day
        next_occurrence += timedelta(days=1)

    return next_occurrence - from_time
