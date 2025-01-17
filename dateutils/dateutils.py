import calendar
import time
from wsgiref.handlers import format_date_time
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
    return datetime.now(timezone.utc).date()


def utc_truncate_epoch_day(ts: int) -> int:
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
    return datetime.combine(day, datetime.min.time())


def datetime_end_of_day(day: date) -> datetime:
    return datetime_start_of_day(day) + timedelta(days=1) - timedelta(seconds=1)


##################
# Quarter operations
##################
def date_to_quarter(dt: date) -> int:
    return ((dt.month - 1) // 3) + 1


def date_to_start_of_quarter(dt: date) -> date:
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
    return datetime(year, 1, 1)


def end_of_year(year: int) -> datetime:
    return datetime(year, 12, 31, 23, 59, 59)


def generate_years(until: int = 1970):
    current_year = date.today().year
    for years_ago in range(current_year + 1 - until):
        yield current_year - years_ago


##################
# Month operations
##################
def start_of_month(year: int, month: int) -> datetime:
    return datetime(year, month, 1)


def end_of_month(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    return datetime(year, month, days_in_month, 23, 59, 59)


def generate_months(until_year=1970, until_m=1):
    today = date.today()
    for year in generate_years(until=until_year):
        for month in range(12, 0, -1):
            if year == today.year and month > today.month:
                continue
            if year == until_year and until_m > month:
                return
            else:
                yield month, year


##################
# Week operations
##################
def generate_weeks(count: int = 500, until_date: date | None = None):
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
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    elif day_diff == 1:
        return "Yesterday"
    elif day_diff < 7:
        return str(day_diff) + " days ago"
    elif day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    elif day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def httpdate(date_time: datetime) -> str:
    """
    Convert a datetime object to an HTTP date string
    """
    stamp = time.mktime(date_time.timetuple())
    return format_date_time(stamp)
