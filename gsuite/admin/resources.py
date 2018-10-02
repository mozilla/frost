from conftest import gsuite_client


def list_users():
    return gsuite_client.list_users()


def list_groups():
    return gsuite_client.list_groups()


def list_members_of_group(group):
    return gsuite_client.list_members_of_group(group)


def list_groups_and_members():
    return [
        {**group, "members": list_members_of_group(group["email"])}
        for group in list_groups()
    ]
