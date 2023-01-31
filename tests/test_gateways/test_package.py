from pathlib import Path

import pytest

from askanna.core.exceptions import GetError
from askanna.gateways.package import PackageGateway


@pytest.mark.usefixtures("api_response")
class TestGatewayPackage:
    def test_list_packages(self):
        result = PackageGateway().list()
        assert len(result.packages) == 1

    def test_list_packages_project(self):
        project_suuid = "1234-1234-1234-1234"
        result = PackageGateway().list(project_suuid=project_suuid)
        assert len(result.packages) == 1

    def test_list_packages_limit_1(self):
        result = PackageGateway().list(page_size=1)
        assert len(result.packages) == 1

    def test_list_packages_not_found(self):
        with pytest.raises(GetError) as e:
            PackageGateway().list(cursor="999")

        assert "404 - Something went wrong while retrieving package list" in e.value.args[0]

    def test_list_packages_not_200(self):
        with pytest.raises(GetError) as e:
            PackageGateway().list(page_size=1, cursor="999")

        assert "500 - Something went wrong while retrieving package list" in e.value.args[0]

    def test_download_package(self, package_zip_file):
        package_suuid = "1234-1234-1234-1234"
        package = PackageGateway().download(package_suuid)

        assert package is not None
        assert package == package_zip_file

    def test_download_package_to_file(self, package_zip_file, temp_dir):
        package_suuid = "1234-1234-1234-1234"
        package_path = str(temp_dir) + "/artifact-1233/test.zip"
        package = PackageGateway().download(package_suuid, package_path)

        assert package is None
        assert Path(package_path).exists()
        assert Path(package_path).is_file()
        assert Path(package_path).read_bytes() == package_zip_file

    def test_download_package_not_found(self):
        package_suuid = "wxyz-wxyz-wxyz-wxyz"
        with pytest.raises(GetError) as e:
            PackageGateway().download(package_suuid)

        assert e.value.args[0] == f"404 - Package SUUID '{package_suuid}' was not found"

    def test_download_package_not_200(self):
        package_suuid = "zyxw-zyxw-zyxw-zyxw"
        with pytest.raises(GetError) as e:
            PackageGateway().download(package_suuid)

        assert f"500 - Something went wrong while retrieving the package SUUID '{package_suuid}'" in e.value.args[0]
