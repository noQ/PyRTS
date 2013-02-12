'''
Created on Jun 6, 2012

@author: Adrian Costia
'''

import datetime
import calendar
from datetime import date as real_date, datetime as real_datetime

class date(real_date):
    def strftime(self, fmt):
        return strftime(self, fmt)

def new_date(d):
    "Generate a safe date from a datetime.date object."
    return date(d.year, d.month, d.day)

def new_datetime(d):
    """
    Generate a safe datetime from a datetime.date or datetime.datetime object.
    """
    kw = [d.year, d.month, d.day]
    if isinstance(d, real_datetime):
        kw.extend([d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
    return datetime(*kw)

def date_to_int(value):
    if  isinstance(value, datetime.datetime):
        if value.utcoffset() is not None:
            value = value - value.utcoffset()
        millis = int(calendar.timegm(value.timetuple()) * 1000 +
                     value.microsecond / 1000)
        return millis    