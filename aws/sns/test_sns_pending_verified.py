import pytest

from aws.sns.resources import sns_subscription_attributes

@pytest.mark.sns
@pytest.mark.parametrize(
    "pending_verification", 
    sns_subscription_attributes(), 
    ids=lambda subscription: subscription["PendingVerification"],
)
def test_sns_pending_verified(pending_verification):
    assert pending_verification == "false"
