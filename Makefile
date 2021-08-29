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
	- rm *.toggl

ics:

%.toggl: cal.%.ics | cal.%.in
	$(eval TOGGL_PROJECT := $(patsubst %.toggl,%,$@))
	python run.py -f $< --from $(TODAY) --format '{toggl}' > $@
	./toggl.sh $| < $@

today:
	$(MAKE) -s clean
	$(MAKE) -s ics
	$(MAKE) -s $(CALENDAR_IN)
