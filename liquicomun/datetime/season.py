# -*- coding: utf-8 -*-
from liquicomun.datetime import datetime
from liquicomun.datetime.timezone import TIMEZONE
import calendar


def get_season(dt):
    assert isinstance(dt, datetime)
    if not dt.tzinfo:
        dt = TIMEZONE.localize(dt)
    if TIMEZONE.normalize(dt).dst():
        return 'summer'
    else:
        return 'winter'

def last_sunday(year, month):
    """Returns last sunday of month to determine dst change day
    """
    for day in reversed(xrange(1, calendar.monthrange(year, month)[1] + 1)):
        if calendar.weekday(year, month, day) == calendar.SUNDAY:
            return day
