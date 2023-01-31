import io
import os
from typing import Optional

import resumable

from askanna.core.exceptions import PostError
from askanna.core.utils.file import file_type
from askanna.core.utils.settings import diskunit
from askanna.gateways.api_client import client


class Upload:
    message_upload_success = "File is uploaded"
    message_upload_fail = "File upload failed"

    def __init__(self):
        self.suuid = None
        self.resumable_file = None

    def register_upload_url(self) -> str:
        raise NotImplementedError(f"Please implement 'register_upload_url' for {self.__class__.__name__}")

    def register_chunk_url(self) -> str:
        raise NotImplementedError(f"Please implement 'register_chunk_url' for {self.__class__.__name__}")

    def upload_chunk_url(self, chunk_uuid: str) -> str:
        raise NotImplementedError(f"Please implement 'upload_chunk_url' for {self.__class__.__name__}")

    def finish_upload_url(self) -> str:
        raise NotImplementedError(f"Please implement 'finish_upload_url' for {self.__class__.__name__}")

    @property
    def chunk_baseinfo(self) -> dict:
        return {
            "resumableChunkSize": self.resumable_file.chunk_size,  # type: ignore
            "resumableTotalSize": self.resumable_file.size,  # type: ignore
            "resumableType": file_type(self.resumable_file.path),  # type: ignore
            "resumableIdentifier": str(self.resumable_file.unique_identifier),  # type: ignore
            "resumableFilename": os.path.basename(self.resumable_file.path),  # type: ignore
            "resumableRelativePath": self.resumable_file.path,  # type: ignore
            "resumableTotalChunks": len(self.resumable_file.chunks),  # type: ignore
            "resumableChunkNumber": 1,
            "resumableCurrentChunkSize": 1,
        }.copy()

    def upload(self, file_path: str):
        self.suuid = self.create_entry(file_path)
        self.upload_file(file_path)
        return self.finish_upload()

    @property
    def entry_extrafields(self) -> dict:
        return {}

    def create_entry(self, file_path) -> str:
        request_dict = {
            "filename": os.path.basename(file_path),
            "size": os.stat(file_path).st_size,
        }

        request_dict.update(**self.entry_extrafields)

        # Register upload on the server
        reg_upload = client.post(self.register_upload_url(), json=request_dict)
        if reg_upload.status_code != 201:
            raise PostError(
                f"In the AskAnna platform something went wrong with creating the upload entry: {reg_upload.json()}",
            )

        return reg_upload.json().get("suuid")

    def upload_file(self, file_path):
        """
        Take a file and make chunks out of it to upload
        """
        self.resumable_file = resumable.file.ResumableFile(file_path, 1 * diskunit.MiB)  # type: ignore
        for chunk in self.resumable_file.chunks:
            self.upload_chunk(chunk)

    @property
    def chunk_dict_template(self) -> dict:
        return {
            "filename": "",
            "size": 0,
            "file_no": 0,
            "is_last": False,
        }

    def upload_chunk(self, chunk):
        chunk_dict = self.chunk_dict_template.copy()
        chunk_dict.update(
            **{
                "filename": chunk.index + 1,
                "size": chunk.size,
                "file_no": chunk.index + 1,
                "is_last": len(self.resumable_file.chunks) == chunk.index + 1,  # type: ignore
            }
        )

        # Register chunk on the server
        reg_chunk = client.post(self.register_chunk_url(), json=chunk_dict)
        if reg_chunk.status_code != 201:
            raise PostError(
                "In the AskAnna platform something went wrong with creating the chunk entry for file_no "
                f"'{chunk_dict.get('file_no')}'.",
            )
        chunk_uuid = reg_chunk.json().get("uuid")

        files = {"file": io.BytesIO(chunk.read())}
        data = self.chunk_baseinfo
        data.update(
            **{
                "resumableChunkNumber": chunk.index + 1,
                "resumableCurrentChunkSize": chunk.size,
            }
        )

        upload_chunk_response = client.post(
            self.upload_chunk_url(chunk_uuid=chunk_uuid),
            data=data,
            files=files,
        )

        if upload_chunk_response.status_code != 200:
            raise PostError(
                f"Chunk with file_no '{chunk_dict.get('file_no')}' and chunk UUID '{chunk_uuid}' could not be uploaded"
            )

    def finish_upload(self):
        # Do final call when all chunks are uploaded
        final_call_dict = self.chunk_baseinfo
        final_call_req = client.post(self.finish_upload_url(), data=final_call_dict)

        if final_call_req.status_code == 200:
            return True, self.message_upload_success
        else:
            return False, self.message_upload_fail


class PackageUpload(Upload):
    message_upload_success = "Package is uploaded"
    message_upload_fail = "Package upload failed"

    def __init__(self, project_suuid: str, description: Optional[str] = None):
        self.project_suuid = project_suuid
        self.description = description
        super().__init__()

    def register_upload_url(self) -> str:
        return client.askanna_url.package.base_package_url

    def register_chunk_url(self) -> str:
        if self.suuid:
            return client.askanna_url.package.package_chunk(self.suuid)
        raise TypeError("No SUUID found for package upload")

    def upload_chunk_url(self, chunk_uuid: str) -> str:
        if self.suuid:
            return client.askanna_url.package.package_chunk_upload(self.suuid, chunk_uuid)
        raise TypeError("No SUUID found for package upload")

    def finish_upload_url(self) -> str:
        if self.suuid:
            return client.askanna_url.package.package_finish_upload(self.suuid)
        raise TypeError("No SUUID found for package upload")

    @property
    def entry_extrafields(self) -> dict:
        return {
            "project_suuid": self.project_suuid,
            "description": self.description,
        }


class ArtifactUpload(Upload):
    message_upload_success = "Artifact is uploaded"
    message_upload_fail = "Artifact upload failed"

    def __init__(self, run_suuid: str):
        self.run_suuid = run_suuid
        super().__init__()

    def register_upload_url(self) -> str:
        if self.run_suuid:
            return client.askanna_url.run.artifact_list(self.run_suuid)
        raise TypeError("No Run SUUID found for artifact upload")

    def register_chunk_url(self) -> str:
        if self.run_suuid and self.suuid:
            return client.askanna_url.run.artifact_chunk(self.run_suuid, self.suuid)
        raise TypeError("No Run SUUID or Artifact SUUID found for artifact upload")

    def upload_chunk_url(self, chunk_uuid: str) -> str:
        if self.run_suuid and self.suuid:
            return client.askanna_url.run.artifact_chunk_upload(self.run_suuid, self.suuid, chunk_uuid)
        raise TypeError("No Run SUUID or Artifact SUUID found for artifact upload")

    def finish_upload_url(self) -> str:
        if self.run_suuid and self.suuid:
            return client.askanna_url.run.artifact_finish_upload(self.run_suuid, self.suuid)
        raise TypeError("No Run SUUID or Artifact SUUID found for artifact upload")


class ResultUpload(Upload):
    message_upload_success = "Result is uploaded"
    message_upload_fail = "Result upload failed"

    def __init__(self, run_suuid: str):
        self.run_suuid = run_suuid
        super().__init__()

    def register_upload_url(self) -> str:
        if self.run_suuid:
            return client.askanna_url.run.result_upload(self.run_suuid)
        raise TypeError("No Run SUUID found for result upload")

    def register_chunk_url(self) -> str:
        if self.run_suuid and self.suuid:
            return client.askanna_url.run.result_chunk(self.run_suuid, self.suuid)
        raise TypeError("No Run SUUID or Result SUUID found for result upload")

    def upload_chunk_url(self, chunk_uuid: str) -> str:
        if self.run_suuid and self.suuid:
            return client.askanna_url.run.result_chunk_upload(self.run_suuid, self.suuid, chunk_uuid)
        raise TypeError("No Run SUUID or Result SUUID found for result upload")

    def finish_upload_url(self) -> str:
        if self.run_suuid and self.suuid:
            return client.askanna_url.run.result_finish_upload(self.run_suuid, self.suuid)
        raise TypeError("No Run SUUID or Result SUUID found for result upload")
