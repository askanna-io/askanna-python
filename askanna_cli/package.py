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
            "filename": chunk.index,
            "size": chunk.size,
            "file_no": chunk.index
        })

        # request chunk id from API

        req_chunk = requests.post(
            chunk_url,
            json=config
        )
        chunk_uuid = req_chunk.json().get('uuid')
        print(req_chunk.text)
        print(chunk_uuid)

        # do actual uploading
        # compose request with actual data