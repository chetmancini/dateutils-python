import datetime
import locale
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest
from freezegun import freeze_time

from dateutils.dateutils import (
    add_business_days,
    age_in_years,
    convert_timezone,
    date_range,
    date_range_generator,
    date_to_quarter,
    date_to_start_of_quarter,
    datetime_end_of_day,
    datetime_start_of_day,
    datetime_to_utc,
    days_since_weekend,
    days_until_weekend,
    end_of_month,
    end_of_quarter,
    end_of_year,
    epoch_s,
    format_date,
    format_datetime,
    format_timezone_offset,
    generate_months,
    generate_quarters,
    generate_weeks,
    generate_years,
    get_available_timezones,
    get_days_in_month,
    get_quarter_start_end,
    get_timezone_offset,
    get_us_federal_holidays,
    get_us_federal_holidays_list,
    get_week_number,
    httpdate,
    is_business_day,
    is_leap_year,
    is_weekend,
    next_business_day,
    now_in_timezone,
    parse_date,
    parse_datetime,
    parse_iso8601,
    previous_business_day,
    start_of_month,
    start_of_quarter,
    start_of_year,
    time_until_next_occurrence,
    to_iso8601,
    today_in_timezone,
    utc_from_timestamp,
    utc_truncate_epoch_day,
    workdays_between,
)


@freeze_time("2024-03-27")
def test_utc_today() -> None:
    """Test that utc_today returns the current UTC date."""
    from dateutils.dateutils import utc_today

    assert utc_today() == datetime.date(2024, 3, 27)


@freeze_time("2024-03-27 14:30:45", tz_offset=0)
def test_utc_now_seconds() -> None:
    """Test that utc_now_seconds returns the correct Unix timestamp."""
    from dateutils.dateutils import utc_now_seconds

    expected_timestamp = 1711549845
    assert utc_now_seconds() == expected_timestamp


def test_utc_truncate_epoch_day() -> None:
    """Test truncating a timestamp to the start of the day in UTC."""
    from dateutils.dateutils import utc_truncate_epoch_day

    # Timestamp for 2024-03-27 15:30:45 UTC
    ts = 1711639845

    # Expected: 2024-03-27 00:00:00 UTC
    expected = 1711584000

    assert utc_truncate_epoch_day(ts) == expected


def test_epoch_s() -> None:
    assert 1397488604 == epoch_s(datetime.datetime(2014, 4, 14, 15, 16, 44))


def test_utc_from_timestamp() -> None:
    """Test converting a timestamp to a datetime in UTC timezone."""
    from dateutils.dateutils import utc_from_timestamp

    # Timestamp for 2024-03-27 15:30:45 UTC
    ts = 1711639845

    dt = utc_from_timestamp(ts)
    assert dt.year == 2024
    assert dt.month == 3
    assert dt.day == 28
    assert dt.hour == 15
    assert dt.minute == 30
    assert dt.second == 45
    assert dt.tzinfo == datetime.timezone.utc


def test_datetime_start_of_day() -> None:
    day = datetime.datetime(2016, 11, 23, 5, 4, 3).date()
    assert datetime_start_of_day(day) == datetime.datetime(2016, 11, 23, 0, 0, 0)


def test_datetime_end_of_day() -> None:
    day = datetime.datetime(2016, 11, 23, 5, 4, 3).date()
    assert datetime_end_of_day(day) == datetime.datetime(2016, 11, 23, 23, 59, 59, 999999)


def test_start_of_year() -> None:
    assert datetime.datetime(2018, 1, 1) == start_of_year(2018)


def test_end_of_year() -> None:
    assert datetime.datetime(2018, 12, 31, 23, 59, 59, 999999) == end_of_year(2018)


@freeze_time("2018-10-12")
def test_generate_years() -> None:
    assert [2018, 2017, 2016, 2015, 2014] == list(generate_years(until=2014))


def test_generate_years_forward() -> None:
    assert [2020, 2021, 2022] == list(generate_years(until=2022, start_year=2020))


def test_generate_years_same_year() -> None:
    """Test generate_years when start_year equals until (same year)."""
    assert [2024] == list(generate_years(until=2024, start_year=2024))


def test_is_leap_year() -> None:
    assert is_leap_year(2020)
    assert not is_leap_year(2021)


@freeze_time("2018-9-12")
def test_generate_quarters() -> None:
    assert [
        (3, 2018),
        (2, 2018),
        (1, 2018),
        (4, 2017),
        (3, 2017),
        (2, 2017),
        (1, 2017),
        (4, 2016),
        (3, 2016),
        (2, 2016),
    ] == list(generate_quarters(until_year=2016, until_q=2))


@freeze_time("2024-01-15")
def test_generate_quarters_natural_loop_exit() -> None:
    """Test generate_quarters when loop completes naturally without early return."""
    # Start from Q1 2024, generate until Q1 2024 (same quarter) - should yield just one
    quarters = list(generate_quarters(until_year=2024, until_q=1))
    assert quarters == [(1, 2024)]


def test_generate_quarters_forward_custom_start() -> None:
    quarters = list(generate_quarters(until_year=2025, until_q=2, start_year=2024, start_quarter=3))
    assert quarters == [(3, 2024), (4, 2024), (1, 2025), (2, 2025)]


def test_generate_quarters_invalid_until_q() -> None:
    """Invalid until_q values should raise ValueError."""
    with pytest.raises(ValueError, match="until_q must be between 1 and 4, got 0"):
        list(generate_quarters(until_year=2024, until_q=0))

    with pytest.raises(ValueError, match="until_q must be between 1 and 4, got 5"):
        list(generate_quarters(until_year=2024, until_q=5))


def test_generate_quarters_invalid_start_quarter() -> None:
    """Invalid start_quarter values should raise ValueError.

    Note: start_quarter=0 is falsy so it uses the default. We test with -1 and 5.
    """
    with pytest.raises(ValueError, match="start_quarter must be between 1 and 4, got -1"):
        list(generate_quarters(until_year=2024, until_q=1, start_year=2024, start_quarter=-1))

    with pytest.raises(ValueError, match="start_quarter must be between 1 and 4, got 5"):
        list(generate_quarters(until_year=2024, until_q=1, start_year=2024, start_quarter=5))


@freeze_time("2018-9-12")
def test_generate_months() -> None:
    assert [
        (9, 2018),
        (8, 2018),
        (7, 2018),
        (6, 2018),
        (5, 2018),
        (4, 2018),
        (3, 2018),
        (2, 2018),
        (1, 2018),
        (12, 2017),
        (11, 2017),
        (10, 2017),
        (9, 2017),
        (8, 2017),
    ] == list(generate_months(until_year=2017, until_m=8))


@freeze_time("2024-03-15")
def test_generate_months_natural_loop_exit() -> None:
    """Test generate_months when loop completes naturally without early return."""
    # Start from March 2024, generate until January 2024
    # This ensures we exhaust the outer loop (only year 2024) without early return
    # because until_m=1 means we yield all months from 3 down to 1
    months = list(generate_months(until_year=2024, until_m=1))
    assert months == [(3, 2024), (2, 2024), (1, 2024)]


def test_generate_months_same_month() -> None:
    """Test generate_months when start month equals target month."""
    start = datetime.date(2024, 6, 15)
    months = list(generate_months(until_year=2024, until_m=6, start_date=start))
    assert months == [(6, 2024)]


def test_generate_months_forward_custom_start() -> None:
    start = datetime.date(2023, 11, 15)
    months = list(generate_months(until_year=2024, until_m=2, start_date=start))
    assert months == [
        (11, 2023),
        (12, 2023),
        (1, 2024),
        (2, 2024),
    ]


@freeze_time("2018-9-12")
def test_generate_weeks() -> None:
    weeks = list(generate_weeks(count=2))
    assert weeks == [
        (datetime.date(2018, 9, 9), datetime.date(2018, 9, 15)),
        (datetime.date(2018, 9, 2), datetime.date(2018, 9, 8)),
    ]


@freeze_time("2018-9-12")
def test_generate_weeks_start_on_monday() -> None:
    weeks = list(generate_weeks(count=2, start_on_monday=True))
    assert weeks == [
        (datetime.date(2018, 9, 10), datetime.date(2018, 9, 16)),
        (datetime.date(2018, 9, 3), datetime.date(2018, 9, 9)),
    ]


@freeze_time("2024-07-22")
def test_generate_weeks_with_until_date() -> None:
    """Test generate_weeks with until_date parameter."""
    until = datetime.date(2024, 7, 10)
    weeks = list(generate_weeks(count=5, until_date=until))
    assert weeks == [
        (datetime.date(2024, 7, 21), datetime.date(2024, 7, 27)),
        (datetime.date(2024, 7, 14), datetime.date(2024, 7, 20)),
        (datetime.date(2024, 7, 7), datetime.date(2024, 7, 13)),
    ]

    # When until_date is in the future we walk forward
    future_until = datetime.date(2024, 8, 10)
    future_weeks = list(generate_weeks(count=5, until_date=future_until))
    assert future_weeks == [
        (datetime.date(2024, 7, 21), datetime.date(2024, 7, 27)),
        (datetime.date(2024, 7, 28), datetime.date(2024, 8, 3)),
        (datetime.date(2024, 8, 4), datetime.date(2024, 8, 10)),
    ]


def test_generate_weeks_custom_start_forward() -> None:
    """Custom start_date moving forward toward until_date."""
    start = datetime.date(2024, 1, 3)  # Wednesday
    until = datetime.date(2024, 1, 20)
    weeks = list(generate_weeks(count=4, start_date=start, until_date=until))
    assert weeks == [
        (datetime.date(2023, 12, 31), datetime.date(2024, 1, 6)),
        (datetime.date(2024, 1, 7), datetime.date(2024, 1, 13)),
        (datetime.date(2024, 1, 14), datetime.date(2024, 1, 20)),
    ]


def test_generate_weeks_custom_start_backward_monday() -> None:
    """Custom start_date moving backward with Monday-based weeks."""
    start = datetime.date(2024, 1, 20)
    until = datetime.date(2023, 12, 31)
    weeks = list(generate_weeks(count=5, start_date=start, until_date=until, start_on_monday=True))
    # Should include week containing until_date (Dec 25-31 contains Dec 31)
    assert weeks == [
        (datetime.date(2024, 1, 15), datetime.date(2024, 1, 21)),
        (datetime.date(2024, 1, 8), datetime.date(2024, 1, 14)),
        (datetime.date(2024, 1, 1), datetime.date(2024, 1, 7)),
        (datetime.date(2023, 12, 25), datetime.date(2023, 12, 31)),
    ]


def test_generate_weeks_start_equals_until() -> None:
    """Test generate_weeks when start_date equals until_date.

    When both dates are the same, direction=0 and exactly one week should be yielded.
    """
    same_date = datetime.date(2024, 7, 17)  # Wednesday

    # Sunday-based weeks (default)
    weeks = list(generate_weeks(count=10, start_date=same_date, until_date=same_date))
    assert len(weeks) == 1
    # July 17, 2024 (Wed) falls in week Sun Jul 14 - Sat Jul 20
    assert weeks == [(datetime.date(2024, 7, 14), datetime.date(2024, 7, 20))]

    # Monday-based weeks
    weeks_monday = list(generate_weeks(count=10, start_date=same_date, until_date=same_date, start_on_monday=True))
    assert len(weeks_monday) == 1
    # July 17, 2024 (Wed) falls in week Mon Jul 15 - Sun Jul 21
    assert weeks_monday == [(datetime.date(2024, 7, 15), datetime.date(2024, 7, 21))]

    # Test with a weekend date
    saturday = datetime.date(2024, 7, 20)
    weeks_sat = list(generate_weeks(count=10, start_date=saturday, until_date=saturday))
    assert len(weeks_sat) == 1
    # Saturday Jul 20 falls in week Sun Jul 14 - Sat Jul 20
    assert weeks_sat == [(datetime.date(2024, 7, 14), datetime.date(2024, 7, 20))]

    # Test with Sunday (week boundary)
    sunday = datetime.date(2024, 7, 14)
    weeks_sun = list(generate_weeks(count=10, start_date=sunday, until_date=sunday))
    assert len(weeks_sun) == 1
    assert weeks_sun == [(datetime.date(2024, 7, 14), datetime.date(2024, 7, 20))]


def test_date_to_quarter() -> None:
    def to_date(m: int, d: int) -> datetime.datetime:
        return datetime.datetime(2018, m, d)

    assert 1 == date_to_quarter(to_date(1, 6))
    assert 1 == date_to_quarter(to_date(3, 31))

    assert 2 == date_to_quarter(to_date(4, 1))
    assert 2 == date_to_quarter(to_date(6, 30))

    assert 3 == date_to_quarter(to_date(7, 30))
    assert 3 == date_to_quarter(to_date(9, 3))

    assert 4 == date_to_quarter(to_date(10, 1))
    assert 4 == date_to_quarter(to_date(12, 31))


def test_date_to_start_of_quarter() -> None:
    def to_date(m: int, d: int) -> datetime.datetime:
        return datetime.datetime(2018, m, d)

    q1 = to_date(1, 1)
    q2 = to_date(4, 1)
    q3 = to_date(7, 1)
    q4 = to_date(10, 1)

    assert q1 == date_to_start_of_quarter(to_date(1, 6))
    assert q1 == date_to_start_of_quarter(to_date(3, 31))

    assert q2 == date_to_start_of_quarter(to_date(4, 1))
    assert q2 == date_to_start_of_quarter(to_date(6, 30))

    assert q3 == date_to_start_of_quarter(to_date(7, 30))
    assert q3 == date_to_start_of_quarter(to_date(9, 3))

    assert q4 == date_to_start_of_quarter(to_date(10, 1))
    assert q4 == date_to_start_of_quarter(to_date(12, 31))


def test_start_of_quarter() -> None:
    assert start_of_quarter(2024, 1) == datetime.datetime(2024, 1, 1)


def test_end_of_quarter() -> None:
    """Test getting the end of a quarter."""
    from dateutils.dateutils import end_of_quarter

    # Q1 should end on March 31
    assert end_of_quarter(2024, 1) == datetime.datetime(2024, 3, 31, 23, 59, 59, 999999)

    # Q2 should end on June 30
    assert end_of_quarter(2024, 2) == datetime.datetime(2024, 6, 30, 23, 59, 59, 999999)

    # Q3 should end on September 30
    assert end_of_quarter(2024, 3) == datetime.datetime(2024, 9, 30, 23, 59, 59, 999999)

    # Q4 should end on December 31
    assert end_of_quarter(2024, 4) == datetime.datetime(2024, 12, 31, 23, 59, 59, 999999)

    # Test non-leap year February (Q1 of 2023)
    assert end_of_quarter(2023, 1) == datetime.datetime(2023, 3, 31, 23, 59, 59, 999999)

    # Test leap year February (Q1 of 2024)
    assert end_of_quarter(2024, 1) == datetime.datetime(2024, 3, 31, 23, 59, 59, 999999)


def test_start_of_month() -> None:
    """Test getting the start of a month."""
    from dateutils.dateutils import start_of_month

    assert start_of_month(2024, 2) == datetime.datetime(2024, 2, 1)
    assert start_of_month(2023, 12) == datetime.datetime(2023, 12, 1)


def test_end_of_month() -> None:
    """Test getting the end of a month."""
    from dateutils.dateutils import end_of_month

    assert end_of_month(2024, 2) == datetime.datetime(2024, 2, 29, 23, 59, 59, 999999)  # Leap year
    assert end_of_month(2023, 2) == datetime.datetime(2023, 2, 28, 23, 59, 59, 999999)  # Non-leap year
    assert end_of_month(2024, 4) == datetime.datetime(2024, 4, 30, 23, 59, 59, 999999)
    assert end_of_month(2024, 12) == datetime.datetime(2024, 12, 31, 23, 59, 59, 999999)


def test_get_days_in_month() -> None:
    """Test getting the number of days in a month."""
    from dateutils.dateutils import get_days_in_month

    assert get_days_in_month(2024, 2) == 29  # Leap year
    assert get_days_in_month(2023, 2) == 28  # Non-leap year
    assert get_days_in_month(2024, 4) == 30
    assert get_days_in_month(2024, 12) == 31


def test_date_range() -> None:
    """Test generating a range of dates."""
    from dateutils.dateutils import date_range

    start = datetime.date(2024, 3, 1)
    end = datetime.date(2024, 3, 5)

    expected = [
        datetime.date(2024, 3, 1),
        datetime.date(2024, 3, 2),
        datetime.date(2024, 3, 3),
        datetime.date(2024, 3, 4),
        datetime.date(2024, 3, 5),
    ]

    assert date_range(start, end) == expected


def test_workdays_between() -> None:
    """Test counting workdays between dates."""
    from dateutils.dateutils import workdays_between

    # Monday to Friday (5 workdays)
    start = datetime.date(2024, 3, 25)  # Monday
    end = datetime.date(2024, 3, 29)  # Friday
    assert workdays_between(start, end) == 5

    # Monday to Monday (6 workdays - excludes weekends)
    start = datetime.date(2024, 3, 25)  # Monday
    end = datetime.date(2024, 4, 1)  # Monday
    assert workdays_between(start, end) == 6

    # Friday to Monday (2 workdays - excludes weekend)
    start = datetime.date(2024, 3, 1)  # Friday
    end = datetime.date(2024, 3, 4)  # Monday
    assert workdays_between(start, end) == 2

    # Edge cases

    # Same day (weekday)
    start = end = datetime.date(2024, 3, 25)  # Monday
    assert workdays_between(start, end) == 1

    # Same day (weekend)
    start = end = datetime.date(2024, 3, 23)  # Saturday
    assert workdays_between(start, end) == 0

    # Same day (holiday)
    holiday = datetime.date(2024, 3, 25)  # Monday
    assert workdays_between(holiday, holiday, [holiday]) == 0

    # End date before start date (should raise ValueError now)
    start = datetime.date(2024, 3, 4)  # Monday
    end = datetime.date(2024, 3, 1)  # Friday of previous week
    with pytest.raises(ValueError):
        workdays_between(start, end)


def test_add_business_days() -> None:
    """Test adding business days to a date."""
    from dateutils.dateutils import add_business_days

    # Add 5 business days from Monday (should be next Monday)
    start = datetime.date(2024, 3, 25)  # Monday
    assert add_business_days(start, 5) == datetime.date(2024, 4, 1)  # Next Monday

    # Add 3 business days from Wednesday (should be next Monday)
    start = datetime.date(2024, 3, 27)  # Wednesday
    assert add_business_days(start, 3) == datetime.date(2024, 4, 1)  # Monday

    # Add 1 business day on Friday (should be next Monday)
    start = datetime.date(2024, 3, 29)  # Friday
    assert add_business_days(start, 1) == datetime.date(2024, 4, 1)  # Monday


@freeze_time("2024-03-27 12:00:00")
def test_pretty_date() -> None:
    """Test pretty date formatting."""
    from dateutils.dateutils import pretty_date

    # Test "just now"
    now = datetime.datetime(2024, 3, 27, 12, 0, 0)
    assert pretty_date(now) == "just now"

    # Test seconds
    seconds_ago = datetime.datetime(2024, 3, 27, 11, 59, 30)
    assert pretty_date(seconds_ago) == "30 seconds ago"

    # Test minutes
    minute_ago = datetime.datetime(2024, 3, 27, 11, 59, 0)
    assert pretty_date(minute_ago) == "a minute ago"

    # Test hours
    hours_ago = datetime.datetime(2024, 3, 27, 10, 0, 0)
    assert pretty_date(hours_ago) == "2 hours ago"

    # Test yesterday
    yesterday = datetime.datetime(2024, 3, 26, 12, 0, 0)
    assert pretty_date(yesterday) == "Yesterday"

    # Test days
    days_ago = datetime.datetime(2024, 3, 23, 12, 0, 0)
    assert pretty_date(days_ago) == "4 days ago"


@freeze_time("2024-03-27 12:00:00")
def test_pretty_date_future() -> None:
    """Test pretty date formatting for future dates."""
    from dateutils.dateutils import pretty_date

    # Test "just now" for very near future
    almost_now = datetime.datetime(2024, 3, 27, 12, 0, 5)
    assert pretty_date(almost_now) == "just now"

    # Test seconds in future
    seconds_future = datetime.datetime(2024, 3, 27, 12, 0, 30)
    assert pretty_date(seconds_future) == "in 30 seconds"

    # Test minutes in future
    minute_future = datetime.datetime(2024, 3, 27, 12, 1, 0)
    assert pretty_date(minute_future) == "in a minute"

    # Test hours in future
    hours_future = datetime.datetime(2024, 3, 27, 14, 0, 0)
    assert pretty_date(hours_future) == "in 2 hours"

    # Test tomorrow
    tomorrow = datetime.datetime(2024, 3, 28, 12, 0, 0)
    assert pretty_date(tomorrow) == "Tomorrow"

    # Test days in future
    days_future = datetime.datetime(2024, 3, 31, 12, 0, 0)
    assert pretty_date(days_future) == "in 4 days"

    # Test weeks in future
    weeks_future = datetime.datetime(2024, 4, 10, 12, 0, 0)
    assert pretty_date(weeks_future) == "in 2 weeks"


def test_pretty_date_with_now_override_and_timestamp() -> None:
    """Test pretty_date with now_override and integer timestamp."""
    from dateutils.dateutils import pretty_date

    # Test with now_override and integer timestamp
    now_ts = 1711540800  # 2024-03-27 12:00:00 UTC
    # 30 seconds ago
    past_ts = now_ts - 30
    assert pretty_date(past_ts, now_override=now_ts) == "30 seconds ago"


def test_pretty_date_with_none_timestamp() -> None:
    """Test pretty_date with None timestamp."""
    from dateutils.dateutils import pretty_date

    # None timestamp should return "just now"
    assert pretty_date(None) == "just now"


def test_pretty_date_with_invalid_timestamp() -> None:
    """Test pretty_date with invalid integer timestamp."""
    from dateutils.dateutils import pretty_date

    # Very large invalid timestamp should return "just now" (timedelta(0))
    invalid_ts = 2**63
    result = pretty_date(invalid_ts)
    assert result == "just now"


def test_pretty_date_naive_datetime() -> None:
    """Test pretty_date with naive datetime (no tzinfo)."""
    from dateutils.dateutils import pretty_date

    # Test with naive datetime - should be treated as UTC
    now_ts = 1711540800  # 2024-03-27 12:00:00 UTC
    naive_dt = datetime.datetime(2024, 3, 27, 11, 59, 30)  # Naive, 30 seconds before
    result = pretty_date(naive_dt, now_override=now_ts)
    assert result == "30 seconds ago"


def test_pretty_date_future_extended() -> None:
    """Test pretty_date for extended future date ranges."""
    from dateutils.dateutils import pretty_date

    now_ts = 1711540800  # 2024-03-27 12:00:00 UTC

    # Test "in X minutes" (line 910)
    minutes_future = datetime.datetime(2024, 3, 27, 12, 15, 0, tzinfo=datetime.timezone.utc)
    assert pretty_date(minutes_future, now_override=now_ts) == "in 15 minutes"

    # Test "in an hour" (line 912)
    one_hour_future = datetime.datetime(2024, 3, 27, 13, 30, 0, tzinfo=datetime.timezone.utc)
    assert pretty_date(one_hour_future, now_override=now_ts) == "in an hour"

    # Test "in X months" (line 920-921)
    months_future = datetime.datetime(2024, 6, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)
    result = pretty_date(months_future, now_override=now_ts)
    assert result == "in 3 months"

    # Test "in X years" (line 922)
    years_future = datetime.datetime(2026, 3, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)
    result = pretty_date(years_future, now_override=now_ts)
    assert result == "in 2 years"


def test_pretty_date_past_extended() -> None:
    """Test pretty_date for extended past date ranges."""
    from dateutils.dateutils import pretty_date

    now_ts = 1711540800  # 2024-03-27 12:00:00 UTC

    # Test "X minutes ago" (line 936)
    minutes_ago = datetime.datetime(2024, 3, 27, 11, 45, 0, tzinfo=datetime.timezone.utc)
    assert pretty_date(minutes_ago, now_override=now_ts) == "15 minutes ago"

    # Test "an hour ago" (line 938)
    one_hour_ago = datetime.datetime(2024, 3, 27, 10, 30, 0, tzinfo=datetime.timezone.utc)
    assert pretty_date(one_hour_ago, now_override=now_ts) == "an hour ago"

    # Test "X weeks ago" (line 945-946)
    weeks_ago = datetime.datetime(2024, 3, 13, 12, 0, 0, tzinfo=datetime.timezone.utc)
    result = pretty_date(weeks_ago, now_override=now_ts)
    assert result == "2 weeks ago"

    # Test "X months ago" (line 947-948)
    months_ago = datetime.datetime(2023, 12, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)
    result = pretty_date(months_ago, now_override=now_ts)
    assert result == "3 months ago"

    # Test "X years ago" (line 949)
    years_ago = datetime.datetime(2022, 3, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)
    result = pretty_date(years_ago, now_override=now_ts)
    assert result == "2 years ago"


def test_httpdate_with_utc_aware_datetime() -> None:
    """Test httpdate with a UTC-aware datetime."""
    dt_utc = datetime.datetime(2015, 4, 14, 19, 16, 44, tzinfo=datetime.timezone.utc)
    result = httpdate(dt_utc)
    assert result == "Tue, 14 Apr 2015 19:16:44 GMT"


def test_httpdate_with_naive_datetime() -> None:
    """Test httpdate with a naive datetime (assumed UTC)."""
    dt_naive = datetime.datetime(2025, 12, 31, 23, 59, 59)
    result = httpdate(dt_naive)
    assert result == "Wed, 31 Dec 2025 23:59:59 GMT"


def test_httpdate_with_non_utc_timezone() -> None:
    """Test httpdate with a non-UTC timezone converted to UTC."""
    dt_ny = datetime.datetime(2015, 4, 14, 15, 16, 44, tzinfo=ZoneInfo("America/New_York"))
    result = httpdate(dt_ny)  # Function converts to UTC before formatting
    assert result == "Tue, 14 Apr 2015 19:16:44 GMT"  # 15:16:44 EDT = 19:16:44 UTC


def test_httpdate_edge_case_leap_year() -> None:
    """Test httpdate with a leap year date."""
    dt_leap = datetime.datetime(2020, 2, 29, 12, 0, 0, tzinfo=datetime.timezone.utc)
    result = httpdate(dt_leap)
    assert result == "Sat, 29 Feb 2020 12:00:00 GMT"


def test_httpdate_invalid_input() -> None:
    """Test httpdate with invalid input raises an appropriate exception."""
    with pytest.raises(AttributeError):
        httpdate("not a datetime")  # type: ignore # Should fail due to missing datetime attrs


def test_httpdate_locale_independence() -> None:
    """httpdate should not be affected by the process locale."""
    dt = datetime.datetime(2024, 7, 22, 14, 30, 0, tzinfo=datetime.timezone.utc)

    original_locale = locale.setlocale(locale.LC_TIME)
    try:
        switched = False
        for candidate in ("fr_FR.UTF-8", "de_DE.UTF-8", "es_ES.UTF-8"):
            try:
                locale.setlocale(locale.LC_TIME, candidate)
                switched = True
                break
            except locale.Error:
                continue
        if not switched:
            pytest.skip("No non-English locale available for testing")

        assert httpdate(dt) == "Mon, 22 Jul 2024 14:30:00 GMT"
    finally:
        locale.setlocale(locale.LC_TIME, original_locale)


##################
# Timezone operations tests
##################


def test_get_available_timezones() -> None:
    """Test that get_available_timezones returns a sorted list of timezone names."""
    timezones = get_available_timezones()
    assert isinstance(timezones, list)
    assert len(timezones) > 0
    assert all(isinstance(tz, str) for tz in timezones)
    assert timezones == sorted(timezones)  # Check they're sorted

    # Check for common timezones
    assert "UTC" in timezones
    assert "America/New_York" in timezones
    assert "Europe/London" in timezones


@freeze_time("2024-03-27 12:00:00", tz_offset=0)  # UTC time
def test_now_in_timezone() -> None:
    """Test getting current time in different timezones."""
    # Get NY time (UTC-5 or UTC-4 depending on DST)
    ny_now = now_in_timezone("America/New_York")
    assert ny_now.tzinfo is not None
    assert ny_now.tzname() == "EDT"

    # In March 2024, NY is in EDT (UTC-4)
    assert ny_now.hour == 8  # 12 UTC - 4 = 8 EDT

    # Test Tokyo (UTC+9)
    tokyo_now = now_in_timezone("Asia/Tokyo")
    assert tokyo_now.tzinfo is not None
    assert tokyo_now.tzname() == "JST"
    assert tokyo_now.hour == 21  # 12 UTC + 9 = 21 JST


@freeze_time("2024-03-27 23:30:00", tz_offset=0)  # UTC time near midnight
def test_today_in_timezone() -> None:
    """Test getting current date in different timezones."""
    # UTC date
    assert today_in_timezone("UTC") == datetime.date(2024, 3, 27)

    # New York (UTC-4 in March 2024) date
    # 23:30 UTC = 19:30 EDT, still same day
    assert today_in_timezone("America/New_York") == datetime.date(2024, 3, 27)

    # Tokyo (UTC+9) date
    # 23:30 UTC = 08:30 next day in Tokyo
    assert today_in_timezone("Asia/Tokyo") == datetime.date(2024, 3, 28)


def test_convert_timezone() -> None:
    """Test converting datetime between timezones."""
    # Create a datetime in UTC
    utc_dt = datetime.datetime(2024, 3, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)

    # Convert to New York (EDT in March 2024, UTC-4)
    ny_dt = convert_timezone(utc_dt, "America/New_York")
    assert ny_dt.tzname() == "EDT"
    assert ny_dt.hour == 8  # 12 - 4 = 8
    assert ny_dt.date() == utc_dt.date()

    # Convert to Tokyo (UTC+9)
    tokyo_dt = convert_timezone(utc_dt, "Asia/Tokyo")
    assert tokyo_dt.tzname() == "JST"
    assert tokyo_dt.hour == 21  # 12 + 9 = 21
    assert tokyo_dt.date() == utc_dt.date()

    # Test with a non-UTC starting timezone
    ny_dt_orig = datetime.datetime(2024, 3, 27, 8, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    tokyo_from_ny = convert_timezone(ny_dt_orig, "Asia/Tokyo")
    assert tokyo_from_ny.hour == 21  # 8 EDT = 21 JST

    # Test error case with naive datetime
    with pytest.raises(ValueError):
        convert_timezone(datetime.datetime(2024, 3, 27, 12, 0, 0), "America/New_York")

    # Test error case with invalid timezone name (now raises ValueError instead of ZoneInfoNotFoundError)
    with pytest.raises(ValueError, match="Invalid timezone name"):
        convert_timezone(utc_dt, "Invalid/Timezone")

    # Test with empty timezone name
    with pytest.raises((ZoneInfoNotFoundError, ValueError)):
        convert_timezone(utc_dt, "")


def test_datetime_to_utc() -> None:
    """Test converting datetime to UTC timezone."""
    # Test with timezone-aware datetime
    ny_dt = datetime.datetime(2024, 3, 27, 8, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    utc_dt = datetime_to_utc(ny_dt)
    assert utc_dt.tzinfo == datetime.timezone.utc
    assert utc_dt.hour == 12  # 8 EDT = 12 UTC

    # Test with naive datetime (assumes UTC, consistent with epoch_s)
    naive_dt = datetime.datetime(2024, 3, 27, 12, 0, 0)
    result = datetime_to_utc(naive_dt)
    assert result.tzinfo == datetime.timezone.utc
    assert result.hour == 12  # Naive datetime assumed to be UTC, so hour unchanged


def test_get_timezone_offset() -> None:
    """Test getting the offset from UTC for a timezone."""
    # Test fixed offset for UTC
    utc_offset = get_timezone_offset("UTC")
    assert utc_offset == datetime.timedelta(0)

    # Test for New York (could be either EST or EDT)
    ny_offset = get_timezone_offset("America/New_York")
    assert isinstance(ny_offset, datetime.timedelta)
    # NY is either UTC-5 (EST) or UTC-4 (EDT)
    assert ny_offset.total_seconds() in (-5 * 3600, -4 * 3600)

    # Test for Tokyo (UTC+9)
    tokyo_offset = get_timezone_offset("Asia/Tokyo")
    assert tokyo_offset == datetime.timedelta(hours=9)


def test_format_timezone_offset() -> None:
    """Test formatting timezone offset as string."""
    # Test UTC (always +00:00)
    assert format_timezone_offset("UTC") == "+00:00"

    # Test for a negative offset (NY is UTC-5 or UTC-4)
    ny_offset = format_timezone_offset("America/New_York")
    assert ny_offset in ("-05:00", "-04:00")

    # Test for a positive offset (Tokyo is UTC+9)
    assert format_timezone_offset("Asia/Tokyo") == "+09:00"

    # Test for timezone with half-hour offset (India is UTC+5:30)
    assert format_timezone_offset("Asia/Kolkata") == "+05:30"


def test_dst_transitions() -> None:
    """Test handling of DST transitions in timezone functions."""
    # Test converting a datetime during DST transition

    # US DST transition (March 10, 2024, 2am -> 3am)
    # 1:59am (pre-transition)
    pre_dst = datetime.datetime(2024, 3, 10, 1, 59, 0, tzinfo=ZoneInfo("America/New_York"))
    # 3:01am (post-transition)
    post_dst = datetime.datetime(2024, 3, 10, 3, 1, 0, tzinfo=ZoneInfo("America/New_York"))

    # Convert both to UTC
    from dateutils.dateutils import datetime_to_utc

    pre_dst_utc = datetime_to_utc(pre_dst)
    post_dst_utc = datetime_to_utc(post_dst)

    # The UTC time difference should be only ~1 hour and 2 minutes, not 2 hours
    # (since 1:59am EST -> 3:01am EDT is actually ~1:02 in real time)
    time_diff = (post_dst_utc - pre_dst_utc).total_seconds()
    assert time_diff == 120  # Only 2 minutes difference in UTC time

    # Explanation: When converting local time to UTC:
    # 1:59am EST = 6:59am UTC
    # 3:01am EDT = 7:01am UTC
    # So the actual difference is just 2 minutes in UTC

    # Test autumn transition (November 3, 2024, 2am -> 1am)
    # 1:30am (first occurrence, EDT)
    before_fallback = datetime.datetime(2024, 11, 3, 1, 30, 0, tzinfo=ZoneInfo("America/New_York"))
    # 1:30am (second occurrence, after fallback, EST)
    after_fallback = datetime.datetime(2024, 11, 3, 1, 30, 0, tzinfo=ZoneInfo("America/New_York"))
    after_fallback = after_fallback.replace(fold=1)  # Mark as the second occurrence

    # Convert both to UTC
    before_utc = datetime_to_utc(before_fallback)
    after_utc = datetime_to_utc(after_fallback)

    # The second 1:30am should be one hour later in UTC
    assert (after_utc - before_utc).total_seconds() == 3600

    # Test getting current time in a timezone around DST transition
    with freeze_time("2024-03-10 06:30:00", tz_offset=0):  # UTC time during US DST spring forward
        from dateutils.dateutils import now_in_timezone

        ny_time = now_in_timezone("America/New_York")
        # 6:30 UTC = 1:30 EST (before transition)
        # The DST transition happens at 2:00 AM local time, so at 6:30 UTC
        # it's still 1:30 AM in New York, not 2:30 EDT yet
        assert ny_time.hour == 1
        assert ny_time.minute == 30


def test_dst_midnight_boundary() -> None:
    """Test timezone functions with DST boundaries at or near midnight.

    This tests edge cases where date boundaries and DST transitions interact.
    """
    from dateutils.dateutils import convert_timezone, now_in_timezone, today_in_timezone

    # === Spring forward: March 10, 2024, 2:00 AM -> 3:00 AM in US Eastern ===

    # Test today_in_timezone right at midnight UTC during spring forward
    # At 2024-03-10 05:00:00 UTC = 2024-03-10 00:00:00 EST (midnight, before transition)
    with freeze_time("2024-03-10 05:00:00", tz_offset=0):
        ny_date = today_in_timezone("America/New_York")
        assert ny_date == datetime.date(2024, 3, 10)

    # At 2024-03-10 07:00:00 UTC = 2024-03-10 03:00:00 EDT (after transition)
    with freeze_time("2024-03-10 07:00:00", tz_offset=0):
        ny_date = today_in_timezone("America/New_York")
        assert ny_date == datetime.date(2024, 3, 10)
        ny_time = now_in_timezone("America/New_York")
        assert ny_time.hour == 3  # 7 UTC - 4 (EDT) = 3

    # Test convert_timezone across midnight during DST transition
    # 11:30 PM EST on March 9 -> should be 11:30 PM same day
    pre_midnight_utc = datetime.datetime(2024, 3, 10, 4, 30, 0, tzinfo=datetime.timezone.utc)
    pre_midnight_ny = convert_timezone(pre_midnight_utc, "America/New_York")
    assert pre_midnight_ny.hour == 23
    assert pre_midnight_ny.day == 9  # Still March 9 in NY

    # === Fall back: November 3, 2024, 2:00 AM -> 1:00 AM in US Eastern ===

    # During fall back, 1:00 AM occurs twice. Test the "repeated hour" scenario.
    # At 2024-11-03 05:30:00 UTC = 2024-11-03 01:30:00 EDT (first 1:30 AM)
    with freeze_time("2024-11-03 05:30:00", tz_offset=0):
        ny_time = now_in_timezone("America/New_York")
        assert ny_time.hour == 1
        assert ny_time.minute == 30

    # At 2024-11-03 06:30:00 UTC = 2024-11-03 01:30:00 EST (second 1:30 AM)
    with freeze_time("2024-11-03 06:30:00", tz_offset=0):
        ny_time = now_in_timezone("America/New_York")
        assert ny_time.hour == 1
        assert ny_time.minute == 30

    # Test that date doesn't change incorrectly during fall back midnight
    # At 2024-11-03 04:00:00 UTC = 2024-11-03 00:00:00 EDT (midnight, before fall back)
    with freeze_time("2024-11-03 04:00:00", tz_offset=0):
        ny_date = today_in_timezone("America/New_York")
        assert ny_date == datetime.date(2024, 11, 3)

    # At 2024-11-03 08:00:00 UTC = 2024-11-03 03:00:00 EST (after fall back)
    with freeze_time("2024-11-03 08:00:00", tz_offset=0):
        ny_date = today_in_timezone("America/New_York")
        assert ny_date == datetime.date(2024, 11, 3)


def test_convert_timezone_dst_nonexistent_time() -> None:
    """Test convert_timezone behavior with times in the DST 'gap'.

    During spring forward (2:00 AM -> 3:00 AM), times like 2:30 AM don't exist.
    Python's ZoneInfo handles this by "folding" forward.
    """
    from dateutils.dateutils import convert_timezone

    # Create a UTC time that would be 2:30 AM EST (which doesn't exist on March 10, 2024)
    # 2:30 AM EST would be 7:30 UTC, but 7:30 UTC on March 10 is actually 3:30 AM EDT
    utc_time = datetime.datetime(2024, 3, 10, 7, 30, 0, tzinfo=datetime.timezone.utc)
    ny_time = convert_timezone(utc_time, "America/New_York")

    # 7:30 UTC = 3:30 EDT (since DST has occurred)
    assert ny_time.hour == 3
    assert ny_time.minute == 30
    assert ny_time.tzname() == "EDT"


##################
# Parsing and formatting tests
##################


def test_parse_date() -> None:
    """Test parsing date strings in various formats."""
    # Test ISO format
    assert parse_date("2024-03-27") == datetime.date(2024, 3, 27)

    # Test various formats
    assert parse_date("27/03/2024") == datetime.date(2024, 3, 27)  # DD/MM/YYYY
    assert parse_date("03/27/2024") == datetime.date(2024, 3, 27)  # MM/DD/YYYY
    assert parse_date("27-03-2024") == datetime.date(2024, 3, 27)  # DD-MM-YYYY
    assert parse_date("03-27-2024") == datetime.date(2024, 3, 27)  # MM-DD-YYYY
    assert parse_date("27.03.2024") == datetime.date(2024, 3, 27)  # DD.MM.YYYY
    assert parse_date("2024/03/27") == datetime.date(2024, 3, 27)  # YYYY/MM/DD

    # Test text formats
    assert parse_date("March 27, 2024") == datetime.date(2024, 3, 27)  # Month DD, YYYY
    assert parse_date("27 March 2024") == datetime.date(2024, 3, 27)  # DD Month YYYY
    assert parse_date("Mar 27, 2024") == datetime.date(2024, 3, 27)  # Mon DD, YYYY
    assert parse_date("27 Mar 2024") == datetime.date(2024, 3, 27)  # DD Mon YYYY

    # Test with custom format
    assert parse_date("2024 03 27", formats=["%Y %m %d"]) == datetime.date(2024, 3, 27)

    # Test invalid date
    assert parse_date("not a date") is None
    assert parse_date("2024-13-45") is None  # Invalid month and day


def test_parse_date_dayfirst() -> None:
    """Test parse_date with dayfirst parameter for ambiguous dates."""
    # Unambiguous dates work the same either way
    assert parse_date("2024-07-22") == datetime.date(2024, 7, 22)
    assert parse_date("2024-07-22", dayfirst=True) == datetime.date(2024, 7, 22)

    # Ambiguous date: 03/04/2024 could be March 4th or April 3rd
    # Default (dayfirst=False): US style, month first -> March 4th
    assert parse_date("03/04/2024") == datetime.date(2024, 3, 4)
    assert parse_date("03/04/2024", dayfirst=False) == datetime.date(2024, 3, 4)

    # dayfirst=True: European style, day first -> April 3rd
    assert parse_date("03/04/2024", dayfirst=True) == datetime.date(2024, 4, 3)

    # Same with dashes
    assert parse_date("03-04-2024") == datetime.date(2024, 3, 4)  # US default
    assert parse_date("03-04-2024", dayfirst=True) == datetime.date(2024, 4, 3)  # European

    # Unambiguous because day > 12 (must be day, not month)
    assert parse_date("22/07/2024") == datetime.date(2024, 7, 22)  # Works with US default
    assert parse_date("22/07/2024", dayfirst=True) == datetime.date(2024, 7, 22)

    # Text formats are unambiguous
    assert parse_date("July 22, 2024") == datetime.date(2024, 7, 22)
    assert parse_date("22 Jul 2024") == datetime.date(2024, 7, 22)
    assert parse_date("July 22, 2024", dayfirst=True) == datetime.date(2024, 7, 22)

    # Custom formats ignore dayfirst
    assert parse_date("2024|07|22", formats=["%Y|%m|%d"]) == datetime.date(2024, 7, 22)
    assert parse_date("2024|07|22", formats=["%Y|%m|%d"], dayfirst=True) == datetime.date(2024, 7, 22)


def test_parse_datetime() -> None:
    """Test parsing datetime strings in various formats."""
    # Test ISO format with space separator
    assert parse_datetime("2024-03-27 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)

    # Test ISO format with T separator
    assert parse_datetime("2024-03-27T14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)

    # Test with milliseconds
    expected_with_ms = datetime.datetime(2024, 3, 27, 14, 30, 45, 123456)
    assert parse_datetime("2024-03-27T14:30:45.123456") == expected_with_ms

    # Test with timezone designator Z
    with_z = parse_datetime("2024-03-27T14:30:45Z")
    assert with_z == datetime.datetime(2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc)

    # Test with microseconds and Z
    with_ms_z = parse_datetime("2024-03-27T14:30:45.123456Z")
    assert with_ms_z == datetime.datetime(2024, 3, 27, 14, 30, 45, 123456, tzinfo=datetime.timezone.utc)

    # Test other date formats with time
    assert parse_datetime("27/03/2024 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)  # DD/MM/YYYY
    assert parse_datetime("03/27/2024 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)  # MM/DD/YYYY
    assert parse_datetime("27-03-2024 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)  # DD-MM-YYYY
    assert parse_datetime("2024/03/27 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)  # YYYY/MM/DD

    # Test with custom format
    assert parse_datetime("2024|03|27|14|30|45", formats=["%Y|%m|%d|%H|%M|%S"]) == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )

    # Test invalid datetime
    assert parse_datetime("not a datetime") is None
    assert parse_datetime("2024-03-27T25:70:80") is None  # Invalid hours, minutes, seconds


def test_parse_iso8601() -> None:
    """Test parsing ISO 8601 formatted strings."""
    # Test date only
    assert parse_iso8601("2024-03-27") == datetime.datetime(2024, 3, 27)

    # Test date and time
    assert parse_iso8601("2024-03-27T14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)

    # Test with milliseconds
    expected_with_ms = datetime.datetime(2024, 3, 27, 14, 30, 45, 123000)
    assert parse_iso8601("2024-03-27T14:30:45.123") == expected_with_ms

    # Test with timezone designator Z
    with_z = parse_iso8601("2024-03-27T14:30:45Z")
    assert with_z == datetime.datetime(2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc)

    # Test with timezone offset with colon
    with_tz_colon = parse_iso8601("2024-03-27T14:30:45+02:00")
    assert with_tz_colon is not None
    assert with_tz_colon.tzinfo is not None
    assert with_tz_colon.hour == 14
    assert with_tz_colon.tzinfo.utcoffset(None) == datetime.timedelta(hours=2)

    # Test with timezone offset without colon
    with_tz_no_colon = parse_iso8601("2024-03-27T14:30:45-0500")
    assert with_tz_no_colon is not None
    assert with_tz_no_colon.tzinfo is not None
    assert with_tz_no_colon.hour == 14
    assert with_tz_no_colon.tzinfo.utcoffset(None) == datetime.timedelta(hours=-5)

    # Additional edge cases

    # Test with microseconds precision
    with_microseconds = parse_iso8601("2024-03-27T14:30:45.123456")
    assert with_microseconds is not None
    assert with_microseconds.microsecond == 123456

    # Test with negative timezone at half-hour offset
    half_hour_offset = parse_iso8601("2024-03-27T14:30:45-05:30")
    assert half_hour_offset is not None
    assert half_hour_offset.tzinfo is not None
    assert half_hour_offset.tzinfo.utcoffset(None) == datetime.timedelta(hours=-5, minutes=-30)

    # Test basic format without T separator (should fail)
    assert parse_iso8601("2024-03-27 14:30:45") is None

    # Test with partial time specification
    assert parse_iso8601("2024-03-27T14") is None
    assert parse_iso8601("2024-03-27T14:30") is None

    # Test invalid patterns
    assert parse_iso8601("not iso8601") is None
    assert parse_iso8601("2024/03/27") is None  # Wrong date separator
    assert parse_iso8601("2024-03-27 14:30:45") is None  # Space instead of T


def test_format_date() -> None:
    """Test formatting dates."""
    test_date = datetime.date(2024, 3, 27)

    # Test default ISO format
    assert format_date(test_date) == "2024-03-27"

    # Test custom formats
    assert format_date(test_date, "%d/%m/%Y") == "27/03/2024"
    assert format_date(test_date, "%m/%d/%Y") == "03/27/2024"
    assert format_date(test_date, "%B %d, %Y") == "March 27, 2024"
    assert format_date(test_date, "%A, %d %B %Y") == "Wednesday, 27 March 2024"

    # Test with datetime input
    test_datetime = datetime.datetime(2024, 3, 27, 14, 30, 45)
    assert format_date(test_datetime) == "2024-03-27"  # Should extract just the date part


def test_format_datetime() -> None:
    """Test formatting datetimes."""
    test_datetime = datetime.datetime(2024, 3, 27, 14, 30, 45)

    # Test default format
    assert format_datetime(test_datetime) == "2024-03-27 14:30:45"

    # Test custom formats
    assert format_datetime(test_datetime, "%Y-%m-%dT%H:%M:%S") == "2024-03-27T14:30:45"
    assert format_datetime(test_datetime, "%d/%m/%Y %H:%M") == "27/03/2024 14:30"
    assert format_datetime(test_datetime, "%B %d, %Y, %I:%M %p") == "March 27, 2024, 02:30 PM"

    # With timezone
    test_datetime_tz = datetime.datetime(2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc)
    assert format_datetime(test_datetime_tz, "%Y-%m-%d %H:%M:%S %Z") == "2024-03-27 14:30:45 UTC"


def test_to_iso8601() -> None:
    """Test converting to ISO 8601 format."""
    # Test with date
    test_date = datetime.date(2024, 3, 27)
    assert to_iso8601(test_date) == "2024-03-27"

    # Test with naive datetime (should assume UTC)
    test_datetime = datetime.datetime(2024, 3, 27, 14, 30, 45)
    # Should add UTC timezone and format with timezone info
    assert to_iso8601(test_datetime) == "2024-03-27T14:30:45+00:00"

    # Test with timezone-aware datetime
    ny_dt = datetime.datetime(2024, 3, 27, 10, 30, 45, tzinfo=ZoneInfo("America/New_York"))
    # Should preserve timezone in output
    iso_ny = to_iso8601(ny_dt)
    assert "2024-03-27T10:30:45" in iso_ny
    assert "-04:00" in iso_ny or "-05:00" in iso_ny  # Depending on DST


##################
# Holiday and business day tests
##################


def test_is_weekend() -> None:
    """Test checking if a date falls on a weekend."""
    # Test a Monday (not weekend)
    monday = datetime.date(2024, 3, 25)
    assert not is_weekend(monday)

    # Test a Friday (not weekend)
    friday = datetime.date(2024, 3, 29)
    assert not is_weekend(friday)

    # Test a Saturday (weekend)
    saturday = datetime.date(2024, 3, 30)
    assert is_weekend(saturday)

    # Test a Sunday (weekend)
    sunday = datetime.date(2024, 3, 31)
    assert is_weekend(sunday)


def test_workdays_between_with_holidays() -> None:
    """Test counting workdays between dates with holiday exclusions."""
    # Set up a date range spanning multiple weeks
    start = datetime.date(2024, 3, 25)  # Monday
    end = datetime.date(2024, 4, 5)  # Friday, 2 weeks later

    # Without holidays, should be 10 workdays (Mon-Fri for 2 weeks)
    assert workdays_between(start, end) == 10

    # Define holidays
    holidays = [
        datetime.date(2024, 3, 29),  # Good Friday
        datetime.date(2024, 4, 1),  # Easter Monday
    ]

    # With holidays, should be 8 workdays (10 - 2 holidays)
    assert workdays_between(start, end, holidays) == 8

    # Test with weekend start/end dates
    weekend_start = datetime.date(2024, 3, 23)  # Saturday
    weekend_end = datetime.date(2024, 3, 31)  # Sunday

    # Should still count only workdays between (5 days, minus 1 holiday)
    assert workdays_between(weekend_start, weekend_end, holidays) == 4

    # Test with a single day range
    single_day = datetime.date(2024, 3, 27)  # Wednesday
    assert workdays_between(single_day, single_day) == 1  # Same day counts as 1

    # Test with holiday on the single day
    holiday_day = datetime.date(2024, 3, 29)  # Friday (Good Friday)
    assert workdays_between(holiday_day, holiday_day, holidays) == 0  # Holiday doesn't count


def test_workdays_between_duplicate_holidays() -> None:
    """Test that duplicate holidays are handled correctly (not double-counted)."""
    start = datetime.date(2024, 3, 25)  # Monday
    end = datetime.date(2024, 3, 29)  # Friday

    # Without holidays: 5 workdays
    assert workdays_between(start, end) == 5

    # With one holiday on Wednesday
    wednesday = datetime.date(2024, 3, 27)
    assert workdays_between(start, end, holidays=[wednesday]) == 4

    # With duplicate holidays - should still be 4, not 3
    assert workdays_between(start, end, holidays=[wednesday, wednesday]) == 4
    assert workdays_between(start, end, holidays=[wednesday, wednesday, wednesday]) == 4

    # With multiple different holidays, some duplicated
    thursday = datetime.date(2024, 3, 28)
    holidays_with_dupes = [wednesday, thursday, wednesday, thursday, wednesday]
    assert workdays_between(start, end, holidays=holidays_with_dupes) == 3  # 5 - 2 unique holidays


def test_workdays_between_with_generator() -> None:
    """Test that workdays_between works with generator-based holiday inputs."""
    start = datetime.date(2024, 3, 25)  # Monday
    end = datetime.date(2024, 3, 29)  # Friday

    # Create a generator that yields holidays
    def holiday_generator():
        yield datetime.date(2024, 3, 27)  # Wednesday
        yield datetime.date(2024, 3, 28)  # Thursday

    # Should work with generator
    assert workdays_between(start, end, holidays=holiday_generator()) == 3


def test_add_business_days_with_holidays() -> None:
    """Test adding business days with holiday exclusions."""
    # Start on a Monday
    start = datetime.date(2024, 3, 25)  # Monday

    # Define holidays
    holidays = [
        datetime.date(2024, 3, 29),  # Good Friday
        datetime.date(2024, 4, 1),  # Easter Monday
    ]

    # Without holidays, adding 5 days should be the next Monday (skipping weekend)
    assert add_business_days(start, 5) == datetime.date(2024, 4, 1)  # Monday

    # With holidays, adding 5 days should be Wednesday (skipping weekend and holidays)
    assert add_business_days(start, 5, holidays) == datetime.date(2024, 4, 3)  # Wednesday

    # Test adding negative days (going backwards)
    end = datetime.date(2024, 4, 5)  # Friday

    # Without holidays, subtracting 5 days should be previous Friday
    assert add_business_days(end, -5) == datetime.date(2024, 3, 29)  # Friday

    # With holidays, subtracting 5 days should be Wednesday (skipping holidays)
    assert add_business_days(end, -5, holidays) == datetime.date(2024, 3, 27)  # Wednesday

    # Test starting on a weekend
    weekend_start = datetime.date(2024, 3, 30)  # Saturday

    # Adding business days from weekend should start from next business day
    assert add_business_days(weekend_start, 1) == datetime.date(2024, 4, 1)  # Monday
    assert add_business_days(weekend_start, 1, holidays) == datetime.date(2024, 4, 2)  # Tuesday (Monday is holiday)

    # Test adding 0 days (should return same day if business day, or error/next business day if not)
    assert add_business_days(start, 0) == start  # Monday stays Monday

    # Edge case: adding a large number of days
    assert add_business_days(start, 10, holidays) == datetime.date(2024, 4, 10)  # Wednesday, 2 weeks later


def test_next_business_day() -> None:
    """Test finding the next business day."""
    # From a Monday
    monday = datetime.date(2024, 3, 25)
    assert next_business_day(monday) == datetime.date(2024, 3, 26)  # Tuesday

    # From a Friday
    friday = datetime.date(2024, 3, 29)
    assert next_business_day(friday) == datetime.date(2024, 4, 1)  # Monday (skipping weekend)

    # From a weekend
    saturday = datetime.date(2024, 3, 30)
    assert next_business_day(saturday) == datetime.date(2024, 4, 1)  # Monday

    # With holidays
    holidays = [datetime.date(2024, 4, 1)]  # Easter Monday
    assert next_business_day(friday, holidays) == datetime.date(2024, 4, 2)  # Tuesday (skipping weekend and holiday)
    assert next_business_day(saturday, holidays) == datetime.date(2024, 4, 2)  # Tuesday


def test_previous_business_day() -> None:
    """Test finding the previous business day."""
    # From a Tuesday
    tuesday = datetime.date(2024, 3, 26)
    assert previous_business_day(tuesday) == datetime.date(2024, 3, 25)  # Monday

    # From a Monday
    monday = datetime.date(2024, 4, 1)
    assert previous_business_day(monday) == datetime.date(2024, 3, 29)  # Friday (skipping weekend)

    # From a weekend
    sunday = datetime.date(2024, 3, 31)
    assert previous_business_day(sunday) == datetime.date(2024, 3, 29)  # Friday

    # With holidays
    holidays = [datetime.date(2024, 3, 29)]  # Good Friday
    assert previous_business_day(monday, holidays) == datetime.date(
        2024, 3, 28
    )  # Thursday (skipping weekend and holiday)
    assert previous_business_day(sunday, holidays) == datetime.date(2024, 3, 28)  # Thursday


def test_get_us_federal_holidays_all_2024() -> None:
    """Test getting all US federal holidays for 2024."""
    holidays_2024 = get_us_federal_holidays(2024)
    # Expected count: 5 fixed + 6 floating = 11
    assert len(holidays_2024) == 11

    # Check fixed holidays
    assert datetime.date(2024, 1, 1) in holidays_2024  # New Year's Day
    assert datetime.date(2024, 6, 19) in holidays_2024  # Juneteenth
    assert datetime.date(2024, 7, 4) in holidays_2024  # Independence Day
    assert datetime.date(2024, 11, 11) in holidays_2024  # Veterans Day
    assert datetime.date(2024, 12, 25) in holidays_2024  # Christmas Day

    # Check floating holidays for 2024
    assert datetime.date(2024, 1, 15) in holidays_2024  # MLK Day (3rd Mon Jan)
    assert datetime.date(2024, 2, 19) in holidays_2024  # Presidents Day (3rd Mon Feb)
    assert datetime.date(2024, 5, 27) in holidays_2024  # Memorial Day (Last Mon May)
    assert datetime.date(2024, 9, 2) in holidays_2024  # Labor Day (1st Mon Sep)
    assert datetime.date(2024, 10, 14) in holidays_2024  # Columbus Day (2nd Mon Oct)
    assert datetime.date(2024, 11, 28) in holidays_2024  # Thanksgiving (4th Thu Nov)


def test_get_us_federal_holidays_all_2025() -> None:
    """Test getting all US federal holidays for 2025 (different floating dates)."""
    holidays_2025 = get_us_federal_holidays(2025)
    assert len(holidays_2025) == 11

    # Check a few floating holidays for 2025
    assert datetime.date(2025, 1, 20) in holidays_2025  # MLK Day
    assert datetime.date(2025, 2, 17) in holidays_2025  # Presidents Day
    assert datetime.date(2025, 5, 26) in holidays_2025  # Memorial Day
    assert datetime.date(2025, 9, 1) in holidays_2025  # Labor Day
    assert datetime.date(2025, 10, 13) in holidays_2025  # Columbus Day
    assert datetime.date(2025, 11, 27) in holidays_2025  # Thanksgiving

    # Check fixed holidays remain the same date (different year)
    assert datetime.date(2025, 1, 1) in holidays_2025
    assert datetime.date(2025, 7, 4) in holidays_2025
    assert datetime.date(2025, 12, 25) in holidays_2025


def test_get_us_federal_holidays_filter_fixed() -> None:
    """Test filtering for only fixed holidays."""
    fixed_types = ("NEW_YEARS_DAY", "JUNETEENTH", "INDEPENDENCE_DAY", "VETERANS_DAY", "CHRISTMAS")
    holidays = get_us_federal_holidays(2024, holiday_types=fixed_types)
    assert len(holidays) == 5
    assert datetime.date(2024, 1, 1) in holidays
    assert datetime.date(2024, 6, 19) in holidays
    assert datetime.date(2024, 7, 4) in holidays
    assert datetime.date(2024, 11, 11) in holidays
    assert datetime.date(2024, 12, 25) in holidays
    # Ensure floating are excluded
    assert datetime.date(2024, 1, 15) not in holidays  # MLK Day
    assert datetime.date(2024, 11, 28) not in holidays  # Thanksgiving


def test_get_us_federal_holidays_filter_floating() -> None:
    """Test filtering for only floating holidays."""
    floating_types = ("MLK_DAY", "PRESIDENTS_DAY", "MEMORIAL_DAY", "LABOR_DAY", "COLUMBUS_DAY", "THANKSGIVING")
    holidays = get_us_federal_holidays(2024, holiday_types=floating_types)
    assert len(holidays) == 6
    assert datetime.date(2024, 1, 15) in holidays
    assert datetime.date(2024, 2, 19) in holidays
    assert datetime.date(2024, 5, 27) in holidays
    assert datetime.date(2024, 9, 2) in holidays
    assert datetime.date(2024, 10, 14) in holidays
    assert datetime.date(2024, 11, 28) in holidays
    # Ensure fixed are excluded
    assert datetime.date(2024, 1, 1) not in holidays  # New Year's Day
    assert datetime.date(2024, 7, 4) not in holidays  # Independence Day


def test_get_us_federal_holidays_filter_subset() -> None:
    """Test filtering for a specific subset of holidays."""
    subset_types = ("THANKSGIVING", "CHRISTMAS", "NEW_YEARS_DAY")
    holidays = get_us_federal_holidays(2024, holiday_types=subset_types)
    assert len(holidays) == 3
    assert datetime.date(2024, 11, 28) in holidays  # Thanksgiving
    assert datetime.date(2024, 12, 25) in holidays  # Christmas
    assert datetime.date(2024, 1, 1) in holidays  # New Year's Day
    assert datetime.date(2024, 7, 4) not in holidays  # Independence Day (not requested)
    assert datetime.date(2024, 1, 15) not in holidays  # MLK Day (not requested)


def test_get_us_federal_holidays_filter_empty() -> None:
    """Test filtering with an empty tuple."""
    holidays = get_us_federal_holidays(2024, holiday_types=())
    assert len(holidays) == 0


def test_get_us_federal_holidays_filter_invalid_type() -> None:
    """Test filtering with an invalid holiday type (should be ignored)."""
    holidays = get_us_federal_holidays(2024, holiday_types=("INVALID_HOLIDAY", "CHRISTMAS"))
    assert len(holidays) == 1
    assert datetime.date(2024, 12, 25) in holidays


def test_get_us_federal_holidays_returns_copy() -> None:
    """Mutating the returned list should not corrupt the cached data."""
    holidays = get_us_federal_holidays(2024)
    assert len(holidays) == 11
    holidays.pop()

    # Subsequent call should still return the full set
    assert len(get_us_federal_holidays(2024)) == 11


##################
# Property-based tests
##################


@pytest.mark.parametrize(
    "date_input",
    [
        datetime.date(2024, 1, 1),  # New Year
        datetime.date(2024, 2, 29),  # Leap day
        datetime.date(2024, 3, 15),  # Regular day
        datetime.date(2024, 12, 31),  # Year end
    ],
)
def test_date_add_business_days_properties(date_input: datetime.date) -> None:
    """Test mathematical properties of adding business days."""
    from dateutils.dateutils import add_business_days

    # Property 1: Adding 0 business days returns the same date (if it's a business day)
    if not is_weekend(date_input):
        assert add_business_days(date_input, 0) == date_input

    # Property 2: Adding then subtracting the same number of business days returns original date
    for days in [1, 5, 10]:
        assert add_business_days(add_business_days(date_input, days), -days) == date_input

    # Property 3: Adding days in sequence is the same as adding the sum
    assert add_business_days(add_business_days(date_input, 3), 2) == add_business_days(date_input, 5)


@pytest.mark.parametrize(
    "year,expected",
    [
        (2020, True),  # Divisible by 4 and 400
        (2024, True),  # Divisible by 4 but not 100
        (2100, False),  # Divisible by 100 but not 400
        (2000, True),  # Divisible by 400
        (1900, False),  # Divisible by 100 but not 400
    ],
)
def test_is_leap_year_properties(year: int, expected: bool) -> None:
    """Test mathematical properties of leap year calculations."""
    from dateutils.dateutils import get_days_in_month, is_leap_year

    assert is_leap_year(year) == expected

    # Property: February has 29 days in leap years, 28 in non-leap years
    if expected:
        assert get_days_in_month(year, 2) == 29
    else:
        assert get_days_in_month(year, 2) == 28


@pytest.mark.parametrize(
    "date1,date2,expected_days",
    [
        # One week apart, 5 business days
        (datetime.date(2024, 3, 25), datetime.date(2024, 3, 29), 5),
        # Weekend in between
        (datetime.date(2024, 3, 22), datetime.date(2024, 3, 25), 2),
        # Same day
        (datetime.date(2024, 3, 26), datetime.date(2024, 3, 26), 1),
    ],
)
def test_workdays_between_properties(date1: datetime.date, date2: datetime.date, expected_days: int) -> None:
    """Test mathematical properties of counting business days."""
    from dateutils.dateutils import workdays_between

    # Property 1: Valid date order should work
    if date1 <= date2:
        assert workdays_between(date1, date2) == expected_days

        # Property 2: Reversed order should raise ValueError (with new validation)
        if date1 < date2:
            with pytest.raises(ValueError):
                workdays_between(date2, date1)

    # Property 3: Consistency with next_business_day
    if date1 < date2 and workdays_between(date1, date2) > 0:
        from dateutils.dateutils import next_business_day

        # The next business day from date1 should be included in the count
        next_day = next_business_day(date1)
        assert workdays_between(next_day, date2) == expected_days - 1


##################
# Validation and Error Handling Tests
##################


def test_start_of_quarter_validation() -> None:
    """Test that start_of_quarter validates quarter input."""
    # Valid quarters should work
    assert start_of_quarter(2024, 1) == datetime.datetime(2024, 1, 1)
    assert start_of_quarter(2024, 4) == datetime.datetime(2024, 10, 1)

    # Invalid quarters should raise ValueError
    with pytest.raises(ValueError, match="Quarter must be between 1 and 4, got 0"):
        start_of_quarter(2024, 0)

    with pytest.raises(ValueError, match="Quarter must be between 1 and 4, got 5"):
        start_of_quarter(2024, 5)

    with pytest.raises(ValueError, match="Quarter must be between 1 and 4, got -1"):
        start_of_quarter(2024, -1)


def test_end_of_quarter_validation() -> None:
    """Test that end_of_quarter validates quarter input."""
    # Valid quarters should work
    assert end_of_quarter(2024, 1) == datetime.datetime(2024, 3, 31, 23, 59, 59, 999999)
    assert end_of_quarter(2024, 4) == datetime.datetime(2024, 12, 31, 23, 59, 59, 999999)

    # Invalid quarters should raise ValueError
    with pytest.raises(ValueError, match="Quarter must be between 1 and 4, got 0"):
        end_of_quarter(2024, 0)

    with pytest.raises(ValueError, match="Quarter must be between 1 and 4, got 6"):
        end_of_quarter(2024, 6)


def test_workdays_between_validation() -> None:
    """Test that workdays_between validates date ordering."""
    start = datetime.date(2024, 1, 1)
    end = datetime.date(2024, 1, 10)

    # Valid order should work
    assert workdays_between(start, end) >= 0

    # Invalid order should raise ValueError
    with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
        workdays_between(end, start)


def test_add_business_days_validation() -> None:
    """Test that add_business_days validates num_days range."""
    start_date = datetime.date(2024, 1, 1)

    # Valid ranges should work
    assert add_business_days(start_date, 100) is not None
    assert add_business_days(start_date, -100) is not None

    # Invalid ranges should raise ValueError
    with pytest.raises(ValueError, match="num_days must be between -10000 and 10000, got 10001"):
        add_business_days(start_date, 10001)

    with pytest.raises(ValueError, match="num_days must be between -10000 and 10000, got -10001"):
        add_business_days(start_date, -10001)


def test_month_function_validation() -> None:
    """Test that month functions validate year and month inputs."""
    # Valid inputs should work
    assert start_of_month(2024, 6) == datetime.datetime(2024, 6, 1)
    assert end_of_month(2024, 6) == datetime.datetime(2024, 6, 30, 23, 59, 59, 999999)
    assert get_days_in_month(2024, 6) == 30

    # Invalid month should raise ValueError
    with pytest.raises(ValueError, match="Month must be between 1 and 12, got 0"):
        start_of_month(2024, 0)

    with pytest.raises(ValueError, match="Month must be between 1 and 12, got 13"):
        end_of_month(2024, 13)

    with pytest.raises(ValueError, match="Month must be between 1 and 12, got -1"):
        get_days_in_month(2024, -1)

    # Invalid year should raise ValueError
    with pytest.raises(ValueError, match="Year must be a positive integer, got 0"):
        start_of_month(0, 6)

    with pytest.raises(ValueError, match="Year must be a positive integer, got -1"):
        end_of_month(-1, 6)


def test_generate_months_validation() -> None:
    """Test that generate_months validates until_m parameter."""
    # Valid month should work
    list(generate_months(until_year=2023, until_m=6))  # Should not raise

    # Invalid month should raise ValueError
    with pytest.raises(ValueError, match="until_m must be between 1 and 12, got 0"):
        list(generate_months(until_year=2023, until_m=0))

    with pytest.raises(ValueError, match="until_m must be between 1 and 12, got 13"):
        list(generate_months(until_year=2023, until_m=13))


def test_timezone_error_handling() -> None:
    """Test that timezone functions handle invalid timezone names."""
    # Valid timezone should work
    assert now_in_timezone("UTC") is not None
    assert today_in_timezone("America/New_York") is not None

    # Invalid timezone should raise ValueError with helpful message
    with pytest.raises(ValueError, match="Invalid timezone name 'Invalid/Timezone'"):
        now_in_timezone("Invalid/Timezone")

    with pytest.raises(ValueError, match="Invalid timezone name 'Bad_Zone'"):
        today_in_timezone("Bad_Zone")

    with pytest.raises(ValueError, match="Invalid timezone name 'Invalid/Zone'"):
        get_timezone_offset("Invalid/Zone")

    with pytest.raises(ValueError, match="Invalid timezone name 'Bad_TZ'"):
        format_timezone_offset("Bad_TZ")


def test_convert_timezone_validation() -> None:
    """Test that convert_timezone validates inputs properly."""
    utc_dt = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)

    # Valid conversion should work
    result = convert_timezone(utc_dt, "America/New_York")
    assert result.tzinfo is not None

    # Naive datetime should raise ValueError
    naive_dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
    with pytest.raises(ValueError, match="Input datetime must include timezone information"):
        convert_timezone(naive_dt, "America/New_York")

    # Invalid timezone should raise ValueError
    with pytest.raises(ValueError, match="Invalid timezone name 'Invalid/Zone'"):
        convert_timezone(utc_dt, "Invalid/Zone")


def test_utc_functions_error_handling() -> None:
    """Test that UTC functions handle invalid timestamps."""
    # Valid timestamp should work
    valid_ts = 1640995200  # 2022-01-01 00:00:00 UTC
    assert utc_from_timestamp(valid_ts) is not None
    assert utc_truncate_epoch_day(valid_ts) is not None

    # Invalid timestamp should raise ValueError
    # Use a timestamp that's definitely out of range for most systems
    invalid_ts = 2**63  # Very large timestamp that will cause overflow
    with pytest.raises(ValueError, match=f"Invalid timestamp: {invalid_ts}"):
        utc_from_timestamp(invalid_ts)

    with pytest.raises(ValueError, match=f"Invalid timestamp: {invalid_ts}"):
        utc_truncate_epoch_day(invalid_ts)


def test_date_range_validation() -> None:
    """Test that date_range validates inputs and size limits."""
    start = datetime.date(2024, 1, 1)
    end = datetime.date(2024, 1, 10)

    # Valid range should work
    dates = date_range(start, end)
    assert len(dates) == 10
    assert dates[0] == start
    assert dates[-1] == end

    # Invalid order should raise ValueError
    with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
        date_range(end, start)

    # Large range should raise ValueError
    large_end = start + datetime.timedelta(days=4000)
    with pytest.raises(ValueError, match="Date range too large .* Consider using a generator"):
        date_range(start, large_end)


##################
# New Utility Function Tests
##################


def test_is_business_day() -> None:
    """Test the is_business_day function."""
    # Monday is a business day
    monday = datetime.date(2024, 7, 22)
    assert is_business_day(monday) is True

    # Friday is a business day
    friday = datetime.date(2024, 7, 26)
    assert is_business_day(friday) is True

    # Saturday is not a business day
    saturday = datetime.date(2024, 7, 27)
    assert is_business_day(saturday) is False

    # Sunday is not a business day
    sunday = datetime.date(2024, 7, 28)
    assert is_business_day(sunday) is False

    # Business day with holiday (list)
    july_4th = datetime.date(2024, 7, 4)  # Thursday
    assert is_business_day(july_4th) is True  # Without holidays
    assert is_business_day(july_4th, holidays=[july_4th]) is False  # With holiday as list

    # Business day with holiday (set) - O(1) lookup
    holiday_set = {july_4th, datetime.date(2024, 12, 25)}
    assert is_business_day(july_4th, holidays=holiday_set) is False
    assert is_business_day(datetime.date(2024, 7, 5), holidays=holiday_set) is True  # Friday, not a holiday

    # Business day with holiday (tuple)
    holiday_tuple = (july_4th, datetime.date(2024, 12, 25))
    assert is_business_day(july_4th, holidays=holiday_tuple) is False

    # Business day with holiday (frozenset)
    holiday_frozenset = frozenset({july_4th, datetime.date(2024, 12, 25)})
    assert is_business_day(july_4th, holidays=holiday_frozenset) is False

    # Business day with holiday (generator)
    def holiday_gen():
        yield july_4th
        yield datetime.date(2024, 12, 25)

    assert is_business_day(july_4th, holidays=holiday_gen()) is False
    assert is_business_day(datetime.date(2024, 7, 5), holidays=holiday_gen()) is True


def test_days_until_weekend() -> None:
    """Test the days_until_weekend function."""
    # Monday (0) -> 5 days until Saturday
    monday = datetime.date(2024, 7, 22)
    assert days_until_weekend(monday) == 5

    # Friday (4) -> 1 day until Saturday
    friday = datetime.date(2024, 7, 26)
    assert days_until_weekend(friday) == 1

    # Saturday (5) -> 0 days (already weekend)
    saturday = datetime.date(2024, 7, 27)
    assert days_until_weekend(saturday) == 0

    # Sunday (6) -> 0 days (already weekend)
    sunday = datetime.date(2024, 7, 28)
    assert days_until_weekend(sunday) == 0


def test_days_since_weekend() -> None:
    """Test the days_since_weekend function."""
    # Monday (0) -> 1 day since Sunday
    monday = datetime.date(2024, 7, 22)
    assert days_since_weekend(monday) == 1

    # Friday (4) -> 5 days since Sunday
    friday = datetime.date(2024, 7, 26)
    assert days_since_weekend(friday) == 5

    # Saturday (5) -> 0 days (currently weekend)
    saturday = datetime.date(2024, 7, 27)
    assert days_since_weekend(saturday) == 0

    # Sunday (6) -> 0 days (currently weekend)
    sunday = datetime.date(2024, 7, 28)
    assert days_since_weekend(sunday) == 0


def test_get_week_number() -> None:
    """Test the get_week_number function."""
    # January 1, 2024 is in week 1
    jan_1 = datetime.date(2024, 1, 1)
    assert get_week_number(jan_1) == 1

    # July 22, 2024 is in week 30
    july_22 = datetime.date(2024, 7, 22)
    assert get_week_number(july_22) == 30

    # December 31, 2024 is in week 1 of 2025 (ISO week date)
    dec_31 = datetime.date(2024, 12, 31)
    assert get_week_number(dec_31) == 1


def test_get_quarter_start_end() -> None:
    """Test the get_quarter_start_end function."""
    # Q1 2024
    start, end = get_quarter_start_end(2024, 1)
    assert start == datetime.date(2024, 1, 1)
    assert end == datetime.date(2024, 3, 31)

    # Q4 2024
    start, end = get_quarter_start_end(2024, 4)
    assert start == datetime.date(2024, 10, 1)
    assert end == datetime.date(2024, 12, 31)

    # Invalid quarter should raise ValueError
    with pytest.raises(ValueError, match="Quarter must be between 1 and 4, got 5"):
        get_quarter_start_end(2024, 5)


def test_age_in_years() -> None:
    """Test the age_in_years function."""
    birth_date = datetime.date(1990, 6, 15)

    # Age on exact birthday
    birthday_2024 = datetime.date(2024, 6, 15)
    assert age_in_years(birth_date, birthday_2024) == 34

    # Age before birthday
    before_birthday = datetime.date(2024, 6, 14)
    assert age_in_years(birth_date, before_birthday) == 33

    # Age after birthday
    after_birthday = datetime.date(2024, 6, 16)
    assert age_in_years(birth_date, after_birthday) == 34

    # Future birth date should raise ValueError
    future_birth = datetime.date(2025, 1, 1)
    with pytest.raises(ValueError, match="Birth date cannot be in the future"):
        age_in_years(future_birth, datetime.date(2024, 1, 1))


@freeze_time("2024-07-22")
def test_age_in_years_without_as_of_date() -> None:
    """Test age_in_years without providing as_of_date (uses today)."""
    # Birth date - will calculate age as of frozen date (2024-07-22)
    birth_date = datetime.date(1990, 7, 22)
    assert age_in_years(birth_date) == 34  # Exact birthday

    birth_date_before = datetime.date(1990, 7, 23)
    assert age_in_years(birth_date_before) == 33  # Birthday tomorrow

    birth_date_after = datetime.date(1990, 7, 21)
    assert age_in_years(birth_date_after) == 34  # Birthday was yesterday


def test_age_in_years_leap_year_birthday() -> None:
    """Test age_in_years for someone born on Feb 29 (leap day).

    This tests the edge case where a birthday only exists in leap years.
    The implementation treats Feb 28 as the effective birthday in non-leap years,
    meaning on Feb 28 of a non-leap year, the person has already had their birthday.
    """
    # Born on Feb 29, 2000 (leap year)
    leap_birthday = datetime.date(2000, 2, 29)

    # === In a leap year (2024) ===
    # Day before birthday (Feb 28)
    assert age_in_years(leap_birthday, datetime.date(2024, 2, 28)) == 23

    # Exact birthday (Feb 29)
    assert age_in_years(leap_birthday, datetime.date(2024, 2, 29)) == 24

    # Day after birthday (Mar 1)
    assert age_in_years(leap_birthday, datetime.date(2024, 3, 1)) == 24

    # === In a non-leap year (2023) ===
    # Feb 27 - day before the effective birthday (Feb 28)
    assert age_in_years(leap_birthday, datetime.date(2023, 2, 27)) == 22

    # Feb 28 - the effective birthday in non-leap year (birthday has occurred)
    assert age_in_years(leap_birthday, datetime.date(2023, 2, 28)) == 23

    # Mar 1 - day after effective birthday
    assert age_in_years(leap_birthday, datetime.date(2023, 3, 1)) == 23

    # === Edge case: born on Feb 29, checking on Feb 29 of same year ===
    assert age_in_years(leap_birthday, datetime.date(2000, 2, 29)) == 0

    # === Edge case: one year later in non-leap year (2001) ===
    # Feb 27, 2001: birthday (treated as Feb 28) hasn't occurred yet
    assert age_in_years(leap_birthday, datetime.date(2001, 2, 27)) == 0

    # Feb 28, 2001: birthday (treated as Feb 28) has occurred
    assert age_in_years(leap_birthday, datetime.date(2001, 2, 28)) == 1

    # Mar 1, 2001: after birthday
    assert age_in_years(leap_birthday, datetime.date(2001, 3, 1)) == 1

    # === Verify leap vs non-leap year boundary behavior ===
    # Someone born Feb 29, 2000 turning 4 years old
    # In leap year 2004: birthday is Feb 29
    assert age_in_years(leap_birthday, datetime.date(2004, 2, 28)) == 3  # Day before
    assert age_in_years(leap_birthday, datetime.date(2004, 2, 29)) == 4  # Birthday
    assert age_in_years(leap_birthday, datetime.date(2004, 3, 1)) == 4  # Day after


@freeze_time("2024-07-22 10:00:00")
def test_time_until_next_occurrence() -> None:
    """Test the time_until_next_occurrence function."""
    # Target time today at 14:00
    target = datetime.datetime(2024, 7, 22, 14, 0, 0)
    delta = time_until_next_occurrence(target)
    assert delta == datetime.timedelta(hours=4)

    # Target time that already passed today (should be tomorrow)
    past_target = datetime.datetime(2024, 7, 22, 8, 0, 0)
    delta = time_until_next_occurrence(past_target)
    assert delta == datetime.timedelta(hours=22)  # Next day at 8:00


def test_time_until_next_occurrence_timezone_branches() -> None:
    """Test time_until_next_occurrence with various timezone combinations."""
    # Test when from_time is None and target_time has tzinfo (line 1515-1517)
    target_with_tz = datetime.datetime(2024, 7, 22, 14, 0, 0, tzinfo=datetime.timezone.utc)
    # This path uses datetime.now(target_time.tzinfo) internally
    delta = time_until_next_occurrence(target_with_tz)
    assert isinstance(delta, datetime.timedelta)

    # Test when from_time is None and target_time has no tzinfo (line 1515, 1519)
    target_naive = datetime.datetime(2024, 7, 22, 14, 0, 0)
    delta = time_until_next_occurrence(target_naive)
    assert isinstance(delta, datetime.timedelta)

    # Test when target_time has no tzinfo but from_time does (line 1522-1523)
    target_naive = datetime.datetime(2024, 7, 22, 14, 0, 0)
    from_time_with_tz = datetime.datetime(2024, 7, 22, 10, 0, 0, tzinfo=datetime.timezone.utc)
    delta = time_until_next_occurrence(target_naive, from_time_with_tz)
    assert delta == datetime.timedelta(hours=4)

    # Test when target_time has tzinfo but from_time doesn't (line 1524-1525)
    target_with_tz = datetime.datetime(2024, 7, 22, 14, 0, 0, tzinfo=datetime.timezone.utc)
    from_time_naive = datetime.datetime(2024, 7, 22, 10, 0, 0)
    delta = time_until_next_occurrence(target_with_tz, from_time_naive)
    assert delta == datetime.timedelta(hours=4)


def test_date_range_generator() -> None:
    """Test the date_range_generator function."""
    start = datetime.date(2024, 1, 1)
    end = datetime.date(2024, 1, 5)

    # Generate dates and convert to list
    dates = list(date_range_generator(start, end))
    assert len(dates) == 5
    assert dates[0] == start
    assert dates[-1] == end
    assert dates[2] == datetime.date(2024, 1, 3)

    # Invalid order should raise ValueError
    with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
        list(date_range_generator(end, start))

    # Test memory efficiency for large ranges (generator shouldn't consume memory upfront)
    large_end = start + datetime.timedelta(days=10000)
    gen = date_range_generator(start, large_end)
    # Just getting the generator shouldn't raise or consume memory
    first_date = next(gen)
    assert first_date == start


def test_get_us_federal_holidays_list_wrapper() -> None:
    """Test the list wrapper for US federal holidays."""
    # Test with list (should work via wrapper)
    holidays_list = get_us_federal_holidays_list(2024, ["NEW_YEARS_DAY", "CHRISTMAS"])
    assert len(holidays_list) == 2
    assert datetime.date(2024, 1, 1) in holidays_list
    assert datetime.date(2024, 12, 25) in holidays_list

    # Test without arguments (should get all holidays)
    all_holidays = get_us_federal_holidays_list(2024)
    assert len(all_holidays) == 11

    # Should produce same results as tuple version
    holidays_tuple = get_us_federal_holidays(2024, ("NEW_YEARS_DAY", "CHRISTMAS"))
    assert holidays_list == holidays_tuple
