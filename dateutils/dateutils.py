
from __future__ import absolute_import, unicode_literals
import calendar
import time
from wsgiref.handlers import format_date_time
from future.backports.datetime import date, datetime, timedelta

from core.time import date_to_quarter

##################
#
##################
def utc_now_seconds():
    return calendar.timegm(time.gmtime())

def utc_today():
    return datetime.datetime.utcnow().date()


def utc_truncate_epoch_day(ts):
    """
    Returns the epoch representing the start of the day (UTC) containing the
    given epoch timestamp.
    """
    dt = datetime.datetime.utcfromtimestamp(ts)
    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return utc_datetime_to_seconds(dt)


def utc_from_timestamp(ts):
    return datetime.datetime.utcfromtimestamp(ts)


def epoch_s(dt):
    """
    Args:
        dt(datetime.datetime):
    Returns:
        int: dt as epoch seconds
    """
    if type(dt) is datetime.date:
        raise ValueError('epoch_s requires a datetime.')
    return calendar.timegm(dt.utctimetuple())

def datetime_start_of_day(day):
    return datetime.datetime.combine(day, datetime.datetime.min.time())


def datetime_end_of_day(day):
    return datetime_start_of_day(day) + datetime.timedelta(
        days=1) - datetime.timedelta(seconds=1)


##################
# Quarter operations
##################
def date_to_quarter(dt):
    return ((dt.month - 1) // 3) + 1


def date_to_start_of_quarter(dt):
    new_month = (((dt.month - 1) // 3) * 3) + 1
    return dt.replace(day=1, month=new_month)


def start_of_quarter(year, q):
    pass


def end_of_quarter(year, q):
    pass


def generate_quarters(until_year=1970, until_q=1):
    today = date.today()
    current_quarter = date_to_quarter(today)
    current_year = today.year
    for year in generate_years(until=until_year):
        for q in xrange(4, 0, -1):
            if year == current_year and q > current_quarter:
                continue
            if year == until_year and until_q > q:
                return
            else:
                yield (q, year)


##################
# Year operations
##################

def start_of_year(year):
    return datetime(year, 1, 1)


def end_of_year(year):
    return datetime(year, 12, 31, 23, 59, 59)

def generate_years(until=1970):
    current_year = date.today().year
    for years_ago in xrange(current_year + 1 - until):
        yield current_year - years_ago


##################
# Month operations
##################
def start_of_month(year, month):
    return datetime(year, month, 1)


def end_of_month(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    return datetime(year, month, days_in_month, 23, 59, 59)


def generate_months(until_year=1970, until_m=1):
    today = date.today()
    for year in generate_years(until=until_year):
        for month in xrange(12, 0, -1):
            if year == today.year and month > today.month:
                continue
            if year == until_year and until_m > month:
                return
            else:
                yield (month, year)

##################
# Week operations
##################
def generate_weeks(count=500, until_date=None):
    this_dow = date.today().weekday()
    monday = date.today() - timedelta(days=this_dow)
    end = monday
    for i in xrange(count):
        start = end - timedelta(days=7)
        ret = (start, end)
        end = start
        if start > until_date:
            yield ret
        else:
            return


def _ts_difference(timestamp=None, now_override=None):
    from datetime import datetime
    now = datetime.now() if not now_override else datetime.fromtimestamp(
        now_override)
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
        return u''
    elif day_diff == 0:
        if second_diff < 10:
            return u"just now"
        if second_diff < 60:
            return str(second_diff) + u" seconds ago"
        if second_diff < 120:
            return u"a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + u" minutes ago"
        if second_diff < 7200:
            return u"an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + u" hours ago"
    elif day_diff == 1:
        return u"Yesterday"
    elif day_diff < 7:
        return str(day_diff) + u" days ago"
    elif day_diff < 31:
        return str(day_diff / 7) + u" weeks ago"
    elif day_diff < 365:
        return str(day_diff / 30) + u" months ago"
    return str(day_diff / 365) + u" years ago"


def httpdate(date_time):
    stamp = time.mktime(date_time.timetuple())
    return format_date_time(stamp)
