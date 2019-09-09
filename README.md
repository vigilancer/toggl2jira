
#### description

util to transfer worklogs from Toggl to JIRA.

it consists of two scripts: `get.py` to get data from Toggl and `post.py` to post data to JIRA. (see usage)

it has no external dependencies except `requests`.


#### peculiarities

it is expected from worklogs in Toggl to have specific JIRA issue id as prefix. (e.g. `MOB-6969`).

on current job we have two special issues in JIRA (per person). one for communications, PR reviews and such (`_JIRA_ISSUE_COMMON` in `env.sh`) and another for working with code outside of main tasks (`_JIRA_ISSUE_CODE`). for `post.py` to account for them use `COD:` and `COM:` prefixes when logging time to Toggl.

worklog without recognized prefix (that is `[A-Z]+-[0-9]+` or `COD:` or `COM:`) will go into `_JIRA_ISSUE_COMMON` task.

#### setup

first,
```sh
cp ./env.sh.example ./env.sh
```

second,
edit `./env.sh`

and third,
```sh
source ./env.sh
```

#### basic usage

```sh
./get.py | ./post.py
```

or

```sh
./get.py '2019-08-30' | ./post.py
```

#### dry-run

just add `-n` to skip actual `post`ing to JIRA (useful to see logs before actually updating JIRA).

```sh
./get.py '2019-08-30' | ./post.py -n
```
