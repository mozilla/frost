
TODAY := $(shell date '+%Y-%m-%d')

.DEFAULT_GOAL := all

AWS_PROFILE := default

PYTEST_OPTS := ''

all: check_venv
	pytest

awsci: check_venv
	pytest --continue-on-collection-errors aws/ \
		--ignore aws/ec2/test_ec2_security_group_in_use.py \
		--json=results-$(AWS_PROFILE)-$(TODAY).json $(PYTEST_OPTS)

check_venv:
ifeq ($(VIRTUAL_ENV),)
	$(error "Run pytest-services from a virtualenv (try 'make install && source venv/bin/activate')")
endif

clean: clean-cache clean-python
	rm -rf venv
	# remember to deactivate your active virtual env

clean-cache: check_venv
	pytest --cache-clear --offline

clean-python:
	find . -type d -name venv -prune -o -type d -name __pycache__ -print0 | xargs -0 rm -rf

doctest: check_venv
	pytest --doctest-modules -s --offline --debug-calls

coverage: check_venv
	pytest --cov-config .coveragerc --cov=. --cov-append \
		--aws-profiles example-account \
		-o python_files=meta_test*.py \
		-o cache_dir=./example_cache/
	coverage report -m
	coverage html

flake8: check_venv
	flake8 --max-line-length 120 $(shell git ls-files | grep \.py$$)

install: venv
	( . venv/bin/activate && pip install -r requirements.txt )

setup_gsuite: check_venv
	python -m bin.auth.setup_gsuite

metatest:
	pytest --aws-profiles example-account \
		-o python_files=meta_test*.py \
		-o cache_dir=./example_cache/

venv:
	python3 -m venv venv

.PHONY:
	all \
	check_venv \
	clean \
	clean-cache \
	clean-python \
	flake8 \
	install \
	venv
