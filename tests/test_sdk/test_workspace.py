import pytest

from askanna.core.exceptions import GetError
from askanna.sdk.workspace import WorkspaceSDK


@pytest.mark.usefixtures("api_response")
class TestWorkspaceSDK:
    def test_workspace_list(self):
        workspace_sdk = WorkspaceSDK()
        result = workspace_sdk.list()

        assert len(result) == 1
        assert result[0].name == "test-workspace"

    def test_workspace_get(self):
        workspace_sdk = WorkspaceSDK()
        result = workspace_sdk.get("1234-1234-1234-1234")

        assert result.name == "test-workspace"

    def test_workspace_get_not_found(self):
        workspace_sdk = WorkspaceSDK()
        with pytest.raises(GetError) as e:
            workspace_sdk.get("7890-7890-7890-7890")

        assert "404 - The workspace SUUID '7890-7890-7890-7890' was not found" in e.value.args[0]

    def test_workspace_create(self):
        workspace_sdk = WorkspaceSDK()
        result = workspace_sdk.create(
            name="a new workspace", description="description new workspace", visibility="PUBLIC"
        )

        assert result.name == "a new workspace"

    def test_workspace_change(self):
        workspace_sdk = WorkspaceSDK()
        result = workspace_sdk.change("1234-1234-1234-1234", name="new name")

        assert result.name == "new name"

    def test_workspace_delete(self):
        workspace_sdk = WorkspaceSDK()
        result = workspace_sdk.delete("1234-1234-1234-1234")
        assert result is True
