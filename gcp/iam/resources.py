from conftest import gcp_client


def service_accounts():
    return gcp_client.list(
        "iam",
        "projects.serviceAccounts",
        results_key="accounts",
        call_kwargs={'name': 'projects/'+gcp_client.get_project_id()}
    )


def service_account_keys(service_account):
    return gcp_client.list(
        "iam",
        "projects.serviceAccounts.keys",
        results_key="keys",
        call_kwargs={'name': service_account['name']}
    )


def all_service_account_keys():
    for sa in service_accounts():
        for key in service_account_keys(sa):
            yield key
