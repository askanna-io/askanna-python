from datetime import datetime, timezone

from askanna.core.dataclasses.package import Package


def test_package(package_detail_for_list):
    package = Package.from_dict(package_detail_for_list.copy())

    assert package.suuid == package_detail_for_list["suuid"]
    assert package.name == package_detail_for_list["name"]
    assert package.description == package_detail_for_list["description"]
    assert package.created_at == datetime.strptime(
        package_detail_for_list["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=timezone.utc)
    assert package.modified_at == datetime.strptime(
        package_detail_for_list["modified_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=timezone.utc)
