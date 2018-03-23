import os
import httplib2

from apiclient import discovery
from oauth2client.file import Storage

ADMIN_DIRECTORY_USER_READONLY = 'admin-directory-user-readonly'
CREDENTIALS = [
    (ADMIN_DIRECTORY_USER_READONLY, 'https://www.googleapis.com/auth/admin.directory.user.readonly'),
]


def get_credential_dir():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    return credential_dir


def get_credential_path(credential_name):
    return os.path.join(get_credential_dir(), credential_name+'.json')


def get_credentials(credential_name):
    store = Storage(get_credential_path(credential_name))
    return store.get()


class GsuiteClient:

    def __init__(self, domain):
        self.domain = domain

        self.directory_client = self.build_directory_client()

    def build_directory_client(self):
        credentials = get_credentials(ADMIN_DIRECTORY_USER_READONLY)
        http = credentials.authorize(httplib2.Http())
        return discovery.build('admin', 'directory_v1', http=http)

    def list_users(self):
        resp = self.directory_client.users().list(domain=self.domain).execute()
        return resp["users"]
