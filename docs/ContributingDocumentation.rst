==========================
Contributing Documentation
==========================

Frost documentation is written in `restructured text <https://en.wikipedia.org/wiki/ReStructuredText>`_ and rendered into HTML with `Sphinx <https://www.sphinx-doc.org>`_.

Create a new documentation branch
---------------------------------

Use a descriptive branch name that describes the changes, such as: **adding_new_toaster_doc_section**.

Create a new branch::

   git clone git@github.com:mozilla/frost.git
   cd frost/docs
   git checkout -b my_descriptive_documentation_branch

Make documentation changes in branch
------------------------------------

Remember that any new sections will need to be listed in the `table of contents <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>`_ in the `index.rst file <https://github.com/mozilla/frost/blame/master/docs/index.rst#L10-L18>`_.

Build docs and read over changes
--------------------------------

build::

   pip install sphinx
   pwd # Should be the docs directory.
   make html

Read over your changes using your `favorite web browser <https://getfirefox.com>`_ by going to a `file:// URL <https://en.wikipedia.org/wiki/File_URI_scheme>`_ for the **index.html** file.

URL::

   echo "file://$(pwd)/index.html"

Commit and review
-----------------

Commit::

   git add .
   git push -m 'Adding new documentation section on video toasters'

File a `PR <https://github.com/mozilla/frost/pulls>`_ and request a review from a `code owner <https://github.com/mozilla/frost/graphs/contributors>`_.
