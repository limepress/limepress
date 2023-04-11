SHELL=/bin/bash
PYTHON=python3.10

PYTHON_ENV_ROOT=envs
PYTHON_DEVELOPMENT_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-development-env
PYTHON_TESTING_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-testing-env
PYTHON_PACKAGING_ENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-packaging-env

.PHONY: clean doc sdist test ci-test dev-env lint shell freeze

# environments ################################################################
# development
$(PYTHON_DEVELOPMENT_ENV): REQUIREMENTS.development.txt setup.py
	rm -rf $(PYTHON_DEVELOPMENT_ENV) && \
	$(PYTHON) -m venv $(PYTHON_DEVELOPMENT_ENV) && \
	. $(PYTHON_DEVELOPMENT_ENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -r ./REQUIREMENTS.development.txt

# testing
$(PYTHON_TESTING_ENV): REQUIREMENTS.testing.txt setup.py
	rm -rf $(PYTHON_TESTING_ENV) && \
	$(PYTHON) -m venv $(PYTHON_TESTING_ENV) && \
	. $(PYTHON_TESTING_ENV)/bin/activate && \
	pip install pip --upgrade && \
	pip install -r ./REQUIREMENTS.testing.txt

# packaging
$(PYTHON_PACKAGING_ENV): REQUIREMENTS.packaging.txt setup.py
	rm -rf $(PYTHON_PACKAGING_ENV) && \
	$(PYTHON) -m venv $(PYTHON_PACKAGING_ENV) && \
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r REQUIREMENTS.packaging.txt

# helper
dev-env: | $(PYTHON_DEVELOPMENT_ENV)

clean:
	rm -rf $(PYTHON_ENV_ROOT)

shell: | $(PYTHON_DEVELOPMENT_ENV)
	. $(PYTHON_DEVELOPMENT_ENV)/bin/activate && \
	rlpython

freeze: | $(PYTHON_DEVELOPMENT_ENV)
	. $(PYTHON_DEVELOPMENT_ENV)/bin/activate && \
	pip freeze

# tests #######################################################################
test: | $(PYTHON_TESTING_ENV)
	. $(PYTHON_TESTING_ENV)/bin/activate && \
	rm -rf htmlcov && \
	time tox $(args)

ci-test: | $(PYTHON_TESTING_ENV)
	. $(PYTHON_TESTING_ENV)/bin/activate && \
	rm -rf htmlcov && \
	time JENKINS_URL=1 tox -r $(args)

# linting #####################################################################
lint: | $(PYTHON_TESTING_ENV)
	. $(PYTHON_TESTING_ENV)/bin/activate && \
	time tox -e lint $(args)

# packaging ###################################################################
sdist: | $(PYTHON_PACKAGING_ENV)
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	rm -rf dist *.egg-info && \
	./setup.py sdist

_release: sdist
	. $(PYTHON_PACKAGING_ENV)/bin/activate && \
	twine upload --config-file ~/.pypirc.fscherf dist/*
