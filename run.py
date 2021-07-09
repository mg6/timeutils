#!/usr/bin/env python3
"""Time scheduling utilities.

Usage:
    timeutils -f FILENAME [--from FROM] [--to TO] [--format FORMAT]
    timeutils --help

Options:
    -f, --file FILENAME     ICS file to read from.
    --format FORMAT         Format to use when showing work log.
    -F, --from FROM         Start date for filtering.
    -T, --to TO             End date for filtering.
    -h, --help              Show help screen.

"""
import os

import hashlib
import json
import re

import arrow
import docopt
import ics


def drop_section(from_match, to_match, iterable):
    from_match = from_match.upper()
    to_match = to_match.upper()
    ignore = False

    for line in iterable:
        if from_match in line.upper():
            ignore = True
        if to_match in line.upper():
            ignore = False
            continue
        if not ignore:
            yield line

out = ''.join(drop_section('<', '>', 'a<c>e')); assert out == 'ae', out
out = ''.join(drop_section('<', '>', 'a<c>e<g>h')); assert out == 'aeh', out
out = ''.join(drop_section('<', '>', 'a<cde')); assert out == 'a', out
out = ''.join(drop_section('<', '>', 'abc>e')); assert out == 'abce', out
out = ''.join(drop_section('<', '>', 'abcde')); assert out == 'abcde', out
out = ''.join(drop_section('<', '>', 'a<c<e')); assert out == 'a', out
out = ''.join(drop_section('<', '>', 'a>c>e')); assert out == 'ace', out
out = ''.join(drop_section('<', '>', 'a<c<e>g')); assert out == 'ag', out
out = ''.join(drop_section('<', '>', 'a>c>e<g')); assert out == 'ace', out
out = ''.join(drop_section('<', '>', 'a>c>e<g>i')); assert out == 'acei', out
out = ''.join(drop_section('<', '>', '<>')); assert out == '', out
out = ''.join(drop_section('<', '>', '<')); assert out == '', out
out = ''.join(drop_section('<', '>', '>')); assert out == '', out
out = ''.join(drop_section('<', '>', '')); assert out == '', out


def extract_section(from_match, to_match, iterable, join_char='\r\n'):
    from_match = from_match.upper()
    to_match = to_match.upper()
    include = False
    buf = []

    for line in iterable:
        if from_match in line.upper():
            include = True
        if to_match in line.upper():
            include = False
            if buf:
                buf.append(line)
                yield join_char.join(buf)
                buf = []
            continue
        if include:
            buf.append(line)

    if buf:
        yield join_char.join(buf)

out = ''.join(extract_section('<', '>', 'a<c>e', join_char='')); assert out == '<c>', out
out = ''.join(extract_section('<', '>', 'a<c>e<g>h', join_char='')); assert out == '<c><g>', out
out = ''.join(extract_section('<', '>', 'a<cde', join_char='')); assert out == '<cde', out
out = ''.join(extract_section('<', '>', 'abc>e', join_char='')); assert out == '', out
out = ''.join(extract_section('<', '>', 'abcde', join_char='')); assert out == '', out
out = ''.join(extract_section('<', '>', 'a<c<e', join_char='')); assert out == '<c<e', out
out = ''.join(extract_section('<', '>', 'a>c>e', join_char='')); assert out == '', out
out = ''.join(extract_section('<', '>', 'a<c<e>g', join_char='')); assert out == '<c<e>', out
out = ''.join(extract_section('<', '>', 'a>c>e<g', join_char='')); assert out == '<g', out
out = ''.join(extract_section('<', '>', 'a>c>e<g>i', join_char='')); assert out == '<g>', out
out = ''.join(extract_section('<', '>', '<>', join_char='')); assert out == '<>', out
out = ''.join(extract_section('<', '>', '<', join_char='')); assert out == '<', out
out = ''.join(extract_section('<', '>', '>', join_char='')); assert out == '', out
out = ''.join(extract_section('<', '>', '', join_char='')); assert out == '', out


def by_begin_date(ev):
    return ev.begin


class WorkLog:

    def __init__(self, name, begin, end):
        if begin > end:
            begin, end = end, begin

        self.begin = begin
        self.end = end
        self.duration = end - begin
        self.ticket = self.extract_ticket(name)
        self.name = self.extract_name(name)
        self.hash = self.extract_hash(name, begin)

    def format(self, fmt):
        return fmt.format(
            name=self.name, ticket=self.ticket,
            begin=self.begin, end=self.end,
            begin_f=self.begin.format('YYYY-MM-DD'),
            begin_t=self.begin.format('HH:mm'),
            end_f=self.end.format('YYYY-MM-DD'),
            end_t=self.end.format('HH:mm'),
            duration=self.duration,
            duration_s=self.duration.seconds,
            duration_h=self.duration.seconds/3600,
            hash = self.hash,
            toggl = json.dumps({
                "time_entry": {
                    "description": self.name,
                    "created_with": "API",
                    "start": str(self.begin),
                    "duration": self.duration.seconds,
                    "pid": os.environ.get("TOGGL_PROJECT", 0),
                }
            }))

    def __repr__(self):
        return self.format("<WorkLog '{name}' ticket:{ticket} begin:{begin} end:{end} hash:{hash}>")

    def __hash__(self):
        return hash(self.begin.format('YYYYMMDD') + self.hash)

    @staticmethod
    def extract_hash(name, begin):
        name = __class__.extract_name(name)
        begin = begin.format('YYYYMMDD')
        params = begin + name
        return hashlib.sha256(params.encode()).hexdigest()[:7]

    @staticmethod
    def extract_name(name):
        return re.sub(r'@\S+', '', name).strip()

    @staticmethod
    def extract_ticket(name):
        try:
            return re.search(r'@\S+', name).group(0)
        except AttributeError:
            return ''

    @staticmethod
    def from_ics_event(ev):
        return WorkLog(name=ev.name, begin=ev.begin, end=ev.end)


def main(args):
    with open(args['--file'], 'r') as f:
        data = f.readlines()
        data = drop_section('BEGIN:VALARM', 'END:VALARM', data)     # drop TRIGGER statements, unsupported by ics

    for chunk in extract_section('BEGIN:VCALENDAR', 'END:VCALENDAR', data):
        dump_events(chunk, args['--from'], args['--to'], args['--format'])


def dump_events(data, since, until, format):
    cal = ics.Calendar(data)
    events = cal.events
    # events = sorted(events, key=by_begin_date)
    if since and until:
        events = filter(lambda e: e.begin >= since and e.end <= until, events)
    events = filter(lambda e: not e.all_day, events)

    for ev in events:
        if format:
            print(WorkLog.from_ics_event(ev).format(format))
        else:
            print(WorkLog.from_ics_event(ev))


def parse_user_date(date, default=None):
    if not date:
        return default

    date = arrow.get(date, ['YYYYMMDD', 'YYMMDD', 'MMDD'])
    if date.year <= 1:
        date = date.replace(year=arrow.now().year)
    return date


def parse_args():
    args = docopt.docopt(__doc__)
    args['--from'] = parse_user_date(args['--from'])
    args['--to'] = parse_user_date(args['--to'], arrow.now())
    if args['--to'] and args['--from'] and args['--to'] < args['--from']:
        args['--to'] = args['--to'].shift(years=+1)
    return args


if __name__ == '__main__':
    main(parse_args())
