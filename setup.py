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
    'PyYAML>=5.3',
    'python-dotenv>=0.14.0',
    'resumable>=0.1.1',
    'gitpython>=3.1.3',
    'appdirs>=1.4.4',
    'dataclasses; python_version=="3.6.*"',
    'python-slugify>=4.0.1',
]

setup_requirements = [
    'wheel~=0.34.2'
]

test_requirements = []

setup(
    name='askanna',
    version=askanna_version,
    author="AskAnna",
    author_email='devops@askanna.io',
    python_requires='>=3.6',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Topic :: Scientific/Engineering",
    ],
    entry_points={
        'console_scripts': [
            'askanna=askanna.cli.tool:cli',
        ],
    },
    install_requires=requirements,
    description="AskAnna CLI is part of the AskAnna platform to kickstart your data science projects",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='askanna ml ai data',
    license="Apache License 2.0",
    packages=find_packages(exclude=['tests']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://askanna.io',
    project_urls={
        "Documentation": "https://docs.askanna.io/#/cli",
        "Source Code": "https://gitlab.askanna.io/open/askanna-cli",
    },
    zip_safe=False,
)
