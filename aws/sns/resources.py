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
    topicArns = {}
    for x, y in enumerate(sns_topics()):
        topicArns[y["TopicArn"]] = 1
    return topicArns


def sns_get_subscription_attrs(subscription):
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#subscription"
    # This function catches the error thrown by the AWS API when attempting to query the attributes of
    # a subscription that has no parent topic.
    try:
        attrs = (
            botocore_client.get(
                service_name="sns",
                method_name="get_subscription_attributes",
                call_args=[],
                call_kwargs={"SubscriptionArn": subscription["SubscriptionArn"]},
                profiles=[subscription["__pytest_meta"]["profile"]],
                regions=[subscription["__pytest_meta"]["region"]],
            )
            .extract_key("Attributes")
            .values()[0]
        )
        return attrs
    except:
        pass


def sns_subscription_attributes():
    "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#subscription"
    return [
        sns_get_subscription_attrs(subscription) for subscription in sns_subscriptions()
    ]


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
