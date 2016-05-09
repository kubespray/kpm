#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'futures',
    'requests',
    'pyyaml',
    'jinja2',
    'jsonpatch',
    'tabulate',
    'termcolor',
    'python-etcd',
    'semantic_version',
    'flask',
    'Flask>=0.10.1',
    'flask-cors',
]

requirements_crypto = [
    'ecdsa',
    'cryptography'
]

test_requirements = [
    "pytest",
    "pytest-cov",
    'pytest-flask',
    "pytest-ordering",
    "requests-mock"
]

setup(
    name='kpm',
    version='0.16.1',
    description="KPM cli",
    long_description=readme + '\n\n' + history,
    author="Antoine Legrand",
    author_email='2t.antoine@gmail.com',
    url='https://github.com/kubespray/kpm',
    packages=[
        'kpm',
        'kpm.api'
    ],
    scripts=[
        'bin/kpm'
    ],
    package_dir={'kpm':
                 'kpm'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache License version 2",
    zip_safe=False,
    keywords=['kpm', 'kpmpy', 'kubernetes'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
