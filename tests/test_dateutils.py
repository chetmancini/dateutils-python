from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time
import datetime

from dateutils.dateutils import (
    date_to_quarter,
    generate_weeks,
    generate_months,
    date_to_start_of_quarter,
    generate_quarters,
    generate_years,
    start_of_year,
    end_of_year,
    epoch_s,
    datetime_end_of_day,
    datetime_start_of_day,
    httpdate,
    start_of_quarter,
    is_leap_year,
)


@freeze_time("2024-03-27")
def test_utc_today():
    """Test that utc_today returns the current UTC date."""
    from dateutils.dateutils import utc_today

    assert utc_today() == datetime.date(2024, 3, 27)


def test_utc_truncate_epoch_day():
    """Test truncating a timestamp to the start of the day in UTC."""
    from dateutils.dateutils import utc_truncate_epoch_day

    # Timestamp for 2024-03-27 15:30:45 UTC
    ts = 1711639845

    # Expected: 2024-03-27 00:00:00 UTC
    expected = 1711584000

    assert utc_truncate_epoch_day(ts) == expected


def test_epoch_s():
    assert 1397488604 == epoch_s(datetime.datetime(2014, 4, 14, 15, 16, 44))


def test_utc_from_timestamp():
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


def test_datetime_start_of_day():
    day = datetime.datetime(2016, 11, 23, 5, 4, 3).date()
    assert datetime_start_of_day(day) == datetime.datetime(2016, 11, 23, 0, 0, 0)


def test_datetime_end_of_day():
    day = datetime.datetime(2016, 11, 23, 5, 4, 3).date()
    assert datetime_end_of_day(day) == datetime.datetime(2016, 11, 23, 23, 59, 59)


def test_start_of_year():
    assert datetime.datetime(2018, 1, 1) == start_of_year(2018)


def test_end_of_year():
    assert datetime.datetime(2018, 12, 31, 23, 59, 59) == end_of_year(2018)


@freeze_time("2018-10-12")
def test_generate_years():
    assert [2018, 2017, 2016, 2015, 2014] == list(generate_years(until=2014))


def test_is_leap_year():
    assert is_leap_year(2020)
    assert not is_leap_year(2021)


@freeze_time("2018-9-12")
def test_generate_quarters():
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


@freeze_time("2018-9-12")
def test_generate_months():
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


@freeze_time("2018-9-12")
def test_generate_weeks():
    assert [
        (datetime.date(2018, 9, 3), datetime.date(2018, 9, 10)),
        (datetime.date(2018, 8, 27), datetime.date(2018, 9, 3)),
    ] == list(generate_weeks(count=2))


def test_date_to_quarter():
    def to_date(m, d):
        return datetime.datetime(2018, m, d)

    assert 1 == date_to_quarter(to_date(1, 6))
    assert 1 == date_to_quarter(to_date(3, 31))

    assert 2 == date_to_quarter(to_date(4, 1))
    assert 2 == date_to_quarter(to_date(6, 30))

    assert 3 == date_to_quarter(to_date(7, 30))
    assert 3 == date_to_quarter(to_date(9, 3))

    assert 4 == date_to_quarter(to_date(10, 1))
    assert 4 == date_to_quarter(to_date(12, 31))


def test_date_to_start_of_quarter():
    def to_date(m, d):
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


def test_start_of_quarter():
    assert start_of_quarter(2024, 1) == datetime.datetime(2024, 1, 1)


def test_end_of_quarter():
    """Test getting the end of a quarter."""
    from dateutils.dateutils import end_of_quarter

    assert end_of_quarter(2024, 1) == datetime.datetime(2024, 3, 1, 23, 59, 59)
    assert end_of_quarter(2024, 2) == datetime.datetime(2024, 6, 1, 23, 59, 59)
    assert end_of_quarter(2024, 3) == datetime.datetime(2024, 9, 1, 23, 59, 59)
    assert end_of_quarter(2024, 4) == datetime.datetime(2024, 12, 1, 23, 59, 59)


def test_start_of_month():
    """Test getting the start of a month."""
    from dateutils.dateutils import start_of_month

    assert start_of_month(2024, 2) == datetime.datetime(2024, 2, 1)
    assert start_of_month(2023, 12) == datetime.datetime(2023, 12, 1)


def test_end_of_month():
    """Test getting the end of a month."""
    from dateutils.dateutils import end_of_month

    assert end_of_month(2024, 2) == datetime.datetime(
        2024, 2, 29, 23, 59, 59
    )  # Leap year
    assert end_of_month(2023, 2) == datetime.datetime(
        2023, 2, 28, 23, 59, 59
    )  # Non-leap year
    assert end_of_month(2024, 4) == datetime.datetime(2024, 4, 30, 23, 59, 59)
    assert end_of_month(2024, 12) == datetime.datetime(2024, 12, 31, 23, 59, 59)


def test_get_days_in_month():
    """Test getting the number of days in a month."""
    from dateutils.dateutils import get_days_in_month

    assert get_days_in_month(2024, 2) == 29  # Leap year
    assert get_days_in_month(2023, 2) == 28  # Non-leap year
    assert get_days_in_month(2024, 4) == 30
    assert get_days_in_month(2024, 12) == 31


def test_date_range():
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


def test_workdays_between():
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


def test_add_business_days():
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
def test_pretty_date():
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


def test_httpdate_with_utc_aware_datetime():
    """Test httpdate with a UTC-aware datetime."""
    dt_utc = datetime.datetime(2015, 4, 14, 19, 16, 44, tzinfo=datetime.timezone.utc)
    result = httpdate(dt_utc)
    assert result == "Tue, 14 Apr 2015 19:16:44 GMT"


def test_httpdate_with_naive_datetime():
    """Test httpdate with a naive datetime (assumed UTC)."""
    dt_naive = datetime.datetime(2025, 12, 31, 23, 59, 59)
    result = httpdate(dt_naive)
    assert result == "Wed, 31 Dec 2025 23:59:59 GMT"


def test_httpdate_with_non_utc_timezone():
    """Test httpdate with a non-UTC timezone converted to UTC."""
    dt_ny = datetime.datetime(
        2015, 4, 14, 15, 16, 44, tzinfo=ZoneInfo("America/New_York")
    )
    dt_ny.astimezone(datetime.timezone.utc)
    result = httpdate(
        dt_ny
    )  # Function should handle timezone conversion if designed to
    assert result == "Tue, 14 Apr 2015 15:16:44 GMT"  # 15:16:44 EDT = 19:16:44 UTC


def test_httpdate_edge_case_leap_year():
    """Test httpdate with a leap year date."""
    dt_leap = datetime.datetime(2020, 2, 29, 12, 0, 0, tzinfo=datetime.timezone.utc)
    result = httpdate(dt_leap)
    assert result == "Sat, 29 Feb 2020 12:00:00 GMT"


def test_httpdate_invalid_input():
    """Test httpdate with invalid input raises an appropriate exception."""
    with pytest.raises(AttributeError):
        httpdate("not a datetime")  # Should fail due to lack of strftime
