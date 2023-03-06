import datetime

from askanna.core.dataclasses.base import Label, MembershipRole, User


def test_label():
    label = Label(name="test name", value="test value", type="string")

    assert label.name == "test name"
    assert str(label) == "test name: test value [type: string]"
    assert label.to_dict() == {"name": "test name", "value": "test value", "type": "string"}


def test_user():
    user = User(
        suuid="test suuid",
        name="test name",
        email="test email",
        is_active=True,
        date_joined=datetime.datetime.now(),
        last_login=datetime.datetime.now(),
    )

    assert user.suuid == "test suuid"
    assert user.name == "test name"
    assert type(user.date_joined) == datetime.datetime
    assert type(user.last_login) == datetime.datetime


def test_membership_role():
    membership_role = MembershipRole(name="test name", code="test code")

    assert membership_role.name == "test name"
    assert membership_role.code == "test code"
