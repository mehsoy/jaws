#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path

import pytest

from exceptions.naming_convention_error import NamingConventionError
from worker.action import Action
from worker.task_status import TaskStatus


@pytest.mark.usefixtures('build_test_environment')
class TestTar:

    def test_directory_compress(self, centos127, archive1, make_tar_task):
        task = make_tar_task(1, centos127, 'johann-test_dir-1/', archive1)
        task.copytool.copy(task)
        assert os.path.exists(task.absolute_target_path) is True
        assert task.status == TaskStatus.COPIED

        task = task.copytool.consistency_check(task)
        assert task.status == TaskStatus.CHECKED

    def test_directory_extract(self, centos127, archive1, make_tar_task):
        task = make_tar_task(1, archive1, 'johann-secret_archive-1/', centos127)
        task = task.copytool.copy(task)

        abs_path = task.absolute_target_path
        assert task.status == TaskStatus.COPIED
        assert os.path.exists(abs_path + 'bible/jesus.txt')
        assert os.path.exists(abs_path + 'bible/maria.rc')
        with open(abs_path + 'bible/jesus.txt', 'r') as f:
            assert f.read().rstrip() == 'Let there be light.'

    def test_bad_naming(self, centos127, archive1, make_tar_task):
        task = make_tar_task(1, centos127, 'bad_naming', archive1)
        with pytest.raises(NamingConventionError):
            task.copytool.copy(task)


def test_action_support(default_tar):
    tar = default_tar
    assert tar.supports(Action.COMPRESS_TAR)
    assert tar.supports(Action.EXTRACT_TAR)
