# icelaunch: Main entry routine
#
# Copyright Jeremy Sanders (2023)
# Released under the MIT Licence

from . import config
from .server import run_server
import logging

def main():
    conf = config.Config('ice_launcher.conf')

    loglevels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }
    logging.basicConfig(level=loglevels[conf.main['log_level']])

    run_server(conf)
