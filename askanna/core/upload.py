import io
import os
import sys

import click
import resumable

from . import client as askanna_client
from askanna.core.utils import _file_type, diskunit


class Upload:
    tpl_register_upload_url = "{ASKANNA_API_SERVER}package/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/packagechunk/"
    tpl_upload_chunk_url = (
        "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/packagechunk/{CHUNK_UUID}/chunk/"
    )
    tpl_final_upload_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/finish_upload/"

    tpl_upload_pass = "File is uploaded"
    tpl_upload_fail = "Upload failed"

    def __init__(self, api_server: str, *args, **kwargs):
        self.ASKANNA_API_SERVER = api_server
        self.suuid = None
        self.resumable_file = None
        self.kwargs = kwargs

    @property
    def chunk_baseinfo(self) -> dict:
        return {
            "resumableChunkSize": self.resumable_file.chunk_size,
            "resumableTotalSize": self.resumable_file.size,
            "resumableType": _file_type(self.resumable_file.path),
            "resumableIdentifier": str(self.resumable_file.unique_identifier),
            "resumableFilename": os.path.basename(self.resumable_file.path),
            "resumableRelativePath": self.resumable_file.path,
            "resumableTotalChunks": len(self.resumable_file.chunks),
            "resumableChunkNumber": 1,
            "resumableCurrentChunkSize": 1,
        }.copy()

    def url_template_arguments(self):
        """
        This method is meant to be overwritten by inheritors
        providing specific url templating variables
        """
        return {
            "ASKANNA_API_SERVER": self.ASKANNA_API_SERVER,
            "PACKAGE_SUUID": self.suuid,
        }

    @property
    def register_upload_url(self) -> str:
        return self.tpl_register_upload_url.format(**self.url_template_arguments())

    @property
    def register_chunk_url(self) -> str:
        return self.tpl_register_chunk_url.format(**self.url_template_arguments())

    def upload_chunk_url(self, chunk_uuid: str) -> str:
        arguments = self.url_template_arguments()
        arguments.update({"CHUNK_UUID": chunk_uuid})
        return self.tpl_upload_chunk_url.format(**arguments)

    @property
    def final_upload_url(self) -> str:
        return self.tpl_final_upload_url.format(**self.url_template_arguments())

    def upload(self, file_obj, config, fileinfo):
        self.create_entry(config=config, fileinfo=fileinfo)
        self.upload_file(file_obj)
        return self.finish_upload()

    def create_entry_extrafields(self):
        return {}

    def create_entry(self, config: dict = None, fileinfo: dict = {}) -> str:
        info_dict = {
            "filename": fileinfo.get("filename"),
            "size": fileinfo.get("size"),
        }

        info_dict.update(**self.create_entry_extrafields())

        # the request to AskAnna API
        req = askanna_client.post(self.register_upload_url, json=info_dict)
        if req.status_code != 201:
            click.echo(
                "In the AskAnna platform something went wrong with creating the upload entry.",
                err=True,
            )
            sys.exit(1)

        res = req.json()

        # the result
        self.suuid = res.get("short_uuid")
        return self.suuid

    def upload_chunk(self, chunk, chunk_dict):
        config = chunk_dict.copy()
        config.update(
            **{
                "filename": chunk.index + 1,
                "size": chunk.size,
                "file_no": chunk.index + 1,
                "is_last": len(self.resumable_file.chunks) == chunk.index + 1,
            }
        )

        # request chunk id from API
        req_chunk = askanna_client.post(self.register_chunk_url, json=config)
        chunk_uuid = req_chunk.json().get("uuid")

        files = {"file": io.BytesIO(chunk.read())}
        data = self.chunk_baseinfo
        data.update(
            **{
                "resumableChunkNumber": chunk.index + 1,
                "resumableCurrentChunkSize": chunk.size,
            }
        )

        specific_chunk_req = askanna_client.post(
            self.upload_chunk_url(chunk_uuid=chunk_uuid), data=data, files=files
        )
        assert specific_chunk_req.status_code == 200, "File could not be uploaded"

    def chunk_dict_template(self):
        return {
            "filename": "",
            "size": 0,
            "file_no": 0,
            "is_last": False,
        }

    def upload_file(self, file_obj):
        """
        Take a file_obj and make chunks out of it to upload
        """
        chunk_dict = self.chunk_dict_template()

        self.resumable_file = resumable.file.ResumableFile(file_obj, 1 * diskunit.MiB)
        for chunk in self.resumable_file.chunks:
            self.upload_chunk(chunk, chunk_dict)

    def finish_upload(self):
        # Do final call when all chunks are uploaded
        final_call_dict = self.chunk_baseinfo

        final_call_req = askanna_client.post(
            self.final_upload_url, data=final_call_dict
        )

        if final_call_req.status_code == 200:
            return True, self.tpl_upload_pass
        else:
            return False, self.tpl_upload_fail


class PackageUpload(Upload):
    tpl_register_upload_url = "{ASKANNA_API_SERVER}package/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/packagechunk/"
    tpl_upload_chunk_url = (
        "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/packagechunk/{CHUNK_UUID}/chunk/"
    )
    tpl_final_upload_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/finish_upload/"

    tpl_upload_pass = "Package is uploaded"
    tpl_upload_fail = "Package upload failed"

    def create_entry_extrafields(self):
        return {
            "project": self.kwargs.get("project_suuid"),
            "description": self.kwargs.get("description"),
        }


class ArtifactUpload(Upload):
    tpl_register_upload_url = "{ASKANNA_API_SERVER}jobrun/{RUN_SUUID}/artifact/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}jobrun/{RUN_SUUID}/artifact/{ARTIFACT_SUUID}/artifactchunk/"
    tpl_upload_chunk_url = "{ASKANNA_API_SERVER}jobrun/{RUN_SUUID}/artifact/{ARTIFACT_SUUID}/artifactchunk/{CHUNK_UUID}/chunk/"  # noqa
    tpl_final_upload_url = "{ASKANNA_API_SERVER}jobrun/{RUN_SUUID}/artifact/{ARTIFACT_SUUID}/finish_upload/"

    tpl_upload_pass = "Artifact is uploaded"
    tpl_upload_fail = "Artifact upload failed"

    def url_template_arguments(self):
        """
        This method is meant to be overwritten by inheritors
        providing specific url templating variables
        """
        return {
            "ASKANNA_API_SERVER": self.ASKANNA_API_SERVER,
            "ARTIFACT_SUUID": self.suuid,
            "RUN_SUUID": self.kwargs.get("run_suuid"),
        }


class ResultUpload(Upload):
    tpl_register_upload_url = "{ASKANNA_API_SERVER}jobrun/{RUN_SUUID}/result/"
    tpl_register_chunk_url = (
        "{ASKANNA_API_SERVER}jobrun/{RUN_SUUID}/result/{RESULT_SUUID}/resultchunk/"
    )
    tpl_upload_chunk_url = "{ASKANNA_API_SERVER}jobrun/{RUN_SUUID}/result/{RESULT_SUUID}/resultchunk/{CHUNK_UUID}/chunk/"  # noqa
    tpl_final_upload_url = (
        "{ASKANNA_API_SERVER}jobrun/{RUN_SUUID}/result/{RESULT_SUUID}/finish_upload/"
    )

    tpl_upload_pass = "Result is uploaded"
    tpl_upload_fail = "Result upload failed"

    def url_template_arguments(self):
        return {
            "ASKANNA_API_SERVER": self.ASKANNA_API_SERVER,
            "RUN_SUUID": self.kwargs.get("RUN_SUUID"),
            "RESULT_SUUID": self.kwargs.get("RESULT_SUUID"),
        }

    def create_entry(self, config: dict = None, fileinfo: dict = {}) -> str:
        """
        We don't have to create a new entry as the RESULT_SUUID is already defined in the enviroment
        """
        # the result
        self.suuid = os.getenv("AA_RESULT_SUUID")
        return self.suuid
