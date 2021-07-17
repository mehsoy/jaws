#!/usr/bin/python
#-*- coding: utf-8 -*-

import pytest

from worker.worker_initializer import WorkerInitializer
#TODO write code to register this worker at the Master on 141.52.39.127:3390

def register(path_to_config: str):
    WorkerInitializer(path_to_config)

def test_register_success():
    register("src/worker/config.ini")

def test_register_double():
    register("src/worker/config.ini")
    with pytest.raises(Exception):
        register("src/worker/config.ini")
