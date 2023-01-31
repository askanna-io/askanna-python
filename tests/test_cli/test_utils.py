import io

import pytest
import responses

from askanna.cli import utils
from askanna.config import config
from askanna.config.api_url import askanna_url
from askanna.core.dataclasses.job import Job
from askanna.core.dataclasses.project import Project
from askanna.core.dataclasses.run import Run
from askanna.core.dataclasses.variable import Variable
from askanna.core.dataclasses.workspace import Workspace


class TestCliAskWhichWorkspace:
    @pytest.mark.usefixtures("api_response")
    def test_ask_which_workspace(self):
        result = utils.ask_which_workspace()
        assert type(result) == Workspace
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    def test_ask_which_workspace_no_response(self):
        responses.get(
            url=f"{askanna_url.workspace.workspace_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={"count": 0, "next": None, "previous": None, "results": []},
        )

        with pytest.raises(SystemExit):
            utils.ask_which_workspace()

    @responses.activate
    @pytest.mark.usefixtures("workspace_detail")
    def test_ask_which_workspace_ask_multiple(self, workspace_detail, monkeypatch):
        responses.get(
            url=f"{askanna_url.workspace.workspace_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [workspace_detail, workspace_detail],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_workspace()

        assert type(result) == Workspace
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    @pytest.mark.usefixtures("workspace_detail")
    def test_ask_which_workspace_long_list(self, workspace_detail, monkeypatch, capsys):
        responses.get(
            url=f"{askanna_url.workspace.workspace_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 100,
                "next": None,
                "previous": None,
                "results": [workspace_detail for _ in range(100)],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_workspace()
        captured = capsys.readouterr()

        assert type(result) == Workspace
        assert result.suuid == "1234-1234-1234-1234"

        assert "Note: the 99 most recent workspaces of 100 workspaces are in the list." in captured.out


class TestCliAskWhichProject:
    @pytest.mark.usefixtures("api_response")
    def test_ask_which_project(self):
        result = utils.ask_which_project()
        assert type(result) == Project
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    def test_ask_which_project_no_response(self):
        responses.get(
            url=f"{askanna_url.project.project_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={"count": 0, "next": None, "previous": None, "results": []},
        )

        with pytest.raises(SystemExit):
            utils.ask_which_project()

    @responses.activate
    @pytest.mark.usefixtures("project_detail")
    def test_ask_which_project_ask_multiple(self, project_detail, monkeypatch):
        responses.get(
            url=f"{askanna_url.project.project_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 0,
                "next": None,
                "previous": None,
                "results": [project_detail, project_detail],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_project()

        assert type(result) == Project
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    @pytest.mark.usefixtures("project_detail")
    def test_ask_which_project_long_list(self, project_detail, monkeypatch, capsys):
        responses.get(
            url=f"{askanna_url.project.project_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 100,
                "next": None,
                "previous": None,
                "results": [project_detail for _ in range(100)],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_project()
        captured = capsys.readouterr()

        assert type(result) == Project
        assert result.suuid == "1234-1234-1234-1234"

        assert "Note: the 99 most recent projects of 100 projects are in the list." in captured.out


class TestCliAskWhichJob:
    @pytest.mark.usefixtures("api_response")
    def test_ask_which_job(self):
        result = utils.ask_which_job()
        assert type(result) == Job
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    def test_ask_which_job_no_response(self):
        responses.get(
            url=f"{askanna_url.job.job_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={"count": 0, "next": None, "previous": None, "results": []},
        )

        with pytest.raises(SystemExit):
            utils.ask_which_job()

    @responses.activate
    @pytest.mark.usefixtures("job_detail")
    def test_ask_which_job_ask_multiple(self, job_detail, monkeypatch):
        responses.get(
            url=f"{askanna_url.job.job_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 0,
                "next": None,
                "previous": None,
                "results": [job_detail, job_detail],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_job()

        assert type(result) == Job
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    @pytest.mark.usefixtures("job_detail")
    def test_ask_which_job_long_list(self, job_detail, monkeypatch, capsys):
        responses.get(
            url=f"{askanna_url.job.job_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 100,
                "next": None,
                "previous": None,
                "results": [job_detail for _ in range(100)],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_job()
        captured = capsys.readouterr()

        assert type(result) == Job
        assert result.suuid == "1234-1234-1234-1234"

        assert "Note: the 99 most recent jobs of 100 jobs are in the list." in captured.out


class TestCliAskWhichRun:
    @pytest.mark.usefixtures("api_response")
    def test_ask_which_run(self):
        result = utils.ask_which_run()
        assert type(result) == Run
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    def test_ask_which_run_no_response(self):
        responses.get(
            url=f"{askanna_url.run.run_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={"count": 0, "next": None, "previous": None, "results": []},
        )

        with pytest.raises(SystemExit):
            utils.ask_which_run()

    @responses.activate
    @pytest.mark.usefixtures("run_detail")
    def test_ask_which_run_ask_multiple(self, run_detail, monkeypatch):
        responses.get(
            url=f"{askanna_url.run.run_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 0,
                "next": None,
                "previous": None,
                "results": [run_detail, run_detail],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_run()

        assert type(result) == Run
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    @pytest.mark.usefixtures("run_detail")
    def test_ask_which_run_long_list(self, run_detail, monkeypatch, capsys):
        responses.get(
            url=f"{askanna_url.run.run_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 100,
                "next": None,
                "previous": None,
                "results": [run_detail for _ in range(100)],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_run()
        captured = capsys.readouterr()

        assert type(result) == Run
        assert result.suuid == "1234-1234-1234-1234"

        assert "Note: the 99 most recent runs of 100 runs are in the list." in captured.out


class TestCliAskWhichVariable:
    @responses.activate
    @pytest.mark.usefixtures("variable_detail")
    def test_ask_which_variable(self, variable_detail):
        responses.get(
            url=f"{askanna_url.variable.variable_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={"count": 1, "next": None, "previous": None, "results": [variable_detail]},
        )
        result = utils.ask_which_variable()
        assert type(result) == Variable
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    def test_ask_which_variable_no_response(self):
        responses.get(
            url=f"{askanna_url.variable.variable_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={"count": 0, "next": None, "previous": None, "results": []},
        )

        with pytest.raises(SystemExit):
            utils.ask_which_variable()

    @responses.activate
    @pytest.mark.usefixtures("variable_detail")
    def test_ask_which_variable_ask_multiple(self, variable_detail, monkeypatch):
        responses.get(
            url=f"{askanna_url.variable.variable_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 0,
                "next": None,
                "previous": None,
                "results": [variable_detail, variable_detail],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_variable()

        assert type(result) == Variable
        assert result.suuid == "1234-1234-1234-1234"

    @responses.activate
    @pytest.mark.usefixtures("variable_detail")
    def test_ask_which_variable_long_list(self, variable_detail, monkeypatch, capsys):
        responses.get(
            url=f"{askanna_url.variable.variable_list()}?page_size=99",
            status=200,
            content_type="application/json",
            json={
                "count": 100,
                "next": None,
                "previous": None,
                "results": [variable_detail for _ in range(100)],
            },
        )

        monkeypatch.setattr("sys.stdin", io.StringIO("1"))
        result = utils.ask_which_variable()
        captured = capsys.readouterr()

        assert type(result) == Variable
        assert result.suuid == "1234-1234-1234-1234"

        assert "Note: the 99 most recent variables of 100 variables are in the list." in captured.out


@pytest.mark.usefixtures("api_response")
class TestCliUtilsDetermineProjectForRunRequest:
    def test_determine_project(self):
        result = utils.determine_project_for_run_request("1234-1234-1234-1234")
        assert type(result) == Project
        assert result.suuid == "1234-1234-1234-1234"

    def test_determine_project_no_project_suuid(self):
        result = utils.determine_project_for_run_request()
        assert type(result) == Project
        assert result.suuid == "1234-1234-1234-1234"


class TestCliMakeOptionListStringForQuestion:
    def test_make_option_list_string_for_question(self):
        variable = Variable(
            suuid="1234-1234-1234-1234",
            name="test",
            value=None,  # type: ignore
            is_masked=None,  # type: ignore
            project=None,  # type: ignore
            workspace=None,  # type: ignore
            created=None,  # type: ignore
            modified=None,  # type: ignore
        )
        result = utils.make_option_list_string_for_question([variable])
        assert result == "1. test\n"

    def test_make_option_list_string_for_question_with_suuid(self):
        variable = Variable(
            suuid="1234-1234-1234-1234",
            name="test",
            value=None,  # type: ignore
            is_masked=None,  # type: ignore
            project=None,  # type: ignore
            workspace=None,  # type: ignore
            created=None,  # type: ignore
            modified=None,  # type: ignore
        )
        result = utils.make_option_list_string_for_question([variable], name_with_suuid=True)
        assert result == "1. test (1234-1234-1234-1234)\n"

    def test_make_option_list_string_for_question_more_then_10(self):
        variables = [
            Variable(
                suuid="1234-1234-1234-1234",
                name="test",
                value=None,  # type: ignore
                is_masked=None,  # type: ignore
                project=None,  # type: ignore
                workspace=None,  # type: ignore
                created=None,  # type: ignore
                modified=None,  # type: ignore
            )
            for _ in range(10)
        ]
        result = utils.make_option_list_string_for_question(variables)
        assert "1.  test\n" in result
        assert "10. test\n" in result


@pytest.mark.usefixtures("api_response")
class TestJobRunRequest:
    def test_job_run_request(self, capsys):
        utils.job_run_request(job_suuid="1234-1234-1234-1234")
        captured = capsys.readouterr()
        assert "Succesfully started a new run for job 'a job'" in captured.out

    def test_job_run_request_fail(self, capsys):
        with pytest.raises(SystemExit):
            utils.job_run_request(job_suuid="7890-7890-7890-7890")
        captured = capsys.readouterr()
        assert "500 - Something went wrong while starting the run for job SUUID '7890-7890-7890-7890'" in captured.out

    def test_job_run_request_determine_job(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("y"))
        utils.job_run_request()
        captured = capsys.readouterr()
        assert "Succesfully started a new run for job 'a job'" in captured.out

    def test_job_run_request_determine_job_abort_run(self, capsys, monkeypatch):
        monkeypatch.setattr("sys.stdin", io.StringIO("n"))
        with pytest.raises(SystemExit):
            utils.job_run_request()
        captured = capsys.readouterr()
        assert "Aborted! Not running job 'a job'." in captured.out

    def test_job_run_request_job_name(self, capsys):
        utils.job_run_request(job_name="a job")
        captured = capsys.readouterr()
        assert "Succesfully started a new run for job 'a job'" in captured.out

    def test_job_run_request_wrong_job_name(self, capsys):
        with pytest.raises(SystemExit):
            utils.job_run_request(job_name="a wrong job")

    def test_job_run_request_with_data(self, capsys):
        utils.job_run_request(job_suuid="1234-1234-1234-1234", data="{}")
        captured = capsys.readouterr()
        assert "Succesfully started a new run for job 'a job'" in captured.out

    def test_job_run_request_with_data_file(self, capsys):
        utils.job_run_request(job_suuid="1234-1234-1234-1234", data_file="tests/fixtures/files/result.json")
        captured = capsys.readouterr()
        assert "Succesfully started a new run for job 'a job'" in captured.out

    def test_job_run_request_with_data_file_no_dict(self, capsys):
        with pytest.raises(SystemExit):
            utils.job_run_request(
                job_suuid="1234-1234-1234-1234", data_file="tests/fixtures/projects/project-001-simple/result.json"
            )
        captured = capsys.readouterr()
        assert "The data cannot be processes becaused it's not in a JSON format" in captured.err

    def test_job_run_request_with_data_and_data_file(self, capsys):
        with pytest.raises(SystemExit):
            utils.job_run_request(
                job_suuid="1234-1234-1234-1234", data="{}", data_file="tests/fixtures/files/result.json"
            )
        captured = capsys.readouterr()
        assert "Cannot use both --data and --data-file." in captured.err

    def test_job_run_request_with_push(self, capsys):
        config.project.project_config_path = "tests/fixtures/projects/project-001-simple/askanna.yml"
        config.project.project_suuid = "1234-1234-1234-1234"
        utils.job_run_request(job_suuid="1234-1234-1234-1234", push_code=True)
        captured = capsys.readouterr()
        assert "Succesfully started a new run for job 'a job'" in captured.out
