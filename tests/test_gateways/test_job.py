import pytest

from askanna.core.exceptions import DeleteError, GetError, PatchError
from askanna.gateways.job import JobGateway


@pytest.mark.usefixtures("api_response")
class TestGatewayJob:
    def test_job_list(self):
        job_gateway = JobGateway()
        result = job_gateway.list()

        assert len(result.jobs) == 1
        assert result.jobs[0].name == "a job"

    def test_job_list_cursor(self):
        job_gateway = JobGateway()
        result = job_gateway.list(page_size=1, cursor="123")

        assert len(result.jobs) == 1
        assert result.jobs[0].name == "a scheduled job"

    def test_job_list_error(self):
        job_gateway = JobGateway()
        with pytest.raises(GetError) as e:
            job_gateway.list(cursor="999")

        assert (
            "500 - Something went wrong while retrieving the job list:\n  {'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_job_list_project(self):
        job_gateway = JobGateway()
        result = job_gateway.list(project_suuid="1234-1234-1234-1234")

        assert len(result.jobs) == 1
        assert result.jobs[0].name == "a job"

    def test_job_detail(self):
        job_gateway = JobGateway()
        result = job_gateway.detail("1234-1234-1234-1234")

        assert result.name == "a job"

    def test_job_detail_not_found(self):
        job_gateway = JobGateway()
        with pytest.raises(GetError) as e:
            job_gateway.detail("7890-7890-7890-7890")

        assert "404 - The job SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_job_detail_error(self):
        job_gateway = JobGateway()
        with pytest.raises(GetError) as e:
            job_gateway.detail("0987-0987-0987-0987")

        assert (
            "500 - Something went wrong while retrieving job SUUID '0987-0987-0987-0987': "
            + "{'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_job_change_no_changes(self):
        job_gateway = JobGateway()
        with pytest.raises(ValueError) as e:
            job_gateway.change("1234-1234-1234-1234")

        assert "At least one of the parameters 'name' or 'description' must be set" in e.value.args[0]

    def test_job_change(self):
        job_gateway = JobGateway()
        result = job_gateway.change("1234-1234-1234-1234", name="new name")

        assert result.name == "new name"

    def test_job_change_error(self):
        job_gateway = JobGateway()
        with pytest.raises(PatchError) as e:
            job_gateway.change("0987-0987-0987-0987", name="new name")

        assert "500 - Something went wrong while updating the job SUUID '0987-0987-0987-0987'" in e.value.args[0]

    def test_job_delete(self):
        job_gateway = JobGateway()
        result = job_gateway.delete("1234-1234-1234-1234")

        assert result is True

    def test_job_delete_not_found(self):
        job_gateway = JobGateway()
        with pytest.raises(DeleteError) as e:
            job_gateway.delete("7890-7890-7890-7890")

        assert "404 - The job SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_project_delete_error(self):
        job_gateway = JobGateway()
        with pytest.raises(DeleteError) as e:
            job_gateway.delete("0987-0987-0987-0987")

        assert "500 - Something went wrong while deleting the job SUUID '0987-0987-0987-0987'" in e.value.args[0]
