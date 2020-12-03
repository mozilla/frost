import pytest

from aws.s3.helpers import get_s3_resource_id
from aws.s3.resources import s3_buckets, s3_buckets_versioning


@pytest.mark.s3
@pytest.mark.parametrize(
    ["s3_bucket", "s3_bucket_versioning"],
    zip(s3_buckets(), s3_buckets_versioning()),
    ids=get_s3_resource_id,
)
def test_s3_bucket_versioning_mfa_delete_enabled(s3_bucket, s3_bucket_versioning):
    """
    Enable MFA delete for versioned S3 buckets to prevent their accidental deletion.
    """
    if s3_bucket_versioning.get("Status", None) != "Enabled":
        return pytest.skip()

    assert s3_bucket_versioning.get("MFADelete", None) != "Disabled"
