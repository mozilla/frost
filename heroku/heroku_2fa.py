#!/usr/bin/env python3
'''
This script identifies org users who do not have 2FA enabled,
along with which apps their account can access. For example:

  $ ./heroku-2fa.py
  The following mozillacorporation users do not have 2FA enabled!

  ~ 1 members:
  some-user1@mozilla.com

  ~ 3 collaborators:
  some-user2@mozilla.com
  some-user3@mozilla.com

  3 apps are affected:

  app-one (some-user3@mozilla.com)
  app-two (some-user2@mozilla.com, some-user4@mozilla.com)
  app-three (some-user1@mozilla.com)

Exit Codes:
    0 - everyone has 2FA enabled
    1 - bad arguments, Heroku not queried
    2 - one or more users without 2FA enabled
    3 - Heroku query failure
'''

from collections import defaultdict
import argparse
import logging

import requests
from requests.utils import get_netrc_auth

# Mozilla defaults
ORG_NAME = 'mozillacorporation'
# https://devcenter.heroku.com/articles/platform-api-reference#organization-member
ORG_USERS_URL = \
    'https://api.heroku.com/organizations/{}/members'.format(ORG_NAME)
# https://devcenter.heroku.com/articles/platform-api-reference#clients
REQUEST_HEADERS = {
    'Accept': 'application/vnd.heroku+json; version=3',
    'User-Agent': 'build-stats',
}

# boilerplate
logger = logging.getLogger(__name__)
exit_code = 0


def update_exit_code(new_code):
    """ Update global exit_code, following rules.

        Current rule is only update if the new value signifies a
        "more severe" error (higher integer value)
    """
    global exit_code
    exit_code = max(exit_code, new_code)


# Script code
session = requests.session()


def have_creds():
    return get_netrc_auth(ORG_USERS_URL)


def find_users_missing_2fa():
    users_missing_2fa = {}
    try:
        org_users = fetch_api_json(ORG_USERS_URL)
        users_missing_2fa = defaultdict(set)
        for user in org_users:
            if not user['two_factor_authentication']:
                users_missing_2fa[user['role']].add(user['email'])
    except Exception:
        logger.critical("Failure communicating with Heroku", exc_info=True)
        update_exit_code(3)
    return users_missing_2fa


def apps_accessible_by_user(email, role):
    if role == 'admin':
        return ['ALL']
    users_apps_url = '{}/{}/apps'.format(ORG_USERS_URL, email)
    return [app['name'] for app in fetch_api_json(users_apps_url)]


def fetch_api_json(url):
    # The requests library will automatically use credentials found in netrc.
    response = session.get(url, headers=REQUEST_HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def find_affected_apps(users_missing_2fa):
    affected_apps = defaultdict(set)
    for role, users in users_missing_2fa.items():
        # print('\n~ {} {}s:'.format(len(users), role))
        for email in sorted(users):
            for app in apps_accessible_by_user(email, role):
                affected_apps[app].add(email)
            # print(email)
    return affected_apps


def generate_csv(users_missing_2fa, affected_apps):
    if affected_apps:
        print('"{}","{}"'.format("Application", "User without 2FA"))
        for app, emails in sorted(affected_apps.items()):
            for email in emails:
                print('"{}","{}"'.format(app, email))
    return


def output_results(users_missing_2fa, affected_apps):
    if not users_missing_2fa:
        print('All {} users have 2FA enabled :)'.format(ORG_NAME))
        return

    print('The following {} users do not have 2FA enabled!'.format(ORG_NAME))
    for role, users in users_missing_2fa.items():
        print('\n~ {} {}s:'.format(len(users), role))
        for email in sorted(users):
            print(email)

    if affected_apps:
        print('\n{} apps are affected:\n'.format(len(affected_apps)))
        for app, emails in sorted(affected_apps.items()):
            print('{} ({})'.format(app, ', '.join(sorted(emails))))


def main(args):
    if not get_netrc_auth(ORG_USERS_URL):
        print('Heroku API credentials not found in `~/.netrc` or `~/_netrc`.\n'
              'Log in using the Heroku CLI to generate them.')
        update_exit_code(1)
        return

    users_missing_2fa = find_users_missing_2fa()
    affected_apps = find_affected_apps(users_missing_2fa)

    if args.csv:
        generate_csv(users_missing_2fa, affected_apps)
    else:
        output_results(users_missing_2fa, affected_apps)

    update_exit_code(0 if not users_missing_2fa else 2)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse
                                     .RawTextHelpFormatter)
    parser.add_argument('--debug', help="include github3 output",
                        action='store_true')
    parser.add_argument('--csv', action='store_true',
                        help='output as csv file')
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('github3').setLevel(logging.DEBUG)
    return args


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    args = parse_args()
    main(args)
    raise SystemExit(exit_code)
