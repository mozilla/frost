==========================
Contributing Documentation
==========================

Frost documentation may be written in either `restructured text <https://en.wikipedia.org/wiki/ReStructuredText>`_ or `Markdown`__ (`Common Mark`__ syntax). All input is rendered into HTML with `Sphinx <https://www.sphinx-doc.org>`_.

__ https://en.wikipedia.org/wiki/Markdown
__ https://en.wikipedia.org/wiki/Markdown#CommonMark

Create a new documentation branch
---------------------------------

Use a descriptive branch name that describes the changes, such as: **adding_new_toaster_doc_section**.

Create a new branch (assumes you already have configured SSH keys for your GitHub account):

.. code:: console

   git clone git@github.com:mozilla/frost.git
   cd frost
   git checkout -b my_descriptive_documentation_branch
   make install-docs

Make documentation changes in branch
------------------------------------

While editing the documentation, you may find it useful to run an "autobuilder". That will allow you to review the completed documentation as you save your work. To activate the autobuilder, open a new terminal window, then::

   cd /path/to/frost
   source venv/bin/activate
   made doc-preview

You will want to terminate the autobuilder prior to doing the final checks below. Just enter ctrl-C in the terminal window running autobuilder. (A number of parameters can be used to adjust the behavior of the autobuilder. Run ``sphinx-autobuilder --help`` for a list, and set the environment variable ``AUTOBUILD_OPTS`` to override.)

Remember that any new sections will need to be listed in the `table of contents <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>`_ in the `index.rst file <https://github.com/mozilla/frost/blame/master/docs/index.rst#L10-L18>`_.

Build docs and read over changes
--------------------------------

The following steps will give you a clean build of the final version of all the docs. You can view those by opening ``/path/to/frost/docs/_build/html/index.html`` in a browser.

build::

   pwd # Should be the main frost directory.
   make doc-build

Read over your changes using your `favorite web browser <https://getfirefox.com>`_ by going to a `file:// URL <https://en.wikipedia.org/wiki/File_URI_scheme>`_ for the **index.html** file.

URL::

   echo "file://$(pwd)/_build/html/index.html"

Commit and review
-----------------

Commit::

   git add .
   git commit -m 'Adding new documentation section on video toasters'
   git push

The first time you push, the URL for creating a PR will be shown in the terminal. If you missed that, display your branch on the web, and create the PR.

File a `PR <https://github.com/mozilla/frost/pulls>`_ and request a review from a `code owner <https://github.com/mozilla/frost/graphs/contributors>`_.
