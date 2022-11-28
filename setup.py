from setuptools import find_packages, setup

from askanna import __author__ as askanna_author
from askanna import __email__ as askanna_email
from askanna import __version__ as askanna_version

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as history_file:
    history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()

setup_requirements = ["wheel~=0.38.4"]


setup(
    name="askanna",
    version=askanna_version,
    author=askanna_author,
    author_email=askanna_email,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    entry_points={
        "console_scripts": [
            "askanna=askanna.cli:cli",
            "askanna-run-utils=askanna.cli.run_utils:cli",
        ],
    },
    description="The AskAnna CLI & Python SDK is part of the AskAnna platform to kickstart your data science projects",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="askanna ml ai data datascience versioncontrol",
    license="BSD 3-Clause License",
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
    setup_requires=setup_requirements,
    url="https://askanna.io",
    project_urls={
        "Documentation Python SDK": "https://docs.askanna.io/python-sdk/",
        "Documentation CLI": "https://docs.askanna.io/cli/",
        "Documentation AskAnna": "https://docs.askanna.io/",
        "Changelog": "https://gitlab.com/askanna/askanna-python/-/blob/master/CHANGELOG.md",
        "Issue tracker": "https://gitlab.com/askanna/askanna-python/issues",
        "Source": "https://gitlab.com/askanna/askanna-python",
    },
    zip_safe=False,
)
