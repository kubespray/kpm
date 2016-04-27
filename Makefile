.PHONY: clean-pyc clean-build docs clean
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"
VERSION := `cat VERSION`

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 kpm tests

test-cli:
	py.test --cov=kpm --cov=bin/kpm --cov-report=html --cov-report=term-missing  --verbose tests -m "cli" --cov-config=.coverage-cli.ini

test:
	py.test --cov=kpm --cov-report=html --cov-report=term-missing  --verbose tests -m "not cli" --cov-config=.coverage-unit.ini

test-all:
	py.test --cov=kpm --cov-report=html --cov-report=term-missing  --verbose tests

tox:
	tox

coverage:
	coverage run --source kpm setup.py test
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs:
	rm -f docs/kpm.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ kpm
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install

flake8:
	python setup.py flake8

coveralls: test
	coveralls

dockerfile: dist
	cp deploy/Dockerfile dist
	docker build --build-arg version=$(VERSION) -t quay.io/kubespray/kpm:v$(VERSION) dist/

dockerfile-canary: dist
	cp deploy/Dockerfile dist
	docker build --build-arg version=$(VERSION) -t quay.io/kubespray/kpm:canary dist/
	docker push quay.io/kubespray/kpm:canary

dockerfile-push: dockerfile
	docker push quay.io/kubespray/kpm:v$(VERSION)
