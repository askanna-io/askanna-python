# Changelog

## 0.24.0 (2024-02-21)

- Add support for Python 3.12 and drop support for Python 3.7
- Add created_by info to Workspace & Project dataclasses

## 0.23.0 (2023-04-05)

- Added new run filters: `status`, `trigger`, `created_by` and `package_suuid`
- Implemented option for exclude version of run filters (e.g. `status__exclude`)
- CLI command `askanna run list` now includes a filter option for `status`
- Defined `status` and `trigger` values using a `Literal` type
- Expanded test coverage and added test utils with date-time helpers
- Removed deprecated `GetRunsSDK`
- Switch from `pytz` to `zoneinfo` and removed [pytz](http://pythonhosted.org/pytz) from dependencies
- Change the build system from [Wheel](https://wheel.readthedocs.io/) to [Hatch](https://hatch.pypa.io/)
- Switch from [Flake8](https://flake8.pycqa.org/) to [Ruff](https://beta.ruff.rs/docs/)
- Introduce parallel matrix for GitLab CI/CD to simplify the config
- Add release related jobs to GitLab CI/CD

## 0.22.0 (2023-03-06)

- Add '_at' suffix to datetime fields in dataclasses to support the new AskAnna Backend API response
- Fix creating a project with description value None
- Update documentation references
- Align printing of object info via CLI
- Update ArtifactInfo dataclass

## 0.21.0 (2023-02-01)

- Add info option to CLI commands
- Support new query options in both Python SDK and CLI. A.o. you can now search for objects.
- Extend run CLI commands, a.o. to retrieve a list of runs or info of a run
- Support new Cursor Pagination setup from the AskAnna Backend
- Refactor to support the new setup of the AskAnna Backend API endpoints

## 0.20.0 (2022-11-28)

- New subcommands to get run status & log
- All commands and SDK modules now have the change & remove/delete option.
- The remove prompt will by default ask for confirmation before removing the object.
- Refactor API endpoints, and align gateway methods, SDK modules & CLI commands. The goal is to make separate
  components that perform a single task. This should make it easier to maintain the AskAnna CLI - Python SDK.
- There is now a separate SDK module with the code necessary for the AskAnna Python SDK. This is related to the
  above change.
- Dataclasses now also contain relation types as a dataclass used within the main dataclasses. For example, to get
  the project workspace name, you can now use `project.workspace.name` i.s.o. `project.workspace.get("name)`.

The following changes are related to breaking changes in the AskAnna Backend:

- The API response does not provide the `uuid` info anymore and the `short_uuid` is renamed to `suuid`.
- Renamed API endpoints to follow the new config of the AskAnna Backend.

## 0.19.2 (2022-09-10)

- Update dataclass for projects

## 0.19.1 (2022-09-01)

- Extend ProjectGateway with `packages` method to get a list of project packages
- Fix `askanna push` with the push-target set to an AskAnna Frontend URL
- Fix `askanna create --push` so that after creating a new project you automatically push an initial version

## 0.19.0 (2022-08-25)

- Update runinfo dataclass to support AskAnna Backend v0.17.0
- Cleanup code & files

## 0.18.0 (2022-07-21)

- Implement new rest auth URLs
- Simplify login in case you're already signed in
- Add experimental GitPod config

## 0.17.0 (2022-06-20)

- For tracking metrics & variables detect type of list and store the specific list type (`list_integer`,
  `list_string`, etc.)
- Extend support for tracking metrics & variables with data type Numpy
- Fixed a bug that Numpy array could not be stored as a metric/variable

## 0.16.0 (2022-05-09)

- Add create and remove workspace to SDK and CLI
- Add delete to project SDK
- Change project & workspace now also supports changing visibility via SDK and CLI
- Change dataclass Workspace to support the changed response of AskAnna Backend

## 0.15.0 (2022-02-11)

- Make the requirements less strict, so it's easier to integrate AskAnna in your existing Python environment.
- Let tzlocal work with newer version of the tzlocal package
- Add job to publish master and version tags to public repos

## 0.14.1 (2022-02-04)

- Added login argument 'url' making it possible to log in on different AskAnna environments using the web URL
- Fix: after successful login, you now get a success message i.s.o. a fail message
- Updated AA_REMOTE and tests to align with new config setup

## 0.14.0 (2021-11-25)

- Refactor server & project Config. If you upgrade from a previous version `0.14.0` the AskAnna CLI will
  automatically update your AskAnna config file to the new format.
- We fixed a bug in [askannaignore](https://docs.askanna.io/code/#ignore-files) where in some circumstances it did not
  read the ignore file.
- Add [bandit](https://bandit.readthedocs.io/en/latest/), [Black](https://black.readthedocs.io/en/stable/) and
  [isort](https://pycqa.github.io/isort/) to the pre-commit stack.

## 0.13.1 (2021-10-29)

- Added `is_member` to dataclasses `Workspace` and `Project` to denote whether the user is member of the object.
  Users can now list public workspaces and workspaces, so this flag can indicate the membership.
- Added `permission` to dataclass `Project` to list permissions the user has for ths particular object.
- Added `visibility` to dataclasses `Workspace` and `Project` to indicate whether this is a `PUBLIC` or `PRIVATE`
  workspace or project.

## 0.13.0 (2021-07-29)

- Added `notifications` to dataclasses `Job` and `Project`. We validate whether notifications are setup correctly.
- Introducing `.askannaignore` using the same syntax as `.gitignore` to exclude files from pushing to AskAnna.

## 0.12.2 (2021-07-22)

- Add dataclass `RunStatus` to fix starting a new run

## 0.12.1 (2021-07-22)

- Add environment to `Run` dataclass

## 0.12.0 (2021-07-08)

- Updated endpoints changes from `/v1/jobrun/` to `/v1/runinfo/`
- We now register an result upload before uploading. This is change required by API `v0.7.0`.
- Updates on the dataclass from `RunInfo` adding fields `environment`, `duration`, `result`, `started`
- Deprecation of dataclass fields on `RunInfo`: `runner`, `deleted`
- `track_metric` now also supports `range` type as a value to track
- We publish our images also on DockerHub starting from now

## 0.11.0 (2021-06-16)

- `track_metric(s)` and `track_variable(s)` now also support date type `list`
- Extended `askanna.runs.get` with the option to filter on `job_name` and to order on `create` date
- When you start a run using the job name via the Python SDK, we now use the project SUUID from the config as a
  default filter.
- If you run a Python script from an AskAnna project directory, we also load the project SUUID in the config.
- Remove deprecated CLI command `askanna artifact add`
- Try to check if an update is available, but don't crash if we cannot run the check

## 0.10.0 (2021-06-03)

- Add functionality to get run results:
  - CLI: `askanna result get`
  - Python SDK: `askanna.result.get()` and `askanna.result.get_content_type()`
- Refactor how we zip artifact paths. The new function fixes an issue with saving individual files. Also, it has some
  built in protection that you cannot zip the full filesystem as an artifact.
- Add run utils function to push the artifact, and prepare for removing `askanna artifact add`

## 0.9.0 (2021-05-19)

- Give runs a name and description when you start them.
  [More info in the documentation.](http://docs.askanna.io/job/run-job/)
- Extend validation of `askanna.yml` with an informative check on the time zone.
- Update dataclasses of API responses where we removed the `UUID` and `title`. We now only show the short UUID and
  `name`.
- In API request add `askanna-agent` and `askanna-agent-version` to inform the platform with which tool and version
  the request is done.
- Added a check if a new version of AskAnna is available. For example, if you run `askanna --version` and a new
  version is available, we show an informative message how you can update.
- Removed deprecated functions and files.
- Updated dependencies and removed the superfluous dependency `appdir`.
- Make `askanna variable add` interactive, so you don't have to look-up the project SUUID to add a variable.
- Changing the name of a workspace or project can now also be done via the CLI.
- Install `tzdata` in the default container-image to make it possible to set the time zone of the run environment.
- Fix retrieval of runs with `askanna.run.get` with `include_metrics=True` on.

## 0.8.0 (2021-04-15)

- Added track_variable and track_variables: from now on you can track variables for your runs. Also run environment
  variables are tracked.
- Added validation for `askanna.yml` to check job names and schedule definitions
- Change name and description of a job via the CLI (`askanna job change`) or Python SDK (`askanna.job.change`)

## 0.7.0 (2021-03-18)

- Adding track_metric and track_metrics: from now on you can track metrics for your runs, both ran on AskAnna servers
  and local runs.
- Regrouped commands used for the askanna-runner under it's own command `askanna-run-utils` instead of `askanna`
- Improvements in the client on how the AskAnna SDK communicates with the AskAnna API
- Update PyYAML library from 5.3 to 5.4.1

## 0.6.2 (2021-03-08)

- Make `askanna init` more friendly to use
- Refer to open source project on GitLab.com
- Tweak configuration and README

## 0.6.1 (2021-02-11)

- Update references to the new documentation of AskAnna

## 0.6.0 (2021-02-03)

- Added push-and-run via `askanna run --push` where you first push your code and then trigger a run
- Installed gcc in the default image we run on AskAnna
- Added developer option to specicy on which AskAnna remote you want to login
- Changes in parameter names for Python SDK (run.status and variable modules). If you used the 0.5.x version of the
  AskAnna Python SDK this version can break your code.

## 0.5.1 (2021-01-27)

- Fix that you can run a job with name and additional options

## 0.5.0 (2021-01-26)

- Use `askanna run job_name` to run a job
- Start of AskAnna Python SDK with support for:
  - starting a run
  - getting the status of a run
  - management of project variables
  - listing jobs
- Refactor code base to support SDK and remove some unused functions
- In `askanna.yml` allow output/artifact to specify which files & directories you want to save

## 0.4.3 (2020-12-25)

- `askanna create --template` will allow you to use your own template to create a new project
- Fix `askanna create` so it will actually create a project
- Update `askanna init` so it uses to same flow as `askanna create`

## 0.4.2 (2020-12-22)

- Fix issue in `askanna init` which now generates a valid `askanna.yml` project config file
- Improvements regarding feedback and error messages when something goes wrong
- Fix issues regarding generating AskAnna config file

## 0.4.1 (2020-12-01)

- Use Python to create a tmp directory so it works on all Python supported platforms

## 0.4.0 (2020-11-26)

- Adding variable management for CLI
- Drop support for Python 3.5 because we use `dataclasses`
- Reorganisation of CLI setup in the code base to prepare for SDK development
- Reorganize how authentication and requests are made for all API communication
- Adding logout for CLI

## 0.3.1 (2020-10-23)

- Improve artifact download to be more reliable in case of download failures

## 0.3.0 (2020-07-31)

- Changed `askanna artifact` to `askanna artifact add`
- Adding `askanna artifact get`
- Adding `askanna variable list` to get a list of variables in askanna
- Adding `askanna variable change` to modify the value of a variable

## 0.2.0 (2020-07-23)

- A default confirm question to confirm that you want to replace the current code package
- Added `askanna push --force` to skip the confirm question
- Added an optional argument to push add a message `askanna push -m "push message"`
- If no push messages provided, but a commit message is available, use the last commit message
- Changing how .askanna.yml is created
- Adding AskAnna functions for running in job
- Adding first test to check on push-target
- Download payload with CLI

## 0.1.0 (2019-12-05)

- First commit to repo
- Basic function to do `askanna login`
- First version of AskAnna code package
