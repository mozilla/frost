from conftest import gsuite_client


def list_users():
    return gsuite_client.list_users()
