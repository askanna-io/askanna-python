import io
import os
import requests
import resumable

from askanna_cli.utils import _file_type, diskunit


class Upload:
    tpl_register_upload_url = "{ASKANNA_API_SERVER}package/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/packagechunk/"
    tpl_upload_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/packagechunk/{CHUNK_UUID}/chunk/"
    tpl_final_upload_url = "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/finish_upload/"

    def __init__(self, token: str, api_server: str, project_uuid: str, *args, **kwargs):
        self.headers = {
            'user-agent': 'askanna-cli/0.0.1',
            'Authorization': 'Token {token}'.format(
                token=token
            )
        }
        self.ASKANNA_API_SERVER = api_server
        self.uuid = None
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
            'PACKAGE_UUID': self.uuid
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

    def upload_chunk_url(self, chunk_uuid: str) -> str:
        arguments = self.url_template_arguments()
        arguments.update({
            'CHUNK_UUID': chunk_uuid
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
        return self.uuid

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
        chunk_uuid = req_chunk.json().get('uuid')

        files = {
            'file': io.BytesIO(chunk.read())
        }
        data = self.chunk_baseinfo
        data.update(**{
            'resumableChunkNumber': chunk.index + 1,
            'resumableCurrentChunkSize': chunk.size
        })

        specific_chunk_req = self.session.post(
            self.upload_chunk_url(chunk_uuid=chunk_uuid),
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
            return True, 'Package is uploaded'
        else:
            return False, "Package upload failed"


class PackageUpload(Upload):
    tpl_register_upload_url = "{ASKANNA_API_SERVER}package/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/packagechunk/"
    tpl_upload_chunk_url = "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/packagechunk/{CHUNK_UUID}/chunk/"
    tpl_final_upload_url = "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/finish_upload/"


class ArtifactUpload(Upload):
    tpl_register_upload_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SHORT_UUID}/artifact/"
    tpl_register_chunk_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SHORT_UUID}/artifact/{ARTIFACT_UUID}/artifactchunk/"
    tpl_upload_chunk_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SHORT_UUID}/artifact/{ARTIFACT_UUID}/artifactchunk/{CHUNK_UUID}/chunk/"  # noqa
    tpl_final_upload_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SHORT_UUID}/artifact/{ARTIFACT_UUID}/finish_upload/"

    def url_template_arguments(self):
        """
        This method is meant to be overwritten by inheritors
        providing specific url templating variables
        """
        return {
            'ASKANNA_API_SERVER': self.ASKANNA_API_SERVER,
            'ARTIFACT_UUID': self.uuid,
            'JOBRUN_SHORT_UUID': self.kwargs.get('JOBRUN_SHORT_UUID')
        }

    def chunk_dict_template(self):
        return {
            "filename": "",
            "size": 0,
            "file_no": 0,
            "is_last": False,
            "artifact": self.uuid,
        }