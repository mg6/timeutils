# timeutils

Time tracking on top of `.ics` calendars. Supports Toggl Track.


## Dependencies

- Python 3
- Pipenv
- curl
- jq
- make


## How does it work?

You need a set of calendars available through CalDAV.

Then, configure Make's `ics` target to save calendars as `.ics` files.

Finally, calendars are mapped into JSON posted to the tracking API.

Everything runs daily from CI at specified time, e.g. 21:00. :tada:


## How to configure it locally?

Fork this repository as a private project.

Start a new branch off `master` for your personal settings.

Go to Toggl, click an entry → Go to project → read project ID from URL.

    /projects/PROJECT_ID

Create & commit an empty `cal.PROJECT_ID.ics` settings file.

Create `private.mk` and configure `ics` target to download the calendar.
You can use the provided Python DAV client.

    .PHONY:
    ics:
        python davc.py --url 'https://caldav.fastmail.com/...' \
            --user '$(CALDAV_USER)' --password '$(CALDAV_PASS)' \
            --date $(TODAY) --name '...' > cal.PROJECT_ID.ics
        # repeat for each project

The real value comes from using *multiple calendars*, one for each Toggle project.

Create `.env` from `.env.example` and supply with your values.

Check everything works locally with:

    pipenv sync
    pipenv run make today


## How to run it from CI?

Configure variables from `.env.example` in CI environment.

Schedule a pipeline to run at desired time for personal branch.

GitLab CI setup is provided.


## How to mark project as billable?

Put the following into desired `cal.PROJECT_ID.in` settings file.

    {
      "toggl": {
        "merge": {
          "time_entry": {
            "billable": true
          }
        }
      }
    }


## Credits

Send me some kudos at @mg6!


## License

[Apache License 2.0](LICENSE)
