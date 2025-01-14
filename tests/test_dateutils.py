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
)


def test_epoch_s():
    assert 1397488604 == epoch_s(datetime.datetime(2014, 4, 14, 15, 16, 44))
    with pytest.raises(ValueError):
        epoch_s(datetime.date(2014, 4, 14))


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
    assert [] == list(generate_weeks(count=10))


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


def test_httpdate():
    dt = datetime.datetime(2014, 4, 14, 15, 16, 44)
    assert "Mon, 14 Apr 2014 15:16:44 GMT" == httpdate(dt)
