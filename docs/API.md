# DateUtils Python — API Reference

This is the complete public API reference for `dateutils`. Every name in
`dateutils.__all__` is documented here, and the Python examples are executed
by `make check` alongside the module doctests.

Quick orientation:

- **Standard library only** — no runtime dependencies beyond Python's stdlib.
- **Naive vs aware** — functions that accept datetimes treat a value without
  a usable UTC offset as UTC (or as the relevant target zone's local wall
  time, where documented). Aware values always represent an instant.
- **DST transitions** — repeated fall-back times carry a `fold` attribute
  (`fold=0` = first occurrence, `fold=1` = second); nonexistent
  spring-forward times normalize forward unless a function documents a
  different policy.
- **Booleans** — quarter numbers and `pretty_date` timestamp arguments
  reject `bool` values (`True`/`False` subclass `int` but are never valid).

## Constants

### `DAYS_IN_MONTH_APPROX`

The approximate number of days in a month (`30`). Useful for coarse
calculations that do not need calendar accuracy.

### `DAYS_IN_MONTH_MAX`

The maximum number of days in any month (`31`).

### `DAYS_IN_WEEK`

The number of days in a week (`7`).

### `DAYS_IN_YEAR`

The number of days in a non-leap year (`365`).

### `MONTHS_IN_QUARTER`

The number of months in a quarter (`3`).

### `MONTHS_IN_YEAR`

The number of months in a year (`12`).

### `QUARTERS_IN_YEAR`

The number of quarters in a year (`4`).

### `RECENT_SECONDS`

The "just now" threshold for `pretty_date` (`10` seconds).

### `SECONDS_IN_DAY`

The number of seconds in a day (`86400`).

### `SECONDS_IN_HOUR`

The number of seconds in an hour (`3600`).

### `SECONDS_IN_MINUTE`

The number of seconds in a minute (`60`).

### `WEEKDAYS_IN_WEEK`

The number of workdays in a standard Monday–Friday week (`5`).

## Exceptions

### `ParseError`

Raised by the strict parsing functions (`parse_date`, `parse_datetime`,
`parse_iso8601`) when an input value cannot be parsed or contains invalid
values. All arguments are keyword-only:

- `parser` — name of the parser that failed.
- `value` — the input string that could not be parsed.
- `reason` — human-readable explanation of the failure.
- `attempted_formats` — optional collection of format strings that were
  tried.

```python
from dateutils import ParseError, parse_date

try:
    parse_date("not-a-date")
except ParseError as exc:
    print(exc.parser, "|", exc.reason)
```

### `InvalidTimezoneError`

Raised when a timezone name cannot be resolved. Subclasses both
`ValueError` and `zoneinfo.ZoneInfoNotFoundError`, so callers catching either
exception keep working. Raised by every timezone function that accepts an
IANA name.

```python
from dateutils import InvalidTimezoneError, now_in_timezone

try:
    now_in_timezone("Invalid/Timezone")
except InvalidTimezoneError as exc:
    print(type(exc).__mro__[1].__name__, "/", type(exc).__mro__[2].__name__)
```

## UTC and Epoch Operations

### `utc_now_seconds`

Return the current time in seconds since the epoch, in UTC.

```python
from dateutils import utc_now_seconds

print(utc_now_seconds() > 1_700_000_000)
```

### `utc_today`

Return the current date in UTC.

```python
from dateutils import utc_today

print(utc_today().year >= 2024)
```

### `epoch_s`

Convert a datetime to whole Unix seconds, flooring fractional seconds.
Datetimes with a usable UTC offset are converted to UTC first; other
datetimes are assumed to be UTC.

```python
from datetime import datetime, timezone
from dateutils import epoch_s

epoch_s(datetime(2023, 10, 26, 12, 0, 0, tzinfo=timezone.utc))
# 1698321600

epoch_s(datetime(2023, 10, 26, 12, 0, 0))  # naive is assumed UTC
# 1698321600
```

### `utc_from_timestamp`

Convert a Unix timestamp to a timezone-aware UTC datetime. Raises
`ValueError` for invalid timestamps.

```python
from dateutils import utc_from_timestamp

utc_from_timestamp(1698321600)
# datetime.datetime(2023, 10, 26, 12, 0, tzinfo=datetime.timezone.utc)
```

### `utc_truncate_epoch_day`

Truncate a timestamp to the start of its day in UTC. Raises `ValueError`
for invalid timestamps.

```python
from dateutils import utc_truncate_epoch_day

utc_truncate_epoch_day(1698321600)  # 2023-10-26 12:00 UTC -> 2023-10-26 00:00 UTC
# 1698278400
```

### `datetime_to_utc`

Convert a datetime to a timezone-aware UTC datetime. Naive datetimes are
assumed to be UTC; aware datetimes are converted as instants. During a
fall-back transition, `fold` selects which occurrence is converted.

```python
from datetime import datetime
from zoneinfo import ZoneInfo
from dateutils import datetime_to_utc

ny = datetime(2024, 7, 22, 10, 0, 0, tzinfo=ZoneInfo("America/New_York"))
print(datetime_to_utc(ny).hour)  # 10 EDT = 14 UTC
# 14
```

## Date Parsing and Formatting

### `parse_date`

Parse a date string using common formats, or an explicit `formats` list.
Ambiguous numeric dates (such as `"03/04/2024"`) follow the current locale
by default; pass `dayfirst` to fix the order or `ambiguous="reject"` to
reject them. Raises `ParseError` when parsing fails. `dayfirst` and
`ambiguous` only apply when `formats` is `None`.

```python
from dateutils import parse_date

parse_date("2024-07-22")
# datetime.date(2024, 7, 22)

parse_date("22/07/2024", dayfirst=True)  # European order
# datetime.date(2024, 7, 22)
```

### `parse_datetime`

Parse a datetime string using common formats, or an explicit `formats`
list. Default parsing accepts timezone-aware values (`Z` designator or
numeric offsets such as `+02:00` / `-0500`) and one to six fractional-second
digits. Raises `ParseError` when parsing fails. `dayfirst` and `ambiguous`
only apply when `formats` is `None`.

```python
from dateutils import parse_datetime

parse_datetime("2024-06-06 12:30:45.123456")
# datetime.datetime(2024, 6, 6, 12, 30, 45, 123456)

parse_datetime("2024-06-06T12:30:00+02:00")
# datetime.datetime(2024, 6, 6, 12, 30, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200)))
```

### `parse_iso8601`

Parse an ISO 8601 / RFC 3339 string: date-only, date and time with optional
seconds, space or lowercase `t`/`z` separators, fractional seconds, and
timezone offsets (`Z`, `+02:00`, `-0500`). Fractional seconds are truncated
to microsecond precision (six digits). Raises `ParseError` for unsupported
shapes.

```python
from dateutils import parse_iso8601

parse_iso8601("2024-06-06 12:30Z")
# datetime.datetime(2024, 6, 6, 12, 30, tzinfo=datetime.timezone.utc)
```

### `to_iso8601`

Convert a date or datetime to an ISO 8601 string.

```python
from datetime import datetime, timezone
from dateutils import to_iso8601

to_iso8601(datetime(2024, 6, 6, 12, 30, 0, tzinfo=timezone.utc))
# '2024-06-06T12:30:00+00:00'
```

### `format_date`

Format a date or datetime using `strftime`-style `format_str`
(`"%Y-%m-%d"` by default).

```python
from datetime import date
from dateutils import format_date

format_date(date(2024, 7, 22))
# '2024-07-22'

format_date(date(2024, 7, 22), "%B %d, %Y")
# 'July 22, 2024'
```

### `format_datetime`

Format a datetime using `strftime`-style `format_str`
(`"%Y-%m-%d %H:%M:%S"` by default).

```python
from datetime import datetime
from dateutils import format_datetime

format_datetime(datetime(2024, 7, 22, 14, 30, 45))
# '2024-07-22 14:30:45'
```

## Date Boundaries, Periods, and Generators

### `start_of_year`

```python
from dateutils import start_of_year

start_of_year(2024)
# datetime.datetime(2024, 1, 1, 0, 0)
```

### `end_of_year`

```python
from dateutils import end_of_year

end_of_year(2024)
# datetime.datetime(2024, 12, 31, 23, 59, 59, 999999)
```

### `start_of_month`

Return the start of the month at `00:00:00`. Raises `ValueError` for an
invalid year or month.

```python
from dateutils import start_of_month

start_of_month(2024, 7)
# datetime.datetime(2024, 7, 1, 0, 0)
```

### `end_of_month`

Return the end of the month at `23:59:59.999999`. Raises `ValueError` for
an invalid year or month.

```python
from dateutils import end_of_month

end_of_month(2024, 2)  # leap year
# datetime.datetime(2024, 2, 29, 23, 59, 59, 999999)
```

### `start_of_quarter`

Return the start of the quarter at `00:00:00`. Raises `ValueError` if
`q` is not between 1 and 4 or is a boolean.

```python
from dateutils import start_of_quarter

start_of_quarter(2024, 3)
# datetime.datetime(2024, 7, 1, 0, 0)
```

### `end_of_quarter`

Return the end of the quarter at `23:59:59.999999`. Raises `ValueError` if
`q` is not between 1 and 4 or is a boolean.

```python
from dateutils import end_of_quarter

end_of_quarter(2024, 3)
# datetime.datetime(2024, 9, 30, 23, 59, 59, 999999)
```

### `date_to_quarter`

Return the quarter (1–4) containing the date.

```python
from datetime import datetime
from dateutils import date_to_quarter

date_to_quarter(datetime(2024, 5, 15))
# 2
```

### `date_to_start_of_quarter`

Return the first date of the quarter containing the date.

```python
from datetime import datetime
from dateutils import date_to_start_of_quarter

date_to_start_of_quarter(datetime(2024, 5, 15))
# datetime.date(2024, 4, 1)
```

### `get_quarter_start_end`

Return the inclusive start and end dates of a quarter. Raises `ValueError`
if `quarter` is not between 1 and 4 or is a boolean.

```python
from dateutils import get_quarter_start_end

get_quarter_start_end(2024, 2)
# (datetime.date(2024, 4, 1), datetime.date(2024, 6, 30))
```

### `get_days_in_month`

Return the number of days in a month. Raises `ValueError` for an invalid
year or month.

```python
from dateutils import get_days_in_month

get_days_in_month(2024, 2)
# 29
```

### `get_week_number`

Return the ISO week number (1–53) of the date.

```python
from datetime import date
from dateutils import get_week_number

get_week_number(date(2024, 6, 6))
# 23
```

### `is_leap_year`

Return `True` when the year is a leap year.

```python
from dateutils import is_leap_year

is_leap_year(2024)
# True
```

### `generate_years`

Yield years from `start_year` (default: the current year) toward `until`
(inclusive), moving forward or backward.

```python
from dateutils import generate_years

list(generate_years(until=2025, start_year=2023))
# [2023, 2024, 2025]
```

### `generate_months`

Yield `(month, year)` tuples from the month of `start_date` (default: the
current month) toward `until_year`/`until_m` (inclusive). Raises
`ValueError` if `until_m` is not between 1 and 12.

```python
from datetime import date
from dateutils import generate_months

list(generate_months(until_year=2024, until_m=3, start_date=date(2024, 11, 30)))
# [(11, 2024), (10, 2024), (9, 2024), (8, 2024), (7, 2024), (6, 2024), (5, 2024), (4, 2024), (3, 2024)]
```

### `generate_quarters`

Yield `(quarter, year)` tuples from the starting quarter toward
`until_year`/`until_q` (inclusive), moving forward or backward. `until_q`
and `start_quarter` must be between 1 and 4; booleans are rejected.

```python
from dateutils import generate_quarters

list(generate_quarters(until_year=2024, until_q=2, start_year=2024, start_quarter=4))
# [(4, 2024), (3, 2024), (2, 2024)]
```

### `generate_weeks`

Yield inclusive `(week_start, week_end)` pairs from the week of
`start_date` (default: today) toward `until_date`, stopping once the week
containing `until_date` is yielded. When `until_date` is `None`, weeks are
generated backwards. Weeks run Sunday→Saturday by default; set
`start_on_monday=True` for Monday→Sunday. Weeks at the representable date
limits clip at `date.min` and `date.max`. Raises `ValueError` if `count` is
negative.

```python
from datetime import date
from dateutils import generate_weeks

list(generate_weeks(count=2, until_date=date(2024, 1, 10), start_date=date(2024, 1, 3)))
# [(datetime.date(2023, 12, 31), datetime.date(2024, 1, 6)),
#  (datetime.date(2024, 1, 7), datetime.date(2024, 1, 13))]

list(
    generate_weeks(
        count=2,
        until_date=date(2024, 1, 10),
        start_date=date(2024, 1, 3),
        start_on_monday=True,
    )
)
# [(datetime.date(2024, 1, 1), datetime.date(2024, 1, 7)),
#  (datetime.date(2024, 1, 8), datetime.date(2024, 1, 14))]
```

### `date_range`

Return a list of dates from `start_date` to `end_date`, inclusive. Raises
`ValueError` if `start_date` is after `end_date` or the range exceeds ten
years.

```python
from datetime import date
from dateutils import date_range

date_range(date(2024, 1, 1), date(2024, 1, 3))
# [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2), datetime.date(2024, 1, 3)]
```

### `date_range_generator`

Like `date_range`, but yield dates lazily for memory-efficient iteration
over large ranges. Raises `ValueError` if `start_date` is after
`end_date`.

```python
from datetime import date
from dateutils import date_range_generator

list(date_range_generator(date(2024, 1, 1), date(2024, 1, 3)))
# [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2), datetime.date(2024, 1, 3)]
```

### `datetime_start_of_day`

Return the start of the day at midnight (`00:00:00`).

```python
from datetime import date
from dateutils import datetime_start_of_day

datetime_start_of_day(date(2024, 7, 22))
# datetime.datetime(2024, 7, 22, 0, 0)
```

### `datetime_end_of_day`

Return the end of the day at `23:59:59.999999`.

```python
from datetime import date
from dateutils import datetime_end_of_day

datetime_end_of_day(date(2024, 7, 22))
# datetime.datetime(2024, 7, 22, 23, 59, 59, 999999)
```

### `start_of_week`

Return the inclusive start of the week containing the date. Weeks run
Sunday→Saturday by default; set `start_on_monday=True` to match
`generate_weeks`. The result is a plain date, not a clock time. A
`datetime` input is normalized to its local calendar date with no UTC
conversion, and weeks at the representable date limits clip at `date.min`
and `date.max`.

```python
from datetime import date
from dateutils import start_of_week

start_of_week(date(2024, 7, 4))  # Thursday -> Sunday
# datetime.date(2024, 6, 30)

start_of_week(date(2024, 7, 4), start_on_monday=True)
# datetime.date(2024, 7, 1)
```

### `end_of_week`

Return the inclusive end of the week containing the date, with the same
defaults and policies as `start_of_week`.

```python
from datetime import date
from dateutils import end_of_week

end_of_week(date(2024, 7, 4))  # Thursday -> Saturday
# datetime.date(2024, 7, 6)

end_of_week(date(2024, 7, 4), start_on_monday=True)
# datetime.date(2024, 7, 7)
```

## Business Days, Holidays, and Calendars

The module-level business-day functions share one policy: `datetime` inputs
and holiday values are normalized to their displayed local calendar dates —
never converted to UTC — and ranges are inclusive of both endpoints. All
functions raise `TypeError` if `holidays` contains values that are neither
`date` nor `datetime`.

### `is_business_day`

Return `True` when the date is a weekday that is not in `holidays`. The
holiday collection is normalized on every call (linear in its size), and
generators are consumed.

```python
from datetime import date
from dateutils import is_business_day

is_business_day(date(2024, 7, 22))  # Monday
# True

is_business_day(date(2024, 7, 27))  # Saturday
# False
```

### `workdays_between`

Count workdays (Monday–Friday) between two dates, inclusive, using an O(1)
algorithm for weekdays and O(h) for holiday exclusion. Raises `ValueError`
if `start_date` is after `end_date`. Holiday generators are consumed on
first use — convert to a list to reuse them.

```python
from datetime import date
from dateutils import workdays_between

workdays_between(date(2024, 7, 1), date(2024, 7, 7))  # Mon..Fri
# 5

us_holidays = [date(2024, 7, 4)]
workdays_between(date(2024, 7, 1), date(2024, 7, 7), holidays=us_holidays)
# 4
```

### `add_business_days`

Add `num_days` business days (negative values go backward), skipping
weekends and holidays. Raises `ValueError` if `num_days` is outside
−10000..10000 and `TypeError` if `num_days` is a boolean or not an integer.
A zero count returns the input unchanged.

```python
from datetime import date
from dateutils import add_business_days

add_business_days(date(2024, 7, 1), 3)
# datetime.date(2024, 7, 4)

add_business_days(date(2024, 7, 3), 3, holidays=[date(2024, 7, 4)])
# datetime.date(2024, 7, 8)
```

### `next_business_day`

Return the first business day strictly after `dt`, skipping weekends and
holidays.

```python
from datetime import date
from dateutils import next_business_day

next_business_day(date(2024, 7, 5))  # Friday -> Monday
# datetime.date(2024, 7, 8)
```

### `previous_business_day`

Return the first business day strictly before `dt`, skipping weekends and
holidays.

```python
from datetime import date
from dateutils import previous_business_day

previous_business_day(date(2024, 7, 8))  # Monday -> Friday
# datetime.date(2024, 7, 5)
```

### `get_us_federal_holidays`

Return the US federal holidays for a year, sorted chronologically. Supports
restricting `holiday_types` (all eleven types by default) and shifting
fixed-date holidays to their federally observed weekday with `observed`.
Results are cached. Raises `ValueError` for years before 1971 or unknown
holiday types, and `TypeError` if `holiday_types` is a single string or
contains non-string values.

```python
from dateutils import get_us_federal_holidays

get_us_federal_holidays(2024, holiday_types=["INDEPENDENCE_DAY"])
# [datetime.date(2024, 7, 4)]
```

### `get_us_federal_holidays_between`

Return US federal holidays between two dates, inclusive. Unlike per-year
calls, this includes observed holidays that cross a year boundary (such as
New Year's Day observed on December 31 of the previous year). `datetime`
inputs use their calendar date. Raises `ValueError` if `start_date` is
after `end_date` or the range starts before 1971, and the holiday-type
validation matches `get_us_federal_holidays`.

```python
from datetime import date
from dateutils import get_us_federal_holidays_between

get_us_federal_holidays_between(date(2027, 12, 1), date(2027, 12, 31), observed=True)
# [datetime.date(2027, 12, 24), datetime.date(2027, 12, 31)]
```

### `get_us_federal_holidays_list`

Backward-compatible alias for `get_us_federal_holidays`, which now accepts
`list[str]` directly. Unknown holiday types raise `ValueError`.

```python
from dateutils import get_us_federal_holidays_list

get_us_federal_holidays_list(2024, holiday_types=["LABOR_DAY"])
# [datetime.date(2024, 9, 2)]
```

### `BusinessCalendar`

`BusinessCalendar(weekdays: Iterable[int] = (0, 1, 2, 3, 4), holidays: Iterable[date | datetime] | None = None)`

An immutable custom workweek and fixed holiday set. Captures a workweek as
a set of weekday numbers (Monday is 0, Sunday is 6) and a fixed set of
holiday dates, then exposes the business-day operations as methods.
`datetime` inputs and holiday values are normalized to their displayed
local calendar dates — never converted to UTC. Counting and movement
include both endpoints, match the module-level Monday–Friday functions when
constructed with the default arguments, and ignore configured holidays
even when they fall inside the workweek.

Constructor validation raises `TypeError` or `ValueError` for non-integer
or out-of-range weekday values, raises `ValueError` for an empty workweek,
and raises `TypeError` for holiday values that are neither `date` nor
`datetime`. Instances are frozen value objects with value equality.

```python
from datetime import date, datetime
from dateutils import BusinessCalendar

# Sun-Thu workweek with July 4th 2024 as a holiday
calendar = BusinessCalendar(
    weekdays=(6, 0, 1, 2, 3),
    holidays=[date(2024, 7, 4)],
)

calendar.is_business_day(date(2024, 7, 3))
# True

calendar.workdays_between(date(2024, 7, 1), date(2024, 7, 7))
# 4  -> Mon, Tue, Wed, Sun; July 4th is a holiday and Fri/Sat are weekend

calendar.add_business_days(date(2024, 7, 3), 1)
# datetime.date(2024, 7, 7)
```

#### is_business_day

`is_business_day(self, dt: date) -> bool`

Return `True` when the date is in the configured workweek and not in the
configured holidays.

```python
from datetime import date
from dateutils import BusinessCalendar

calendar = BusinessCalendar(weekdays=(6, 0, 1, 2, 3), holidays=[date(2024, 7, 4)])
calendar.is_business_day(date(2024, 7, 4))
# False
```

#### workdays_between

`workdays_between(self, start_date: date, end_date: date) -> int`

Count workdays between two dates, inclusive, using the configured workweek
and holidays. Raises `ValueError` if `start_date` is after `end_date`.

```python
from datetime import date
from dateutils import BusinessCalendar

BusinessCalendar().workdays_between(date(2024, 7, 1), date(2024, 7, 7))
# 5
```

#### add_business_days

`add_business_days(self, dt: date, num_days: int) -> date`

Add `num_days` business days (negative values go backward) using the
configured workweek and holidays. Raises `ValueError` if `num_days` is
outside −10000..10000 and `TypeError` if `num_days` is a boolean or not an
integer.

```python
from datetime import date
from dateutils import BusinessCalendar

calendar = BusinessCalendar(weekdays=(6, 0, 1, 2, 3), holidays=[date(2024, 11, 28)])
calendar.add_business_days(date(2024, 11, 27), 1)
# datetime.date(2024, 12, 1)
```

#### next_business_day

`next_business_day(self, dt: date) -> date`

Return the first configured business day strictly after `dt`.

```python
from datetime import date
from dateutils import BusinessCalendar

BusinessCalendar().next_business_day(date(2024, 7, 5))
# datetime.date(2024, 7, 8)
```

#### previous_business_day

`previous_business_day(self, dt: date) -> date`

Return the first configured business day strictly before `dt`.

```python
from datetime import date
from dateutils import BusinessCalendar

BusinessCalendar().previous_business_day(date(2024, 7, 8))
# datetime.date(2024, 7, 5)
```

## Relative Time, Scheduling, and HTTP Dates

### `pretty_date`

Format a timestamp as a natural-language relative time string ("2 hours
ago", "Yesterday", "in 2 hours"). Accepts:

- `int`/`float` Unix timestamps, interpreted as UTC.
- `datetime` values — naive values are assumed UTC, aware values are
  converted to UTC.
- `None`, which returns `"just now"`.

`now_override` pins the reference "now" (useful for deterministic output)
and follows the same naive-UTC / aware-instant rules. `bool` values are
rejected for both timestamp arguments.

```python
from datetime import datetime, timedelta, timezone
from dateutils import pretty_date

now = datetime(2024, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
pretty_date(now - timedelta(hours=2), now_override=now)
# '2 hours ago'

pretty_date(now - timedelta(days=1), now_override=now)
# 'Yesterday'
```

### `age_in_years`

Calculate age in whole years as of `as_of_date` (default: today). Leap-day
birthdays (Feb 29) are considered to fall on Feb 28 in non-leap years.
Raises `ValueError` if `birth_date` is in the future.

```python
from datetime import date
from dateutils import age_in_years

age_in_years(date(1990, 6, 15), as_of_date=date(2024, 6, 20))
# 34
```

### `is_weekend`

Return `True` when the date is a Saturday or Sunday.

```python
from datetime import date
from dateutils import is_weekend

is_weekend(date(2024, 7, 20))  # Saturday
# True

is_weekend(date(2024, 7, 22))  # Monday
# False
```

### `days_until_weekend`

Return the number of days until the next Saturday (0 when the date is
already a weekend).

```python
from datetime import date
from dateutils import days_until_weekend

days_until_weekend(date(2024, 6, 3))  # Monday
# 5
```

### `days_since_weekend`

Return the number of days since the last Sunday (0 when the date is
already a weekend).

```python
from datetime import date
from dateutils import days_since_weekend

days_since_weekend(date(2024, 6, 3))  # Monday
# 1
```

### `next_occurrence`

Return the next daily occurrence of a time-of-day, strictly after
`from_time` (or the current time when omitted). The date portion of a
`datetime` target is ignored; the target's time-of-day drives the result.
Naive inputs produce a naive result; aware inputs produce an occurrence in
the target timezone, and when only one input is aware, the naive input is
interpreted in the aware input's timezone. Nonexistent spring-forward times
roll forward; ambiguous fall-back times honor `target_time.fold`.

```python
from datetime import datetime
from dateutils import next_occurrence

next_occurrence(
    datetime(2024, 6, 6, 15, 30),
    from_time=datetime(2024, 6, 6, 14, 0),
)
# datetime.datetime(2024, 6, 6, 15, 30)
```

### `time_until_next_occurrence`

Return the `timedelta` until the next daily occurrence of a time-of-day.
Always positive; usually at most 24 hours, but up to 25 hours when a DST
fall-back transition in the target timezone lies in between. Timezone
handling matches `next_occurrence`.

```python
from datetime import datetime, time
from dateutils import time_until_next_occurrence

time_until_next_occurrence(
    time(15, 30),
    from_time=datetime(2024, 6, 6, 14, 0),
)
# datetime.timedelta(seconds=5400)
```

### `httpdate`

Convert a datetime to an RFC 7231 HTTP date string, always in GMT/UTC.
Datetimes with a usable UTC offset are converted first; other datetimes are
assumed to be UTC. Uses `email.utils.format_datetime` to avoid
locale-dependent names.

```python
from datetime import datetime, timezone
from dateutils import httpdate

httpdate(datetime(2024, 7, 22, 14, 30, 0, tzinfo=timezone.utc))
# 'Mon, 22 Jul 2024 14:30:00 GMT'
```

## Timezone Operations

All functions accept either an IANA timezone name or a `tzinfo` instance.
Invalid names raise `InvalidTimezoneError` (a subclass of both `ValueError`
and `zoneinfo.ZoneInfoNotFoundError`).

### `now_in_timezone`

Return the current instant as an aware datetime in the given timezone.

```python
from dateutils import now_in_timezone

print(now_in_timezone("America/New_York").tzinfo is not None)
```

### `today_in_timezone`

Return the current calendar date in the given timezone.

```python
from dateutils import today_in_timezone

print(today_in_timezone("Asia/Tokyo").year >= 2024)
```

### `convert_timezone`

Convert an aware datetime to another timezone. Raises `ValueError` if the
input has no usable UTC offset and `TypeError` if `to_tz` is neither a name
nor a `tzinfo` instance. During fall-back, the result honors the input's
`fold`; during spring-forward, nonexistent local times normalize forward.

```python
from datetime import datetime, timezone
from dateutils import convert_timezone

utc_time = datetime(2024, 7, 22, 14, 30, 0, tzinfo=timezone.utc)
print(convert_timezone(utc_time, "America/Los_Angeles"))
# 2024-07-22 07:30:00-07:00
```

### `localize_datetime`

Attach a timezone to a naive datetime treated as `tz` local wall time,
with explicit DST-transition policies. Raises `ValueError` if the input
already has a usable UTC offset. `ambiguous` resolves repeated fall-back
times (`"raise"`, `"earliest"`, or `"latest"`); `nonexistent` resolves
missing spring-forward times (`"raise"` or `"shift_forward"`).

```python
from datetime import datetime
from dateutils import localize_datetime

# 1:30 AM occurs twice on 2024-11-03 in US Eastern
localize_datetime(datetime(2024, 11, 3, 1, 30), "America/New_York", ambiguous="earliest")
# datetime.datetime(2024, 11, 3, 1, 30, tzinfo=zoneinfo.ZoneInfo(key='America/New_York'))
```

### `get_available_timezones`

Return the list of available IANA timezone names.

```python
from dateutils import get_available_timezones

zones = get_available_timezones()
print("America/New_York" in zones)
```

### `get_timezone_offset`

Return the UTC offset of a timezone as a `timedelta`. `at` selects the
instant: an aware value is converted to `tz`; a naive value is treated as
`tz` local wall time (repeated times honor `fold`, nonexistent times shift
forward). Omitted, it uses the current moment. Raises
`InvalidTimezoneError` for unknown names and `TypeError` for invalid `tz`
or `at` types.

```python
from datetime import datetime, timedelta
from dateutils import get_timezone_offset

get_timezone_offset("America/New_York", at=datetime(2024, 1, 15, 12)) == timedelta(hours=-5)
# True

get_timezone_offset("America/New_York", at=datetime(2024, 7, 15, 12)) == timedelta(hours=-4)
# True
```

### `format_timezone_offset`

Return the UTC offset of a timezone as a `"+HH:MM"` / `"-HH:MM"` string,
with the same `at` semantics as `get_timezone_offset`. A `":SS"` seconds
component is included when the offset is not a whole number of minutes, and
a `".ffffff"` fraction when the offset has sub-second precision.

```python
from datetime import datetime, timedelta, timezone
from dateutils import format_timezone_offset

format_timezone_offset(timezone(timedelta(hours=5, minutes=45)))
# '+05:45'

format_timezone_offset("America/New_York", at=datetime(2024, 1, 15, 12))
# '-05:00'

format_timezone_offset(timezone(timedelta(hours=5, minutes=45, seconds=30)))
# '+05:45:30'
```
