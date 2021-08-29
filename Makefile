TODAY := $(shell date +"%Y%m%d")

CALDAV_USER :=
CALDAV_PASS :=
TOGGL_API_TOKEN :=

-include .env
export

all: today


CALENDAR_IN = $(patsubst cal.%.in,%.toggl,$(wildcard cal.*.in))

clean:
	- rm *.ics

ics:

%.toggl: cal.%.ics
	TOGGL_PROJECT=$(patsubst %.toggl,%,$@) python run.py -f $< --from $(TODAY) --format '{toggl}' | ./toggl.sh

today:
	$(MAKE) -s clean ics
	$(MAKE) -s $(CALENDAR_IN)
