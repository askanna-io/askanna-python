# History

## 0.6.0 (2020-02-03)

- Added push-and-run via `askanna run --push` where you first push your code and then trigger a run
- Installed gcc in the default image we run on AskAnna
- Added developer option to specicy on which AskAnna remote you want to login
- Changes in parameter names for Python SDK (run.status and variable modules). If you used the 0.5.x version of the
  AskAnna Python SDK this version can break your code.

## 0.5.1 (2020-01-27)

- Fix that you can run a job with name and additional options

## 0.5.0 (2020-01-26)

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
- Basic function to do askanna login
- First version of askanna package
