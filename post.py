#!/usr/bin/env python3

#
# Jira API: https://docs.atlassian.com/software/jira/docs/api/REST/7.3.3/?_ga=2.174542626.1666439307.1519293627-1080493640.1514451808#api/2/issue-updateWorklog
# Jira auth: https://developer.atlassian.com/server/jira/platform/basic-authentication/
#
# Known issues:
# timeSpentSeconds should be >= 60,
# otherwise server will return 400 "You must indicate the time spent working"
#
# JIRA is adjusting start datetime of worklog depending on worklog's timezone
# and timezone selected in user's profile in JIRA.
# As rule of thumb keep timezone of user's profile in JIRA same
# as tz of device where you track work in Toggl and you'll be fine. Most likely.
#


import re
import ast
import json
import requests
import sys
import os
from datetime import datetime
import argparse

BASE_URL=os.getenv('_JIRA_URL')

WORKLOG_ENDPOINT="/rest/api/2/issue/{issueIdOrKey}/worklog"
SESSION_ENDPOINT="/rest/auth/1/session"

LOGIN=os.getenv('_JIRA_LOGIN')
PASSWORD=os.getenv('_JIRA_PASSWORD')

ISSUE_COMMON=os.getenv('_JIRA_ISSUE_COMMON')
ISSUE_CODE=os.getenv('_JIRA_ISSUE_CODE')

DRY_RUN = False


def _parse_issue_desctiption(description: str):
    """
        COM: comment
        COD: comment
        <ISSUE_ID>: comment
        <ISSUE_ID>
        comment -> COM: comment

        colon sign (:) is optional and will be ignored
    """

    if description.startswith('COM:'):
        # COMMON issue
        issue = ISSUE_COMMON
        comment = description[4:].lstrip()
    elif description.startswith('COD:'):
        # CODE issue
        issue = ISSUE_CODE
        comment = description[4:].lstrip()
    else:
        issue_match = re.search('^[A-Z]+-[0-9]+', description)
        if issue_match:
            # specific issue
            issue = issue_match[0]
            if description.startswith(f"{issue} "):
                # find comment after first whitespace
                comment = description.split(" ", 1)[1]
            elif description.startswith(f"{issue}:"):
                # ... or after first semicolon
                comment = description.split(":", 1)[1]
            else:
                # ... or use empty comment
                comment=''
        else:
            # otherwise whole description is a comment to COMMON issue
            issue = ISSUE_COMMON
            comment = description

    return (issue, comment)


def _process(worklog: str):
    # XXX validate data

    # that's how we parse "malformed" json (with single quotes)
    for entry in ast.literal_eval(worklog):
        _process_entry(entry)


def _process_entry(entry: dict):

    with requests.Session() as session:
        url = "{}{}".format(BASE_URL, SESSION_ENDPOINT)
        creds = {
                'username': LOGIN,
                'password': PASSWORD
        }
        r = session.post(url, json={'username': LOGIN, 'password': PASSWORD})
        if (r.status_code != 200):
            print("E: jira login failed")
            print("E: {r.status_code} | {r.content}")
            exit(1)

        data = {}

        issue, description = _parse_issue_desctiption(entry['description'])

        data['timeSpentSeconds'] = entry['duration']
        if data['timeSpentSeconds'] < 60:
            data['timeSpentSeconds'] = 60

        # based on REST Browser it needs: "2014-06-03T08:21:01.273+0000"
        data['started'] = datetime.fromisoformat(entry['start']).strftime("%Y-%m-%dT%H:%M:%S.000%z")

        data['comment'] = description

        url = "{}{}".format(
                BASE_URL,
                WORKLOG_ENDPOINT.format(issueIdOrKey = issue)
        )

        print(f'I: post {issue} {data}')

        if not DRY_RUN:
            r = session.post(url, json = data)
            if (r.status_code != 201):
                print("E: can't add worklog")
                print(f"E: {r.status_code} | {r.content}")
                exit(1)


def main():
    if not (LOGIN and PASSWORD):
        print("E: LOGIN or PASSWORD is empty")
        print("E: do `source ./env.sh`")
        exit(1)

    piped = not sys.stdin.isatty()  # read from input only when piped to
    if piped:
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--dry-run", action="store_true", default=False,
                help="when true specified data will not be actually posted")
        args = parser.parse_args()
        global DRY_RUN
        DRY_RUN = args.dry_run

        _process(sys.stdin.read())
    else:
        print("E: only data from stdin is supported")
        exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interupted. Bye")
        exit(127)
