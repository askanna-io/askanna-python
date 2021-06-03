# -*- coding: utf-8 -*-
import sys
import click

from askanna.core import client as askanna_client, exceptions


class ResultGateway:
    def __init__(self, *args, **kwargs):
        self.client = askanna_client

    def get(self, run_suuid: str):
        result_url = f"{self.client.config.remote}result/{run_suuid}/"

        try:
            result = self.client.get(result_url)
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

        if result.status_code != 200:
            raise exceptions.GetError(
                f"{result.status_code} - We cannot find this result for you"
            )

        return result.content

    def get_content_type(self, run_suuid: str) -> str:
        result_url = f"{self.client.config.remote}result/{run_suuid}/"
        result_header = self.client.head(result_url)

        if result_header.status_code != 200:
            raise exceptions.HeadError(
                f"{result_header.status_code} - We cannot find this result for you"
            )

        return str(result_header.headers.get("Content-Type"))
