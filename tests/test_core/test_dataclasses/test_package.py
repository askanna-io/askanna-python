from askanna.core.dataclasses.package import Package
from tests.utils import str_to_datetime


def test_package(package_detail_for_list):
    package = Package.from_dict(package_detail_for_list.copy())

    assert package.suuid == package_detail_for_list["suuid"]
    assert package.name == package_detail_for_list["name"]
    assert package.description == package_detail_for_list["description"]
    assert package.created_at == str_to_datetime(package_detail_for_list["created_at"])
    assert package.modified_at == str_to_datetime(package_detail_for_list["modified_at"])
