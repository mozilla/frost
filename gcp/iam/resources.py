from conftest import gcp_client


def service_accounts():
    results = []
    for project_id in gcp_client.project_list:
        results += gcp_client.list(
            "iam",
            "projects.serviceAccounts",
            results_key="accounts",
            call_kwargs={"name": "projects/" + project_id},
        )
    return results


def service_account_keys(service_account):
    return gcp_client.list(
        "iam",
        "projects.serviceAccounts.keys",
        results_key="keys",
        call_kwargs={"name": service_account["name"]},
    )


def all_service_account_keys():
    keys = []
    for sa in service_accounts():
        for key in service_account_keys(sa):
            keys.append(key)
    return keys


def project_iam_bindings():
    bindings = []
    policies = gcp_client.get_project_iam_policies()
    for policy in policies:
        for binding in policy.get("bindings", []):
            bindings.append(binding)
    return bindings
