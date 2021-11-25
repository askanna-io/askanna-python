# -*- coding: utf-8 -*-
import math
import os
import sys

import click

from askanna.core.apiclient import client
from askanna.core.utils import diskunit


class ChunkedDownload:
    def __init__(self, url : str):
        """
        Takes an url to download from, this can be a url which could redirect to another URI.
        """
        self.history = []
        self.download_queue = []
        self.chunk_size = 10 * diskunit.MiB

        self.url = url
        self.size = 0
        self.accept_ranges = "none"

        self.client = client
        self.perform_preflight(url=url)

    @property
    def status_code(self):
        """
        Return the last status_code
        """
        return self.history[-1][1]

    def perform_preflight(self, url):
        """
        We take the session from self.client and will do a preflight request to
        determine whether the url will result in a (final) http_response_code=200
        """
        r = self.client.head(url)
        self.history.append([url, r.status_code, r.headers])

        if r.status_code in [301, 302] and r.headers.get("Location"):
            self.url = r.headers.get("Location")
            return self.perform_preflight(url=r.headers.get("Location"))
        elif r.status_code == 200:
            self.size = int(r.headers.get("Content-Length"))
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
        # fix last end byte
        self.download_queue[-1][-1] = self.size

    def download(self, output_file : str):
        """
        Download the target_url, we consume the queue and write partial files.
        In the end we glue them to the original intended file.
        """
        self.setup_download()
        finished_queue = []
        while len(self.download_queue):
            chunk = self.download_queue.pop(0)
            range_header = {
                "Range": "{accept_ranges}={start}-{end}".format(
                    accept_ranges=self.accept_ranges, start=chunk[1], end=chunk[2]
                )
            }

            try:
                r = self.client.get(self.url, stream=True, headers=range_header)
                if not r.content or r.status_code != 206:
                    click.echo(f"HTTP response status code: {r.status_code}", err=True)
                    click.echo("Something went wrong with downloading the file content. Please try again.", err=True)
                    sys.exit(1)

                # so far so good on the download, save the result
                with open("file_{}.part".format(chunk[0]), "wb") as f:
                    for dlchunk in r.iter_content(chunk_size=1024):
                        f.write(dlchunk)
            except Exception as e:
                click.echo(e)
                self.download_queue.append(chunk)
            else:
                finished_queue.append(chunk)

        # combine the chunks in to one file
        with open(output_file, "wb") as f:
            finished_queue = sorted(finished_queue, key=lambda x: x[0])
            for chunk in finished_queue:
                chunkfilename = "file_{}.part".format(chunk[0])
                with open(chunkfilename, "rb") as chunkfile:
                    f.write(chunkfile.read())
                # delete the chunkfile
                os.remove(chunkfilename)
