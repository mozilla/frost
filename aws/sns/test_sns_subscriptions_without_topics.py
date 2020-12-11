import pytest
from helpers import get_param_id

from aws.sns.resources import sns_subscriptions
from aws.sns.resources import sns_topic_arns


@pytest.fixture
def topics():
    return sns_topic_arns()


@pytest.mark.sns
@pytest.mark.rationale(
    """
SNS subscriptions subscribed to non-existent topics cannot
receive messages.  They are good candidates for removal.
"""
)
@pytest.mark.parametrize(
    "subscription",
    sns_subscriptions(),
    ids=lambda subscription: get_param_id(subscription, "SubscriptionArn"),
)
def test_sns_subscriptions_without_parent_topics(subscription, topics):
    assert topics[subscription["TopicArn"]] == 1
