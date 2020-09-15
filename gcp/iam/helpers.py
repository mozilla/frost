import datetime


def is_service_account_key_old(service_account_key):
    """
    Tests whether a service account key is older than 90 days.
    """
    creation_date = datetime.datetime.strptime(
        service_account_key["validAfterTime"][:10], "%Y-%m-%d"
    )
    # TODO: Make configurable
    return creation_date > datetime.datetime.now(
        datetime.timezone.utc
    ) - datetime.timedelta(days=90)
