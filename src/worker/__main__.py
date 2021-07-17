#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from helpers import get_conf_directory
from worker.worker_initializer import WorkerInitializer


def main(args=None):
    """The main routine for worker."""
    if args is None:
        args = sys.argv[1:]

    conf_dir = get_conf_directory()
    abs_conf_path = conf_dir + 'worker/conf.toml'
    abs_copytools_path = conf_dir + 'worker/copytools.ini'
    print(' '.join(["Starting worker with config at:", abs_conf_path, 'and', abs_copytools_path]))
    worker_initializer = WorkerInitializer(config_path=abs_conf_path, copytool_path=abs_copytools_path)
    worker_initializer.register_to_master()
    worker_initializer.run_app()


if __name__ == "__main__":
    main()
