import pytest

from askanna.config.api_url import askanna_url
from askanna.core.exceptions import PostError
from askanna.core.upload import ArtifactUpload, PackageUpload, ResultUpload, Upload


class TestUploadInit:
    def test_upload_init(self):
        upload = Upload()

        assert upload is not None
        assert upload.suuid is None
        assert upload.resumable_file is None
        assert upload.message_upload_success == "File is uploaded"
        assert upload.message_upload_fail == "File upload failed"
        assert type(upload.chunk_dict_template) == dict

        with pytest.raises(NotImplementedError):
            assert upload.register_upload_url() is None
        with pytest.raises(NotImplementedError):
            assert upload.register_chunk_url() is None
        with pytest.raises(NotImplementedError):
            assert upload.upload_chunk_url(chunk_uuid="ab-ab-ab-ab") is None
        with pytest.raises(NotImplementedError):
            assert upload.finish_upload_url() is None

        with pytest.raises(NotImplementedError):
            upload.upload("tests/fixtures/files/zip_file.zip")

    def test_package_upload_init(self):
        project_suuid = "1234-1234-1234-1234"

        chunk_uuid = "efgh-efgh-efgh-efgh"

        upload = PackageUpload(project_suuid)

        assert upload is not None
        assert upload.suuid is None
        assert upload.resumable_file is None
        assert upload.message_upload_success == "Package is uploaded"
        assert upload.message_upload_fail == "Package upload failed"
        assert type(upload.chunk_dict_template) == dict
        assert upload.entry_extrafields == {"project_suuid": project_suuid, "description": None}

        assert upload.register_upload_url() == askanna_url.package.base_package_url
        with pytest.raises(TypeError):
            upload.register_chunk_url()
        with pytest.raises(TypeError):
            upload.upload_chunk_url(chunk_uuid)
        with pytest.raises(TypeError):
            upload.finish_upload_url()

    def test_package_upload_init_fail(self):
        with pytest.raises(TypeError):
            PackageUpload()  # type: ignore

    def test_artifact_upload_init(self):
        run_suuid = "1234-1234-1234-1234"
        chunk_uuid = "efgh-efgh-efgh-efgh"

        upload = ArtifactUpload(run_suuid)

        assert upload is not None
        assert upload.suuid is None
        assert upload.resumable_file is None
        assert upload.message_upload_success == "Artifact is uploaded"
        assert upload.message_upload_fail == "Artifact upload failed"
        assert type(upload.chunk_dict_template) == dict

        assert upload.register_upload_url() == askanna_url.run.artifact_list(run_suuid)
        with pytest.raises(TypeError):
            upload.register_chunk_url()
        with pytest.raises(TypeError):
            upload.upload_chunk_url(chunk_uuid)
        with pytest.raises(TypeError):
            upload.finish_upload_url()

    def test_artifact_upload_init_fail(self):
        with pytest.raises(TypeError):
            ArtifactUpload()  # type: ignore

    def test_result_upload_init(self):
        run_suuid = "1234-1234-1234-1234"
        chunk_uuid = "efgh-efgh-efgh-efgh"

        upload = ResultUpload(run_suuid)

        assert upload is not None
        assert upload.suuid is None
        assert upload.resumable_file is None
        assert upload.message_upload_success == "Result is uploaded"
        assert upload.message_upload_fail == "Result upload failed"
        assert type(upload.chunk_dict_template) == dict

        assert upload.register_upload_url() == askanna_url.run.result_upload(run_suuid)
        with pytest.raises(TypeError):
            upload.register_chunk_url()
        with pytest.raises(TypeError):
            upload.upload_chunk_url(chunk_uuid)
        with pytest.raises(TypeError):
            upload.finish_upload_url()

    def test_result_upload_init_fail(self):
        with pytest.raises(TypeError):
            ResultUpload()  # type: ignore


@pytest.mark.usefixtures("api_response")
class TestUploadSuccess:
    def test_package_upload(self):
        project_suuid = "1234-1234-1234-1234"
        package_suuid = "abcd-abcd-abcd-abcd"

        upload = PackageUpload(project_suuid)

        assert upload is not None

        result = upload.upload("tests/fixtures/files/zip_file.zip")

        assert upload.suuid == package_suuid
        assert result == (True, "Package is uploaded")

    def test_package_upload_with_description(self):
        project_suuid = "1234-1234-1234-1234"
        package_suuid = "abcd-abcd-abcd-abcd"
        description = "This is a description"

        upload = PackageUpload(project_suuid, description)

        assert upload is not None
        assert upload.entry_extrafields == {"project_suuid": project_suuid, "description": description}

        result = upload.upload("tests/fixtures/files/zip_file.zip")

        assert upload.suuid == package_suuid
        assert result == (True, "Package is uploaded")

    def test_artifact_upload(self):
        run_suuid = "1234-1234-1234-1234"
        artifact_suuid = "abcd-abcd-abcd-abcd"

        upload = ArtifactUpload(run_suuid)

        assert upload is not None

        result = upload.upload("tests/fixtures/files/zip_file.zip")

        assert upload.suuid == artifact_suuid
        assert result == (True, "Artifact is uploaded")

    def test_result_upload(self):
        run_suuid = "1234-1234-1234-1234"
        result_suuid = "abcd-abcd-abcd-abcd"

        upload = ResultUpload(run_suuid)

        assert upload is not None

        result = upload.upload("tests/fixtures/files/zip_file.zip")

        assert upload.suuid == result_suuid
        assert result == (True, "Result is uploaded")


@pytest.mark.usefixtures("api_response")
class TestUploadFail:
    def test_artifact_upload_fail(self):
        run_suuid = "5678-5678-5678-5678"

        upload = ArtifactUpload(run_suuid)

        assert upload is not None

        with pytest.raises(PostError) as error:
            upload.upload("tests/fixtures/files/zip_file.zip")

        assert "In the AskAnna platform something went wrong with creating the upload entry:" in error.value.args[0]

    def test_result_upload_fail(self):
        run_suuid = "5678-5678-5678-5678"

        upload = ResultUpload(run_suuid)

        assert upload is not None

        with pytest.raises(PostError) as error:
            upload.upload("tests/fixtures/files/zip_file.zip")

        assert "In the AskAnna platform something went wrong with creating the upload entry" in error.value.args[0]
