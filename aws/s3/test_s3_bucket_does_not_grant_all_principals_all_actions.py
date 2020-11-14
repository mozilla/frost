import json

import pytest

from aws.s3.helpers import get_s3_resource_id
from aws.s3.resources import s3_buckets, s3_buckets_policy


STAR_ACTIONS = ["*", "s3:*", "s3:delete*", "s3:put*", "s3:get*", "s3:list*"]


@pytest.mark.s3
@pytest.mark.parametrize(
    ["s3_bucket", "s3_bucket_policy"],
    zip(s3_buckets(), s3_buckets_policy()),
    ids=get_s3_resource_id,
)
def test_s3_bucket_does_not_grant_all_principals_all_actions(
    s3_bucket, s3_bucket_policy
):
    """
    Check policy does not allow all principals all actions on the S3 Bucket.

    Mitigations:

    * limit actions instead of using * or S3:* http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html
    * limit principals to specific IAMs
      http://docs.aws.amazon.com/AmazonS3/latest/dev/s3-bucket-user-policy-specifying-principal-intro.html
    * add conditions http://docs.aws.amazon.com/AmazonS3/latest/dev/amazon-s3-policy-keys.html
    """
    if not s3_bucket_policy:
        pytest.skip("Bucket has no policy, which means it defaults to private.")
        # https://docs.aws.amazon.com/config/latest/developerguide/s3-bucket-policy.html

    policy = json.loads(s3_bucket_policy)

    for statement in policy["Statement"]:
        if "Condition" in statement:
            continue

        actions = (
            [statement["Action"]]
            if isinstance(statement["Action"], str)
            else statement["Action"]
        )
        actions = [action.lower() for action in actions]

        assert not (
            statement["Effect"] == "Allow"
            and any(action in STAR_ACTIONS for action in actions)
            and "Principal" == "*"
        )
