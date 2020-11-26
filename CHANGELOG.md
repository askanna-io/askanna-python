# History

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
