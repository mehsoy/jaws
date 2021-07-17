#!/usr/bin/python
# -*- coding: utf-8 -*-

from worker.action import Action
from worker.copytool.copytool import Copytool
from worker.task import Task
from worker.task_status import TaskStatus

from exceptions.action_not_supported_exception import ActionNotSupportedException
from exceptions.copy_fail_error import CopyFailError


class Tar(Copytool):
    """A wrapper class for the linux commandline tool tar. THis is best to be used with tape archives.
    Implemets the COpytool interface."""
    # declare error messages:
    NO_TAR_MODE = "At worker '%s' in task '%d' copy process: No tar mode was found in task.special_options."
    MODE_NOT_IMPLEMENTED = "At worker '%s' in task '%d': this special_tool_option does not work with tar."

    @property
    def SUPPORTED_ACTIONS(self, ):
        return [
            Action.EXTRACT_TAR,
            Action.COMPRESS_TAR
        ]

    def create_cmd(self, task: Task):
        cmd = []
        # We need to make sure, that the directory we want to copy into
        # actually exists. # TODO maybe extract this into copytool module
        cmd.extend(['mkdir', '-p', task.absolute_target_path, '&&'])

        if task.action == Action.EXTRACT_TAR:
            # Extract all .tar* files in the requested directory.
            # WARNING: If files inside the tarballs have the same name, one of them is overwritten!
            # TODO *.tar currently. May also have to match *.tar.gz based on options ('-z')
            cmd.extend(['ls', task.absolute_source_path + '*.tar', '|', 'xargs', '-i'])

            cmd.append(self._executable_path)
            cmd.extend(self._options.split(" "))
            cmd.extend(['-x', "-f", '{}'])
            cmd.extend(["-C", task.absolute_target_path])

        elif task.action == Action.COMPRESS_TAR:
            cmd.append(self._executable_path)
            cmd.extend(self._options.split(" "))
            # We define a tarball name in our directory into which we can compress.
            # TODO Refactor this ~
            cmd.extend(['-c', "-f", task.absolute_target_path + (task.absolute_target_path.split('/')[-2] + '.tar')])
            cmd.extend(["-C", task.absolute_source_path, '.'])
        else:
            raise ActionNotSupportedException(str(task.action))
        return cmd

    @classmethod
    def parse_stats(cls, output: str):
        stats = dict()
        lines = output.split('\n')
        #  lists every moved file in a new line w/ verbose flag
        stats['n_of_files'] = len(lines) - 2
        stats['total_size'], _, _ = cls._get_list_of_numbers(lines[-2])
        return stats

    def handle_error(self, retcode, cmd, output, task: Task):
        """Evaluates the returncode of tar and throws suiting Errors.
        
        :raises: CopyFailError, ConnectionFailedError"""
        # WARNING this error handling assumes tar version 1.30 or older!
        if retcode == -1:
            # the process was killed intendedly, so we just update its status
            task.status = TaskStatus.TERMINATED
            return task
        elif retcode == 1:
            # some files differ -> consistency check was not successfull
            if self._retries < self._retry_count:
                self._retries += 1
                self.execute_cmd(cmd, task)
            else:
                task.add_error(CopyFailError(Copytool.CHECK_FAIL
                                             % (task.worker_name, task.get_id(), str(cmd), output)))
        elif retcode == 2:
            # a fatal, unrecoverable error occured
            task.add_error(CopyFailError(Copytool.WRITE_FAIL
                                         % (task.worker_name, task.get_id(), str(cmd), output)))
        else:
            task.add_error(CopyFailError(Copytool.WRITE_FAIL
                                         % (task.worker_name, task.get_id(), str(cmd), output)))
        task.status = TaskStatus.ERROR
        return task
