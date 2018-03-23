import os

from oauth2client.file import Storage


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
