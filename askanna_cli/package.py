import glob
import io
import mimetypes
import os
import shutil
import subprocess
import sys
import uuid
import zipfile
from zipfile import ZipFile

import click
import requests
import resumable

from askanna_cli.utils import check_for_project

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

    random_name = os.path.join(
        "/", "tmp", "{pwd_dir_name}_{random_suffix}.zip".format(
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

    ASKANNA_API_SERVER = 'http://localhost:8005/api/v1/'

    pwd = os.getcwd()

    click.echo("We are located in: {pwd}".format(pwd=pwd))
    click.echo("\nPackaging your project...")

    ziparchive = package(pwd)

    click.echo("Finished package: {ziparchive}".format(ziparchive=ziparchive))
    click.echo("Uploading to AskAnna...")
 
    package_dict = {
        "filename": os.path.basename(ziparchive),
        "storage_location": "somewhere",
        "project_id": 0,  # FIXME: Need to extract this from config or local config
        "size": os.stat(ziparchive).st_size, ## to be determined
        "created_by": 1,  # FIXME: our user
    }

    # first register package
    package_url = "{ASKANNA_API_SERVER}package/".format(
        ASKANNA_API_SERVER=ASKANNA_API_SERVER
    )
    req = requests.post(
        package_url,
        json=package_dict
    )
    res = req.json()
    package_uuid = res.get('uuid')
    print("Package uuid: {uuid}".format(uuid=package_uuid))

    # use resumable chunk
    chunk_url = "{ASKANNA_API_SERVER}chunkpackagepart/".format(
        ASKANNA_API_SERVER=ASKANNA_API_SERVER
    )
    chunk_dict = {
        "filename": "",
        "size": 0,
        "file_no": 0,
        "is_last": False,
        "package": package_uuid,
    }

    resumable_file = resumable.file.ResumableFile(ziparchive, 100*KiB)
    for chunk in resumable_file.chunks:
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
        chunk_url_ep = "{ASKANNA_API_SERVER}chunkpackagepart/{uuid}/chunk_receiver/".format(
            uuid=chunk_uuid,
            ASKANNA_API_SERVER=ASKANNA_API_SERVER
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

    # Do final call when all chunks are uploaded
    final_call_url = "{ASKANNA_API_SERVER}package/{package_uuid}/finish_upload/".format(
        package_uuid=package_uuid,
        ASKANNA_API_SERVER=ASKANNA_API_SERVER
    )
    final_call_dict = {
        'package': package_uuid
    }

    data = {
        'resumableChunkSize': resumable_file.chunk_size,
        'resumableTotalSize': resumable_file.size,
        'resumableType': _file_type(resumable_file.path),
        'resumableIdentifier': str(resumable_file.unique_identifier),
        'resumableFilename': os.path.basename(resumable_file.path),
        'resumableRelativePath': resumable_file.path,
        'resumableTotalChunks': len(resumable_file.chunks),
        'resumableChunkNumber': 1,
        'resumableCurrentChunkSize': 1
    }
    final_call_dict.update(**data)

    final_call_req = requests.post(
        final_call_url,
        data=final_call_dict
    )
    if final_call_req.status_code == 200:
        print('Package is uploaded correctly')
        sys.exit(0)
    else:
        print("Package upload is not ok")
        sys.exit(1)
