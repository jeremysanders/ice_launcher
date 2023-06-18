# icelaunch: Main entry routine
#
# Copyright Jeremy Sanders (2023)
# Released under the MIT Licence

import argparse
import logging

from . import config
from .server import run_server

def main():
    parser = argparse.ArgumentParser(
        prog='ice_launcher',
        description='Launch ffmpeg source processes on demand for icecast2',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--config', default='ice_launcher.conf',
        help='Input configuration file',
    )
    args = parser.parse_args()

    conf = config.Config(args.config)

    loglevels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }
    logging.basicConfig(level=loglevels[conf.main['log_level']])

    run_server(conf)
