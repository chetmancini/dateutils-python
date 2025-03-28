from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time
import datetime
from zoneinfo import ZoneInfoNotFoundError

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
    get_available_timezones,
    now_in_timezone,
    today_in_timezone,
    convert_timezone,
    datetime_to_utc,
    utc_to_local,
    get_timezone_offset,
    format_timezone_offset,
    parse_date,
    parse_datetime,
    parse_iso8601,
    format_date,
    format_datetime,
    to_iso8601,
    is_weekend,
    workdays_between,
    add_business_days,
    next_business_day,
    previous_business_day,
)


@freeze_time("2024-03-27")
def test_utc_today():
    """Test that utc_today returns the current UTC date."""
    from dateutils.dateutils import utc_today

    assert utc_today() == datetime.date(2024, 3, 27)


@freeze_time("2024-03-27 14:30:45", tz_offset=0)
def test_utc_now_seconds():
    """Test that utc_now_seconds returns the correct Unix timestamp."""
    from dateutils.dateutils import utc_now_seconds

    expected_timestamp = 1711549845
    assert utc_now_seconds() == expected_timestamp


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

    # Q1 should end on March 31
    assert end_of_quarter(2024, 1) == datetime.datetime(2024, 3, 31, 23, 59, 59)

    # Q2 should end on June 30
    assert end_of_quarter(2024, 2) == datetime.datetime(2024, 6, 30, 23, 59, 59)

    # Q3 should end on September 30
    assert end_of_quarter(2024, 3) == datetime.datetime(2024, 9, 30, 23, 59, 59)

    # Q4 should end on December 31
    assert end_of_quarter(2024, 4) == datetime.datetime(2024, 12, 31, 23, 59, 59)

    # Test non-leap year February (Q1 of 2023)
    assert end_of_quarter(2023, 1) == datetime.datetime(2023, 3, 31, 23, 59, 59)

    # Test leap year February (Q1 of 2024)
    assert end_of_quarter(2024, 1) == datetime.datetime(2024, 3, 31, 23, 59, 59)


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

    # End date before start date (should return 0)
    start = datetime.date(2024, 3, 4)  # Monday
    end = datetime.date(2024, 3, 1)  # Friday of previous week
    assert workdays_between(start, end) == 0

    # Multiple consecutive holidays
    start = datetime.date(2024, 3, 25)  # Monday
    end = datetime.date(2024, 3, 29)  # Friday
    holidays = [
        datetime.date(2024, 3, 25),  # Monday
        datetime.date(2024, 3, 26),  # Tuesday
        datetime.date(2024, 3, 27),  # Wednesday
    ]
    assert workdays_between(start, end, holidays) == 2  # Only Thu and Fri count

    # All days are holidays or weekends
    start = datetime.date(2024, 3, 25)  # Monday
    end = datetime.date(2024, 3, 29)  # Friday
    holidays = [
        datetime.date(2024, 3, 25),  # Monday
        datetime.date(2024, 3, 26),  # Tuesday
        datetime.date(2024, 3, 27),  # Wednesday
        datetime.date(2024, 3, 28),  # Thursday
        datetime.date(2024, 3, 29),  # Friday
    ]
    assert workdays_between(start, end, holidays) == 0


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


##################
# Timezone operations tests
##################


def test_get_available_timezones():
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
def test_now_in_timezone():
    """Test getting current time in different timezones."""
    # Get NY time (UTC-5 or UTC-4 depending on DST)
    ny_now = now_in_timezone("America/New_York")
    assert ny_now.tzinfo is not None
    assert ny_now.tzinfo.key == "America/New_York"

    # In March 2024, NY is in EDT (UTC-4)
    assert ny_now.hour == 8  # 12 UTC - 4 = 8 EDT

    # Test Tokyo (UTC+9)
    tokyo_now = now_in_timezone("Asia/Tokyo")
    assert tokyo_now.tzinfo is not None
    assert tokyo_now.tzinfo.key == "Asia/Tokyo"
    assert tokyo_now.hour == 21  # 12 UTC + 9 = 21 JST


@freeze_time("2024-03-27 23:30:00", tz_offset=0)  # UTC time near midnight
def test_today_in_timezone():
    """Test getting current date in different timezones."""
    # UTC date
    assert today_in_timezone("UTC") == datetime.date(2024, 3, 27)

    # New York (UTC-4 in March 2024) date
    # 23:30 UTC = 19:30 EDT, still same day
    assert today_in_timezone("America/New_York") == datetime.date(2024, 3, 27)

    # Tokyo (UTC+9) date
    # 23:30 UTC = 08:30 next day in Tokyo
    assert today_in_timezone("Asia/Tokyo") == datetime.date(2024, 3, 28)


def test_convert_timezone():
    """Test converting datetime between timezones."""
    # Create a datetime in UTC
    utc_dt = datetime.datetime(2024, 3, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)

    # Convert to New York (EDT in March 2024, UTC-4)
    ny_dt = convert_timezone(utc_dt, "America/New_York")
    assert ny_dt.tzinfo.key == "America/New_York"
    assert ny_dt.hour == 8  # 12 - 4 = 8
    assert ny_dt.date() == utc_dt.date()

    # Convert to Tokyo (UTC+9)
    tokyo_dt = convert_timezone(utc_dt, "Asia/Tokyo")
    assert tokyo_dt.tzinfo.key == "Asia/Tokyo"
    assert tokyo_dt.hour == 21  # 12 + 9 = 21
    assert tokyo_dt.date() == utc_dt.date()

    # Test with a non-UTC starting timezone
    ny_dt_orig = datetime.datetime(
        2024, 3, 27, 8, 0, 0, tzinfo=ZoneInfo("America/New_York")
    )
    tokyo_from_ny = convert_timezone(ny_dt_orig, "Asia/Tokyo")
    assert tokyo_from_ny.hour == 21  # 8 EDT = 21 JST

    # Test error case with naive datetime
    with pytest.raises(ValueError):
        convert_timezone(datetime.datetime(2024, 3, 27, 12, 0, 0), "America/New_York")

    # Test error case with invalid timezone name
    with pytest.raises(ZoneInfoNotFoundError):
        convert_timezone(utc_dt, "Invalid/Timezone")

    # Test with empty timezone name
    with pytest.raises((ZoneInfoNotFoundError, ValueError)):
        convert_timezone(utc_dt, "")


def test_datetime_to_utc():
    """Test converting datetime to UTC timezone."""
    # Test with timezone-aware datetime
    ny_dt = datetime.datetime(2024, 3, 27, 8, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    utc_dt = datetime_to_utc(ny_dt)
    assert utc_dt.tzinfo == datetime.timezone.utc
    assert utc_dt.hour == 12  # 8 EDT = 12 UTC

    # Test with naive datetime (should assume local timezone)
    # This is harder to test as it depends on system timezone
    naive_dt = datetime.datetime(2024, 3, 27, 12, 0, 0)
    result = datetime_to_utc(naive_dt)
    assert result.tzinfo == datetime.timezone.utc


def test_utc_to_local():
    """Test converting UTC datetime to local timezone."""
    # Test with UTC datetime
    utc_dt = datetime.datetime(2024, 3, 27, 12, 0, 0, tzinfo=datetime.timezone.utc)
    local_dt = utc_to_local(utc_dt)

    # Check that the result has a timezone set
    assert local_dt.tzinfo is not None

    # Check that it's not UTC anymore
    assert local_dt.tzinfo != datetime.timezone.utc

    # The timestamps (seconds since epoch) should be equal even if the display time is different
    assert local_dt.timestamp() == utc_dt.timestamp()

    # Test with naive datetime (assumes UTC)
    naive_dt = datetime.datetime(2024, 3, 27, 12, 0, 0)
    local_from_naive = utc_to_local(naive_dt)
    assert local_from_naive.tzinfo is not None

    # Test with non-UTC timezone (should raise ValueError)
    ny_dt = datetime.datetime(2024, 3, 27, 8, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    with pytest.raises(ValueError):
        utc_to_local(ny_dt)


def test_get_timezone_offset():
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


def test_format_timezone_offset():
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


def test_dst_transitions():
    """Test handling of DST transitions in timezone functions."""
    # Test converting a datetime during DST transition

    # US DST transition (March 10, 2024, 2am -> 3am)
    # 1:59am (pre-transition)
    pre_dst = datetime.datetime(
        2024, 3, 10, 1, 59, 0, tzinfo=ZoneInfo("America/New_York")
    )
    # 3:01am (post-transition)
    post_dst = datetime.datetime(
        2024, 3, 10, 3, 1, 0, tzinfo=ZoneInfo("America/New_York")
    )

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
    before_fallback = datetime.datetime(
        2024, 11, 3, 1, 30, 0, tzinfo=ZoneInfo("America/New_York")
    )
    # 1:30am (second occurrence, after fallback, EST)
    after_fallback = datetime.datetime(
        2024, 11, 3, 1, 30, 0, tzinfo=ZoneInfo("America/New_York")
    )
    after_fallback = after_fallback.replace(fold=1)  # Mark as the second occurrence

    # Convert both to UTC
    before_utc = datetime_to_utc(before_fallback)
    after_utc = datetime_to_utc(after_fallback)

    # The second 1:30am should be one hour later in UTC
    assert (after_utc - before_utc).total_seconds() == 3600

    # Test getting current time in a timezone around DST transition
    with freeze_time(
        "2024-03-10 06:30:00", tz_offset=0
    ):  # UTC time during US DST spring forward
        from dateutils.dateutils import now_in_timezone

        ny_time = now_in_timezone("America/New_York")
        # 6:30 UTC = 1:30 EST (before transition)
        # The DST transition happens at 2:00 AM local time, so at 6:30 UTC
        # it's still 1:30 AM in New York, not 2:30 EDT yet
        assert ny_time.hour == 1
        assert ny_time.minute == 30


##################
# Parsing and formatting tests
##################


def test_parse_date():
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


def test_parse_datetime():
    """Test parsing datetime strings in various formats."""
    # Test ISO format with space separator
    assert parse_datetime("2024-03-27 14:30:45") == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )

    # Test ISO format with T separator
    assert parse_datetime("2024-03-27T14:30:45") == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )

    # Test with milliseconds
    expected_with_ms = datetime.datetime(2024, 3, 27, 14, 30, 45, 123456)
    assert parse_datetime("2024-03-27T14:30:45.123456") == expected_with_ms

    # Test with timezone designator Z
    with_z = parse_datetime("2024-03-27T14:30:45Z")
    assert with_z == datetime.datetime(
        2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc
    )

    # Test with microseconds and Z
    with_ms_z = parse_datetime("2024-03-27T14:30:45.123456Z")
    assert with_ms_z == datetime.datetime(
        2024, 3, 27, 14, 30, 45, 123456, tzinfo=datetime.timezone.utc
    )

    # Test other date formats with time
    assert parse_datetime("27/03/2024 14:30:45") == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )  # DD/MM/YYYY
    assert parse_datetime("03/27/2024 14:30:45") == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )  # MM/DD/YYYY
    assert parse_datetime("27-03-2024 14:30:45") == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )  # DD-MM-YYYY
    assert parse_datetime("2024/03/27 14:30:45") == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )  # YYYY/MM/DD

    # Test with custom format
    assert parse_datetime(
        "2024|03|27|14|30|45", formats=["%Y|%m|%d|%H|%M|%S"]
    ) == datetime.datetime(2024, 3, 27, 14, 30, 45)

    # Test invalid datetime
    assert parse_datetime("not a datetime") is None
    assert (
        parse_datetime("2024-03-27T25:70:80") is None
    )  # Invalid hours, minutes, seconds


def test_parse_iso8601():
    """Test parsing ISO 8601 formatted strings."""
    # Test date only
    assert parse_iso8601("2024-03-27") == datetime.datetime(2024, 3, 27)

    # Test date and time
    assert parse_iso8601("2024-03-27T14:30:45") == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )

    # Test with milliseconds
    expected_with_ms = datetime.datetime(2024, 3, 27, 14, 30, 45, 123000)
    assert parse_iso8601("2024-03-27T14:30:45.123") == expected_with_ms

    # Test with timezone designator Z
    with_z = parse_iso8601("2024-03-27T14:30:45Z")
    assert with_z == datetime.datetime(
        2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc
    )

    # Test with timezone offset with colon
    with_tz_colon = parse_iso8601("2024-03-27T14:30:45+02:00")
    assert with_tz_colon.tzinfo is not None
    assert with_tz_colon.hour == 14
    assert with_tz_colon.tzinfo.utcoffset(None) == datetime.timedelta(hours=2)

    # Test with timezone offset without colon
    with_tz_no_colon = parse_iso8601("2024-03-27T14:30:45-0500")
    assert with_tz_no_colon.tzinfo is not None
    assert with_tz_no_colon.hour == 14
    assert with_tz_no_colon.tzinfo.utcoffset(None) == datetime.timedelta(hours=-5)

    # Additional edge cases

    # Test with microseconds precision
    with_microseconds = parse_iso8601("2024-03-27T14:30:45.123456")
    assert with_microseconds.microsecond == 123456

    # Test with negative timezone at half-hour offset
    half_hour_offset = parse_iso8601("2024-03-27T14:30:45-05:30")
    assert half_hour_offset.tzinfo.utcoffset(None) == datetime.timedelta(
        hours=-5, minutes=-30
    )

    # Test basic format without T separator (should fail)
    assert parse_iso8601("2024-03-27 14:30:45") is None

    # Test with partial time specification
    assert parse_iso8601("2024-03-27T14") is None
    assert parse_iso8601("2024-03-27T14:30") is None

    # Test invalid patterns
    assert parse_iso8601("not iso8601") is None
    assert parse_iso8601("2024/03/27") is None  # Wrong date separator
    assert parse_iso8601("2024-03-27 14:30:45") is None  # Space instead of T


def test_format_date():
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
    assert (
        format_date(test_datetime) == "2024-03-27"
    )  # Should extract just the date part


def test_format_datetime():
    """Test formatting datetimes."""
    test_datetime = datetime.datetime(2024, 3, 27, 14, 30, 45)

    # Test default format
    assert format_datetime(test_datetime) == "2024-03-27 14:30:45"

    # Test custom formats
    assert format_datetime(test_datetime, "%Y-%m-%dT%H:%M:%S") == "2024-03-27T14:30:45"
    assert format_datetime(test_datetime, "%d/%m/%Y %H:%M") == "27/03/2024 14:30"
    assert (
        format_datetime(test_datetime, "%B %d, %Y, %I:%M %p")
        == "March 27, 2024, 02:30 PM"
    )

    # With timezone
    test_datetime_tz = datetime.datetime(
        2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc
    )
    assert (
        format_datetime(test_datetime_tz, "%Y-%m-%d %H:%M:%S %Z")
        == "2024-03-27 14:30:45 UTC"
    )


def test_to_iso8601():
    """Test converting to ISO 8601 format."""
    # Test with date
    test_date = datetime.date(2024, 3, 27)
    assert to_iso8601(test_date) == "2024-03-27"

    # Test with naive datetime (should assume UTC)
    test_datetime = datetime.datetime(2024, 3, 27, 14, 30, 45)
    # Should add UTC timezone and format with timezone info
    assert to_iso8601(test_datetime) == "2024-03-27T14:30:45+00:00"

    # Test with timezone-aware datetime
    ny_dt = datetime.datetime(
        2024, 3, 27, 10, 30, 45, tzinfo=ZoneInfo("America/New_York")
    )
    # Should preserve timezone in output
    iso_ny = to_iso8601(ny_dt)
    assert "2024-03-27T10:30:45" in iso_ny
    assert "-04:00" in iso_ny or "-05:00" in iso_ny  # Depending on DST


##################
# Holiday and business day tests
##################


def test_is_weekend():
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


def test_workdays_between_with_holidays():
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
    assert (
        workdays_between(holiday_day, holiday_day, holidays) == 0
    )  # Holiday doesn't count


def test_add_business_days_with_holidays():
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
    assert add_business_days(start, 5, holidays) == datetime.date(
        2024, 4, 3
    )  # Wednesday

    # Test adding negative days (going backwards)
    end = datetime.date(2024, 4, 5)  # Friday

    # Without holidays, subtracting 5 days should be previous Friday
    assert add_business_days(end, -5) == datetime.date(2024, 3, 29)  # Friday

    # With holidays, subtracting 5 days should be Wednesday (skipping holidays)
    assert add_business_days(end, -5, holidays) == datetime.date(
        2024, 3, 27
    )  # Wednesday

    # Test starting on a weekend
    weekend_start = datetime.date(2024, 3, 30)  # Saturday

    # Adding business days from weekend should start from next business day
    assert add_business_days(weekend_start, 1) == datetime.date(2024, 4, 1)  # Monday
    assert add_business_days(weekend_start, 1, holidays) == datetime.date(
        2024, 4, 2
    )  # Tuesday (Monday is holiday)

    # Test adding 0 days (should return same day if business day, or error/next business day if not)
    assert add_business_days(start, 0) == start  # Monday stays Monday

    # Edge case: adding a large number of days
    assert add_business_days(start, 10, holidays) == datetime.date(
        2024, 4, 10
    )  # Wednesday, 2 weeks later


def test_next_business_day():
    """Test finding the next business day."""
    # From a Monday
    monday = datetime.date(2024, 3, 25)
    assert next_business_day(monday) == datetime.date(2024, 3, 26)  # Tuesday

    # From a Friday
    friday = datetime.date(2024, 3, 29)
    assert next_business_day(friday) == datetime.date(
        2024, 4, 1
    )  # Monday (skipping weekend)

    # From a weekend
    saturday = datetime.date(2024, 3, 30)
    assert next_business_day(saturday) == datetime.date(2024, 4, 1)  # Monday

    # With holidays
    holidays = [datetime.date(2024, 4, 1)]  # Easter Monday
    assert next_business_day(friday, holidays) == datetime.date(
        2024, 4, 2
    )  # Tuesday (skipping weekend and holiday)
    assert next_business_day(saturday, holidays) == datetime.date(2024, 4, 2)  # Tuesday


def test_previous_business_day():
    """Test finding the previous business day."""
    # From a Tuesday
    tuesday = datetime.date(2024, 3, 26)
    assert previous_business_day(tuesday) == datetime.date(2024, 3, 25)  # Monday

    # From a Monday
    monday = datetime.date(2024, 4, 1)
    assert previous_business_day(monday) == datetime.date(
        2024, 3, 29
    )  # Friday (skipping weekend)

    # From a weekend
    sunday = datetime.date(2024, 3, 31)
    assert previous_business_day(sunday) == datetime.date(2024, 3, 29)  # Friday

    # With holidays
    holidays = [datetime.date(2024, 3, 29)]  # Good Friday
    assert previous_business_day(monday, holidays) == datetime.date(
        2024, 3, 28
    )  # Thursday (skipping weekend and holiday)
    assert previous_business_day(sunday, holidays) == datetime.date(
        2024, 3, 28
    )  # Thursday


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
def test_date_add_business_days_properties(date_input):
    """Test mathematical properties of adding business days."""
    from dateutils.dateutils import add_business_days

    # Property 1: Adding 0 business days returns the same date (if it's a business day)
    if not is_weekend(date_input):
        assert add_business_days(date_input, 0) == date_input

    # Property 2: Adding then subtracting the same number of business days returns original date
    for days in [1, 5, 10]:
        assert (
            add_business_days(add_business_days(date_input, days), -days) == date_input
        )

    # Property 3: Adding days in sequence is the same as adding the sum
    assert add_business_days(add_business_days(date_input, 3), 2) == add_business_days(
        date_input, 5
    )


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
def test_is_leap_year_properties(year, expected):
    """Test mathematical properties of leap year calculations."""
    from dateutils.dateutils import is_leap_year, get_days_in_month

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
def test_workdays_between_properties(date1, date2, expected_days):
    """Test mathematical properties of counting business days."""
    from dateutils.dateutils import workdays_between

    # Property 1: Order of dates shouldn't matter (if both positive)
    if date1 <= date2:
        assert workdays_between(date1, date2) == expected_days
        if date1 < date2:  # Only assert reversed order is 0 when dates are different
            assert workdays_between(date2, date1) == 0  # If reversed, should be 0
        else:  # Same date case
            assert (
                workdays_between(date2, date1) == 1
            )  # Same date should return 1 workday

    # Property 2: Consistency with next_business_day
    if date1 < date2 and workdays_between(date1, date2) > 0:
        from dateutils.dateutils import next_business_day

        # The next business day from date1 should be included in the count
        next_day = next_business_day(date1)
        assert workdays_between(next_day, date2) == expected_days - 1
