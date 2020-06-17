import io
import os
import requests
import resumable

from askanna_cli.utils import _file_type, diskunit


class Upload:
    tpl_register_upload_url = "{ASKANNA_API_SERVER}package/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/packagechunk/"
    tpl_upload_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/packagechunk/{CHUNK_SUUID}/chunk/"
    tpl_final_upload_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/finish_upload/"

    tpl_upload_pass = "uploaded"
    tpl_upload_fail = "failed"

    def __init__(self, token: str, api_server: str, project_uuid: str, *args, **kwargs):
        self.headers = {
            'user-agent': 'askanna-cli/0.2.0',
            'Authorization': 'Token {token}'.format(
                token=token
            )
        }
        self.ASKANNA_API_SERVER = api_server
        self.suuid = None
        self.session = requests.Session()
        self.project_uuid = project_uuid
        self.resumable_file = None
        self.kwargs = kwargs

    @property
    def chunk_baseinfo(self) -> dict:
        return {
            'resumableChunkSize': self.resumable_file.chunk_size,
            'resumableTotalSize': self.resumable_file.size,
            'resumableType': _file_type(self.resumable_file.path),
            'resumableIdentifier': str(self.resumable_file.unique_identifier),
            'resumableFilename': os.path.basename(self.resumable_file.path),
            'resumableRelativePath': self.resumable_file.path,
            'resumableTotalChunks': len(self.resumable_file.chunks),
            'resumableChunkNumber': 1,
            'resumableCurrentChunkSize': 1
        }.copy()

    def url_template_arguments(self):
        """
        This method is meant to be overwritten by inheritors
        providing specific url templating variables
        """
        return {
            'ASKANNA_API_SERVER': self.ASKANNA_API_SERVER,
            'PACKAGE_SUUID': self.suuid
        }

    @property
    def register_upload_url(self) -> str:
        return self.tpl_register_upload_url.format(
            **self.url_template_arguments()
        )

    @property
    def register_chunk_url(self) -> str:
        return self.tpl_register_chunk_url.format(
            **self.url_template_arguments()
        )

    def upload_chunk_url(self, chunk_suuid: str) -> str:
        arguments = self.url_template_arguments()
        arguments.update({
            'CHUNK_SUUID': chunk_suuid
        })
        return self.tpl_upload_chunk_url.format(
            **arguments
        )

    @property
    def final_upload_url(self) -> str:
        return self.tpl_final_upload_url.format(
            **self.url_template_arguments()
        )

    def upload(self, file_obj, config, fileinfo):
        self.create_entry(config=config, fileinfo=fileinfo)
        self.upload_file(file_obj)
        return self.finish_upload()

    def create_entry(self, config: dict = None, fileinfo: dict = {}) -> str:
        info_dict = {
            "filename": fileinfo.get('filename'),
            "project": self.project_uuid,
            "size": fileinfo.get('size')
        }

        # the request to AskAnna API
        req = self.session.post(
            self.register_upload_url,
            json=info_dict,
            headers=self.headers
        )
        res = req.json()

        # the result
        self.uuid = res.get('uuid')
        self.suuid = res.get('short_uuid')
        return self.suuid

    def upload_chunk(self, chunk, chunk_dict):
        config = chunk_dict.copy()
        config.update(**{
            "filename": chunk.index + 1,
            "size": chunk.size,
            "file_no": chunk.index + 1,
            "is_last": len(self.resumable_file.chunks) == chunk.index + 1
        })

        # request chunk id from API
        req_chunk = self.session.post(
            self.register_chunk_url,
            json=config,
            headers=self.headers
        )
        chunk_suuid = req_chunk.json().get('short_uuid')

        files = {
            'file': io.BytesIO(chunk.read())
        }
        data = self.chunk_baseinfo
        data.update(**{
            'resumableChunkNumber': chunk.index + 1,
            'resumableCurrentChunkSize': chunk.size
        })

        specific_chunk_req = self.session.post(
            self.upload_chunk_url(chunk_suuid=chunk_suuid),
            data=data,
            files=files,
            headers=self.headers
        )
        assert specific_chunk_req.status_code == 200, "Code could not be uploaded"

    def chunk_dict_template(self):
        return {
            "filename": "",
            "size": 0,
            "file_no": 0,
            "is_last": False,
            "package": self.uuid,
        }

    def upload_file(self, file_obj):
        """
        Take a file_obj and make chunks out of it to upload
        """
        chunk_dict = self.chunk_dict_template()

        self.resumable_file = resumable.file.ResumableFile(
            file_obj, 1*diskunit.MiB)
        for chunk in self.resumable_file.chunks:
            self.upload_chunk(chunk, chunk_dict)

    def finish_upload(self):
        # Do final call when all chunks are uploaded
        final_call_dict = self.chunk_baseinfo

        final_call_req = self.session.post(
            self.final_upload_url,
            data=final_call_dict,
            headers=self.headers
        )

        if final_call_req.status_code == 200:
            # print(final_call_req.text)
            return True, self.tpl_upload_pass
        else:
            return False, self.tpl_upload_fail


class PackageUpload(Upload):
    tpl_register_upload_url = "{ASKANNA_API_SERVER}package/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/packagechunk/"
    tpl_upload_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/packagechunk/{CHUNK_SUUID}/chunk/"
    tpl_final_upload_url = "{ASKANNA_API_SERVER}package/{PACKAGE_SUUID}/finish_upload/"

    tpl_upload_pass = "Package is uploaded"
    tpl_upload_fail = "Package upload failed"


class ArtifactUpload(Upload):
    tpl_register_upload_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SUUID}/artifact/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SUUID}/artifact/{ARTIFACT_SUUID}/artifactchunk/"
    tpl_upload_chunk_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SUUID}/artifact/{ARTIFACT_SUUID}/artifactchunk/{CHUNK_SUUID}/chunk/"  # noqa
    tpl_final_upload_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SUUID}/artifact/{ARTIFACT_SUUID}/finish_upload/"

    tpl_upload_pass = "Artifact is uploaded"
    tpl_upload_fail = "Artifact upload failed"

    def url_template_arguments(self):
        """
        This method is meant to be overwritten by inheritors
        providing specific url templating variables
        """
        return {
            'ASKANNA_API_SERVER': self.ASKANNA_API_SERVER,
            'ARTIFACT_SUUID': self.suuid,
            'JOBRUN_SUUID': self.kwargs.get('JOBRUN_SUUID')
        }

    def chunk_dict_template(self):
        return {
            "filename": "",
            "size": 0,
            "file_no": 0,
            "is_last": False,
            "artifact": self.uuid,
        }
