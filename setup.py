#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=7.0',
    'cookiecutter>=1.6.0',
    'requests>=2.22.0',
    'PyYAML==5.3',
    'python-dotenv==0.13.0',
    'resumable==0.1.1'
]

setup_requirements = [
    'wheel~=0.32.1'
]

test_requirements = []

# FIXME: add license information
setup(
    author="AskAnna",
    author_email='devops@askanna.io',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="AskAnna Command line and library interface",
    entry_points={
        'console_scripts': [
            'askanna=askanna_cli.tool:cli',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='askanna',
    name='askanna-cli',
    packages=find_packages(include=['askanna_cli', 'askanna_cli.core'], exclude=['tests']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.askanna.io/askanna/askanna-cli',
    version='0.2.0',
    zip_safe=False,
)
