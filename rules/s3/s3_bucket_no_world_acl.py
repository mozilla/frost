
import pytest


@pytest.mark.s3
def test_s3_bucket_no_world_acl(s3_bucket_from_list_buckets,
                                s3_grant_from_get_bucket_acl):
    """
    Check S3 bucket does not allow global predefined AWS groups access.

    http://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html
    """
    grantee = s3_grant_from_get_bucket_acl['Grantee']
    if 'URI' not in grantee:
        pytest.skip()  # reason='S3 Bucket ACL does not use URI.'

    grantee_uri = grantee['URI']
    aws_predefined_groups = [
        # allow any AWS account to access the resource with a signed/authed request
        'http://acs.amazonaws.com/groups/global/AuthenticatedUsers',

        # allows anyone in the world access to the resource
        'http://acs.amazonaws.com/groups/global/AllUsers',
    ]
    assert not any(grantee_uri.startswith(group) for group in aws_predefined_groups)
