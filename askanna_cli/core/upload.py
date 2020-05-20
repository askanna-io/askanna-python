import io
import os
import uuid
import requests
import resumable

from askanna_cli.utils import check_for_project, zipFilesInDir, _file_type, diskunit


class Upload:
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

    @property
    def register_upload_url(self) -> str:
        return "{ASKANNA_API_SERVER}package/".format(
            ASKANNA_API_SERVER=self.ASKANNA_API_SERVER
        )

    @property
    def register_chunk_url(self) -> str:
        return "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/packagechunk/".format(
            ASKANNA_API_SERVER=self.ASKANNA_API_SERVER,
            PACKAGE_UUID=self.uuid
        )

    def upload_chunk_url(self, chunk_uuid: str) -> str:
        return "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/packagechunk/{CHUNK_UUID}/chunk/".format(
            CHUNK_UUID=chunk_uuid,
            ASKANNA_API_SERVER=self.ASKANNA_API_SERVER,
            PACKAGE_UUID=self.uuid
        )

    @property
    def final_upload_url(self) -> str:
        return "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/finish_upload/".format(
            PACKAGE_UUID=self.uuid,
            ASKANNA_API_SERVER=self.ASKANNA_API_SERVER
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
        # print(req.text)

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
        # print(specific_chunk_req.headers)
        # print(specific_chunk_req.text)

    def upload_file(self, file_obj):
        """
        Take a file_obj and make chunks out of it to upload
        """
        chunk_dict = {
            "filename": "",
            "size": 0,
            "file_no": 0,
            "is_last": False,
            "package": self.uuid,
        }

        self.resumable_file = resumable.file.ResumableFile(
            file_obj, 1*diskunit.MiB)
        for chunk in self.resumable_file.chunks:
            self.upload_chunk(chunk, chunk_dict)

    def finish_upload(self):
        # Do final call when all chunks are uploaded
        final_call_url = "{ASKANNA_API_SERVER}package/{PACKAGE_UUID}/finish_upload/".format(
            PACKAGE_UUID=self.uuid,
            ASKANNA_API_SERVER=self.ASKANNA_API_SERVER
        )
        final_call_dict = self.chunk_baseinfo
        # data = self.chunk_baseinfo
        # final_call_dict.update(**data)

        final_call_req = self.session.post(
            final_call_url,
            data=final_call_dict,
            headers=self.headers
        )

        if final_call_req.status_code == 200:
            # print(final_call_req.text)
            return True, 'Package is uploaded'
        else:
            return False, "Package upload failed"
