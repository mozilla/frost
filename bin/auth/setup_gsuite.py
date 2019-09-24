import os

from gsuite.client import (
    CREDS_NAME,
    SCOPES,
    get_credentials,
    get_credential_dir,
    get_credential_path,
)

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

APPLICATION_NAME = "frost"


def get_client_secret_file():
    return os.path.join(get_credential_dir(), "client_secret.json")


def get_or_create_credentials(credential_name, scopes):
    credentials = get_credentials(credential_name)
    if not credentials or credentials.invalid:
        store = Storage(get_credential_path(credential_name))
        flow = client.flow_from_clientsecrets(get_client_secret_file(), scopes)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, None)
        print("Storing credentials to " + get_credential_path(credential_name))
    return credentials


def main():
    get_or_create_credentials(CREDS_NAME, SCOPES)


if __name__ == "__main__":
    main()
