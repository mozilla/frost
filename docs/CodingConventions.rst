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

.. _doctest: https://docs.python.org/3.8/library/doctest.html
