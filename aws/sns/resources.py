from conftest import botocore_client


def sns_subscriptions():
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#subscription"
    return (
        botocore_client.get("sns", "list_subscriptions", [], {})
        .extract_key("Subscriptions")
        .flatten()
        .values()
    )


def sns_topics():
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#topic"
    return (
        botocore_client.get("sns", "list_topics", [], {})
        .extract_key("Topics")
        .flatten()
        .values()
    )


def sns_topic_arns():
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#topic"
    return {x["TopicArn"] for x in sns_topics()}


def sns_subscriptions_by_topic():
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#topic"
    return [
        {
            **{
                "Subscriptions": botocore_client.get(
                    service_name="sns",
                    method_name="list_subscriptions_by_topic",
                    call_args=[],
                    call_kwargs={"TopicArn": topic["TopicArn"]},
                    profiles=[topic["__pytest_meta"]["profile"]],
                    regions=[topic["__pytest_meta"]["region"]],
                )
                .extract_key("Subscriptions")
                .values()[0]
            },
            **topic,
        }
        for topic in sns_topics()
    ]
