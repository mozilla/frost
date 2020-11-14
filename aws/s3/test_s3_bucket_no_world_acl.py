import pytest

from aws.s3.helpers import get_s3_resource_id
from aws.s3.resources import s3_buckets, s3_buckets_acls


AWS_PREDEFINED_GROUPS = [
    # allow any AWS account to access the resource with a signed/authed request
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers",
    # allows anyone in the world access to the resource
    "http://acs.amazonaws.com/groups/global/AllUsers",
]


@pytest.mark.s3
@pytest.mark.parametrize(
    ["s3_bucket", "s3_bucket_acl"],
    zip(s3_buckets(), s3_buckets_acls()),
    ids=get_s3_resource_id,
)
def test_s3_bucket_no_world_acl(s3_bucket, s3_bucket_acl):
    """
    Check S3 bucket does not allow global predefined AWS groups access.

    http://docs.aws.amazon.com/AmazonS3/latest/dev/acl-overview.html
    """
    for grant in s3_bucket_acl["Grants"]:
        grantee = grant["Grantee"]
        if "URI" not in grantee:
            pytest.skip("S3 Bucket ACL does not use URI.")

        grantee_uri = grantee["URI"]
        assert not any(grantee_uri.startswith(group) for group in AWS_PREDEFINED_GROUPS)
