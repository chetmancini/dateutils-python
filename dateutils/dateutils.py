import calendar
import time
from datetime import timezone
from datetime import datetime
from datetime import date
from datetime import timedelta


##################
# UTC
##################
def utc_now_seconds() -> int:
    """
    Get the current time in seconds since epoch in UTC
    """
    return calendar.timegm(time.gmtime())


def utc_today() -> date:
    """
    Get the current date in UTC
    """
    return datetime.now(timezone.utc).date()


def utc_truncate_epoch_day(ts: int) -> int:
    """
    Truncate a timestamp to the start of the day in UTC
    """
    dt = datetime.fromtimestamp(ts, timezone.utc)
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return epoch_s(dt)


def utc_from_timestamp(ts: int):
    """
    Convert a timestamp to a datetime object in UTC timezone
    """
    return datetime.fromtimestamp(ts, timezone.utc)


def epoch_s(dt: datetime) -> int:
    """
    Convert a datetime object to a unix timestamp
    """
    return calendar.timegm(dt.utctimetuple())


def datetime_start_of_day(day: date) -> datetime:
    """
    Get the start of the day for a specific date
    """
    return datetime.combine(day, datetime.min.time())


def datetime_end_of_day(day: date) -> datetime:
    """
    Get the end of the day for a specific date
    """
    return datetime_start_of_day(day) + timedelta(days=1) - timedelta(seconds=1)


##################
# Quarter operations
##################
def date_to_quarter(dt: date) -> int:
    """
    Get the quarter of the year for a specific date
    """
    return ((dt.month - 1) // 3) + 1


def date_to_start_of_quarter(dt: date) -> date:
    """
    Get the start of the quarter for a specific date
    """
    new_month = (((dt.month - 1) // 3) * 3) + 1
    return dt.replace(day=1, month=new_month)


def start_of_quarter(year: int, q: int) -> datetime:
    """
    Get the start of the quarter
    """
    return datetime(year, (q - 1) * 3 + 1, 1)


def end_of_quarter(year: int, q: int):
    """
    Get the end of the quarter
    """
    return datetime(year, q * 3, 1, 23, 59, 59)


def generate_quarters(until_year=1970, until_q=1):
    """
    Generate quarters from the current quarter until a specific year and quarter
    """
    today = date.today()
    current_quarter = date_to_quarter(today)
    current_year = today.year
    for year in generate_years(until=until_year):
        for q in range(4, 0, -1):
            if year == current_year and q > current_quarter:
                continue
            if year == until_year and until_q > q:
                return
            else:
                yield q, year


##################
# Year operations
##################


def start_of_year(year: int) -> datetime:
    """
    Get the start of the year
    """
    return datetime(year, 1, 1)


def end_of_year(year: int) -> datetime:
    """
    Get the end of the year
    """
    return datetime(year, 12, 31, 23, 59, 59)


def generate_years(until: int = 1970):
    """
    Generate years from the current year until a specific year
    """
    current_year = date.today().year
    for years_ago in range(current_year + 1 - until):
        yield current_year - years_ago


def is_leap_year(year: int) -> bool:
    """
    Check if a year is a leap year
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


##################
# Month operations
##################
def start_of_month(year: int, month: int) -> datetime:
    """
    Get the start of the month
    """
    return datetime(year, month, 1)


def end_of_month(year, month):
    """
    Get the end of the month
    """
    days_in_month = calendar.monthrange(year, month)[1]
    return datetime(year, month, days_in_month, 23, 59, 59)


def generate_months(until_year=1970, until_m=1):
    """
    Generate months from the current month until a specific year and month
    """
    today = date.today()
    for year in generate_years(until=until_year):
        for month in range(12, 0, -1):
            if year == today.year and month > today.month:
                continue
            if year == until_year and until_m > month:
                return
            else:
                yield month, year


def get_days_in_month(year: int, month: int) -> int:
    """
    Get the number of days in a specific month and year
    """
    return calendar.monthrange(year, month)[1]


##################
# Week operations
##################
def generate_weeks(count: int = 500, until_date: date | None = None):
    """
    Generate weeks from the current week until a specific date
    """
    this_dow = date.today().weekday()
    monday = date.today() - timedelta(days=this_dow)
    end = monday
    for i in range(count):
        start = end - timedelta(days=7)
        ret = (start, end)
        end = start
        if until_date and start > until_date:
            yield ret
        elif not until_date:
            yield ret
        else:
            return


##################
# Day operations
##################


def date_range(start_date: date, end_date: date) -> list[date]:
    """
    Generate a list of dates between start_date and end_date inclusive
    """
    days = (end_date - start_date).days + 1
    return [start_date + timedelta(days=i) for i in range(days)]


def workdays_between(start_date: date, end_date: date) -> int:
    """
    Count workdays (Mon-Fri) between two dates
    """
    count = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # 0-4 are Monday to Friday
            count += 1
        current += timedelta(days=1)
    return count


def add_business_days(dt: date, num_days: int) -> date:
    """
    Add business days to a date, skipping weekends
    """
    current = dt
    added = 0
    while added < num_days:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Weekday (0-4 are Mon-Fri)
            added += 1
    return current


def _ts_difference(timestamp: int | datetime | None = None, now_override=None):
    now = datetime.now() if not now_override else datetime.fromtimestamp(now_override)
    if type(timestamp) is int:
        diff = now - datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, datetime):
        diff = now - timestamp
    elif not time:
        diff = now - now
    return diff


def pretty_date(timestamp=None, now_override=None):  # NOQA
    """
    Adapted from
    http://stackoverflow.com/questions/1551382/
    user-friendly-time-format-in-python
    """
    diff = _ts_difference(timestamp, now_override)
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ""
    elif day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    elif day_diff == 1:
        return "Yesterday"
    elif day_diff < 7:
        return str(int(day_diff)) + " days ago"
    elif day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    elif day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"


def httpdate(date_time: datetime) -> str:
    """
    Convert a datetime object to an HTTP date string (RFC 7231 compliant).
    Assumes the input datetime is in UTC if not timezone-aware.
    """
    if date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=timezone.utc)
    return date_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
