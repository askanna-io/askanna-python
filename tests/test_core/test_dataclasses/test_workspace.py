from askanna.core.dataclasses.workspace import Workspace
from tests.utils import str_to_datetime


def test_workspace(workspace_detail):
    workspace = Workspace.from_dict(workspace_detail.copy())

    assert workspace.suuid == workspace_detail["suuid"]
    assert workspace.name == workspace_detail["name"]
    assert workspace.description == workspace_detail["description"]
    assert workspace.visibility == workspace_detail["visibility"]
    assert workspace.created_by.suuid == workspace_detail["created_by"]["suuid"]
    assert workspace.permission == workspace_detail["permission"]
    assert workspace.is_member == workspace_detail["is_member"]
    assert workspace.created_at == str_to_datetime(workspace_detail["created_at"])
    assert workspace.modified_at == str_to_datetime(workspace_detail["modified_at"])

    assert str(workspace) == "Workspace: test-workspace (1234-1234-1234-1234)"
