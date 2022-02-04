# History

## 0.14.1 (2022-02-04)

- Added login argument 'url' making it possible to log in on different AskAnna environments using the web URL
- Fix: after successful login, you now get a success message i.s.o. a fail message
- Updated AA_REMOTE and tests to align with new config setup

## 0.14.0 (2021-11-22)

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
  [More info in the documentation.](http://docs.askanna.io/jobs/run-job/)
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
