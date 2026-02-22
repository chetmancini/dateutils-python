"""
Date parsing and formatting helpers.
"""

import re
from collections.abc import Iterable
from datetime import date, datetime, timedelta, timezone

_MAX_TZ_OFFSET_HOURS = 23
_MAX_TZ_OFFSET_MINUTES = 59

# Compiled regex for ISO 8601 parsing (verbose mode for readability)
_ISO8601_PATTERN = re.compile(
    r"""
    ^
    (\d{4}-\d{2}-\d{2})           # Date part: YYYY-MM-DD (required)
    (?:
        T(\d{2}:\d{2}:\d{2})      # Time part: THH:MM:SS (optional)
        (\.\d+)?                  # Fractional seconds: .123456 (optional)
        (Z | [+-]\d{2}:?\d{2})?   # Timezone: Z or ±HH:MM or ±HHMM (optional)
    )?
    $
    """,
    re.VERBOSE,
)

# Locale-independent English month parsing for parse_date()
_ENGLISH_MONTH_BY_NAME = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}
_MONTH_DAY_YEAR_PATTERN = re.compile(r"^(?P<month>[A-Za-z.]+)\s+(?P<day>\d{1,2}),\s*(?P<year>\d{4})$")
_DAY_MONTH_YEAR_PATTERN = re.compile(r"^(?P<day>\d{1,2})\s+(?P<month>[A-Za-z.]+)\s+(?P<year>\d{4})$")

# Shared default datetime parsing formats for parse_datetime()
_COMMON_DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",  # 2023-01-31 14:30:45
    "%Y-%m-%d %H:%M:%S%z",  # 2023-01-31 14:30:45+02:00
    "%Y-%m-%d %H:%M:%S %z",  # 2023-01-31 14:30:45 +02:00
    "%Y-%m-%dT%H:%M:%S",  # 2023-01-31T14:30:45
    "%Y-%m-%dT%H:%M:%S%z",  # 2023-01-31T14:30:45+02:00
    "%Y-%m-%dT%H:%M:%S.%f",  # 2023-01-31T14:30:45.123456
    "%Y-%m-%dT%H:%M:%S.%f%z",  # 2023-01-31T14:30:45.123456+02:00
    "%Y-%m-%dT%H:%M:%SZ",  # 2023-01-31T14:30:45Z
    "%Y-%m-%dT%H:%M:%S.%fZ",  # 2023-01-31T14:30:45.123456Z
)
_TIME_SUFFIXES = ("%H:%M:%S", "%H:%M:%S%z", "%H:%M:%S %z")
_AMBIGUOUS_DATE_FORMATS = {
    True: ("%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"),
    False: ("%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y"),
}


def _build_default_date_formats(dayfirst: bool) -> tuple[str, ...]:
    """Build ordered default parse_date formats for day-first or month-first preference."""
    return (
        "%Y-%m-%d",  # 2023-01-31 (ISO - unambiguous)
        *_AMBIGUOUS_DATE_FORMATS[dayfirst],
        "%d.%m.%Y",  # 31.01.2023
        "%Y/%m/%d",  # 2023/01/31
    )


_DEFAULT_DATE_FORMATS = {
    True: _build_default_date_formats(dayfirst=True),
    False: _build_default_date_formats(dayfirst=False),
}


def _build_default_datetime_formats(dayfirst: bool) -> tuple[str, ...]:
    """Build ordered default parse_datetime formats for day-first or month-first preference."""
    formats = list(_COMMON_DATETIME_FORMATS)
    ordered_date_formats = (*_AMBIGUOUS_DATE_FORMATS[dayfirst], "%Y/%m/%d")
    for date_fmt in ordered_date_formats:
        formats.extend(f"{date_fmt} {time_fmt}" for time_fmt in _TIME_SUFFIXES)
    return tuple(formats)


_DEFAULT_DATETIME_FORMATS = {
    True: _build_default_datetime_formats(dayfirst=True),
    False: _build_default_datetime_formats(dayfirst=False),
}


class ParseError(ValueError):
    """Raised when strict parsing functions cannot parse an input value."""

    def __init__(
        self,
        *,
        parser: str,
        value: str,
        reason: str,
        attempted_formats: Iterable[str] | None = None,
    ) -> None:
        self.parser = parser
        self.value = value
        self.reason = reason.rstrip(".")
        self.attempted_formats = tuple(attempted_formats or ())

        details = f"Failed to parse {self.parser} from {self.value!r}: {self.reason}."
        if self.attempted_formats:
            details += f" Attempted formats: {', '.join(self.attempted_formats)}."
        super().__init__(details)


def _resolve_date_formats(formats: list[str] | None, dayfirst: bool) -> tuple[tuple[str, ...], bool]:
    """Return date formats and whether defaults are being used."""
    if formats is None:
        return _DEFAULT_DATE_FORMATS[dayfirst], True
    return tuple(formats), False


def _is_calendar_date_value_error(error: ValueError) -> bool:
    """Return True when a strptime/date ValueError indicates calendar-invalid fields."""
    message = str(error).lower()
    return "out of range" in message or "must be in range" in message or "invalid date" in message


def _parse_date_from_formats(date_str: str, parse_formats: Iterable[str]) -> tuple[date | None, ValueError | None]:
    """Attempt to parse a date against the provided formats."""
    calendar_error: ValueError | None = None
    # Exception-driven parsing is expected here while trying multiple date layouts.
    for fmt in parse_formats:
        try:
            return datetime.strptime(date_str, fmt).date(), None
        except ValueError as e:  # noqa: PERF203
            if calendar_error is None and _is_calendar_date_value_error(e):
                calendar_error = e
            continue
    return None, calendar_error


def parse_date(
    date_str: str,
    formats: list[str] | None = None,
    *,
    dayfirst: bool = False,
) -> date:
    """
    Parse a date string using multiple possible formats.

    Tries a list of common formats if `formats` is not provided.
    For ambiguous dates like "03/04/2024", the `dayfirst` parameter controls
    interpretation: False (default) treats it as March 4th (US style),
    True treats it as April 3rd (European style).

    Args:
        date_str: The date string to parse.
        formats: Optional list of format strings (e.g., "%Y/%m/%d") to try.
            If provided, `dayfirst` is ignored.
        dayfirst: If True, ambiguous dates are parsed as day/month/year (European).
            If False (default), ambiguous dates are parsed as month/day/year (US).
            Only applies when `formats` is None.

    Returns:
        A parsed date object.

    Raises:
        ParseError: If the input cannot be parsed or if parsed values are invalid.

    Examples:
        >>> from datetime import date
        >>> parse_date("2024-07-22")
        datetime.date(2024, 7, 22)

        >>> parse_date("07/22/2024")  # US format (default)
        datetime.date(2024, 7, 22)

        >>> parse_date("22/07/2024", dayfirst=True)  # European format
        datetime.date(2024, 7, 22)

        >>> # Ambiguous date: 03/04/2024
        >>> parse_date("03/04/2024")  # Default: March 4th
        datetime.date(2024, 3, 4)

        >>> parse_date("03/04/2024", dayfirst=True)  # European: April 3rd
        datetime.date(2024, 4, 3)

        >>> parse_date("22 Jul 2024")
        datetime.date(2024, 7, 22)

        >>> parse_date("July 22, 2024")
        datetime.date(2024, 7, 22)

        >>> # Using a custom format
        >>> parse_date("20242207", formats=["%Y%d%m"])
        datetime.date(2024, 7, 22)

        >>> try:
        ...     parse_date("invalid date string")
        ... except ParseError as e:
        ...     print(e.parser)
        ...     print(e.value)
        date
        invalid date string

    """
    date_str = date_str.strip()

    parse_formats, default_formats = _resolve_date_formats(formats, dayfirst)
    if not parse_formats:
        raise ParseError(parser="date", value=date_str, reason="no formats were provided")

    parsed, calendar_error = _parse_date_from_formats(date_str, parse_formats)
    if parsed is not None:
        return parsed
    if calendar_error is not None:
        raise ParseError(
            parser="date",
            value=date_str,
            reason=f"invalid calendar date ({calendar_error})",
            attempted_formats=parse_formats,
        ) from calendar_error

    # Locale-independent fallback for English month names in the default parser.
    if default_formats:
        try:
            parsed_english = _parse_english_textual_date(date_str)
        except ValueError as e:
            raise ParseError(
                parser="date",
                value=date_str,
                reason=f"invalid calendar date ({e})",
                attempted_formats=parse_formats,
            ) from e
        if parsed_english is not None:
            return parsed_english

    reason = "value did not match any supported format"
    if default_formats:
        reason += " (including English month-name forms)"
    raise ParseError(parser="date", value=date_str, reason=reason, attempted_formats=parse_formats)


def _parse_english_textual_date(date_str: str) -> date | None:
    """Parse common English month-name date formats without locale dependencies."""
    normalized = re.sub(r"\s+", " ", date_str.strip())
    for pattern in (_MONTH_DAY_YEAR_PATTERN, _DAY_MONTH_YEAR_PATTERN):
        match = pattern.match(normalized)
        if not match:
            continue
        month_name = match.group("month").lower().rstrip(".")
        month = _ENGLISH_MONTH_BY_NAME.get(month_name)
        if month is None:
            # Unknown month tokens are treated as "no textual match" so parse_date
            # can continue to generic format-mismatch handling.
            return None
        year = int(match.group("year"))
        day = int(match.group("day"))
        try:
            return date(year, month, day)
        except ValueError:
            # Calendar-invalid textual dates (for example "Feb 29, 2023") are
            # re-raised so parse_date can surface a specific invalid-date reason.
            raise
    return None


def _resolve_datetime_formats(formats: list[str] | None, dayfirst: bool) -> tuple[str, ...]:
    """Return datetime formats."""
    if formats is None:
        return _DEFAULT_DATETIME_FORMATS[dayfirst]
    return tuple(formats)


def _parse_datetime_from_formats(datetime_str: str, parse_formats: Iterable[str]) -> datetime | None:
    """Attempt to parse a datetime against the provided formats."""
    # Exception-driven parsing is expected here while trying multiple datetime layouts.
    for fmt in parse_formats:
        try:
            dt = datetime.strptime(datetime_str, fmt)
            # Handle ISO 8601 format with timezone designator
            if datetime_str.endswith("Z"):
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:  # noqa: PERF203
            continue
    return None


def parse_datetime(datetime_str: str, formats: list[str] | None = None, dayfirst: bool = False) -> datetime:
    """
    Parse a datetime string using multiple possible formats.

    Supports timezone-aware values in default parsing, including:
    - UTC designator `Z`
    - Numeric offsets with or without a colon (for example `+02:00`, `-0500`)

    Args:
        datetime_str: The datetime string to parse
        formats: List of format strings to try (if None, uses common formats).
            If provided, `dayfirst` is ignored.
        dayfirst: If True, ambiguous dates are parsed as day/month/year (European).
            If False (default), ambiguous dates are parsed as month/day/year (US).
            Only applies when `formats` is None.

    Returns:
        A parsed datetime object.

    Raises:
        ParseError: If the input cannot be parsed.
    """
    datetime_str = datetime_str.strip()

    parse_formats = _resolve_datetime_formats(formats, dayfirst)

    if not parse_formats:
        raise ParseError(parser="datetime", value=datetime_str, reason="no formats were provided")

    parsed = _parse_datetime_from_formats(datetime_str, parse_formats)
    if parsed is not None:
        return parsed

    raise ParseError(
        parser="datetime",
        value=datetime_str,
        reason="value did not match any supported format",
        attempted_formats=parse_formats,
    )


def parse_iso8601(iso_str: str) -> datetime:
    """
    Parse an ISO 8601 formatted date/time string.

    This handles various ISO 8601 formats including:
    - Date only: 2023-01-31
    - Date and time: 2023-01-31T14:30:45
    - With milliseconds: 2023-01-31T14:30:45.123
    - With timezone: 2023-01-31T14:30:45+02:00

    Note:
        Fractional seconds are limited to microsecond precision (6 digits).
        Any digits beyond 6 are silently truncated. For example,
        ".123456789" (nanoseconds) becomes ".123456" (microseconds).

    Args:
        iso_str: The ISO 8601 string to parse

    Returns:
        A parsed datetime object.

    Raises:
        ParseError: If the input does not match supported ISO 8601 shapes.
    """
    normalized = iso_str.strip()
    try:
        return _parse_iso8601_unchecked(normalized)
    except ValueError as e:
        raise ParseError(parser="ISO 8601 datetime", value=normalized, reason=str(e)) from e


def _parse_iso8601_unchecked(iso_str: str) -> datetime:
    """Parse ISO 8601 string and raise ValueError on invalid inputs."""
    match = _ISO8601_PATTERN.match(iso_str)
    if not match:
        raise ValueError("value does not match supported pattern YYYY-MM-DD[THH:MM:SS[.fraction][Z|±HH:MM|±HHMM]]")

    date_part, time_part, ms_part, tz_part = match.groups()

    if time_part is None:
        # Date only (regex guarantees ms_part and tz_part are also None)
        return datetime.strptime(date_part, "%Y-%m-%d")

    # Combine date and time
    dt_str = f"{date_part}T{time_part}"
    dt_format = "%Y-%m-%dT%H:%M:%S"

    if ms_part:
        # Truncate to microsecond precision (6 digits max after the decimal point)
        max_fractional_len = 7  # ".XXXXXX" (1 dot + 6 digits)
        if len(ms_part) > max_fractional_len:
            ms_part = ms_part[:max_fractional_len]
        dt_str += ms_part
        dt_format += ".%f"

    dt = datetime.strptime(dt_str, dt_format)

    # Handle timezone
    if tz_part:
        if tz_part == "Z":
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # Convert +HH:MM or +HHMM to ±HHMM and validate components
            tz_digits = tz_part.replace(":", "")
            sign = -1 if tz_digits[0] == "-" else 1
            hours = int(tz_digits[1:3])
            minutes = int(tz_digits[3:5])

            if hours > _MAX_TZ_OFFSET_HOURS or minutes > _MAX_TZ_OFFSET_MINUTES:
                raise ValueError(f"timezone offset is out of range: {tz_part}")

            offset = sign * timedelta(hours=hours, minutes=minutes)
            dt = dt.replace(tzinfo=timezone(offset))

    return dt


def format_date(dt: date | datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a date or datetime object using the specified format.

    Args:
        dt: The date or datetime to format
        format_str: Format string (default ISO format)

    Returns:
        Formatted date string
    """
    if isinstance(dt, datetime):
        dt = dt.date()

    return dt.strftime(format_str)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object using the specified format.

    Args:
        dt: The datetime to format
        format_str: Format string (default ISO format without T)

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def to_iso8601(dt: date | datetime) -> str:
    """
    Convert a date or datetime to ISO 8601 format.

    Args:
        dt: Date or datetime to convert

    Returns:
        ISO 8601 formatted string
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt.isoformat()

    # It's a datetime
    if dt.tzinfo is None:
        # Assume UTC for naive datetimes
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.isoformat()
