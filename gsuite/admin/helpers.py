from dateutil.parser import parse


def user_is_inactive(user, no_activity_since):
    """
    Compares the lastLoginTime with no_activity_since.
    """
    return parse(user["lastLoginTime"]) > no_activity_since


def owners_of_a_group(members):
    """
    Returns a list of owners from a list of group members
    """
    return [member for member in members if is_owner_of_group(member)]


def is_owner_of_group(member):
    """
    Check whether a member of a group is an owner with a status of 'ACTIVE'.
    """
    return (
        member["type"] == "USER"
        and member["role"] == "OWNER"
        and member["status"] == "ACTIVE"
    )
