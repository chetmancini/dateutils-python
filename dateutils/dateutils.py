
from __future__ import absolute_import, unicode_literals

import calendar

from future.backports.datetime import date, datetime, timedelta
from future.moves import itertools

from core.time import date_to_quarter

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


