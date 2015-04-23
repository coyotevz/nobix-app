from collections import namedtuple, OrderedDict
from itertools import groupby, chain
from datetime import datetime, time, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse


Interval = namedtuple("Interval", "input output")
IntervalInfo = namedtuple("IntervalInfo", "input output late")
Record = namedtuple("Record", "day intervals")

worktime_spec = {
    0: (['8:30', '12:30'], ['16:00', '20:00']),
    1: (['8:30', '12:30'], ['16:00', '20:00']),
    2: (['8:30', '12:30'], ['16:00', '20:00']),
    3: (['8:30', '12:30'], ['16:00', '20:00']),
    4: (['8:30', '12:30'], ['16:00', '20:00']),
    5: (['9:00', '13:00'],),
}

def perfect_grid(year, month):
    sdate = date(year, month, 1)
    edate = sdate+relativedelta(day=31)

    workdays = rrule(DAILY, dtstart=sdate, until=edate,
                     byweekday=worktime_spec.keys())

    grid = [(day.date(),
             [Interval(parse(i[0]).time(), parse(i[1]).time())\
              for i in worktime_spec.get(day.weekday())])\
            for day in workdays]
    return grid


def time_diff(t1, t2):
    "Return timedelta form 2 time() objects"
    t1_sec = (t1.hour*60+t1.minute)*60+t1.second
    t2_sec = (t2.hour*60+t2.minute)*60+t2.second
    return timedelta(seconds=t1_sec-t2_sec)

def _gdate(item):
    return item.datetime.date()

def min_diff_index(l, t):
    "Return index of the minimum difference"
    ci = 0
    cd = None
    for i, r in enumerate(l):
        diff = abs(time_diff(r[0], t).total_seconds())
        if cd is None or diff < cd:
            ci = i
            cd = diff
    return ci

def grouped(iterable, n=2):
    "Return n elements at time from iterable"
    return zip(*[iter(iterable)]*n)

def fixed_records(query, year, month):
    """Return a list with fixed records from query.

    return list of (day, [Interval(), Interval(), ...])
    """
    grid = perfect_grid(year, month)

    records = dict((day, [r.datetime.time() for r in record])\
                    for day, record in groupby(query, _gdate))

    fixed = []
    for day, intervals in grid:
        day_records = records.get(day, [])
        pairs = [[i, None] for i in chain(*intervals)]
        # FIXME: This can fall in an infinite loop
        processed = 0
        while len(day_records) and processed < len(pairs)*10:
            processed += 1
            rec = day_records.pop(0)
            mini = min_diff_index(pairs, rec)
            if pairs[mini][1] is not None:
                day_records.append(pairs[mini][1])
            pairs[mini][1] = rec
        ints = []
        for s, e in grouped(pairs):
            if s[1]:
                diff = time_diff(s[1], s[0])
                if diff.total_seconds() < 0:
                    diff = timedelta(seconds=0)
            else:
                diff = None
            ints.append(IntervalInfo(s[1], e[1], diff))
        fixed.append(Record(day, ints))
    return fixed
