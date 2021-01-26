import logging
import click
from askanna.core.push import push

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

HELP = """
Wrapper command to push the current working folder to archive.\n
Afterwards we send this to AskAnna
"""

SHORT_HELP = "Push code to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option('--force', '-f', is_flag=True, help='Force push')
@click.option('--message', '-m', default='', type=str, help='Add description to this code')
def cli(force, message):
    push(force, message)
