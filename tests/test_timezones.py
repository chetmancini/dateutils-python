import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest
from freezegun import freeze_time

from dateutils.dateutils import (
    convert_timezone,
    datetime_to_utc,
    format_timezone_offset,
    get_available_timezones,
    get_timezone_offset,
    now_in_timezone,
    today_in_timezone,
)

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


def test_get_available_timezones_returns_fresh_list() -> None:
    """The returned list should be safe to mutate without affecting future calls."""
    first = get_available_timezones()
    first.append("Fake/Timezone")

    second = get_available_timezones()
    assert "Fake/Timezone" not in second


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
    with pytest.raises(ValueError, match="timezone information"):
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


def test_datetime_to_utc_dst_ambiguous_times() -> None:
    """Test and document datetime_to_utc behavior with DST ambiguous times.

    During DST fall-back (Nov 3, 2024 at 2:00 AM → 1:00 AM in US Eastern),
    times like 1:30 AM occur twice. The `fold` attribute determines which:
    - fold=0 (default): First 1:30 AM (EDT, UTC-4) → 5:30 AM UTC
    - fold=1: Second 1:30 AM (EST, UTC-5) → 6:30 AM UTC
    """
    # First 1:30 AM (fold=0 is default, EDT side of transition)
    first_130am = datetime.datetime(2024, 11, 3, 1, 30, 0, tzinfo=ZoneInfo("America/New_York"))
    first_130am_utc = datetime_to_utc(first_130am)
    assert first_130am_utc.hour == 5  # 1:30 AM EDT = 5:30 AM UTC
    assert first_130am_utc.minute == 30

    # Second 1:30 AM (fold=1, EST side of transition)
    second_130am = datetime.datetime(2024, 11, 3, 1, 30, 0, tzinfo=ZoneInfo("America/New_York")).replace(fold=1)
    second_130am_utc = datetime_to_utc(second_130am)
    assert second_130am_utc.hour == 6  # 1:30 AM EST = 6:30 AM UTC
    assert second_130am_utc.minute == 30

    # The two occurrences are 1 hour apart in UTC
    time_diff = (second_130am_utc - first_130am_utc).total_seconds()
    assert time_diff == 3600  # 1 hour difference


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

    # Test for timezone with 45-minute offset (Nepal is UTC+5:45)
    assert format_timezone_offset("Asia/Kathmandu") == "+05:45"


def test_format_timezone_offset_dst_variance() -> None:
    """Test that format_timezone_offset returns the offset at the current moment.

    For DST zones, the offset varies throughout the year. This test documents
    and verifies this behavior using freezegun.
    """
    # Winter time (EST, UTC-5)
    with freeze_time("2024-01-15 12:00:00", tz_offset=0):
        winter_offset = format_timezone_offset("America/New_York")
        assert winter_offset == "-05:00"

    # Summer time (EDT, UTC-4)
    with freeze_time("2024-07-15 12:00:00", tz_offset=0):
        summer_offset = format_timezone_offset("America/New_York")
        assert summer_offset == "-04:00"

    # Verify UTC is always +00:00 regardless of time
    with freeze_time("2024-01-15 12:00:00", tz_offset=0):
        assert format_timezone_offset("UTC") == "+00:00"
    with freeze_time("2024-07-15 12:00:00", tz_offset=0):
        assert format_timezone_offset("UTC") == "+00:00"


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


def test_timezone_error_handling() -> None:
    """Test that timezone functions handle invalid timezone names."""
    # Valid timezone should work
    assert now_in_timezone("UTC") is not None
    assert today_in_timezone("America/New_York") is not None

    # now_in_timezone/today_in_timezone propagate ZoneInfoNotFoundError from zoneinfo
    with pytest.raises(ZoneInfoNotFoundError):
        now_in_timezone("Invalid/Timezone")

    with pytest.raises(ZoneInfoNotFoundError):
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
