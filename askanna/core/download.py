import math
from pathlib import Path
from typing import Union

import click

from askanna.core.exceptions import GetError
from askanna.core.utils.settings import diskunit
from askanna.gateways.api_client import client


class ChunkedDownload:
    def __init__(self, url: str):
        """
        Takes an url to download from, this can be a url which could redirect to another URI.
        """
        self.history = []
        self.download_queue = []
        self.chunk_size = 10 * diskunit.MiB

        self.url = url
        self.size = 0
        self.accept_ranges = "none"

        self.perform_preflight(url=url)

    @property
    def status_code(self):
        """
        Return the last status_code
        """
        return self.history[-1][1]

    def perform_preflight(self, url):
        """
        We take the session from client and will do a preflight request to
        determine whether the url will result in a (final) http_response_code=200
        """
        r = client.head(url)
        self.history.append([url, r.status_code, r.headers])

        if r.status_code in [301, 302] and r.headers.get("Location"):
            self.url = r.headers.get("Location")
            return self.perform_preflight(url=r.headers.get("Location"))
        elif r.status_code == 200:
            self.size = int(r.headers.get("Content-Length", 0))
            self.content_type = r.headers.get("Content-Type")
            self.accept_ranges = r.headers.get("Accept-Ranges", "none")

    def setup_download(self):
        """
        Download the self.url and chunk (if needed) the download
        """
        no_chunks = math.ceil(self.size / self.chunk_size)
        for chunk_no in range(0, no_chunks):
            self.download_queue.append(
                [
                    chunk_no,
                    chunk_no * self.chunk_size,
                    (chunk_no + 1) * self.chunk_size - 1,
                ]
            )
        # Fix last end byte
        self.download_queue[-1][-1] = self.size

    def download(self, output_file: Union[Path, str], overwrite: bool = False):
        """
        Download the target_url, we consume the queue and write partial files.
        In the end we glue them to the original intended file.
        """
        self.setup_download()
        finished_queue = []

        output_file = Path(output_file)
        if output_file.is_dir():
            raise ValueError(f"The output path '{output_file}' is a directory, but should be a file name")
        if output_file.exists() and not overwrite:
            raise ValueError(f"The output file '{output_file}' already exists.")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        chunk_retry = 0
        while len(self.download_queue):
            chunk = self.download_queue.pop(0)
            range_header = {
                "Range": "{accept_ranges}={start}-{end}".format(
                    accept_ranges=self.accept_ranges, start=chunk[1], end=chunk[2]
                )
            }

            try:
                r = client.get(self.url, stream=True, headers=range_header)
                if not r.content or r.status_code not in [200, 206]:
                    raise GetError(f"Could not download chunk {chunk[0]} from {self.url} (code={r.status_code})")

                # So far so good on the download, save the result
                with Path(f"file_{chunk[0]}.part").open("wb") as f:
                    for r_chunk in r.iter_content(chunk_size=1024):
                        f.write(r_chunk)
            except Exception as e:
                click.echo(e)
                self.download_queue.append(chunk)
                chunk_retry += 1
                if chunk_retry > 5:
                    raise GetError(f"Could not download chunk {chunk[0]} from {self.url} after 5 retries")
            else:
                finished_queue.append(chunk)

        # Combine the chunks in to one file
        with output_file.open("wb") as f:
            finished_queue = sorted(finished_queue, key=lambda x: x[0])
            for chunk in finished_queue:
                chunkfilename = Path(f"file_{chunk[0]}.part")
                with chunkfilename.open("rb") as chunkfile:
                    f.write(chunkfile.read())
                # Delete the chunkfile
                chunkfilename.unlink()
