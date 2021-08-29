#!/bin/bash

set -euo pipefail

SETTINGS_FILE="$1"

# read event merge params
MERGE_JSON="$(jq -c .toggl.merge < "$SETTINGS_FILE")"
# default to empty merge params otherwise
MERGE_JSON="${MERGE_JSON:-$(printf "{}")}"

while read -r line; do
    # merge event with provided params
    event="$(jq -nc '$event * $settings' --argjson event "$line" --argjson settings "$MERGE_JSON")"

    # upload
    curl -sSfL -u "${TOGGL_API_TOKEN}:api_token" \
        -H "Content-Type: application/json" \
        -d "$event" \
        -X POST https://api.track.toggl.com/api/v8/time_entries
done
