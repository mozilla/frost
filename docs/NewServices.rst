.. raw:: html

   <!-- This Source Code Form is subject to the terms of the Mozilla Public
      - License, v. 2.0. If a copy of the MPL was not distributed with this
      - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

============================
Adding a New Service
============================
Here are the steps to add a new service to the Frost framework.

Claim a name
============

Like 'heroku' ;)

Create a new directory by that name
-----------------------------------

Clone the repo::

   git clone git@github.com:mozilla/frost.git
   git checkout -b new_service

Setup for new service::

   mkdir heroku
   cd heroku

Create Default Files
--------------------

The new service should be a Python Package::

   touch __init__.py client.py resources.py conftest.py

Commit shell::

   git add .
   git push -m 'Adding new service Heroku'

Add Service Specific Content
============================

``client.py``: responsible for obtaining data from the service, and
placing it into the PyTest cache. The client module typically exposes the data via a
"{service}_client" object. The PyTest framework will instantiate the client
before any tests are run with all the configuration & credential
information provided by the configuration files and command line
options. (See :ref:`architecture` for status of cache functionality.) (See
:ref:`doctest offline support <offline>` for other requirements.)

``resources.py``: holds mapping functions which convert the data from
the cache into the format expected by the tests. This should be the only
file which imports the instantiation of the client. (Future best
practices may pre-populate the cache outside of the PyTest execution.)

``conftest.py`` (optional) As much as possible, put service specific
options, etc. in this local file. (Some things may not work c.f. BUG.)
In conventional ``PyTest`` usage, ``conftest.py`` would contain fixture
routines which did the combined steps of fetching the data and providing to the
tests.  If caching is not important, the traditional approach may be used.

Tests for these support files should be included as doc tests whenever
practical. If possible, the default of executing the module should be to run
the doc tests.

Add Service Specific Tests
--------------------------

``test_*.py``: normal PyTest tests, which each import the resources they
need to test.
