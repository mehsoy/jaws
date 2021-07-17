#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys

from helpers import get_conf_directory
from master.master_initializer import MasterInitializer

def main(args=None):
    """The main routine of master package."""
    if args is None:
        args = sys.argv[1:]

    conf_dir = get_conf_directory()
    abs_conf_path = conf_dir + 'master/config.ini'
    print("Starting master with config at: " + abs_conf_path)
    MasterInitializer(config_path=abs_conf_path)

if __name__ == "__main__":
    main() 
