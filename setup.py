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
    'cnr-server>=0.2,<=0.3',
    'cnrclient>=0.2,<=0.3',
    'futures',
    'requests==2.11.1',
    'pyyaml',
    'jinja2==2.8',
    'jsonpatch',
    'tabulate',
    'termcolor',
    'python-etcd',
    'semantic_version==2.6.0',
    'flask',
    'Flask>=0.10.1',
    'flask-cors',
    'jsonnet>=0.9.0',
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
    version='0.24.0',
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

)
