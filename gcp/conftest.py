def pytest_configure(config):
    # register custom marks for gcp services
    for svc_name in [
        "gcp",
        "gcp_compute",
        "gcp_iam",
        "gcp_sql",
    ]:
        config.addinivalue_line(
            "markers", "{}: mark tests against {}".format(svc_name, svc_name)
        )
