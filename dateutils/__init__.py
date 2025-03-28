"""
dateutils-python: Comprehensive date and time utilities for Python

This package provides utilities for working with dates, times,
and timezones in Python, simplifying common date/time operations.
"""

# Import all public functions explicitly
from .dateutils import (
    # UTC operations
    utc_now_seconds,
    utc_today,
    utc_truncate_epoch_day,
    utc_from_timestamp,
    epoch_s,
    datetime_start_of_day,
    datetime_end_of_day,
    # Quarter operations
    date_to_quarter,
    date_to_start_of_quarter,
    start_of_quarter,
    end_of_quarter,
    generate_quarters,
    # Year operations
    start_of_year,
    end_of_year,
    generate_years,
    is_leap_year,
    # Month operations
    start_of_month,
    end_of_month,
    generate_months,
    get_days_in_month,
    # Week operations
    generate_weeks,
    # Day operations
    date_range,
    # Holiday operations
    is_weekend,
    workdays_between,
    add_business_days,
    next_business_day,
    previous_business_day,
    # Date formatting
    pretty_date,
    httpdate,
    # Parsing and formatting
    parse_date,
    parse_datetime,
    parse_iso8601,
    format_date,
    format_datetime,
    to_iso8601,
    # Timezone operations
    get_available_timezones,
    now_in_timezone,
    today_in_timezone,
    convert_timezone,
    datetime_to_utc,
    utc_to_local,
    get_timezone_offset,
    format_timezone_offset,
)

# Define public API
__all__ = [
    # UTC operations
    "utc_now_seconds",
    "utc_today",
    "utc_truncate_epoch_day",
    "utc_from_timestamp",
    "epoch_s",
    "datetime_start_of_day",
    "datetime_end_of_day",
    # Quarter operations
    "date_to_quarter",
    "date_to_start_of_quarter",
    "start_of_quarter",
    "end_of_quarter",
    "generate_quarters",
    # Year operations
    "start_of_year",
    "end_of_year",
    "generate_years",
    "is_leap_year",
    # Month operations
    "start_of_month",
    "end_of_month",
    "generate_months",
    "get_days_in_month",
    # Week operations
    "generate_weeks",
    # Day operations
    "date_range",
    # Holiday operations
    "is_weekend",
    "workdays_between",
    "add_business_days",
    "next_business_day",
    "previous_business_day",
    # Date formatting
    "pretty_date",
    "httpdate",
    # Parsing and formatting
    "parse_date",
    "parse_datetime",
    "parse_iso8601",
    "format_date",
    "format_datetime",
    "to_iso8601",
    # Timezone operations
    "get_available_timezones",
    "now_in_timezone",
    "today_in_timezone",
    "convert_timezone",
    "datetime_to_utc",
    "utc_to_local",
    "get_timezone_offset",
    "format_timezone_offset",
]

__version__ = "0.1.0"
