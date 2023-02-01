import os
import shutil
import tempfile
import unittest
from pathlib import Path

import pytest
import responses
from responses import matchers

from askanna.core.download import ChunkedDownload
from askanna.core.exceptions import GetError
from askanna.gateways.api_client import client
from tests.create_fake_files import create_zip_file


@pytest.fixture(autouse=True)
def test_setup_and_teardown():
    cwd = os.getcwd()

    yield

    os.chdir(cwd)


class TestDownload(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-core-download-")
        self.base_url = client.askanna_url.base_url
        url_download_file = "https://cdn-beta-api.askanna.eu/files/artifacts/65deef6cc430ab83b451e659ba4562cf/476120827b1e224d747c6e444961c9e6/afdf82c9a39161d6041d785bcbd8f0e4/artifact_2abeb6346f5a679078379d500043e41d.zip"  # noqa

        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "artifact/abcd-abcd-abcd-abcd/",
            headers={"Location": f"{url_download_file}"},
            status=302,
        )
        self.responses.add(
            responses.HEAD,
            url=url_download_file,
            headers={"Content-Length": "926", "Accept-Ranges": "bytes"},
            content_type="application/zip",
            status=200,
        )
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "artifact/wxyz-wxyz-wxyz-wxyz/",
            status=404,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_init_download(self):
        download = ChunkedDownload(url=self.base_url + "artifact/abcd-abcd-abcd-abcd/")
        self.assertEqual(download.content_type, "application/zip")
        self.assertEqual(download.status_code, 200)

    def test_init_download_file_not_exist(self):
        download = ChunkedDownload(url=self.base_url + "artifact/wxyz-wxyz-wxyz-wxyz/")
        self.assertEqual(download.status_code, 404)

    def test_setup_download(self):
        url_artifact_zip = "https://cdn.askanna.eu/v1/artifact/test-setup-download.zip"
        content_lenght = 213243556  # 21 chunks of 20 MiB per chunk

        self.responses.add(
            responses.HEAD,
            url=url_artifact_zip,
            headers={"Content-Length": str(content_lenght), "Accept-Ranges": "bytes"},
            content_type="application/zip",
            status=200,
        )

        download = ChunkedDownload(url=url_artifact_zip)
        download.setup_download()

        self.assertEqual(download.status_code, 200)
        self.assertEqual(len(download.download_queue), 21)
        self.assertEqual(download.download_queue[-1][-1], content_lenght)

    def test_fail_download(self):
        url_artifact_zip = "https://cdn.askanna.eu/v1/artifact/a-fail.zip"
        content_lenght = 213243556  # 21 chunks of 20 MiB per chunk
        output_zip_file = Path(f"{self.tempdir}/artifact_download_fail.zip")

        self.responses.add(
            responses.HEAD,
            url=url_artifact_zip,
            headers={"Content-Length": str(content_lenght), "Accept-Ranges": "bytes"},
            content_type="application/zip",
            status=200,
        )
        self.responses.add(
            responses.GET,
            url=url_artifact_zip,
            headers={"Range": f"bytes=0-{content_lenght}"},
            match=[matchers.request_kwargs_matcher({"stream": True})],
            content_type="application/zip",
            status=200,
        )

        download = ChunkedDownload(url=url_artifact_zip)
        with pytest.raises(GetError) as e:
            download.download(output_file=output_zip_file)

        assert (
            "Could not download chunk 5 from https://cdn.askanna.eu/v1/artifact/a-fail.zip after 5 retries"
            in e.value.args[0]
        )

    def test_actual_download_one_chunk(self):
        url_artifact_zip = "https://cdn.askanna.eu/v1/artifact/a-zip-file-one-chunk.zip"
        zip_file = create_zip_file(self.tempdir, 100)
        output_zip_file = Path(f"{self.tempdir}/artifact_download_random_json_one_chunk.zip")

        with open(zip_file, "rb") as f:
            content = f.read(os.path.getsize(zip_file))

        self.responses.add(
            responses.HEAD,
            url=url_artifact_zip,
            headers={"Content-Length": str(os.path.getsize(zip_file)), "Accept-Ranges": "bytes"},
            content_type="application/zip",
            status=200,
        )
        self.responses.add(
            responses.GET,
            url=url_artifact_zip,
            headers={"Range": f"bytes=0-{os.path.getsize(zip_file)}"},
            match=[matchers.request_kwargs_matcher({"stream": True})],
            content_type="application/zip",
            status=206,
            body=content,
        )

        download = ChunkedDownload(url=url_artifact_zip)
        download.download(output_file=output_zip_file)

        self.assertEqual(os.path.getsize(zip_file), os.path.getsize(output_zip_file))

        os.remove(zip_file)
        os.remove(output_zip_file)

        self.assertEqual(download.status_code, 200)

    def test_actual_download_multi_chunk(self):
        url_artifact_zip = "https://cdn.askanna.eu/v1/artifact/a-zip-file.zip"
        zip_file = Path("tests/fixtures/files/artifact_15MB.zip")
        output_zip_file = Path(f"{self.tempdir}/artifact_download_random_json.zip")

        self.responses.add(
            responses.HEAD,
            url=url_artifact_zip,
            headers={"Content-Length": str(zip_file.stat().st_size), "Accept-Ranges": "bytes"},
            content_type="application/zip",
            status=200,
        )

        download = ChunkedDownload(url=url_artifact_zip)
        with open(zip_file, "rb") as f:
            chunk_1 = f.read(download.chunk_size)
            chunk_2 = f.read(zip_file.stat().st_size)

        self.responses.add(
            responses.GET,
            url=url_artifact_zip,
            headers={"Range": f"bytes=0-{download.chunk_size}"},
            match=[matchers.request_kwargs_matcher({"stream": True})],
            content_type="application/zip",
            status=206,
            body=chunk_1,
        )
        self.responses.add(
            responses.GET,
            url=url_artifact_zip,
            headers={"Range": f"bytes={download.chunk_size+1}-{zip_file.stat().st_size}"},
            match=[matchers.request_kwargs_matcher({"stream": True})],
            content_type="application/zip",
            status=206,
            body=chunk_2,
        )

        download.download(output_file=output_zip_file)

        self.assertEqual(zip_file.stat().st_size, output_zip_file.stat().st_size)

        os.remove(output_zip_file)

        self.assertEqual(download.status_code, 200)
