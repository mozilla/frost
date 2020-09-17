def pytest_configure(config):
    # register custom marks for aws services
    for svc_name in [
        "aws",
        "cloudtrail",
        "ec2",
        "elasticsearch",
        "elb",
        "iam",
        "rds",
        "redshift",
        "s3",
        "sns",
    ]:
        config.addinivalue_line(
            "markers", "{}: mark tests against {}".format(svc_name, svc_name)
        )
