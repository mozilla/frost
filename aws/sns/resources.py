from conftest import botocore_client


def sns_subscriptions():
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#subscription"
    return (
        botocore_client.get("sns", "list_subscriptions", [], {})
        .extract_key("Subscriptions")
        .flatten()
        .values()
    )


def sns_subscription_attributes():
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#subscription"
    return [
        botocore_client.get_details(
            resource=subscription,
            service_name="sns",
            method_name="get_subscription_attributes",
            call_args=[],
            call_kwargs={"SubscriptionArn": subscription["SubscriptionArn"]},
        )["Attributes"]
        for subscription in sns_subscriptions()
    ]
