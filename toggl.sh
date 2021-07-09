#!/bin/bash

set -euo pipefail

while read -r line; do
    curl -sSfL -u "${TOGGL_API_TOKEN}:api_token" \
        -H "Content-Type: application/json" \
        -d "$line" \
        -X POST https://api.track.toggl.com/api/v8/time_entries
done
