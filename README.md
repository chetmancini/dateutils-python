# DateUtils Python

[![PyPI version](https://badge.fury.io/py/dateutils-python.svg)](https://pypi.org/project/dateutils-python/)
[![PyPI downloads](https://img.shields.io/pypi/dm/dateutils-python.svg)](https://pypi.org/project/dateutils-python/)
[![Python versions](https://img.shields.io/pypi/pyversions/dateutils-python.svg)](https://pypi.org/project/dateutils-python/)
[![CI](https://github.com/chetmancini/dateutils-python/actions/workflows/main.yml/badge.svg)](https://github.com/chetmancini/dateutils-python/actions/workflows/main.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/chetmancini/dateutils-python)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Typed](https://img.shields.io/badge/typed-100%25-blue.svg)](https://github.com/chetmancini/dateutils-python)

A comprehensive collection of date and time utilities for Python applications.

## Features

- **UTC Operations**: Easily work with UTC timestamps and dates
- **Date/Time Parsing**: Parse dates and times from strings in various formats
- **Timezone Handling**: Convert between timezones with robust error handling
- **Business Days**: Calculate business days with support for holidays and validation
- **Quarter/Month/Week Operations**: Helpers for working with larger time spans
- **Date Formatting**: Convert dates to various string formats including ISO 8601
- **Human-readable Dates**: Generate user-friendly date strings like "2 hours ago"
- **Additional Utilities**: Age calculation, weekend detection, week numbers, and more
- **Memory Efficiency**: Generator-based functions for large date ranges
- **Input Validation**: Comprehensive validation with helpful error messages

## Why dateutils-python?

There are several excellent date/time libraries in the Python ecosystem. Here's how dateutils-python compares:

| Feature | dateutils-python | python-dateutil | arrow | pendulum |
|---------|-----------------|-----------------|-------|----------|
| **Zero dependencies** | Yes | Yes | No (1 dep) | No (3 deps) |
| **Business day calculations** | Built-in | No | No | No |
| **US Federal holidays** | Built-in | No | No | No |
| **Fully typed** | Yes | Partial | Partial | Yes |
| **Human-readable output** | Yes | No | Yes | Yes |
| **Timezone handling** | Yes | Yes | Yes | Yes |
| **Date parsing** | Multi-format | Powerful/fuzzy | ISO-focused | ISO-focused |
| **Relative date parsing** | No | Yes ("next Friday") | Yes | Yes |
| **Maintained** | Active | Active | Active | Active |

### Choose dateutils-python if you want:

- **Zero dependency overhead** - Uses only Python's standard library. No transitive dependencies to audit, no version conflicts, no supply chain concerns.
- **Business day logic out of the box** - Calculate workdays, skip holidays, find next/previous business day without additional libraries.
- **US Federal holidays included** - No need to maintain your own holiday list or pull in another package.
- **Full type coverage** - Every function is fully typed for IDE autocompletion and static analysis.
- **Lightweight and focused** - Does common date operations well without trying to be everything.

### Consider alternatives if you need:

- **Fuzzy date parsing** ("next tuesday", "in 2 weeks") - Use `python-dateutil`
- **Immutable date objects with method chaining** - Use `pendulum`
- **Drop-in datetime replacement** - Use `arrow` or `pendulum`
- **Extensive internationalization** - Use `pendulum` or `babel`

## Installation

```bash
pip install dateutils-python
```

## Usage Examples

### UTC and Timestamp Operations

```python
from dateutils.dateutils import utc_now_seconds, utc_today, epoch_s

# Get current UTC timestamp
timestamp = utc_now_seconds()  # e.g., 1717682345

# Get current UTC date
today = utc_today()  # e.g., datetime.date(2024, 6, 6)

# Convert a datetime to timestamp
from datetime import datetime
dt = datetime(2024, 6, 6, 12, 30, 0)
ts = epoch_s(dt)  # e.g., 1717682345
```

### Business Day Calculations

```python
from dateutils.dateutils import (
    workdays_between, add_business_days, next_business_day,
    previous_business_day, is_business_day
)
from datetime import date

# Calculate workdays between dates
start = date(2024, 6, 1)
end = date(2024, 6, 10)
workdays = workdays_between(start, end)  # Excludes weekends

# With holiday support
holidays = [date(2024, 6, 5)]  # Example holiday
workdays = workdays_between(start, end, holidays)  # Excludes weekends and holidays

# Add business days
new_date = add_business_days(start, 5)  # Skip weekends
new_date = add_business_days(start, 5, holidays)  # Skip weekends and holidays

# Check if a date is a business day
monday = date(2024, 6, 3)
is_business = is_business_day(monday)  # True
is_business_with_holiday = is_business_day(monday, holidays=[monday])  # False

# Get next/previous business day
next_bday = next_business_day(date(2024, 6, 7))  # Friday -> Monday
prev_bday = previous_business_day(date(2024, 6, 3))  # Monday -> Friday
```

### Holiday Support

```python
from dateutils.dateutils import get_us_federal_holidays, get_us_federal_holidays_list

# Get all US federal holidays for a year (cached for performance)
holidays_2024 = get_us_federal_holidays(2024)  # Returns 11 holidays

# Get specific holiday types
fixed_holidays = get_us_federal_holidays(2024, ("NEW_YEARS_DAY", "CHRISTMAS"))

# Use with business day functions
workdays = workdays_between(start, end, holidays=holidays_2024)
```

### Date Parsing and Formatting

```python
from dateutils.dateutils import parse_date, parse_datetime, parse_iso8601, to_iso8601

# Parse a date string (tries multiple formats)
dt = parse_date("2024-06-06")  # Returns date object
dt = parse_date("06/06/2024")  # Also works
dt = parse_date("June 6, 2024")  # Also works

# Parse ISO 8601 datetime
dt = parse_iso8601("2024-06-06T12:30:45Z")  # With timezone
dt = parse_iso8601("2024-06-06")  # Date only

# Format as ISO 8601
iso_str = to_iso8601(dt)  # e.g., "2024-06-06T12:30:45+00:00"
```

### Timezone Handling

```python
from dateutils.dateutils import (
    now_in_timezone, convert_timezone, get_available_timezones,
    get_timezone_offset, format_timezone_offset
)

# Get current time in a timezone
nyc_now = now_in_timezone("America/New_York")

# Convert between timezones
from datetime import datetime, timezone
utc_dt = datetime(2024, 6, 6, 12, 0, 0, tzinfo=timezone.utc)
tokyo_dt = convert_timezone(utc_dt, "Asia/Tokyo")

# Get available timezones
timezones = get_available_timezones()  # List of all available timezone names

# Get timezone offset
offset = get_timezone_offset("America/New_York")  # Returns timedelta
offset_str = format_timezone_offset("America/New_York")  # Returns "-05:00" or "-04:00" (DST)
```

### Quarter and Month Operations

```python
from dateutils.dateutils import (
    date_to_quarter, date_to_start_of_quarter, get_quarter_start_end,
    start_of_quarter, end_of_quarter, start_of_month, end_of_month
)
from datetime import datetime

# Get quarter for a date
dt = datetime(2024, 5, 15)
quarter = date_to_quarter(dt)  # Returns 2 (Q2)

# Get start of quarter
start_date = date_to_start_of_quarter(dt)  # Returns 2024-04-01

# Get quarter date range
start, end = get_quarter_start_end(2024, 2)  # Q2 2024: (2024-04-01, 2024-06-30)

# Get precise quarter boundaries
q_start = start_of_quarter(2024, 2)  # 2024-04-01 00:00:00
q_end = end_of_quarter(2024, 2)      # 2024-06-30 23:59:59
```

### Additional Utility Functions

```python
from dateutils.dateutils import (
    age_in_years, days_until_weekend, days_since_weekend,
    get_week_number, time_until_next_occurrence
)
from datetime import date, datetime

# Calculate age in years
birth_date = date(1990, 6, 15)
age = age_in_years(birth_date, date(2024, 6, 20))  # 34 years old

# Weekend-related functions
monday = date(2024, 6, 3)
days_to_weekend = days_until_weekend(monday)  # 5 days until Saturday
days_from_weekend = days_since_weekend(monday)  # 1 day since Sunday

# Get ISO week number
week_num = get_week_number(date(2024, 6, 6))  # Week number (1-53)

# Calculate time until next occurrence
target_time = datetime(2024, 6, 6, 15, 30, 0)  # 3:30 PM today/tomorrow
time_delta = time_until_next_occurrence(target_time)  # Time until next 3:30 PM
```

### Memory-Efficient Date Ranges

```python
from dateutils.dateutils import date_range, date_range_generator
from datetime import date

# Standard date range (good for small ranges)
start = date(2024, 1, 1)
end = date(2024, 1, 10)
dates = date_range(start, end)  # Returns list of dates

# Memory-efficient generator (good for large ranges)
large_end = date(2024, 12, 31)
date_gen = date_range_generator(start, large_end)  # Returns generator

# Process large ranges without memory issues
for dt in date_gen:
    if dt.month == 6:  # Only process June dates
        print(dt)
        break
```

### Human-readable Dates

```python
from dateutils.dateutils import pretty_date
from datetime import datetime, timedelta

# Format a datetime as a human-readable string
now = datetime.now()
an_hour_ago = now - timedelta(hours=1)
a_day_ago = now - timedelta(days=1)

pretty_date(an_hour_ago)  # "an hour ago"
pretty_date(a_day_ago)    # "Yesterday"
```

### Error Handling and Validation

The library now includes comprehensive input validation with helpful error messages:

```python
from datetime import date
from zoneinfo import ZoneInfoNotFoundError

from dateutils.dateutils import now_in_timezone, start_of_quarter, workdays_between

# Invalid quarter raises ValueError
try:
    start_of_quarter(2024, 5)  # Quarters must be 1-4
except ValueError as e:
    print(e)  # "Quarter must be between 1 and 4, got 5"

# Invalid date ordering raises ValueError
try:
    workdays_between(date(2024, 6, 10), date(2024, 6, 1))  # end < start
except ValueError as e:
    print(e)  # "start_date (2024-06-10) must be <= end_date (2024-06-01)"

# Invalid timezone names raise ZoneInfoNotFoundError
try:
    now_in_timezone("Invalid/Timezone")
except ZoneInfoNotFoundError as e:
    print(e)  # e.g., "No time zone found with key Invalid/Timezone"
```

## Performance Features

- **Cached Holiday Calculations**: US federal holidays are cached for better performance when called multiple times
- **Memory-Efficient Generators**: Use `date_range_generator()` for large date ranges
- **Optimized UTC Operations**: Improved performance for timestamp operations
- **Input Validation**: Early validation prevents expensive operations on invalid data

## Running Tests

### Makefile
```sh
make init # ensures uv is installed
make deps
make test
make lint
make format
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
