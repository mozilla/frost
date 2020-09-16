.. raw:: html

   <!-- This Source Code Form is subject to the terms of the Mozilla Public
      - License, v. 2.0. If a copy of the MPL was not distributed with this
      - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

.. _architecture:

============
Architecture
============

PyTest supports several different ways of organizing tests. For frost, we use a
mixture of class based and declarative tests.

In general the class holds session information, as PyTest treats class
``__init__`` functions as session scoped fixtures. The class methods provide raw
access to the service, and cache the result.

Traditional PyTest fixtures (in ``conftest.py``) or "cache access functions" (in
``resources.py``) are used to supply the data to tests. The tests are
conventionally written in ``test_<foo>.py`` files, with a single function of the
same name as the file. *(With "Black_", we stopped the tabs-vs-spaces debate,
so redirected that energy to one-or-many-tests-per-file debate.)*

A recommended way to organize your code is to create a directory per type of
resource you test. E.g. ``aws/{elb,ec2,iam}/`` or
``github/{orgs,branches,users}``. Whether it makes sense to have ``conftest.py``
files at each level is up to the developer. There should only be one session
client per service though.

Caching
=======

.. note::
   The caching operations is under consideration for deprecation. If you
   intend to rely on caching, you should check with the active developers first.

To implement caching:

   #. Your class ``__init__`` method must accept and store a cache object.

   #. Your data retrieval functions should be written to try the cache first
         before fetching data from the service under test.

   #. A cache_key global function is recommended as a means to ensure consistent
         and non conflicting keys to store data in the cache. (The existing
         functions tend to marshal the full data location path and arguments
         into a string.)

Expected Output flow
====================

Every test that fails needs to output sufficient information to allow downstream
processes to take action on the failure (open an issue, or bug, or email the
team or ...). All that information must be contained in the test id. Use the
``ids`` argument to the ``pytest.mark.parametrize`` decorator to generate rich
ids as needed. (See `PyTest docs`_.)

A PyTest plugin in frost adds the option ``--json`` which outputs test failures
as JSON objects which include the test's id, in addition to other context about
the failed test. Using the ``--json`` option is the recommended way to provide
actionalble data to processes further down the pipeline.

The output flow will be installation specific.

.. _PyTest docs: https://docs.pytest.org/en/stable/example/parametrize.html#paramexamples>`)

.. _Black: https://black.readthedocs.io/
