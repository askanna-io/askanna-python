# -*- coding: utf-8 -*-
import math
import os
import sys
import time
from zipfile import ZipFile
import click

from askanna.core import client as askanna_client
from askanna.core.utils import zipPaths
from askanna.core.utils import scan_config_in_path
from askanna.core.utils import get_config, string_expand_variables
from askanna.core.upload import ArtifactUpload


@click.group()
def cli1():
    pass


@click.group()
def cli2():
    pass


def create_artifact(cwd: str, paths: list) -> str:
    # expand and translate paths if they are configured with variables
    paths = string_expand_variables(paths)

    zipFileName = '/tmp/artifact.zip'
    with ZipFile(zipFileName, mode='w') as zipObj:
        zipPaths(zipObj, paths, cwd)

    return zipFileName


@cli1.command(help="After a run, save the artifact",
              short_help="Save artifact from a run")
def add():
    config = get_config()
    token = config['auth']['token']
    api_server = config['askanna']['remote']

    project_uuid = os.getenv('PROJECT_UUID')
    project_suuid = os.getenv('PROJECT_SUUID')

    jobrun_suuid = os.getenv('JOBRUN_SUUID')
    jobrun_jobname = os.getenv('JOBRUN_JOBNAME')

    if not project_suuid:
        click.echo("Cannot upload from unregistered project to AskAnna")
        sys.exit(1)

    # first check whether we need to create artifacts or not
    # if output.artifact or output.paths is not specified
    # then we skip this step and report this to the stdout
    paths_defined = config[jobrun_jobname].get('output', {}).get("paths", [])
    paths_defined = paths_defined + config[jobrun_jobname].get('output', {}).get("artifact", [])

    if not paths_defined:
        click.echo("Artifact creation aborted, no `output/artifact` or `output/paths` defined for "
                   "this job in `askanna.yml`")
        sys.exit(0)

    cwd = os.getcwd()

    upload_folder = cwd
    askanna_config = scan_config_in_path()
    project_folder = os.path.dirname(askanna_config)

    def ask_which_folder(cwd, project_folder) -> str:
        confirm = input("Proceed upload [c]urrent or [p]roject folder? : ")
        answer = confirm.strip()
        if answer not in ['c', 'p']:
            return ask_which_folder(cwd, project_folder)
        if confirm == 'c':
            return cwd
        if confirm == 'p':
            return project_folder

    if not cwd == project_folder:
        click.echo("You are not at the root folder of the project '{}'.".format(project_folder))
        upload_folder = ask_which_folder(cwd, project_folder)

    artifact_archive = create_artifact(cwd=upload_folder, paths=paths_defined)

    click.echo("Uploading artifact to AskAnna...")

    fileinfo = {
        "filename": os.path.basename(artifact_archive),
        "size": os.stat(artifact_archive).st_size,
    }
    uploader = ArtifactUpload(
        token=token,
        api_server=api_server,
        project_uuid=project_uuid,
        JOBRUN_SUUID=jobrun_suuid
    )
    status, msg = uploader.upload(artifact_archive, config, fileinfo)
    if status:
        print(msg)
        sys.exit(0)
    else:
        print(msg)
        sys.exit(1)


class ChunkedDownload:
    def __init__(self, url, client, output=None):
        """
        Takes an url to download from, this can be a url which could redirect to another URI.
        """
        self.history = []
        self.download_queue = []
        self.chunk_size = 1024 * 1024 * 100  # 100MB
        self.output_target = output

        self.url = url
        self.size = 0
        self.accept_ranges = 'none'

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

        if r.status_code in [301, 302] and r.headers.get('Location'):
            self.url = r.headers.get('Location')
            return self.perform_preflight(url=r.headers.get('Location'))
        elif r.status_code == 200:
            self.size = int(r.headers.get('Content-Length'))
            self.accept_ranges = r.headers.get('Accept-Ranges', 'none')

    def setup_download(self):
        """
        Download the self.url and chunk (if needed) the download
        """
        no_chunks = math.ceil(self.size / self.chunk_size)
        for chunk_no in range(0, no_chunks):
            self.download_queue.append([chunk_no, chunk_no * self.chunk_size, (chunk_no + 1) * self.chunk_size - 1])
        # fix last end byte
        self.download_queue[-1][-1] = self.size

    def download(self):
        """
        Download the target_url, we consume the queue and write partial files.
        In the end we glue them to the original intended file.
        """
        self.setup_download()
        finished_queue = []
        while len(self.download_queue):
            chunk = self.download_queue.pop(0)
            range_header = {
                'Range': "{accept_ranges}={start}-{end}".format(
                    accept_ranges=self.accept_ranges,
                    start=chunk[1],
                    end=chunk[2]
                )
            }

            try:
                r = self.client.get(self.url, stream=True, headers=range_header)
                # so far so good on the download, save the result
                with open('file_{}.part'.format(chunk[0]), 'wb') as f:
                    for dlchunk in r.iter_content(chunk_size=1024):
                        f.write(dlchunk)
            except Exception as e:
                print(e)
                self.download_queue.append(chunk)
            else:
                finished_queue.append(chunk)
        # combine the chunks in to one file
        with open(self.output_target, 'wb') as f:
            finished_queue = sorted(finished_queue, key=lambda x: x[0])
            for chunk in finished_queue:
                chunkfilename = 'file_{}.part'.format(chunk[0])
                with open(chunkfilename, 'rb') as chunkfile:
                    f.write(chunkfile.read())
                # delete the chunkfile
                os.remove(chunkfilename)


@cli2.command(help="Download an artifact of a run", short_help="Download a run artifact")
@click.option('--id', '-i', required=True, type=str, help='Job run SUUID')
@click.option('--output', '-o', show_default=True, type=click.Path())
def get(id, output):
    """
    Download an artifact of a job run
    """
    config = get_config()
    ASKANNA_API_SERVER = config.get('askanna', {}).get('remote')

    base_url = "{server}".format(server=ASKANNA_API_SERVER)
    url = base_url + "artifact/{}".format(id)

    if not output:
        output = "artifact_{suuid}_{datetime}.zip".format(suuid=id, datetime=time.strftime("%Y%m%d-%H%M%S"))

    if os.path.exists(output):
        print("The output file already exists. We will not overwrite the existing file.")
        sys.exit(1)

    stable_download = ChunkedDownload(url=url,
                                      client=askanna_client,
                                      output=output)
    if stable_download.status_code != 200:
        print("We cannot find this artifact for you")
        sys.exit(1)
    print("Downloading the artifact has started.")
    stable_download.download()

    print("We have succesfully downloaded the job run artifact.")
    print("The artifact is saved in: {file}".format(file=output))


cli = click.CommandCollection(sources=[cli1, cli2], help="Save and download run artifacts",
                              short_help="Save and download run artifacts")
