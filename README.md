# DateUtils Python

A comprehensive collection of date and time utilities for Python applications.

## Features

- **UTC Operations**: Easily work with UTC timestamps and dates
- **Date/Time Parsing**: Parse dates and times from strings in various formats
- **Timezone Handling**: Convert between timezones with ease
- **Business Days**: Calculate business days with support for holidays
- **Quarter/Month/Week Operations**: Helpers for working with larger time spans
- **Date Formatting**: Convert dates to various string formats including ISO 8601
- **Human-readable Dates**: Generate user-friendly date strings like "2 hours ago"

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
from dateutils.dateutils import workdays_between, add_business_days
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
```

### Date Parsing and Formatting

```python
from dateutils.dateutils import parse_date, parse_datetime, to_iso8601

# Parse a date string (tries multiple formats)
dt = parse_date("2024-06-06")  # Returns date object
dt = parse_date("06/06/2024")  # Also works

# Parse ISO 8601 datetime
dt = parse_iso8601("2024-06-06T12:30:45Z")  # With timezone
dt = parse_iso8601("2024-06-06")  # Date only

# Format as ISO 8601
iso_str = to_iso8601(dt)  # e.g., "2024-06-06T12:30:45+00:00"
```

### Timezone Handling

```python
from dateutils.dateutils import now_in_timezone, convert_timezone

# Get current time in a timezone
nyc_now = now_in_timezone("America/New_York")

# Convert between timezones
from datetime import datetime, timezone
utc_dt = datetime(2024, 6, 6, 12, 0, 0, tzinfo=timezone.utc)
tokyo_dt = convert_timezone(utc_dt, "Asia/Tokyo")
```

### Quarter and Month Operations

```python
from dateutils.dateutils import date_to_quarter, date_to_start_of_quarter
from datetime import datetime

# Get quarter for a date
dt = datetime(2024, 5, 15)
quarter = date_to_quarter(dt)  # Returns 2 (Q2)

# Get start of quarter
start_date = date_to_start_of_quarter(dt)  # Returns 2024-04-01
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
