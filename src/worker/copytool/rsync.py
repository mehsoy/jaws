#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

from exceptions.action_not_supported_exception import ActionNotSupportedException
from exceptions.connection_failed_error import ConnectionFailedError
from worker.action import Action
from worker.copytool.copytool import Copytool
from worker.task import Task
from worker.task_status import TaskStatus

from exceptions.copy_fail_error import CopyFailError


class Rsync(Copytool):
    """A wrapper class for the linux commandline tool rsync. Implemets the COpytool interface."""

    @property
    def SUPPORTED_ACTIONS(self, ):
        return [Action.COPY]

    def create_cmd(self, task: Task):
        if self.supports(task.action):
            cmd = [self._executable_path]
            for option in self._options.split(" "):
                cmd.append(option)
            cmd.append(task.absolute_source_path)
            cmd.append(task.absolute_target_path)
            return cmd
        else:
            raise ActionNotSupportedException()

    @classmethod
    def parse_stats(cls, output: str):
        print(output)
        stats = dict()
        lines = output.split('\n')
        numbers = cls._get_list_of_numbers(lines[1])

        #  If the directory has no files, there will be no "reg:" entry in the output.
        stats['n_of_files'], _, stats['n_of_dirs'] = numbers if len(numbers) == 3 else (numbers[0], 0, numbers[1])
        stats['total_size'], = cls._get_list_of_numbers(lines[6])
        return stats

    def handle_error(self, retcode, cmd, output, task):
        """Evaluates the returncode of rsync and raises suiting Errors.
        
        :raises: CopyFailError, ConnectionFailedError"""
        if retcode < 0:
            # the process was killed intendedly, so we just update its status
            task.status = TaskStatus.TERMINATED
            return task
        elif retcode == 1:
            # syntax or usage error
            task.add_error(CopyFailError(super().WRONG_SYNTAX % (task.get_worker_name(), task.get_id(), output)))
        elif retcode == 3:
            # file selection error
            task.add_error(CopyFailError(super().NO_FILE_ERR % (task.get_worker_name(), task.get_id(), output)))
        elif retcode == 23:
            # partial transfer due error
            if self._retries < self._retry_count:
                self._retries += 1
                task.add_error()
                self.execute_cmd(cmd, task)
            else:
                task.add_error(CopyFailError(super().WRITE_FAIL
                                             % (task.worker_name, task.get_id(), str(cmd), output)))
        elif retcode == 24:
            # partial transfer because source file vanished
            task.add_error(CopyFailError(super().SRC_VANISHED % (task.worker_name, task.get_id())))
        elif (retcode == 35) or (retcode == 30):
            task.add_error(ConnectionFailedError(Copytool.CONN_TIMEOUT
                                                 % (task.worker_name, task.get_id(), output)))
        else:
            # connection timeouts
            task.add_error(CopyFailError(Copytool.STANDARD % (task.worker_name, task.get_id(), output)))
        task.status = TaskStatus.ERROR
        return task
