import gevent.monkey
import os
from helpers import get_conf_directory
os.environ["SUPPORT_GEVENT"] = 'True'

gevent.monkey.patch_all()

import sys
from controller.controller_initializer import ControllerInitializer


def main(args=None):
    conf_dir = get_conf_directory()
    abs_conf_path = conf_dir + 'controller/config.ini'
    print("Starting controller with config at: " + abs_conf_path)
    ControllerInitializer(config_path=abs_conf_path)


if __name__ == "__main__":
    main() 
