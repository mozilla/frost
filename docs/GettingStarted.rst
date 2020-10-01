.. raw:: html

   <!-- This Source Code Form is subject to the terms of the Mozilla Public
      - License, v. 2.0. If a copy of the MPL was not distributed with this
      - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

===============
Getting Started
===============
Get started by installing Frost and running some pre-built tests.

Installing Frost
================

Clone the repo::

   git clone git@github.com:mozilla/frost.git

Create a virtual environment::

   cd frost
   python3 -m venv venv  

Activate the virtual environment::

   . venv/bin/activate

Upgrade pip::

   pip install --upgrade pip

Install Requirements::

   pip install -r requirements.txt

Running a pre-built AWS test
============================

Pre-requirements
----------------

Frost uses the `boto 3 <https://github.com/boto/boto3/>`_ library to communicate with AWS. Prior to running tests you must `configure <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration>`_ your environment authentication credentials to work with boto3, and then authenticate to AWS.  See the AWS `documentation <https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html>`_ for assistance.

Pick a test
-----------

The tests for AWS live under the associated services directories in the aws directory.

Example run::

   pytest aws/elb/test_elb_instances_attached.py

Example Output::

   pytest aws/elb/test_elb_instances_attached.py
   ============================= test session starts ==============================
   platform XYZ -- Python 3.7.1, pytest-6.0.2, py-1.9.0, pluggy-0.13.1
   rootdir: frost
   plugins: cov-2.10.0, json-0.4.0, metadata-1.10.0
   collected 18 items
   
   aws/elb/test_elb_instances_attached.py .......F.....FFF..FFFF....F.F.... [ 37%]
   F......F.......F..F..F.F....F.F......F...............F.                  [100%]
   
   =================================== FAILURES ===================================
   _______________ test_elb_instances_attached[elb1] ________________

   elb = {'AvailabilityZones': ['us-east-1e', 'us-east-1d', 'us-east-1c', 'us-east-1a'], 'BackendServerDescriptions': [], 'Cano...eName': 'elb1.us-east-1.elb.amazonaws.com', 'CanonicalHostedZoneNameID': 'ZZZZZZZZZZZZ', ...}

       @pytest.mark.elb
       @pytest.mark.parametrize(
           "elb", elbs(), ids=lambda e: get_param_id(e, "LoadBalancerName"),
       )
       def test_elb_instances_attached(elb):
           """
           Checks to see that an ELB has attached instances and fails if
           there are 0
           """
   >       assert len(elb["Instances"]) > 0, "ELB has zero attached instances"
   E       AssertionError: ELB has zero attached instances
   E       assert 0 > 0
   E        +  where 0 = len([])
   ...

.. _pytest:  https://pytest.org/
.. _frost: https://github.com/mozilla/frost
