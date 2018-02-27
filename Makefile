
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

clean: clean-cache
	rm -rf venv

clean-cache: check_venv
	pytest --cache-clear --aws-profiles $(AWS_PROFILE)

doctest: check_venv
	pytest --doctest-modules -s --offline --aws-debug-calls

doctest-coverage: check_venv
	pytest --cov-config .coveragerc --cov=. --doctest-modules -s --offline --aws-debug-calls
	coverage report -m
	coverage html

flake8: check_venv
	flake8 --max-line-length 120 $(shell find . -name '*.py' -not -path "./venv/*")

install: venv
	( . venv/bin/activate && pip install -r requirements.txt )

metatest:
	pytest --aws-profiles example-account \
		--aws-regions us-east-1 \
		-o python_files=meta_test*.py \
		-o cache_dir=./example_cache/

venv:
	python3 -m venv venv

.PHONY:
	all \
	check_venv \
	clean \
	clean-cache \
	flake8 \
	install \
	venv
