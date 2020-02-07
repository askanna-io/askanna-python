import io
import os
import glob
import requests
import shutil
import subprocess
import uuid
import zipfile
from zipfile import ZipFile

import click
import requests
import resumable
import mimetypes


from askanna_cli.utils import check_for_project

ASKANNA_FILEUPLOAD_ENDPOINT = "http://localhost:8005/api/v1/upload/"

HELP = """
Wrapper command to package the current working folder to archive
Afterwards we send this to the ASKANNA_FILEUPLOD_ENDPOINT
"""

SHORT_HELP = "Package code for askanna"


# Zip the files from given directory that matches the filter
def zipFilesInDir(dirName, zipFileName, filter):
    os.chdir(dirName)
    # create a ZipFile object
    with ZipFile(zipFileName, mode='w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk('.'):
            for filename in filenames:
                if filter(filename):
                    # create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath)


def package(src):

    pwd_dir_name = os.path.basename(src)
    random_suffix = uuid.uuid4().hex

    # export_file_path = os.path.join(
    #     '/',
    #     'tmp',
    #     f"{pwd_dir_name}_package"
    # )

    # shutil.rmtree(export_file_path) #delete dst before write to
    # shutil.copytree(src, export_file_path)

    random_name = os.path.join("/", "tmp", "{pwd_dir_name}_{random_suffix}.zip".format(
        pwd_dir_name=pwd_dir_name,
        random_suffix=random_suffix
    ))

    zipFilesInDir(src, random_name, lambda x: x)
    return random_name

KiB = 1024
MiB = 1024 * KiB

def _file_type(path):
    """Mimic the type parameter of a JS File object.
    Resumable.js uses the File object's type attribute to guess mime type,
    which is guessed from file extention accoring to
    https://developer.mozilla.org/en-US/docs/Web/API/File/type.
    Parameters
    ----------
    path : str
        The path to guess the mime type of
    Returns
    -------
    str
        The inferred mime type, or '' if none could be inferred
    """
    type_, _ = mimetypes.guess_type(path)
    # When no type can be inferred, File.type returns an empty string
    return '' if type_ is None else type_


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    pwd = os.getcwd()

    click.echo("We are located in: {pwd}".format(pwd=pwd))
    click.echo("\nPackaging your project...")

    ziparchive = package(pwd)

    click.echo("Finished package: {ziparchive}".format(ziparchive=ziparchive))
    click.echo("Uploading to AskAnna...")
 
    package_dict = {
        "filename": os.path.basename(ziparchive),
        "storage_location": "somewhere",
        "project_id": 0,  ## Need to extract this from config or local config
        "size": os.stat(ziparchive).st_size, ## to be determined
        "created_by": 1,  # our user
        "deleted_at": "2020-02-07T10:43:31.930Z"
    }

    # first register package
    package_url = "http://localhost:8005/api/v1/package/"
    req = requests.post(
        package_url,
        json=package_dict
    )
    res = req.json()
    package_uuid = res.get('uuid')
    print("Package uuid: {uuid}".format(uuid=package_uuid))

    # use resumable chunk
    chunk_url = "http://localhost:8005/api/v1/chunkpackagepart/"
    chunk_dict = {
        "filename": "",
        "size": 0,
        "file_no": 0,
        "is_last": False,
        "package": package_uuid,
        "deleted_at": "2020-02-07T13:29:35.910Z"
    }

    resumable_file = resumable.file.ResumableFile(ziparchive, 100*KiB)
    for i, chunk in enumerate(resumable_file.chunks):
        config = chunk_dict.copy()
        config.update(**{
            "filename": chunk.index + 1,
            "size": chunk.size,
            "file_no": chunk.index + 1,
            "is_last": len(resumable_file.chunks) == chunk.index + 1
        })

        # request chunk id from API
        req_chunk = requests.post(
            chunk_url,
            json=config
        )
        chunk_uuid = req_chunk.json().get('uuid')
        # print(req_chunk.text)
        # print(chunk_uuid)

        # do actual uploading
        # compose request with actual data
        chunk_url_ep = "http://localhost:8005/api/v1/chunkpackagepart/{uuid}/chunk_receiver/".format(
            uuid=chunk_uuid
        )

        files = {
            'file': io.BytesIO(chunk.read())
        }
        data = {
            'resumableChunkSize': resumable_file.chunk_size,
            'resumableTotalSize': resumable_file.size,
            'resumableType': _file_type(resumable_file.path),
            'resumableIdentifier': str(resumable_file.unique_identifier),
            'resumableFilename': os.path.basename(resumable_file.path),
            'resumableRelativePath': resumable_file.path,
            'resumableTotalChunks': len(resumable_file.chunks),
            'resumableChunkNumber': chunk.index + 1,
            'resumableCurrentChunkSize': chunk.size
        }
        specific_chunk_req = requests.post(
            chunk_url_ep,
            data=data,
            files=files
        )
        # print(specific_chunk_req.headers)
        # print(specific_chunk_req.text)