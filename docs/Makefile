# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# tcp/ip port for previewing docs
PORT ?= 

# Put it first so that "make" without argument is like "make help".
help: check_venv
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile check_venv
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

###############################
#
# Local Modifications
#
###############################

check_venv:
ifeq ($(VIRTUAL_ENV),)
		$(e#rror "Build frost documents from a virtualenv (try 'make -C .. install && source ../venv/bin/activate')")
endif
ifeq ($(shell type -p sphinx-build),)
		$(error "Install document toolchain (try 'make install')")
endif

install: check_venv
		pip install -r requirements.txt

preview: check_venv
	python3 -m http.server --directory _build/html/ $(PORT)


.PHONY: check_venv install preview
