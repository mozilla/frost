def pytest_configure(config):
    # register custom marks for heroku services
    for svc_name in [
        "heroku",
    ]:
        config.addinivalue_line(
            "markers", "{}: mark tests against {}".format(svc_name, svc_name)
        )
