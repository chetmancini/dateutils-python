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
from dateutils.dateutils import workdays_between

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
import time
import re
from datetime import timezone
from datetime import datetime
from datetime import date
from datetime import timedelta
from typing import Generator, Optional, Union, Tuple, List
from zoneinfo import ZoneInfo, available_timezones

##################
# Constants
##################
RECENT_SECONDS = 10
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR
DAYS_IN_YEAR = 365
DAYS_IN_MONTH_APPROX = 30
DAYS_IN_WEEK = 7


##################
# UTC
##################
def utc_now_seconds() -> int:
    """
    Get the current time in seconds since epoch in UTC.

    Returns:
        int: Current UTC time as Unix timestamp (seconds since epoch)
    """
    return calendar.timegm(time.gmtime())


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
    """
    dt = datetime.fromtimestamp(ts, timezone.utc)
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return epoch_s(dt)


def utc_from_timestamp(ts: int) -> datetime:
    """
    Convert a timestamp to a datetime object in UTC timezone.

    Args:
        ts: Unix timestamp (seconds since epoch)

    Returns:
        datetime: Datetime object in UTC timezone
    """
    return datetime.fromtimestamp(ts, timezone.utc)


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
    return calendar.timegm(dt.utctimetuple())


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
        datetime: Datetime at 23:59:59
    """
    return datetime_start_of_day(day) + timedelta(days=1) - timedelta(seconds=1)


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
        datetime: Datetime at 00:00:00
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
    """
    return datetime(year, (q - 1) * 3 + 1, 1)

def end_of_quarter(year: int, q: int) -> datetime:
    """
    Get the end of the quarter

    Args:
        year: Year to get end of quarter for
        q: Quarter to get end of (1-4)

    Returns:
        datetime: Datetime at 23:59:59
    """
    # Calculate the month at the end of the quarter
    month = q * 3
    # Get the last day of that month
    days_in_month = calendar.monthrange(year, month)[1]
    return datetime(year, month, days_in_month, 23, 59, 59)


def generate_quarters(until_year: int = 1970, until_q: int = 1) -> Generator[Tuple[int, int], None, None]:
    """
    Generate quarters from the current quarter until a specific year and quarter

    Args:
        until_year: Year to generate quarters until
        until_q: Quarter to generate quarters until (1-4)

    Returns:
        Generator[Tuple[int, int], None, None]: Quarters from current quarter to the specified year and quarter
    """
    today = date.today()
    current_quarter = date_to_quarter(today)
    current_year = today.year
    for year in generate_years(until=until_year):
        for q in range(4, 0, -1):
            if year == current_year and q > current_quarter:
                continue
            if year == until_year and until_q > q:
                return
            else:
                yield q, year


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
    Get the end of the year

    Args:
        year: Year to get end of year for

    Returns:
        datetime: Datetime at 23:59:59
    """
    return datetime(year, 12, 31, 23, 59, 59)


def generate_years(until: int = 1970) -> Generator[int, None, None]:
    """
    Generate years from the current year until a specific year

    Returns:
        Generator[int, None, None]: Years from current year to the specified year
    """
    current_year = date.today().year
    for years_ago in range(current_year + 1 - until):
        yield current_year - years_ago


def is_leap_year(year: int) -> bool:
    """
    Check if a year is a leap year

    Args:
        year: Year to check if it is a leap year

    Returns:
        bool: True if the year is a leap year, False otherwise
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


##################
# Month operations
##################
def start_of_month(year: int, month: int) -> datetime:
    """
    Get the start of the month

    Args:
        year: Year to get start of month for
        month: Month to get start of (1-12)

    Returns:
        datetime: Datetime at 00:00:00
    """
    return datetime(year, month, 1)


def end_of_month(year: int, month: int) -> datetime:
    """
    Get the end of the month

    Args:
        year: Year to get end of month for
        month: Month to get end of (1-12)

    Returns:
        datetime: Datetime at 23:59:59
    """
    days_in_month = calendar.monthrange(year, month)[1]
    return datetime(year, month, days_in_month, 23, 59, 59)


def generate_months(until_year: int = 1970, until_m: int = 1) -> Generator[Tuple[int, int], None, None]:
    """
    Generate months from the current month until a specific year and month

    Returns:
        Generator[Tuple[int, int], None, None]: Months from current month to the specified year and month
    """
    today = date.today()
    for year in generate_years(until=until_year):
        for month in range(12, 0, -1):
            if year == today.year and month > today.month:
                continue
            if year == until_year and until_m > month:
                return
            else:
                yield month, year


def get_days_in_month(year: int, month: int) -> int:
    """
    Get the number of days in a specific month and year

    Args:
        year: Year to get days in month for
        month: Month to get days in (1-12)

    Returns:
        int: Number of days in the specified month
    """
    return calendar.monthrange(year, month)[1]


##################
# Week operations
##################
def generate_weeks(count: int = 500, until_date: Optional[date] = None) -> Generator[Tuple[date, date], None, None]:
    """
    Generate weeks from the current week until a specific date

    Args:
        count: Number of weeks to generate
        until_date: Date to generate weeks until

    Returns:
        Generator[Tuple[date, date], None, None]: Weeks from current week to the specified date
    """
    this_dow = date.today().weekday()
    monday = date.today() - timedelta(days=this_dow)
    end = monday
    for i in range(count):
        start = end - timedelta(days=7)
        ret = (start, end)
        end = start
        if until_date and start > until_date:
            yield ret
        elif not until_date:
            yield ret
        else:
            return


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
    """
    days = (end_date - start_date).days + 1
    return [start_date + timedelta(days=i) for i in range(days)]


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
    return dt.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def get_us_federal_holidays(year: int, holiday_types: Optional[List[str]] = None) -> List[date]:
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
        holiday_types: Optional list of holiday types to include. If None, all holidays are included.
                      Valid values: "NEW_YEARS_DAY", "MLK_DAY", "PRESIDENTS_DAY", "MEMORIAL_DAY",
                      "JUNETEENTH", "INDEPENDENCE_DAY", "LABOR_DAY", "COLUMBUS_DAY",
                      "VETERANS_DAY", "THANKSGIVING", "CHRISTMAS"

    Returns:
        List[date]: A list of date objects for the holidays in that year.

    Examples:
        >>> from datetime import date
        >>> holidays_2024 = get_us_federal_holidays(2024)
        >>> date(2024, 1, 1) in holidays_2024  # New Year's Day
        True
        >>> date(2024, 11, 28) in holidays_2024  # Thanksgiving
        True

        >>> # Get only fixed holidays
        >>> fixed_holidays = get_us_federal_holidays(2024, ["NEW_YEARS_DAY", "JUNETEENTH",
        ...                                                "INDEPENDENCE_DAY", "VETERANS_DAY", "CHRISTMAS"])
        >>> date(2024, 1, 1) in fixed_holidays
        True
        >>> date(2024, 1, 15) in fixed_holidays  # MLK Day (floating)
        False
    """
    # Define all possible holiday types
    ALL_HOLIDAY_TYPES: dict[str, date] = {
        # Fixed holidays
        "NEW_YEARS_DAY": date(year, 1, 1),
        "JUNETEENTH": date(year, 6, 19),
        "INDEPENDENCE_DAY": date(year, 7, 4),
        "VETERANS_DAY": date(year, 11, 11),
        "CHRISTMAS": date(year, 12, 25),

        # Floating holidays - will be calculated below
        # "MLK_DAY": None,
        # "PRESIDENTS_DAY": None,
        # "MEMORIAL_DAY": None,
        # "LABOR_DAY": None,
        # "COLUMBUS_DAY": None,
        # "THANKSGIVING": None
    }

    # Calculate floating holidays

    # Find the 3rd Monday in January (Martin Luther King Jr. Day)
    mlk_day = date(year, 1, 1)
    while mlk_day.weekday() != 0:  # 0 = Monday
        mlk_day += timedelta(days=1)
    mlk_day += timedelta(days=14)  # Move to 3rd Monday
    ALL_HOLIDAY_TYPES["MLK_DAY"] = mlk_day

    # Find the 3rd Monday in February (Presidents Day)
    presidents_day = date(year, 2, 1)
    while presidents_day.weekday() != 0:  # 0 = Monday
        presidents_day += timedelta(days=1)
    presidents_day += timedelta(days=14)  # Move to 3rd Monday
    ALL_HOLIDAY_TYPES["PRESIDENTS_DAY"] = presidents_day

    # Find the last Monday in May (Memorial Day)
    memorial_day = date(year, 5, 31)
    while memorial_day.weekday() != 0:  # 0 = Monday
        memorial_day -= timedelta(days=1)
    ALL_HOLIDAY_TYPES["MEMORIAL_DAY"] = memorial_day

    # Find the 1st Monday in September (Labor Day)
    labor_day = date(year, 9, 1)
    while labor_day.weekday() != 0:  # 0 = Monday
        labor_day += timedelta(days=1)
    ALL_HOLIDAY_TYPES["LABOR_DAY"] = labor_day

    # Find the 2nd Monday in October (Columbus Day)
    columbus_day = date(year, 10, 1)
    while columbus_day.weekday() != 0:  # 0 = Monday
        columbus_day += timedelta(days=1)
    columbus_day += timedelta(days=7)  # Move to 2nd Monday
    ALL_HOLIDAY_TYPES["COLUMBUS_DAY"] = columbus_day

    # Find the 4th Thursday in November (Thanksgiving Day)
    thanksgiving = date(year, 11, 1)
    while thanksgiving.weekday() != 3:  # 3 = Thursday
        thanksgiving += timedelta(days=1)
    thanksgiving += timedelta(days=21)  # Move to 4th Thursday
    ALL_HOLIDAY_TYPES["THANKSGIVING"] = thanksgiving

    # If holiday_types is None, return all holidays
    if holiday_types is None:
        return list(ALL_HOLIDAY_TYPES.values())

    # Otherwise, return only the specified holiday types
    result = []
    for holiday_type in holiday_types:
        if holiday_type in ALL_HOLIDAY_TYPES:
            result.append(ALL_HOLIDAY_TYPES[holiday_type])

    return result


def workdays_between(start_date: date, end_date: date, holidays: Optional[List[date]] = None) -> int:
    """
    Count workdays (Monday-Friday) between two dates, inclusive.

    Optionally excludes specified holidays. For basic US fixed holidays, you
    can generate them using `get_us_federal_holidays()`.

    Args:
        start_date: The start date (inclusive).
        end_date: The end date (inclusive).
        holidays: Optional list of holiday dates to exclude.

    Returns:
        int: Number of workdays between the start and end dates.

    Examples:
        >>> from datetime import date
        >>> start = date(2024, 7, 1) # Monday
        >>> end = date(2024, 7, 7)   # Sunday
        >>> workdays_between(start, end)
        5 # Mon, Tue, Wed, Thu, Fri

        >>> # Using built-in US fixed holidays for 2024
        >>> us_holidays = get_us_federal_holidays(2024)
        >>> workdays_between(start, end, holidays=us_holidays) # July 4th is excluded
        4 # Mon, Tue, Wed, Fri

        >>> start = date(2024, 12, 23)
        >>> end = date(2024, 12, 27)
        >>> workdays_between(start, end, holidays=get_us_federal_holidays(2024)) # Excludes Dec 25
        4 # Mon, Tue, Thu, Fri
    """
    if holidays is None:
        holidays = []

    holidays_set = set(holidays)
    count = 0
    current = start_date

    while current <= end_date:
        if current.weekday() < 5 and current not in holidays_set:  # Weekday and not a holiday
            count += 1
        current += timedelta(days=1)

    return count


def add_business_days(dt: date, num_days: int, holidays: Optional[List[date]] = None) -> date:
    """
    Add business days to a date, skipping weekends and holidays.

    For basic US holidays, you can generate them using
    `get_us_federal_holidays()`.

    Args:
        dt: The starting date.
        num_days: Number of business days to add (can be negative).
        holidays: Optional list of holiday dates to skip.

    Returns:
        A new date with the business days added.

    Examples:
        >>> from datetime import date
        >>> start_date = date(2024, 7, 1) # Monday
        >>> add_business_days(start_date, 3)
        datetime.date(2024, 7, 4) # Thu

        >>> # Skip July 4th holiday
        >>> us_holidays = get_us_federal_holidays(2024)
        >>> add_business_days(start_date, 3, holidays=us_holidays)
        datetime.date(2024, 7, 5) # Fri

        >>> # Add negative days
        >>> end_date = date(2024, 7, 8) # Monday
        >>> add_business_days(end_date, -2)
        datetime.date(2024, 7, 4) # Thu

        >>> # Add negative days skipping holiday
        >>> add_business_days(end_date, -2, holidays=us_holidays)
        datetime.date(2024, 7, 3) # Wed
    """
    if holidays is None:
        holidays = []

    holidays_set = set(holidays)
    current = dt
    added = 0
    days_to_add = 1 if num_days >= 0 else -1

    while added < abs(num_days):
        current += timedelta(days=days_to_add)
        if current.weekday() < 5 and current not in holidays_set:  # Weekday and not a holiday
            added += 1

    return current


def next_business_day(dt: date, holidays: Optional[List[date]] = None) -> date:
    """
    Find the next business day from a given date, skipping weekends and holidays.

    For basic US fixed holidays, you can generate them using
    `get_us_federal_holidays()`.

    Args:
        dt: The starting date.
        holidays: Optional list of holiday dates to skip.

    Returns:
        The next business day.

    Examples:
        >>> from datetime import date
        >>> friday = date(2024, 7, 5)
        >>> next_business_day(friday)
        datetime.date(2024, 7, 8) # Monday

        >>> wednesday = date(2024, 7, 3)
        >>> # July 4th is a holiday
        >>> us_holidays = get_us_federal_holidays(2024)
        >>> next_business_day(wednesday, holidays=us_holidays)
        datetime.date(2024, 7, 5) # Friday
    """
    return add_business_days(dt, 1, holidays)


def previous_business_day(dt: date, holidays: Optional[List[date]] = None) -> date:
    """
    Find the previous business day from a given date, skipping weekends and holidays.

    For basic US fixed holidays, you can generate them using
    `get_us_federal_holidays()`.

    Args:
        dt: The starting date.
        holidays: Optional list of holiday dates to skip.

    Returns:
        The previous business day.

    Examples:
        >>> from datetime import date
        >>> monday = date(2024, 7, 8)
        >>> previous_business_day(monday)
        datetime.date(2024, 7, 5) # Friday

        >>> friday = date(2024, 7, 5)
        >>> # July 4th is a holiday
        >>> us_holidays = get_us_federal_holidays(2024)
        >>> previous_business_day(friday, holidays=us_holidays)
        datetime.date(2024, 7, 3) # Wednesday
    """
    return add_business_days(dt, -1, holidays)


def _ts_difference(timestamp: Optional[Union[int, datetime]] = None, now_override: Optional[int] = None) -> timedelta:
    now = datetime.now() if not now_override else datetime.fromtimestamp(now_override)
    if type(timestamp) is int:
        diff = now - datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, datetime):
        diff = now - timestamp
    elif not timestamp:
        diff = now - now
    return diff


def pretty_date(timestamp: Optional[Union[int, datetime]] = None, now_override: Optional[int] = None) -> str:  # NOQA
    """
    Adapted from
    http://stackoverflow.com/questions/1551382/
    user-friendly-time-format-in-python
    """
    diff = _ts_difference(timestamp, now_override)
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ""
    elif day_diff == 0:
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
        if second_diff < 24 * SECONDS_IN_HOUR:
            return str(int(second_diff / SECONDS_IN_HOUR)) + " hours ago"
    elif day_diff == 1:
        return "Yesterday"
    elif day_diff < DAYS_IN_WEEK:
        return str(int(day_diff)) + " days ago"
    elif day_diff < 31:
        return str(int(day_diff / DAYS_IN_WEEK)) + " weeks ago"
    elif day_diff < DAYS_IN_YEAR:
        return str(int(day_diff / DAYS_IN_MONTH_APPROX)) + " months ago"
    return str(int(day_diff / DAYS_IN_YEAR)) + " years ago"


def httpdate(date_time: datetime) -> str:
    """
    Convert a datetime object to an HTTP date string (RFC 7231 compliant).
    Assumes the input datetime is in UTC if not timezone-aware.
    """
    if date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=timezone.utc)
    return date_time.strftime("%a, %d %b %Y %H:%M:%S GMT")


##################
# Parsing and formatting
##################
def parse_date(date_str: str, formats: Optional[List[str]] = None) -> Optional[date]:
    """
    Parse a date string using multiple possible formats.

    Tries a list of common formats if `formats` is not provided.
    See the function code for the default list.

    Args:
        date_str: The date string to parse.
        formats: Optional list of format strings (e.g., "%Y/%m/%d") to try.

    Returns:
        A date object if parsing was successful, None otherwise.

    Examples:
        >>> from datetime import date
        >>> parse_date("2024-07-22")
        datetime.date(2024, 7, 22)

        >>> parse_date("07/22/2024")
        datetime.date(2024, 7, 22)

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
        formats = [
            "%Y-%m-%d",  # 2023-01-31
            "%d/%m/%Y",  # 31/01/2023
            "%m/%d/%Y",  # 01/31/2023
            "%d-%m-%Y",  # 31-01-2023
            "%m-%d-%Y",  # 01-31-2023
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


def parse_datetime(datetime_str: str, formats: Optional[List[str]] = None) -> Optional[datetime]:
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


def parse_iso8601(iso_str: str) -> Optional[datetime]:
    """
    Parse an ISO 8601 formatted date/time string

    This handles various ISO 8601 formats including:
    - Date only: 2023-01-31
    - Date and time: 2023-01-31T14:30:45
    - With milliseconds: 2023-01-31T14:30:45.123
    - With timezone: 2023-01-31T14:30:45+02:00

    Args:
        iso_str: The ISO 8601 string to parse

    Returns:
        A datetime object, or None if parsing failed
    """
    iso_regex = (
        r"^(\d{4}-\d{2}-\d{2})"  # Date part (required)
        r"(?:T(\d{2}:\d{2}:\d{2}))?"  # Time part (optional)
        r"(\.\d+)?"  # Milliseconds (optional)
        r"(Z|[+-]\d{2}:?\d{2})?$"  # Timezone (optional)
    )

    match = re.match(iso_regex, iso_str)
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


def format_date(dt: Union[date, datetime], format_str: str = "%Y-%m-%d") -> str:
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


def to_iso8601(dt: Union[date, datetime]) -> str:
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
def get_available_timezones() -> List[str]:
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
        ValueError: If the input datetime `dt` is naive (tzinfo is None).
        zoneinfo.ZoneInfoNotFoundError: If `to_tz` is not a valid timezone name.

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

    target_tz = ZoneInfo(to_tz)
    return dt.astimezone(target_tz)


def datetime_to_utc(dt: datetime) -> datetime:
    """
    Convert a datetime to UTC

    Args:
        dt: The datetime to convert (if naive, assumes local timezone)

    Returns:
        The datetime in UTC
    """
    if dt.tzinfo is None:
        # Assume system local timezone
        dt = dt.astimezone()

    return dt.astimezone(timezone.utc)


def get_timezone_offset(tz_name: str) -> timedelta:
    """
    Get the current offset from UTC for a timezone

    Args:
        tz_name: Timezone name

    Returns:
        Timedelta representing the offset from UTC
    """
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    return now.utcoffset() or timedelta(0)


def format_timezone_offset(tz_name: str) -> str:
    """
    Get the current offset from UTC for a timezone as a formatted string

    Args:
        tz_name: Timezone name

    Returns:
        String in format "+HH:MM" or "-HH:MM"
    """
    offset = get_timezone_offset(tz_name)

    # Convert timedelta to hours and minutes
    total_seconds = int(offset.total_seconds())
    hours, remainder = divmod(abs(total_seconds), SECONDS_IN_HOUR)
    minutes, _ = divmod(remainder, SECONDS_IN_MINUTE)

    sign = "-" if total_seconds < 0 else "+"
    return f"{sign}{hours:02d}:{minutes:02d}"
