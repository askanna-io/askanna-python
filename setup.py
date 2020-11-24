#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from askanna import __version__ as askanna_version

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.1',
    'cookiecutter>=1.6.0',
    'requests>=2.22.0',
    'PyYAML==5.3',
    'python-dotenv==0.14.0',
    'resumable==0.1.1',
    'gitpython==3.1.3',
    'appdirs==1.4.4',
    'dataclasses; python_version=="3.6.*"'
]

setup_requirements = [
    'wheel~=0.34.2'
]

test_requirements = []

# FIXME: add license information
setup(
    author="AskAnna",
    author_email='devops@askanna.io',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="AskAnna Command line and library interface",
    entry_points={
        'console_scripts': [
            'askanna=askanna.cli.tool:cli',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='askanna',
    name='askanna',
    packages=find_packages(include=['askanna'], exclude=['tests']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.askanna.io/open/askanna-cli',
    version=askanna_version,
    zip_safe=False,
)
