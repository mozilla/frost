.. raw:: html

   <!-- This Source Code Form is subject to the terms of the Mozilla Public
      - License, v. 2.0. If a copy of the MPL was not distributed with this
      - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

===========
Conventions
===========

- As mentioned elsewhere, all function *not* within a ``test_*.py`` file should
  have doctest_ tests.


- Frost tests are expected to support the ``--json`` option by ensuring ids used
  in ``pytest.mark.parametrize`` contain sufficient information for downstream
  processing.

.. _offline:

- All data access routines should respect the ``--offline`` command line option
  that is a ``frost`` extension. The value of ``--offline`` is passed as a value to
  the "client" constructor.

  If you do not properly implement this option, you will break "``make doctest``" for
  everything. (I.e. you're advised to run "``make doctest``" early & often while
  implementing a new service.)

.. _doctest: https://docs.python.org/3.6/library/doctest.html

