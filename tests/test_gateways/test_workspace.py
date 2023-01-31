import pytest

from askanna.core.exceptions import CreateError, DeleteError, GetError, PatchError
from askanna.gateways.workspace import WorkspaceGateway


@pytest.mark.usefixtures("api_response")
class TestGatewayWorkspace:
    def test_workspace_list(self):
        workspace_gateway = WorkspaceGateway()
        result = workspace_gateway.list()

        assert len(result.workspaces) == 1
        assert result.workspaces[0].name == "test-workspace"

    def test_workspace_list_cursor(self):
        workspace_gateway = WorkspaceGateway()
        result = workspace_gateway.list(page_size=1, cursor="123")

        assert len(result.workspaces) == 1
        assert result.workspaces[0].name == "a new workspace"

    def test_workspace_list_error(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(GetError) as e:
            workspace_gateway.list(cursor="999")

        assert (
            "500 - Something went wrong while retrieving the workspace list:\n  {'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_workspace_detail(self):
        workspace_gateway = WorkspaceGateway()
        result = workspace_gateway.detail("1234-1234-1234-1234")

        assert result.name == "test-workspace"

    def test_workspace_detail_not_found(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(GetError) as e:
            workspace_gateway.detail("7890-7890-7890-7890")

        assert "404 - The workspace SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_workspace_detail_error(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(GetError) as e:
            workspace_gateway.detail("0987-0987-0987-0987")

        assert (
            "500 - Something went wrong while retrieving workspace SUUID '0987-0987-0987-0987': "
            + "{'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_workspace_create(self):
        workspace_gateway = WorkspaceGateway()
        result = workspace_gateway.create(
            name="a new workspace", description="description new workspace", visibility="PUBLIC"
        )

        assert result.name == "a new workspace"

    def test_workspace_create_wrong_visibility(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(ValueError) as e:
            workspace_gateway.create(name="a new workspace", visibility="PUB")

        assert "Visibility must be either PUBLIC or PRIVATE" in e.value.args[0]

    def test_workspace_create_error(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(CreateError) as e:
            workspace_gateway.create(name="workspace with error")

        assert (
            "500 - Something went wrong while creating the workspace: {'error': 'Internal Server Error'}"
            in e.value.args[0]
        )

    def test_workspace_change_no_changes(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(ValueError) as e:
            workspace_gateway.change("1234-1234-1234-1234")

        assert "At least one of the parameters 'name', 'description' or 'visibility' must be set" in e.value.args[0]

    def test_workspace_change(self):
        workspace_gateway = WorkspaceGateway()
        result = workspace_gateway.change("1234-1234-1234-1234", name="new name")

        assert result.name == "new name"

    def test_workspace_change_wrong_visibility(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(ValueError) as e:
            workspace_gateway.change("1234-1234-1234-1234", visibility="PUB")

        assert "Visibility must be either PUBLIC or PRIVATE" in e.value.args[0]

    def test_workspace_change_error(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(PatchError) as e:
            workspace_gateway.change("0987-0987-0987-0987", name="new name")

        assert "500 - Something went wrong while updating the workspace SUUID '0987-0987-0987-0987'" in e.value.args[0]

    def test_workspace_delete(self):
        workspace_gateway = WorkspaceGateway()
        result = workspace_gateway.delete("1234-1234-1234-1234")

        assert result is True

    def test_workspace_delete_not_found(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(DeleteError) as e:
            workspace_gateway.delete("7890-7890-7890-7890")

        assert "404 - The workspace SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_workspace_delete_error(self):
        workspace_gateway = WorkspaceGateway()
        with pytest.raises(DeleteError) as e:
            workspace_gateway.delete("0987-0987-0987-0987")

        assert "500 - Something went wrong while deleting the workspace SUUID '0987-0987-0987-0987'" in e.value.args[0]
