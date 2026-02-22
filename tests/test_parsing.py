import datetime
import locale
from typing import cast
from zoneinfo import ZoneInfo

import pytest

from dateutils.dateutils import (
    ParseError,
    format_date,
    format_datetime,
    parse_date,
    parse_datetime,
    parse_iso8601,
    to_iso8601,
)

##################
# Parsing and formatting tests
##################


def _parse_error(exc_info: pytest.ExceptionInfo[BaseException]) -> ParseError:
    return cast(ParseError, exc_info.value)


def test_parse_date() -> None:
    """Test parsing date strings in various formats."""
    assert parse_date(" 2024-03-27 ") == datetime.date(2024, 3, 27)

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
    with pytest.raises(ParseError):
        parse_date("not a date")
    with pytest.raises(ParseError):
        parse_date("2024-13-45")  # Invalid month and day


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


def test_parse_date_english_month_names_locale_independent() -> None:
    """English month-name parsing should not depend on process locale."""
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

        assert parse_date("March 27, 2024") == datetime.date(2024, 3, 27)
        assert parse_date("27 Mar 2024") == datetime.date(2024, 3, 27)
    finally:
        locale.setlocale(locale.LC_TIME, original_locale)


def test_parse_date_custom_formats_do_not_use_default_fallbacks() -> None:
    """When custom formats are supplied, default format/text parsing should be skipped."""
    with pytest.raises(ParseError):
        parse_date("March 27, 2024", formats=["%Y/%m/%d"])


def test_parse_date_invalid_english_month_name() -> None:
    """Unknown month names should raise ParseError."""
    with pytest.raises(ParseError):
        parse_date("Foober 27, 2024")


def test_parse_date_invalid_calendar_dates() -> None:
    """Invalid but recognizable calendar dates should raise ParseError."""
    # Feb 29 in non-leap year
    with pytest.raises(ParseError):
        parse_date("2023-02-29")  # 2023 is not a leap year
    with pytest.raises(ParseError) as exc_info:
        parse_date("Feb 29, 2023")
    assert "invalid calendar date" in _parse_error(exc_info).reason

    # Feb 30 never exists
    with pytest.raises(ParseError):
        parse_date("2024-02-30")
    with pytest.raises(ParseError):
        parse_date("February 30, 2024")

    # April, June, September, November have 30 days (not 31)
    with pytest.raises(ParseError) as exc_info:
        parse_date("2024-04-31")  # April has 30 days
    assert "invalid calendar date" in _parse_error(exc_info).reason
    with pytest.raises(ParseError):
        parse_date("2024-06-31")  # June has 30 days
    with pytest.raises(ParseError):
        parse_date("2024-09-31")  # September has 30 days
    with pytest.raises(ParseError):
        parse_date("2024-11-31")  # November has 30 days

    # Invalid month
    with pytest.raises(ParseError):
        parse_date("2024-13-01")
    with pytest.raises(ParseError):
        parse_date("2024-00-15")

    # Invalid day
    with pytest.raises(ParseError):
        parse_date("2024-01-32")
    with pytest.raises(ParseError):
        parse_date("2024-01-00")

    # Valid leap year Feb 29 should work
    assert parse_date("2024-02-29") == datetime.date(2024, 2, 29)  # 2024 is a leap year
    assert parse_date("Feb 29, 2024") == datetime.date(2024, 2, 29)


def test_parse_date_errors_include_details() -> None:
    """Date parsing should raise ParseError with useful details."""
    assert parse_date("03/04/2024", dayfirst=True) == datetime.date(2024, 4, 3)
    assert parse_date("2024|03|27", formats=["%Y|%m|%d"]) == datetime.date(2024, 3, 27)

    with pytest.raises(ParseError, match="Failed to parse date") as exc_info:
        parse_date("not a date")

    err = _parse_error(exc_info)
    assert err.parser == "date"
    assert err.value == "not a date"
    assert "supported format" in err.reason
    assert "%Y-%m-%d" in err.attempted_formats

    with pytest.raises(ParseError, match="no formats were provided"):
        parse_date("2024-03-27", formats=[])


def test_parse_datetime() -> None:
    """Test parsing datetime strings in various formats."""
    assert parse_datetime(" 2024-03-27T14:30:45Z ") == datetime.datetime(
        2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc
    )

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

    # Test with timezone offset with colon (ISO)
    with_tz_colon = parse_datetime("2024-03-27T14:30:45+02:00")
    assert with_tz_colon is not None
    assert with_tz_colon.tzinfo is not None
    assert with_tz_colon.tzinfo.utcoffset(None) == datetime.timedelta(hours=2)

    # Test with timezone offset without colon (ISO)
    with_tz_no_colon = parse_datetime("2024-03-27T14:30:45-0500")
    assert with_tz_no_colon is not None
    assert with_tz_no_colon.tzinfo is not None
    assert with_tz_no_colon.tzinfo.utcoffset(None) == datetime.timedelta(hours=-5)

    # Test other date formats with time
    assert parse_datetime("27/03/2024 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)  # DD/MM/YYYY
    assert parse_datetime("03/27/2024 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)  # MM/DD/YYYY
    assert parse_datetime("27-03-2024 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)  # DD-MM-YYYY
    assert parse_datetime("2024/03/27 14:30:45") == datetime.datetime(2024, 3, 27, 14, 30, 45)  # YYYY/MM/DD
    assert parse_datetime("03/27/2024 14:30:45-0500") == datetime.datetime(
        2024,
        3,
        27,
        14,
        30,
        45,
        tzinfo=datetime.timezone(datetime.timedelta(hours=-5)),
    )
    assert parse_datetime("03/27/2024 14:30:45 +02:00") == datetime.datetime(
        2024,
        3,
        27,
        14,
        30,
        45,
        tzinfo=datetime.timezone(datetime.timedelta(hours=2)),
    )

    # Test with custom format
    assert parse_datetime("2024|03|27|14|30|45", formats=["%Y|%m|%d|%H|%M|%S"]) == datetime.datetime(
        2024, 3, 27, 14, 30, 45
    )

    # Test ambiguous date defaults to US style (month first), consistent with parse_date
    assert parse_datetime("03/04/2024 12:00:00") == datetime.datetime(2024, 3, 4, 12, 0, 0)

    # Test dayfirst=True interprets ambiguous date as European (day first)
    assert parse_datetime("03/04/2024 12:00:00", dayfirst=True) == datetime.datetime(2024, 4, 3, 12, 0, 0)

    # Test dayfirst with dash separator
    assert parse_datetime("03-04-2024 12:00:00") == datetime.datetime(2024, 3, 4, 12, 0, 0)
    assert parse_datetime("03-04-2024 12:00:00", dayfirst=True) == datetime.datetime(2024, 4, 3, 12, 0, 0)

    # Test invalid datetime
    with pytest.raises(ParseError):
        parse_datetime("not a datetime")
    with pytest.raises(ParseError):
        parse_datetime("2024-03-27T25:70:80")  # Invalid hours, minutes, seconds
    with pytest.raises(ParseError):
        parse_datetime("2024-03-27T14:30:45+25:00")  # Invalid timezone offset


def test_parse_datetime_errors_include_details() -> None:
    """Datetime parsing should raise ParseError with format details on failure."""
    assert parse_datetime("2024-03-27T14:30:45Z") == datetime.datetime(
        2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc
    )

    with pytest.raises(ParseError, match="Failed to parse datetime"):
        parse_datetime("not a datetime")

    with pytest.raises(ParseError) as exc_info:
        parse_datetime("not a datetime", formats=["%Y|%m|%d"])

    err = _parse_error(exc_info)
    assert err.parser == "datetime"
    assert err.value == "not a datetime"
    assert err.attempted_formats == ("%Y|%m|%d",)

    with pytest.raises(ParseError, match="no formats were provided"):
        parse_datetime("2024-03-27 14:30:45", formats=[])


def test_parse_iso8601() -> None:
    """Test parsing ISO 8601 formatted strings."""
    assert parse_iso8601(" 2024-03-27T14:30:45Z ") == datetime.datetime(
        2024, 3, 27, 14, 30, 45, tzinfo=datetime.timezone.utc
    )

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
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27 14:30:45")

    # Test with partial time specification
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T14")
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T14:30")

    # Test invalid patterns
    with pytest.raises(ParseError):
        parse_iso8601("not iso8601")
    with pytest.raises(ParseError):
        parse_iso8601("2024/03/27")  # Wrong date separator
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27 14:30:45")  # Space instead of T
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27+0200")  # Timezone without time
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27+02:00")  # Timezone without time
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27Z")  # UTC designator without time
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27.123")  # Fractional seconds without time
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27.123Z")  # Fractional + timezone without time


def test_parse_iso8601_malformed_edge_cases() -> None:
    """Test that malformed date+tz and date+fraction combinations are handled correctly."""
    # Fractional seconds with non-Z timezone offset (valid ISO 8601)
    result = parse_iso8601("2024-03-27T14:30:45.123+02:00")
    assert result is not None
    assert result.microsecond == 123000
    assert result.tzinfo is not None
    assert result.tzinfo.utcoffset(None) == datetime.timedelta(hours=2)

    result = parse_iso8601("2024-03-27T14:30:45.123456-05:30")
    assert result is not None
    assert result.microsecond == 123456
    assert result.tzinfo is not None
    assert result.tzinfo.utcoffset(None) == datetime.timedelta(hours=-5, minutes=-30)

    # Invalid timezone offset values (accepted by regex, rejected by validation)
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T14:30:45+25:00")  # Hours > 23
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T14:30:45+00:60")  # Minutes > 59
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T14:30:45.123+25:00")  # Fraction + invalid tz

    # Invalid calendar dates (accepted by regex, rejected by strptime)
    with pytest.raises(ParseError):
        parse_iso8601("2024-13-01T14:30:45")  # Month 13
    with pytest.raises(ParseError):
        parse_iso8601("2024-02-30T14:30:45")  # Feb 30
    with pytest.raises(ParseError):
        parse_iso8601("2024-00-15T14:30:45")  # Month 0

    # Malformed fraction/tz patterns (rejected by regex)
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T14:30:45.")  # Trailing dot, no digits
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27TZ")  # T without time, then Z
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T+02:00")  # T without time, then tz offset
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T.123")  # T without time, then fraction


def test_parse_iso8601_nanosecond_truncation() -> None:
    """Test that nanosecond precision is truncated to microseconds."""
    # Nanosecond precision (9 digits) should be truncated to microseconds (6 digits)
    result = parse_iso8601("2024-03-27T14:30:45.123456789")
    assert result is not None
    assert result.microsecond == 123456  # Truncated from .123456789

    # 7 digits should be truncated
    result = parse_iso8601("2024-03-27T14:30:45.1234567")
    assert result is not None
    assert result.microsecond == 123456

    # Exactly 6 digits should work as-is
    result = parse_iso8601("2024-03-27T14:30:45.999999")
    assert result is not None
    assert result.microsecond == 999999

    # With timezone and nanoseconds
    result = parse_iso8601("2024-03-27T14:30:45.123456789Z")
    assert result is not None
    assert result.microsecond == 123456
    assert result.tzinfo == datetime.timezone.utc


def test_parse_iso8601_invalid_values_raise() -> None:
    """Invalid calendar/time/offset values should raise ParseError."""
    with pytest.raises(ParseError):
        parse_iso8601("2024-02-30")
    with pytest.raises(ParseError):
        parse_iso8601("2024-13-01")
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T25:00:00")
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T14:30:45+24:00")
    with pytest.raises(ParseError):
        parse_iso8601("2024-03-27T14:30:45+02:99")


def test_parse_iso8601_errors_include_details() -> None:
    """ISO parsing should raise ParseError with clear reasons."""
    assert parse_iso8601("2024-03-27T14:30:45+02:00") == datetime.datetime(
        2024,
        3,
        27,
        14,
        30,
        45,
        tzinfo=datetime.timezone(datetime.timedelta(hours=2)),
    )

    with pytest.raises(ParseError, match="supported pattern"):
        parse_iso8601("2024-03-27 14:30:45")

    with pytest.raises(ParseError, match="timezone offset is out of range"):
        parse_iso8601("2024-03-27T14:30:45+25:00")

    with pytest.raises(ParseError) as exc_info:
        parse_iso8601("2024-02-30")

    err = _parse_error(exc_info)
    assert err.parser == "ISO 8601 datetime"
    assert err.value == "2024-02-30"
    assert err.reason
    assert "invalid value" not in err.reason


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
