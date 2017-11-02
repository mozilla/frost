
import json

import pytest


@pytest.mark.s3
def test_s3_bucket_does_not_grant_all_principals_all_actions(
        s3_bucket_from_list_buckets,
        s3_policy):
    """
    Check policy does not allow all principals all actions on the S3 Bucket.

    Mitigations:

    * limit actions instead of using * or S3:* http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html
    * limit principals to specific IAMs http://docs.aws.amazon.com/AmazonS3/latest/dev/s3-bucket-user-policy-specifying-principal-intro.html
    * add conditions http://docs.aws.amazon.com/AmazonS3/latest/dev/amazon-s3-policy-keys.html
    """
    if s3_policy is None:
        pytest.skip()  # reason='Bucket has no policy.'

    policy = json.loads(s3_policy)

    star_actions = [
        '*',
        's3:*',
        's3:delete*',
        's3:putt*',
        's3:get*',
        's3:list*',
    ]

    for statement in policy['Statement']:
        if 'Condition' in statement:
            continue

        actions = [statement['Action']] if isinstance(statement['Action'], str) else statement['Action']
        actions = [action.lower() for action in actions]

        assert not (statement['Effect'] == 'Allow'
                    and any(action in star_actions for action in actions)
                    and 'Principal' == '*')
