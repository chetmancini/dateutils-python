"""
DateUtils Library Entry Point
"""

# Re-export public functions and constants for easier access
from .dateutils import (
    # Constants
    RECENT_SECONDS,
    SECONDS_IN_MINUTE,
    SECONDS_IN_HOUR,
    SECONDS_IN_DAY,
    DAYS_IN_YEAR,
    DAYS_IN_MONTH_APPROX,
    DAYS_IN_WEEK,

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
    get_us_federal_holidays,
    workdays_between,
    add_business_days,
    next_business_day,
    previous_business_day,

    # Human-readable dates
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
    get_timezone_offset,
    format_timezone_offset,
)

__all__ = [
    # Constants
    "RECENT_SECONDS",
    "SECONDS_IN_MINUTE",
    "SECONDS_IN_HOUR",
    "SECONDS_IN_DAY",
    "DAYS_IN_YEAR",
    "DAYS_IN_MONTH_APPROX",
    "DAYS_IN_WEEK",
    # UTC
    "utc_now_seconds",
    "utc_today",
    "utc_truncate_epoch_day",
    "utc_from_timestamp",
    "epoch_s",
    "datetime_start_of_day",
    "datetime_end_of_day",
    # Quarter
    "date_to_quarter",
    "date_to_start_of_quarter",
    "start_of_quarter",
    "end_of_quarter",
    "generate_quarters",
    # Year
    "start_of_year",
    "end_of_year",
    "generate_years",
    "is_leap_year",
    # Month
    "start_of_month",
    "end_of_month",
    "generate_months",
    "get_days_in_month",
    # Week
    "generate_weeks",
    # Day
    "date_range",
    # Holiday/Business Day
    "is_weekend",
    "get_us_federal_holidays",
    "workdays_between",
    "add_business_days",
    "next_business_day",
    "previous_business_day",
    # Formatting/Parsing/Misc
    "pretty_date",
    "httpdate",
    "parse_date",
    "parse_datetime",
    "parse_iso8601",
    "format_date",
    "format_datetime",
    "to_iso8601",
    # Timezone
    "get_available_timezones",
    "now_in_timezone",
    "today_in_timezone",
    "convert_timezone",
    "datetime_to_utc",
    "get_timezone_offset",
    "format_timezone_offset",
]

__version__ = "0.1.0"
