from askanna.core.dataclasses.variable import Variable
from tests.utils import str_to_datetime


def test_variable(variable_detail):
    variable = Variable.from_dict(variable_detail.copy())

    assert variable.suuid == variable_detail["suuid"]
    assert variable.name == variable_detail["name"]
    assert variable.value == variable_detail["value"]
    assert variable.is_masked == variable_detail["is_masked"]
    assert variable.project.suuid == variable_detail["project"]["suuid"]
    assert variable.workspace.suuid == variable_detail["workspace"]["suuid"]
    assert variable.created_at == str_to_datetime(variable_detail["created_at"])
    assert variable.modified_at == str_to_datetime(variable_detail["modified_at"])
