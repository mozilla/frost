import os
import httplib2

from apiclient import discovery
import google.auth

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
]


class GsuiteClient:
    def __init__(self, domain, offline):
        self.domain = domain
        self.offline = offline

        if not self.offline:
            self.directory_client = self.build_directory_client()

    def build_directory_client(self):
        # TODO: Support service accounts:
        #   https://googleapis.github.io/google-api-python-client/docs/oauth-server.html#examples
        credentials, _ = google.auth.default(scopes=SCOPES)
        return discovery.build("admin", "directory_v1", credentials=credentials)

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
