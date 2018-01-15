
TODAY := $(shell date '+%Y-%m-%d')

ENTER_VENV := source venv/bin/activate

.DEFAULT_GOAL := all

clean: clean-cache

clean-cache:
	pytest --cache-clear

venv:
	python3 -m venv venv

install: venv
	$(ENTER_VENV) && pip3 install -r requirements.txt

all:
	pytest

.PHONY:
	all \
	clean \
	clean-cache \
	install \
	venv
