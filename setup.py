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
    'cnr-server',
    'cnrclient',
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
    'jsonnet',
]

secure_requirements = [
    'ecdsa',
    'cryptography',
    'urllib3[secure]',
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
    version='0.22.0-pre',
    description="KPM cli",
    long_description=readme + '\n\n' + history,
    author="Antoine Legrand",
    author_email='2t.antoine@gmail.com',
    url='https://github.com/coreos/kpm',
    packages=[
        'kpm',
        'kpm.api',
        'kpm.api.impl',
        'kpm.commands',
        'kpm.platforms',
        'kpm.formats',
        'kpm.convert'
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
    tests_require=test_requirements,
    extras_require={
        'secure': secure_requirements
    },
    dependency_links=[
        'https://github.com/google/jsonnet/archive/227079272a19d03adf34332e2a0c11906e081894.zip#egg=jsonnet'
    ]
)
