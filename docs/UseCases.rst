=====================
Use Cases & Philosopy
=====================

.. warning:: Incorrect Information below

    Until this document is reviewed and corrected, it is known to contain errors, especially w.r.t. philosopy.

Philosophy
=========

Frost is intended to build upon the pytest framework to provide extra features to support "infrastructure auditing".

The added features include:

    - providing a standard way to inject meta data in the JSON test result file.
    - providing a CLI wrapper (the ``frost`` program) to simplify execution of tests within the full supported frost environment.

Note that the added features are all extensions to the normal pytest operations. Therefore, all tests can be executed directly from pytest. This can be highly useful for adhoc queries, and the development of new tests.

Target Domain
-------------

Frost is intended to simplify the process of auditing existing system configurations, when the configuration data is accessible via an API. Frost assumes that the test results (in JSON format) will be acted upon by a subsequent non-Frost process.

Since, in general, the number of configuration items to check is not statically known when the test is writen or executed, some lesser used features of pytest are needed. In particular, the test collection phase often requires API calls to the service to discover the complete list of resources to be checked. While uncommon in internet examples, dynamic test discovery is fully supported by pytest.

In practice, many of the same calls needed to determine the list of items may need to be repeated to collect the additional information needed by one or more tests. This leads to a tension between collecting all potentially needed data in the first (discovery) pass, or making many duplicate calls to the service as each test collects the additional information it requires.

Use Cases
=========

- as an automation system, I want to execute robustly, so folks can trust my reporting.
- as an SRE, I want to be able to easily create new suites of tests, so I can pay special attention to something for a while. (Maybe new service, service migration, etc)
- as an SRE, I want to be able to easily add additional tests to a service, so new cloud features are monitored as we start to use them. (Or to apply lessons learned from an incident)
- as a Frost Developer, I want to easily be able to develop support for a new service, so I don't have to re-implement the framework.
