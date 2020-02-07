import os
import glob
import click
import requests
import shutil
import subprocess
import uuid

from askanna_cli.utils import check_for_project
import zipfile
from zipfile import ZipFile

ASKANNA_FILEUPLOAD_ENDPOINT = "http://localhost:8005/api/v1/upload/"

HELP = """
Wrapper command to package the current working folder to archive
Afterwards we send this to the ASKANNA_FILEUPLOD_ENDPOINT
"""

SHORT_HELP = "Package code for askanna"


# Zip the files from given directory that matches the filter
def zipFilesInDir(dirName, zipFileName, filter):
   # create a ZipFile object
   with ZipFile(zipFileName, mode='w') as zipObj:
       # Iterate over all the files in directory
       for folderName, subfolders, filenames in os.walk(dirName):
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

    random_name = os.path.join("/", "tmp", f"{pwd_dir_name}_{random_suffix}.zip")

    zipFilesInDir(src, random_name, lambda x: x)
    return random_name


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    pwd = os.getcwd()

    click.echo("We are located in: {pwd}".format(pwd=pwd))
    click.echo("\nPackaging your project...")

    ziparchive = package(pwd)

    click.echo(f"Finished package: {ziparchive}")
    click.echo("Uploading to AskAnna...")
 