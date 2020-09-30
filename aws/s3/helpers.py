from helpers import get_param_id


def get_s3_bucket_name(bucket):
    return get_param_id(bucket, "Name")


def get_s3_bucket_name_only(bucket):
    if isinstance(bucket, dict) and "Name" in bucket:
        return get_s3_bucket_name(bucket)
    return None
