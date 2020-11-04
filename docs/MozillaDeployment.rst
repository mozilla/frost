.. raw:: html

   <!-- This Source Code Form is subject to the terms of the Mozilla Public
      - License, v. 2.0. If a copy of the MPL was not distributed with this
      - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

==================
Mozilla Deployment
==================

Some details of the Mozilla deployment of Frost are listed here as an example of
how it can be done.

Frost jobs are run via Jenkins. Jobs are organized for both convenience and to
accommodate different reporting intervals. Usually only a single service is
queried in any particular job.

The actual job runs in a docker container, which has the frost repository
already checked out. Separate configuration repositories are also checked out at
runtime, based on job parameters.

Jobs have a common entry script, which performs any job-specific tasks before
and after the main frost run. PyTest is always invoked with the ``--json``
options supported by the frost extensions, and post processing steps are
expected to use the JSON as input.

[The deployment is under revision. A rough "as is" doc may be found `here`__.]

__ https://docs.google.com/document/d/1ePUkJPcHEj9XxaVYr2TSABOxRjhDBKr2KSQ2EzgHJm4

Adjacent Tools at Mozilla
=========================

We feed some of the output of Frost tests into our metrics system. While the output of Frost is JSON, it's not in a format 
that is easily consumable by our injestion engine: AWS Athena reading from S3.  For that, more traditional formats, 
such as CSV and un-nested JSON are easier to work with. To support that, our jobs typically post process the Frost JSON 
into reasonable morsels for our metrics. Our conventions__ may be of interest.

__ https://github.com/mozilla-services/foxsec-tools/tree/master/metrics/utils/Conventions.md
