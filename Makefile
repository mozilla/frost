
TODAY := $(shell date '+%Y-%m-%d')

ENTER_VENV := source venv/bin/activate

.DEFAULT_GOAL := all

AWS_PROFILE := default

doctest:
	for f in $$(find . -name '*.py' | grep -vP '(venv|test|resources|init)'); do venv/bin/python -m doctest $$f; done

clean: clean-cache

clean-cache:
	venv/bin/pytest --cache-clear --aws-profiles $(AWS_PROFILE)

awsci: clean-aws-ci

clean-aws-ci:
	venv/bin/pytest --cache-clear aws/ --aws-profiles $(AWS_PROFILE) --json=results-$(AWS_PROFILE)-$(TODAY).json

venv:
	python3 -m venv venv

install: venv
	venv/bin/pip3 install -r requirements.txt

all:
	venv/bin/pytest

.PHONY:
	all \
	clean \
	clean-cache \
	install \
	venv
