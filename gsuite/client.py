import os
import httplib2

from apiclient import discovery
from oauth2client.file import Storage

CREDS_NAME = "frost-gsuite-readonly"
SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
]


def get_credential_dir():
    home_dir = os.path.expanduser("~")
    credential_dir = os.path.join(home_dir, ".credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    return credential_dir


def get_credential_path(credential_name):
    return os.path.join(get_credential_dir(), credential_name + ".json")


def get_credentials(credential_name):
    store = Storage(get_credential_path(credential_name))
    return store.get()


class GsuiteClient:
    def __init__(self, domain, offline):
        self.domain = domain
        self.offline = offline

        if not self.offline:
            self.directory_client = self.build_directory_client()

    def build_directory_client(self):
        # TODO: Support passing creds name as config option
        credentials = get_credentials(CREDS_NAME)
        http = credentials.authorize(httplib2.Http())
        return discovery.build("admin", "directory_v1", http=http)

    def list_users(self):
        """
        https://developers.google.com/admin-sdk/directory/v1/reference/users#resource
        """
        if self.offline:
            return []

        req = self.directory_client.users().list(domain=self.domain)
        users = []
        while req is not None:
            resp = req.execute()
            users += resp.get("users", [])
            req = self.directory_client.users().list_next(req, resp)
        return users

    def list_groups(self):
        """
        https://developers.google.com/admin-sdk/directory/v1/reference/groups
        """
        if self.offline:
            return []

        req = self.directory_client.groups().list(domain=self.domain)
        groups = []
        while req is not None:
            resp = req.execute()
            groups += resp.get("groups", [])
            req = self.directory_client.groups().list_next(req, resp)
        return groups

    def list_members_of_group(self, group):
        if self.offline:
            return []

        req = self.directory_client.members().list(groupKey=group)
        members = []
        while req is not None:
            resp = req.execute()
            members += resp.get("members", [])
            req = self.directory_client.members().list_next(req, resp)
        return members
