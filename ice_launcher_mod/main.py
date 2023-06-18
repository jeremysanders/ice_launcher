from . import config
from .server import run_server
import logging

def main():
    logging.basicConfig(level=logging.INFO)

    conf = config.Config('ice_launcher.conf')
    run_server(conf)
