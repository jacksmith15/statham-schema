.PHONY: build

RUN_CLEAN_TEST:=bash run_test.sh -c
CHECK_VIRTUALENV:=python -c "import sys;sys.real_prefix"


help: ## Prints this help/overview message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-17s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Cleans all testing metadata and .pyc files.
	$(RUN_CLEAN_TEST)

install: ## Installs all dependencies
	$(CHECK_VIRTUALENV) || (echo "Not inside a virtualenv, aborting."; exit 1)
	pip install -r requirements.txt -r requirements-test.txt	

test: install ## Runs all tests
	$(RUN_CLEAN_TEST) -a

lint: install ## Runs linter on source code and tests.
	$(RUN_CLEAN_TEST) -l

unit: install ## Runs all unit tests with coverage test.
	$(RUN_CLEAN_TEST) -u

type: install ## Runs type checker. Does not update requirements or rules.
	$(RUN_CLEAN_TEST) -t

build: test ## Creates a new build for publishing. Deletes previous builds.
	rm -rf build/* dist/*
	pip install -U setuptools wheel
	python setup.py sdist bdist_wheel

publish: build  ## Publishes 1 build package to users default PyPi server specified in .pypirc
	python release.py
	echo "No pypi publishing set up!"
# 	python setup.py sdist upload -v -r pyshop