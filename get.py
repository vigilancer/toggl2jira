#!/usr/bin/env python3

#
# toggl report api
# https://github.com/toggl/toggl_api_docs/blob/master/reports.md
#

import argparse
import os
import requests
from datetime import date, timedelta


URL="https://toggl.com/reports/api/v2/details"
TOKEN=os.getenv("TOGGL_SCRIPT_TOKEN")
USER_ANENT="@ae toggl2jira script"
WORKSPACE_ID=os.getenv("TOGGL_SCRIPT_WORKSPACE_ID")


def parse_input_date():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            'date',
            metavar='DATE',
            type=str,
            nargs='?',
            help='date for which to download report from toggl'
    )
    args = parser.parse_args()
    if not args.date:
        return None

    try:
        return date.fromisoformat(args.date)
    except ValueError:
        print(f"E: invalid date: {args.date}")
        exit(1)


def main():
    if not (USER_ANENT and WORKSPACE_ID):
        print("E: USER_AGENT or WORKSPACE_ID is empty")
        print("E: do `source ./env.sh`")
        exit(1)

    since = parse_input_date()
    if not since:
        since = date.today()
    until = since + timedelta(days=1)

    payload = {
        'user_agent': USER_ANENT,
        'workspace_id': WORKSPACE_ID,
        'since': since.strftime("%Y-%m-%d"),
        'until': until.strftime("%Y-%m-%d")
    }

    r = requests.get(URL, auth=(TOKEN, "api_token"), params=payload)

    if (r.status_code != 200):
        print(f"E: {r.content}")
        exit(r.status_code)

    print(r.json()['data'])


if __name__ == "__main__":
    main()
