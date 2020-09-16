import pytest

from aws.sns.resources import sns_subscription_attributes

@pytest.mark.sns
@pytest.mark.parametrize(
    "subscription_attrs",
    sns_subscription_attributes(),
    ids=lambda subscription: subscription["SubscriptionArn"],
)
def test_sns_pending_verified(subscription_attrs):
    assert subscription_attrs["PendingConfirmation"] == "false"
