import pytest

from askanna.core.exceptions import CreateError, DeleteError, GetError, PatchError
from askanna.gateways.project import ProjectGateway


@pytest.mark.usefixtures("api_response")
class TestGatewayProject:
    def test_project_list(self):
        project_gateway = ProjectGateway()
        result = project_gateway.list()

        assert len(result.projects) == 1
        assert result.projects[0].name == "a project"

    def test_project_list_cursor(self):
        project_gateway = ProjectGateway()
        result = project_gateway.list(page_size=1, cursor="123")

        assert len(result.projects) == 1
        assert result.projects[0].name == "a new project"

    def test_project_list_error(self):
        project_gateway = ProjectGateway()
        with pytest.raises(GetError) as e:
            project_gateway.list(cursor="999")

        assert (
            "500 - Something went wrong while retrieving the project list:\n  {'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_project_list_workspace(self):
        project_gateway = ProjectGateway()
        result = project_gateway.list(workspace_suuid="1234-1234-1234-1234")

        assert len(result.projects) == 1
        assert result.projects[0].name == "a project"

    def test_project_detail(self):
        project_gateway = ProjectGateway()
        result = project_gateway.detail("1234-1234-1234-1234")

        assert result.name == "a project"

    def test_project_detail_not_found(self):
        project_gateway = ProjectGateway()
        with pytest.raises(GetError) as e:
            project_gateway.detail("7890-7890-7890-7890")

        assert "404 - The project SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_project_detail_error(self):
        project_gateway = ProjectGateway()
        with pytest.raises(GetError) as e:
            project_gateway.detail("0987-0987-0987-0987")

        assert (
            "500 - Something went wrong while retrieving project SUUID '0987-0987-0987-0987': "
            + "{'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_project_create(self):
        project_gateway = ProjectGateway()
        result = project_gateway.create(
            workspace_suuid="1234-1234-1234-1234",
            name="a new project",
            description="description new project",
            visibility="PUBLIC",
        )

        assert result.name == "a new project"

    def test_project_create_wrong_visibility(self):
        project_gateway = ProjectGateway()
        with pytest.raises(ValueError) as e:
            project_gateway.create(workspace_suuid="1234-1234-1234-1234", name="a new project", visibility="PUB")

        assert "Visibility must be either PUBLIC or PRIVATE" in e.value.args[0]

    def test_project_create_error(self):
        project_gateway = ProjectGateway()
        with pytest.raises(CreateError) as e:
            project_gateway.create(workspace_suuid="1234-1234-1234-1234", name="project with error")

        assert (
            "500 - Something went wrong while creating the project: {'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_project_change_no_changes(self):
        project_gateway = ProjectGateway()
        with pytest.raises(ValueError) as e:
            project_gateway.change("1234-1234-1234-1234")

        assert "At least one of the parameters 'name', 'description' or 'visibility' must be set" in e.value.args[0]

    def test_project_change(self):
        project_gateway = ProjectGateway()
        result = project_gateway.change("1234-1234-1234-1234", name="new name")

        assert result.name == "new name"

    def test_project_change_wrong_visibility(self):
        project_gateway = ProjectGateway()
        with pytest.raises(ValueError) as e:
            project_gateway.change("1234-1234-1234-1234", visibility="PUB")

        assert "Visibility must be either PUBLIC or PRIVATE" in e.value.args[0]

    def test_project_change_error(self):
        project_gateway = ProjectGateway()
        with pytest.raises(PatchError) as e:
            project_gateway.change("0987-0987-0987-0987", name="new name")

        assert "500 - Something went wrong while updating the project SUUID '0987-0987-0987-0987'" in e.value.args[0]

    def test_project_delete(self):
        project_gateway = ProjectGateway()
        result = project_gateway.delete("1234-1234-1234-1234")

        assert result is True

    def test_project_delete_not_found(self):
        project_gateway = ProjectGateway()
        with pytest.raises(DeleteError) as e:
            project_gateway.delete("7890-7890-7890-7890")

        assert "404 - The project SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_project_delete_error(self):
        project_gateway = ProjectGateway()
        with pytest.raises(DeleteError) as e:
            project_gateway.delete("0987-0987-0987-0987")

        assert "500 - Something went wrong while deleting the project SUUID '0987-0987-0987-0987'" in e.value.args[0]
