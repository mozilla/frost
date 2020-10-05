
TODAY := $(shell date '+%Y-%m-%d')

.DEFAULT_GOAL := all

AWS_PROFILE := default

PYTEST_OPTS := ''

all: check_venv
	frost test

awsci: check_venv
	frost test --continue-on-collection-errors -m aws aws/**/*.py \
		-k "not test_ec2_security_group_in_use" \
		--json=results-$(AWS_PROFILE)-$(TODAY).json $(PYTEST_OPTS)

check_venv:
ifeq ($(VIRTUAL_ENV),)
	$(error "Run frost from a virtualenv (try 'make install && source venv/bin/activate')")
endif

check_conftest_imports:
	# refs: https://github.com/mozilla/frost/issues/119
	grep --recursive --exclude-dir '*venv' --include '*.py' '^import\s+conftest|^from\s+conftest\s+import\s+pytest' ./ ; [ $$? -eq 1 ]

clean: clean-cache clean-python
	rm -rf venv
	# remember to deactivate your active virtual env

clean-cache: check_venv
	@# do as little work as possible to clear the cache, and guarantee success
	frost test  --cache-clear --continue-on-collection-errors \
		--collect-only -m "no_such_marker" \
		--noconftest --tb=no --disable-warnings --quiet \
	    || true

clean-python:
	find . -type d -name venv -prune -o -type d -name __pycache__ -print0 | xargs -0 rm -rf

doc-build: check_venv
	type sphinx-build || { echo "please run `make install-docs` to build docs"; false; }
	make -C docs html

doctest: check_venv
	frost test -vv --doctest-modules --doctest-glob='*.py' -s --offline --debug-calls $(shell find . -type f -name '*.py' | grep -v venv | grep -v .pyenv | grep -v setup.py)
	 --doctest-modules -s --offline --debug-calls

coverage: check_venv
	frost test --cov-config .coveragerc --cov=. \
		--aws-profiles example-account \
		-o python_files=meta_test*.py \
		-o cache_dir=./example_cache/ \
		--offline \
		$(shell find . -type f -name '*.py' | grep -v venv | grep -v .pyenv | grep -v setup.py)
	coverage report -m
	coverage html

flake8: check_venv
	flake8 --max-line-length 120 $(shell git ls-files | grep \.py$$)

black: check_venv
	pre-commit run black --all-files

install: venv
	( . venv/bin/activate && pip install -U pip && pip install -r requirements.txt && python setup.py develop && pre-commit install )

install-docs: venv
	( . venv/bin/activate && pip install -r docs-requirements.txt )

setup_gsuite: check_venv
	python -m bin.auth.setup_gsuite

metatest:
	frost test --aws-profiles example-account \
		-o python_files=meta_test*.py \
		-o cache_dir=./example_cache/

venv:
	python3 -m venv venv

build-image:
	docker build -t localhost/frost:latest .

.PHONY: \
	all \
	awsci \
	black \
	build-image \
	check_conftest_imports \
	check_venv \
	clean \
	clean-cache \
	clean-python \
	coverage \
	doc-build \
	doctest \
	flake8 \
	install \
	install-docs \
	metatest \
	setup_gsuite \
	venv
