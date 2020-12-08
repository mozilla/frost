======================
Use Cases & Philosophy
======================

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

Frost is intended to simplify the process of auditing existing system configurations, when the configuration data is accessible via an API. While any pytest compliant test *can* be driven via Frost, Frost is optimized for processing auditing controls and providing a report of the current state.


Since, in general, the number of configuration resources to check is not statically known when the test is written or executed, some lesser used features of pytest are needed. In particular, the test collection phase often requires API calls to the service to discover the complete list of resources to be checked. While uncommon in internet pytest examples, dynamic test discovery is fully supported by pytest.

In practice, many of the same calls needed to determine the list of resources may need to be repeated to collect the additional information needed by one or more tests. This leads to a tension between collecting all potentially needed data in the first (discovery) pass, or making many duplicate calls to the service as each test collects the additional information it requires. This leads to 2 common data collection paths:

- Path 1: Frost service API clients collect all need resources during the test collection phase, and caches the responses for use by other tests within the same run of Frost and (optionally) by subsequent runs of Frost. All test output is delivered in a JSON file for subsequent processing as appropriate.

- Path 2: Frost service builds the list of resources to be audited during the test collection phase. The current system state is collected via API calls during the test.

.. mermaid::

    sequenceDiagram

        participant p1 as Path 1
        participant s as Service
        participant c as Pytest Managed Data
        participant p2 as Path 2

    note over p1, p2: Test Collection Phase
    note over p1: AWS, gSuite, ...
        p1->>+s: enumerate resources and data
        s->>-p1: all data
        p1 ->> c: resources & data

    note over c: Pytest Data Caching
    note over p2: GitHub (new)
        p2->>+s: enumerate resources
        s->>-p2: all resources
        p2->>c: resources

    note over p1, p2: Test Execution Phase

    c-->>p1: data for test

    c-->>p2: resources for test
    p2->>+s: request data for resource
    s->>-p2: data for test

    note over c: Results caching

        p1->>c: test results
        p2->>c: test results

    note over p1, p2: Paths rejoin here for test output processing

In both cases, all test output is delivered in a JSON file for subsequent processing as appropriate.

Frost Supported Use Cases
=========================

While Frost could be considered a wrapper around pytest, it is optimized to support the following use cases:

- as part of an automated system, Frost will execute robustly, and without user intervention, so folks can trust my reporting.
- as an SRE, I want to be able to easily create new suites of tests, so I can pay special attention to something for a while. (Maybe new service, service migration, etc)
- as an SRE, I want to be able to easily add additional tests to a service, so new cloud features are monitored as we start to use them. (Or to apply lessons learned from an incident)
- as a Frost Developer, I want to easily be able to develop support for a new service, so I don't have to re-implement the framework.
- as a SecOps incident responder, I want to quickly obtain easy-to-understand status of a specific account or subsystems, so I can eliminate, or focus in on, aspects of the system that appear abnormal.

Unsupported Use Cases
---------------------

.. admonition:: Add away

    Fair game to add out of scope use cases here, including moving down from above.

The following use cases are explicitly out of scope for Frost.
