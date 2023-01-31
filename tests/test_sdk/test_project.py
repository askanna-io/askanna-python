import pytest

from askanna.core.exceptions import GetError
from askanna.sdk.project import ProjectSDK


@pytest.mark.usefixtures("api_response")
class TestProjectSDK:
    def test_project_list(self):
        project_sdk = ProjectSDK()
        result = project_sdk.list()

        assert len(result) == 1
        assert result[0].name == "a project"

    def test_project_get(self):
        project_sdk = ProjectSDK()
        result = project_sdk.get("1234-1234-1234-1234")

        assert result.name == "a project"

    def test_project_get_not_found(self):
        project_sdk = ProjectSDK()
        with pytest.raises(GetError) as e:
            project_sdk.get("7890-7890-7890-7890")

        assert "404 - The project SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_project_create(self):
        project_sdk = ProjectSDK()
        result = project_sdk.create(
            workspace_suuid="1234-1234-1234-1234",
            name="a new project",
            description="description new project",
            visibility="PUBLIC",
        )

        assert result.name == "a new project"

    def test_project_change(self):
        project_sdk = ProjectSDK()
        result = project_sdk.change("1234-1234-1234-1234", name="new name")

        assert result.name == "new name"

    def test_project_delete(self):
        project_sdk = ProjectSDK()
        result = project_sdk.delete("1234-1234-1234-1234")

        assert result is True
