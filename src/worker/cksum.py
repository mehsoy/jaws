#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess

from worker.consistency_check_tool import ConsistencyCheckTool
from worker.task import Task
from worker.task_status import TaskStatus

from exceptions.copy_not_successfull_exception import CopyNotSuccessfullException
from exceptions.system_setup_error import SystemSetupError


class Cksum(ConsistencyCheckTool):
    # better declare error messages here to easily change them
    CKSUM_NOSUCCESS = ("Consistency check of task %d was not successfull."
                       + "\ncksum value of source: %d\ncksum value of target: %d")
    CKSUM_ERR = "During consistency_check of task %d Cksum exited with following message:\n%s"
    WRONG_CONFIG = "At worker %s:\nCksum could not be executed due following ValueError:\n%s"

    def __init__(self):
        pass

    @staticmethod
    def get_name():
        return "cksum"

    @staticmethod
    def consistency_check(task: Task):
        """Performs a consistency check on copied file using the tool cksum.
        
        :raises: IncorrectConfigInWorkerException, CopyNotSuccessfullException, SystemSetupError
        """
        orig_path = task.absolute_source_path
        copy_path = task.absolute_target_path
        # Because cksum only can check single files, we have to recurse manually
        orig_sum = 0
        if os.path.isdir(orig_path):
            # as we only compare the sums in the end, we don't depend on having the same order checking files
            for root, dirs, files in os.walk(orig_path):
                for fname in files:
                    full_path = os.path.join(root, fname)
                    try:
                        orig_sum += int(Cksum._execute_cksum(full_path, task)[:-2].split(" ")[0])
                    except CopyNotSuccessfullException as e:
                        task.add_exception(e)
                        task.status = TaskStatus.EXCEPTION
                        return task
        else:
            # we just have one file to check:
            try:
                orig_sum += int(Cksum._execute_cksum(orig_path, task)[:-2].split(" ")[0])
            except CopyNotSuccessfullException as e:
                task.add_exception(e)
                task.sstatus = TaskStatus.EXCEPTION
                return task

        copy_sum = 0
        if os.path.isdir(copy_path):
            # as we only compare the sums in the end, we don't depend on having the same order checking files
            for root, dirs, files in os.walk(copy_path):
                for fname in files:
                    full_path = os.path.join(root, fname)
                    try:
                        copy_sum += int(Cksum._execute_cksum(full_path, task)[:-2].split(" ")[0])
                    except CopyNotSuccessfullException as e:
                        task.add_exception(e)
                        task.status = TaskStatus.EXCEPTION
                        return task
        else:
            # we just have one file to check:
            try:
                copy_sum += int(Cksum._execute_cksum(copy_path, task)[:-2].split(" ")[0])
            except CopyNotSuccessfullException as e:
                task.add_exception(e)
                task.status = TaskStatus.EXCEPTION
                return task
        # now we compare both sums and see whether they are equal.
        if orig_sum == copy_sum:
            task.status = TaskStatus.CHECKED
        else:
            task.add_exception(CopyNotSuccessfullException(Cksum.CKSUM_NOSUCCESS
                                                           % (task.get_id(), orig_sum, copy_sum)))
            task.status = TaskStatus.EXCEPTION
        return task

    @staticmethod
    def _execute_cksum(path: str, task: Task):
        """Executes cksum with given path and returns its output as int.
        
        :raises: IncorrectConfigInWorkerException, CopyNotSuccessfullException, SystemSetupError
        """
        cmd = ["cksum", path]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as process_err:
            # cksum errors all seem to have return code 1...
            raise (CopyNotSuccessfullException(Cksum.CKSUM_ERR % (task.get_id(), process_err.output)))
        except ValueError as value_err:
            raise (IncorrectConfigInWorkerException(Cksum.WRONG_CONFIG % (task.worker_name, value_err.output)))
        except OSError as os_err:
            raise (SystemSetupError(ConsistencyCheckTool.WRONG_SETUP
                                    % (task.worker_name, Cksum.get_name(), os_err.output)))
        return output
