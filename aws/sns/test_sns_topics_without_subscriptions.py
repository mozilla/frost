import pytest
from helpers import get_param_id

from aws.sns.resources import sns_subscriptions_by_topic

@pytest.mark.sns
@pytest.mark.parametrize(
    "topic",
    sns_subscriptions_by_topic(),
    ids=lambda topic: get_param_id(topic, "TopicArn"),
)
def test_sns_topics_without_subscriptions(topic):
    assert len(topic["Subscriptions"]) > 0
