============================
Adding a New Service
============================
Here are the steps to add a new service to the pytest framework.

Claim a name
============

Like 'heroku' ;)

Create a new directory by that name
-----------------------------------

Clone the repo::

   git clone git@github.com:mozilla-services/pytest-services.git
   git checkout -b new_service

Setup for new service::

   mkdir heroku
   cd heroku

Create Default Files
--------------------

The new service should be a Python Package::

   touch __init__.py client.py resources.py

Commit shell::

   git add .
   git push -m 'Adding new service Heroku'

Add Service Specific Content
============================

``client.py``: responsible for obtaining data from the service, and
placing it into the pytest cache. The client module typically exposes the data via a
"{service}_client" object. The pytest framework will instantiate the client
before any tests are run with all the configuration & credential
information provided by the configureation files and command line
options.

``resources.py``: holds mapping functions which convert the data from
the cache into the format expected by the tests. This should be the only
file which imports the instantiation of the client. (Future best
practices may pre-populate the cache outside of the pytest execution.)

``conftest.py`` (optional) As much as possible, put service specific
options, etc. in this local file. (Some things may not work c.f. BUG.)

Tests for these support files should be included as doc tests whenever
practical.

Add Service Specific Tests
--------------------------

``test_*.py``: normal pytest tests, which each import the resources they
need to test.
