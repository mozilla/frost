def pytest_configure(config):
    # register custom marks for gsuite services
    for svc_name in [
        "gsuite_admin",
    ]:
        config.addinivalue_line(
            "markers", "{}: mark tests against {}".format(svc_name, svc_name)
        )
