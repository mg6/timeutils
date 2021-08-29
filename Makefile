TODAY := $(shell date +"%Y%m%d")

CALDAV_USER :=
CALDAV_PASS :=
TOGGL_API_TOKEN :=

-include .env
export

.PHONY: all
all: today


CALENDAR_IN = $(patsubst cal.%.in,%.toggl,$(wildcard cal.*.in))

.PHONY: clean
clean:
	- rm *.ics
	- rm *.toggl

.PHONY: ics
ics:

%.toggl: cal.%.ics | cal.%.in
	$(eval TOGGL_PROJECT := $(patsubst %.toggl,%,$@))
	python run.py -f $< --from $(TODAY) --format '{toggl}' > $@
	./toggl.sh $| < $@

.PHONY: today
today:
	$(MAKE) -s clean
	$(MAKE) -s ics
	$(MAKE) -s $(CALENDAR_IN)

-include private.mk
