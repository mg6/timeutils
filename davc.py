#!/usr/bin/env python3
"""
Usage:
    davc.py [--url URL] [--name CALNAME] [--user USER] [--password PASSWORD]

Options:
    --url URL
    -n, --name CALNAME
    -u, --user USER
    -p, --password PASSWORD
    -h, --help

"""
import caldav
import docopt
import sys


def main(args):
    url = args['--url']

    client = caldav.DAVClient(url, username=args['--user'], password=args['--password'])
    principal = client.principal()
    calendars = principal.calendars()

    if not args['--name']:
        for cal in calendars:
            print(cal.name, dir(cal))
        sys.exit(0)

    selected_cal = None
    for cal in calendars:
        if cal.name == args['--name']:
            selected_cal = cal

    if not selected_cal:
        raise ValueError('Cannot find calendar:', args['--name'])

    for event in selected_cal.events():
        print(event.data)


if __name__ == '__main__':
    main(docopt.docopt(__doc__))


# if len(calendars) > 0:
#     calendar = calendars[0]
#     print "Using calendar", calendar
#
#     print "Renaming"
#     calendar.set_properties([dav.DisplayName("Test calendar"),])
#     print calendar.get_properties([dav.DisplayName(),])
#
#     event = calendar.add_event(vcal)
#     print "Event", event, "created"
#
#     print "Looking for events in 2010-05"
#     results = calendar.date_search(
#         datetime(2010, 5, 1), datetime(2010, 6, 1))
#
#     for event in results:
#         print "Found", event
