import pytest

from askanna.core.exceptions import GetError
from askanna.sdk.job import JobSDK


@pytest.mark.usefixtures("api_response")
class TestSDKJob:
    def test_job_list(self):
        job_sdk = JobSDK()
        result = job_sdk.list()

        assert len(result) == 1
        assert result[0].name == "a job"

    def test_job_get(self):
        job_sdk = JobSDK()
        result = job_sdk.get("1234-1234-1234-1234")

        assert result.name == "a job"

    def test_job_get_not_found(self):
        job_sdk = JobSDK()
        with pytest.raises(GetError) as e:
            job_sdk.get("7890-7890-7890-7890")

        assert "404 - The job SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_job_get_by_name(self):
        job_sdk = JobSDK()
        result = job_sdk.get_job_by_name("a job")

        assert result.name == "a job"

    def test_job_get_by_name_not_found(self):
        job_sdk = JobSDK()
        with pytest.raises(GetError) as e:
            job_sdk.get_job_by_name("job that does not exist")

        assert "A job with this name is not available. Did you push your code?" in e.value.args[0]

    def test_job_get_by_name_multiple_found(self):
        job_sdk = JobSDK()
        with pytest.raises(GetError) as e:
            job_sdk.get_job_by_name("a job", project_suuid="abcd-abcd-abcd-abcd")

        assert (
            "There are multiple jobs with the same name. This could happen if you changed names of the job manually. "
            "Please make sure the job names are unique." in e.value.args[0]
        )

    def test_job_change(self):
        job_sdk = JobSDK()
        result = job_sdk.change("1234-1234-1234-1234", name="new name")

        assert result.name == "new name"

    def test_job_delete(self):
        job_sdk = JobSDK()
        result = job_sdk.delete("1234-1234-1234-1234")

        assert result is True
