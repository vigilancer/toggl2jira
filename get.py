#!/usr/bin/env python3

#
# toggl report api
# https://github.com/toggl/toggl_api_docs/blob/master/reports.md
#

import os
import requests
from datetime import date, timedelta


URL="https://toggl.com/reports/api/v2/details"
TOKEN=os.getenv("TOGGL_SCRIPT_TOKEN")
USER_ANENT="@ae toggl2jira script"
WORKSPACE_ID=os.getenv("TOGGL_SCRIPT_WORKSPACE_ID")


def main():
    since = date.today().strftime("%Y-%m-%d")
    until = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    payload={
        'user_agent': USER_ANENT,
        'workspace_id': WORKSPACE_ID,
        'since': since,
        'until': until
    }

    r = requests.get(URL, auth=(TOKEN, "api_token"), params=payload)

    if (r.status_code != 200):
        print(r.content)
        exit(r.status_code)

    print(r.json()['data'])


if __name__ == "__main__":
    main()
