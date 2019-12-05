import click
import time

HELP = """
Demonstrate how the interface can pontentially work, by faking requests
and responses.
"""


SHORT_HELP = "Mocking interactions with AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    verbose = 3
    print("**** performing askanna push ******")
    print("**** read .askanna (system) ******")
    time.sleep(50/1000)
    print("**** read ~/.askanna (user homedir) ******")
    time.sleep(50/1000)
    print("**** read .askanna (project) ******")
    time.sleep(50/1000)
    print("**** packaging current directoy ******")
    time.sleep(150/1000)
    print("**** create manifest ******")
    time.sleep(5/10000)
    print("**** upload manifest to askanna.io ******")
    time.sleep(150/1000)
    print("**** received upload token from askanna.io ******")
    time.sleep(250/1000)
    print("**** chunking package 1000 GB into 100 pieces *****")
    time.sleep(2000/1000)
    print("**** Start upload to https://sa080asdf098ads0f8a08asfd.afs.askanna.io/awesomeproject/upload ****")
    for x in range(1, 100):
        if verbose > 2:
            print(f"**** uploading piece {x}/100 ")
        time.sleep(100/1000)
    print("**** upload completed *****")
    time.sleep(250/1000)
    print("**** Waiting for ack from askanna.io *****")
    time.sleep(500/1000)
    print("**** [ASKANNA] Congratulations Bob! Your submission is well received ****")
    print("**** [ASKANNA] Access: https://askanna.io/awesomeproject/job/49283/status *****")
    print("**** [ASKANNA] End of of message *****")
