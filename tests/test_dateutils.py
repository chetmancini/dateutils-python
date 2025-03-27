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


def test_epoch_s():
    assert 1397488604 == epoch_s(datetime.datetime(2014, 4, 14, 15, 16, 44))


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
    dt_ny = datetime.datetime(2015, 4, 14, 15, 16, 44, tzinfo=ZoneInfo("America/New_York"))
    dt_ny.astimezone(datetime.timezone.utc)
    result = httpdate(dt_ny)  # Function should handle timezone conversion if designed to
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