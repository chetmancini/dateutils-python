"""
DateUtils Library Entry Point
"""

import re
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version
from pathlib import Path

# Re-export public functions and constants for easier access
from .dateutils import (
    DAYS_IN_MONTH_APPROX,
    DAYS_IN_MONTH_MAX,
    DAYS_IN_WEEK,
    DAYS_IN_YEAR,
    MONTHS_IN_QUARTER,
    MONTHS_IN_YEAR,
    QUARTERS_IN_YEAR,
    RECENT_SECONDS,
    SECONDS_IN_DAY,
    SECONDS_IN_HOUR,
    SECONDS_IN_MINUTE,
    WEEKDAYS_IN_WEEK,
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
    pretty_date,
    previous_business_day,
    start_of_month,
    start_of_quarter,
    start_of_year,
    time_until_next_occurrence,
    to_iso8601,
    today_in_timezone,
    utc_from_timestamp,
    utc_now_seconds,
    utc_today,
    utc_truncate_epoch_day,
    workdays_between,
)

__all__ = [
    "DAYS_IN_MONTH_APPROX",
    "DAYS_IN_MONTH_MAX",
    "DAYS_IN_WEEK",
    "DAYS_IN_YEAR",
    "MONTHS_IN_QUARTER",
    "MONTHS_IN_YEAR",
    "QUARTERS_IN_YEAR",
    "RECENT_SECONDS",
    "SECONDS_IN_DAY",
    "SECONDS_IN_HOUR",
    "SECONDS_IN_MINUTE",
    "WEEKDAYS_IN_WEEK",
    "add_business_days",
    "age_in_years",
    "convert_timezone",
    "date_range",
    "date_range_generator",
    "date_to_quarter",
    "date_to_start_of_quarter",
    "datetime_end_of_day",
    "datetime_start_of_day",
    "datetime_to_utc",
    "days_since_weekend",
    "days_until_weekend",
    "end_of_month",
    "end_of_quarter",
    "end_of_year",
    "epoch_s",
    "format_date",
    "format_datetime",
    "format_timezone_offset",
    "generate_months",
    "generate_quarters",
    "generate_weeks",
    "generate_years",
    "get_available_timezones",
    "get_days_in_month",
    "get_quarter_start_end",
    "get_timezone_offset",
    "get_us_federal_holidays",
    "get_us_federal_holidays_list",
    "get_week_number",
    "httpdate",
    "is_business_day",
    "is_leap_year",
    "is_weekend",
    "next_business_day",
    "now_in_timezone",
    "parse_date",
    "parse_datetime",
    "parse_iso8601",
    "pretty_date",
    "previous_business_day",
    "start_of_month",
    "start_of_quarter",
    "start_of_year",
    "time_until_next_occurrence",
    "to_iso8601",
    "today_in_timezone",
    "utc_from_timestamp",
    "utc_now_seconds",
    "utc_today",
    "utc_truncate_epoch_day",
    "workdays_between",
]


def _version_from_pyproject() -> str | None:
    """Read the project version from pyproject.toml when distribution metadata is unavailable."""
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    version_pattern = re.compile(r'^version = "([^"]+)"$')
    try:
        for line in pyproject_path.read_text(encoding="utf-8").splitlines():
            match = version_pattern.match(line.strip())
            if match:
                return match.group(1)
    except OSError:
        return None
    return None


def _resolve_version() -> str:
    """Resolve package version from distribution metadata, falling back to pyproject in source checkouts."""
    try:
        return _distribution_version("dateutils-python")
    except PackageNotFoundError:
        return _version_from_pyproject() or "0+unknown"


__version__ = _resolve_version()
