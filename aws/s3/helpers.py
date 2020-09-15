from helpers import get_param_id


def get_s3_bucket_name(bucket):
    return get_param_id(bucket, "Name")
