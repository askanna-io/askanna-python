from askanna.config.project import config as config_project
from askanna.config.server import config as config_server


class Config:
    @property
    def server(self):
        return config_server

    @property
    def project(self):
        return config_project


config = Config()
