Adding a New Service
====================

When adding a new service (i.e. directory in this repo), it is helpful to
understand both:

  - How PyTest is used in this application.
  - What our naming conventions are.

Recap of PyTest Services
------------------------

The expected workflow for a pytest service is:

-   ``pytest`` runs, and produces a results*.json file:
      - fetch any needed data
      - test that data
      - for failures, see if the failure is expected
-   ``generate_service_report`` runs, and transforms the json file into a compact
    listing of errors
-   ``create_bugs`` [#create_bugs]_ runs, and takes action as appropriate (e.g.
    open a bug).

The expected use cases are:

  - As an system operator, I can execute pytest interactively from the command
    line to check parts of the system-under-test.

  - As a test developer, I can specify how the tests should be run inside a
    docker container, include taking automatic actions.

  - As a test operator, I can invoke docker instances from automation to perform
    the tests.

  - As an interested party, I can easily modify parts of this code for use in my
    environment.

Overview
--------

To add a new service, you'll be writing or modifiying at least the following
files:

+----------------------------------------------------------+--------+------------------------------------------------------------+
|file                                                      | action | description                                                |
+==========================================================+========+============================================================+
| pytest-services/{NEW_SERVICE}                            | create | directory to hold the service specific files               |
+----------------------------------------------------------+--------+------------------------------------------------------------+
| pytest-services/{NEW_SERVICE}/test_*.py                  | write  | your test cases. One per file is convention. Ideally       |
|                                                          |        | very simple tests, asserting a value about a function      |
|                                                          |        | in ``helpers.py``                                          |
+----------------------------------------------------------+--------+------------------------------------------------------------+
| pytest-services/{NEW_SERVICE}/resources.py               | write  | Code to fetch & format the data you need to test           |
+----------------------------------------------------------+--------+------------------------------------------------------------+
| pytest-services/{NEW_SERVICE}/helpers.py                 | write  | Code to simplify writing tests. Typically, all the         |
|                                                          |        | "real" logic is here, and tested via doctests.             |
+----------------------------------------------------------+--------+------------------------------------------------------------+
| pytest-services/{NEW_SERVICE}/client.py                  | write  | Code to handle connection to the service, and pass         |
|                                                          |        | pytest arguements to service.                              |
+----------------------------------------------------------+--------+------------------------------------------------------------+
| pytest-services/conftest.py                              | modify | add any new option flags to the pytest invocation          |
+----------------------------------------------------------+--------+------------------------------------------------------------+

In the Mozilla production environment, we invoke the tests inside docker
containers. To properly configure the docker environment for your service, you'd
need to also create or modify the following files, which all execute inside the
base docker container except as noted.

+----------------------------------------------------------+--------+------------------------------------------------------------+
|file                                                      | action | description                                                |
+==========================================================+========+============================================================+
|foxsec/tools/pytest-services/{NEW_SERVICE}                | create | directory to hold the service specific run files           |
+----------------------------------------------------------+--------+------------------------------------------------------------+
|foxsec/tools/pytest-services/{NEW_SERVICE}/run.sh         | write  | code to invoke pytest for your service                     |
+----------------------------------------------------------+--------+------------------------------------------------------------+
|foxsec/tools/pytest-services/{NEW_SERVICE}/config.yaml    | write  | expected failure information                               |
+----------------------------------------------------------+--------+------------------------------------------------------------+
|foxsec/tools/pytest-services/{NEW_SERVICE}/pre-docker.sh  | write  | code to pass any needed data into the container (optional) |
+----------------------------------------------------------+--------+------------------------------------------------------------+


PyTest Differences
------------------

While most of the PyTest usage is standard, there is one place where we have
significantly changed from the normal conventions. The way PyTest Services uses
"xfail" is quite different:

  - you never mark a test function with the ``pytest.mark.xfail`` attribute.
  - you will never get ``XPASS`` as a test result.

A failed test is then checked against the list of expected exceptions (in
``config.yaml``). If the failure was expected, the ``xfail`` attribute is
injected into pytest's state, replacing the ``FAILURE`` value (yes, this is a
bit of a hack). ``xfail`` provides the information needed for the post
processing programs to identify expected failures.


-----------------

Footnotes

.. [#create_bugs] This may be renamed into something like ``take_action``, as any
    action can be taken
