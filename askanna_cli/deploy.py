import os
import glob
import click
import requests
import subprocess

from askanna_cli.utils import check_for_project

# FIXME: this will be an AskAnna public link in the future
# For dev purposes, add your local path to the cookiecutter template
# ASKANNA_FILEUPLOAD_ENDPOINT = "REPLACEME"
ASKANNA_FILEUPLOAD_ENDPOINT = "http://localhost:8000/u/api/upload/"

HELP = """
This command will allow you to deploy a DSP - Data Science Project to
the AskAnna platform.
"""

SHORT_HELP = "Deploy a Data Science Project to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():

    pwd = os.getcwd()

    print("We are located in: {pwd}".format(pwd=pwd))

    if not check_for_project():
        click.echo("Not in a project folder, exiting")
        return 0

    click.echo("\nPackaging your project...")
    export_file = '/tmp/{}_package/'.format(pwd.split('/')[-1])
    # subprocess.Popen(f"python setup.py sdist bdist_wheel -d {export_file}",
    #                 shell=True)
    subprocess.run(
        ["python", "setup.py", "sdist", "bdist_wheel", "-d", export_file],
        capture_output=True)

    wheel_package = glob.glob(export_file + '*.whl')[0]
    click.echo("Finished package: {}".format(wheel_package.split('/')[-1]))
    click.echo("Uploading to AskAnna...")

    # path_to_wheel = '/tmp/barShop/dist/barShop-0.1.0-py3-none-any.whl'
    # files = {'crazyfile': open(path_to_wheel, 'rb')}

    files = {'crazyfile': open(wheel_package, 'rb')}
    r = requests.post(ASKANNA_FILEUPLOAD_ENDPOINT, files=files)

    if r.status_code == 201 or r.status_code == 200:
        click.echo("Upload complete!")
        click.echo("You can see your package in: ")
        askanna_location = r.json()
        _location = askanna_location.get('crazyfile')
        click.echo("\t{_location}".format(_location=_location))
