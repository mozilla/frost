import os

from gsuite.client import (
    get_credentials,
    get_credential_dir,
    get_credential_path
)

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


APPLICATION_NAME = 'pytest-services'


def get_client_secret_file():
    return os.path.join(get_credential_dir(), 'client_secret.json')


def get_or_create_credentials(credential_name, scopes):
    credentials = get_credentials(credential_name)
    if not credentials or credentials.invalid:
        store = Storage(get_credential_path(credential_name))
        flow = client.flow_from_clientsecrets(get_client_secret_file(), scopes)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + get_credential_path(credential_name))
    return credentials


def get_or_create_credentials_directory_user_readonly():
    return get_or_create_credentials(
        'admin-directory-user-readonly',
        'https://www.googleapis.com/auth/admin.directory.user.readonly'
    )


def main():
    get_or_create_credentials_directory_user_readonly()


if __name__ == '__main__':
    main()
