<!-- This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

# Frequently Asked Questions

About [``pytest-services``][pts].


[pts]: https://github.com/mozilla-services/pytest-services

**What's the general flow of a ``test``?**

When you invoke a test, ``pytest-services`` uses features of
[``pytest``][pytest] to execute the test. Most commonly, the test will
validate certain relationships about data files representing
configuration data of some external service.

If the data-under-test is already cached (and fresh enough), the cached
data will be used. If the data is not available locally, ``pytest``
fixtures are used to obtain or refresh the data required by that test.
Any freshly retrieved data is cached for use by other tests.

This "lazy evaluation" of supplying data ensures the quickest possible
turnaround time for ad-how queries.


[pytest]: https://pytest.org/
