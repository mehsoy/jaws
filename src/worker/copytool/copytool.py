#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from abc import ABCMeta, abstractmethod
import shutil
import subprocess
from threading import Lock
import os
import signal

from exceptions.operation_not_allowed_exception import OperationNotAllowedException
from worker.action import Action
from worker.cct_mock import CCTMock
from worker.consistency_check_tool import ConsistencyCheckTool
from worker.msg_out import Out
from worker.task import Task
from worker.task_status import TaskStatus

from exceptions.action_not_supported_exception import ActionNotSupportedException
from exceptions.copy_process_failed_exception import CopyProcessFailedException
from exceptions.system_setup_error import SystemSetupError


class Copytool:
    """The interface for Copytools such as rsync or tar. Defines required methods."""
    __metaclass__ = ABCMeta
    # better declare error messages here to easily change them
    INVALID_SOURCE = ("In task '%d' The source with path: '%s' is neither a file nor a directory. "
                      + "We cannot work with that...")
    INVALID_OP = ("At worker '%s':\nDeleting files without checking the consistency first is prohibited. "
                  + "Please make sure to check consistency first.")
    NO_FILE_ERR = "At worker '%s' in task '%d' copy a file was not found.\nThe Errormessage was:\n%s"
    NO_SRC_FILE_ERR = "In task '%d' delete process the source file was not found.\nThe errormessage was:\n%s"
    NO_SRC_FILE_CK = ("In task '%d' delete process the sourcefile was not found. "
                      + "It probably got deleted before...")
    SRC_VANISHED = ("At worker '%s' in task '%d' the file could not be written partially because "
                    + "the source file vanished during process.")
    NO_PERM = ("In task '%d' the source could  not be deleted due PermissionError.\n"
               + "Check if the files are writeable.")
    TOOL_NOT_RUNNING = ("At worker '%s': You cannot kill a process that is not running. "
                        + "Please make sure to have it installed.")
    CHECK_FAIL = ("At worker '%s', in task %d:\nconsistency check with tool '%s' was not successful, "
                  + "Following Error occured:\n %s \n"
                  + "there must have been data loss in copy process. "
                  + "Please make sure not to change data during copy process.")
    WRONG_SYNTAX = "At worker '%s' in task '%d' there was a Syntax or usage Error:\n%s"
    WRONG_SETUP = 'At worker %s with copy tool %s following error occured: %s'
    WRITE_FAIL = ("At worker '%s' in task '%d' the file could not be written partially while executing command:"
                  + "\n%s\nFollowing Error occured:\n%s")
    CONN_TIMEOUT = "At worker '%s':\nDuring copying of task '%d' following ConnectionTimeoutError occured:\n%s"
    STANDARD = "At worker '%s':\nDuring copying of task '%d' following Error occured:\n%s"

    def __init__(self,
                 retry_count: int,
                 options: str,
                 executable_path: str,
                 consistency_check_tool: ConsistencyCheckTool = CCTMock):
        self._executable_path = executable_path
        self._options = options
        self._retry_count = retry_count
        self._consistency_check_tool = consistency_check_tool
        self._retries = 0
        self._process = None
        self._process_lock = Lock()

    @property
    def SUPPORTED_ACTIONS(self, ):
        raise NotImplementedError

    def copy(self, task):
        """Copies the source data to target with given special_tool_options.
        First checks if source file is accessible, then defines the mode of the used underlying copytool.
        Finally runs the copytool with all its options and handles potentially occuring errors.
        After exiting the copy process, updates the task status and returns it.
        If copy was successfull TaskStatus is set to copied.
        If any error/exception occured it is added to task and TaskStatus is set to error/exception.

        This is a default implementation, which will work for most tools. Other-
        wise this method should be overridden.
        
        :param task: the task to be used for copy.
        :return task: the updated task.
        """
        cmd = self.create_cmd(task)
        task.status = TaskStatus.COPYING
        stats = self.execute_cmd(cmd, task)
        return stats

    def supports(self, action: Action):
        """Returns True, if 'action' is supported by this copytool and
        False otherwise.
        """
        return True if action in self.SUPPORTED_ACTIONS else False

    def create_cmd(self, task: Task):
        """Initializes the parameters and options for execution and returns
        those in a list.
        """

    @abstractmethod
    def execute_cmd(self, cmd, task):
        """Executes the command and handles its output

        :raises: SystemSetupError, CopyFailError, ConnectionFailedError
        """
        try:
            # TODO bad security
            # TODO when ls displays error the retcode can still be 0 and the operation fail?
            shell_cmd = ' '.join(cmd)
            self._process = subprocess.Popen(shell_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                             universal_newlines=True, preexec_fn=os.setpgrp)
        except OSError as os_err:
            raise (SystemSetupError(Copytool.WRONG_SETUP
                                    % (task.get_worker_name(), self._executable_path, os_err.output)))

        output, unused_err = self._process.communicate()

        # as communicate() already waited for process to terminate, we just read the return code here
        # if the process was killed by kill_process, it will be negative
        retcode = self._process.poll()

        # syncronize this to avoid race with kill_process
        self._process_lock.acquire()
        self._process = None
        self._process_lock.release()
        task.status = TaskStatus.COPIED

        # this is the case if the job has been canceled intentionally with SIGTERM
        # TODO put this in handle_error method
        if retcode == -15:
            task.status = TaskStatus.TERMINATED
            return task

        if retcode is not 0:
            return self.handle_error(retcode, cmd, output, task)

        # TODO should this only be sent, if consistency_check was successful? -> put in buffer or
        #  the like. Also implement Error handling here
        stats = self.parse_stats(output)

        return stats

    @classmethod
    @abstractmethod
    def parse_stats(cls, output: str):
        # Return None instead of NotImplementedError. It may be very common for
        # copytools not to support this function.
        return None

    @staticmethod
    def _get_list_of_numbers(string :str):
        # Helper function used by parse_stats
        numbers = []
        string = string.strip(',')
        strings = re.split(':| ', string)
        for s in strings:
            number = ''.join(filter(str.isdigit, s.split('.')[0]))
            if number:
                numbers.append(int(number))
        return numbers

    @abstractmethod
    def handle_error(self, retcode, cmd, output, task):
        raise NotImplementedError

    def consistency_check(self, task: Task):
        """Uses a ConsistencyCheckTool to check if the before copied data is consistent.
        If anything in this method fails, the task status is set to error/exception and can then only be resumed 
        by the command of an administrator. This is to make sure we do not have any data loss.
        
        :param task: the task to be checked.
        :return task: the updated task.
        """
        task = self._consistency_check_tool.consistency_check(task)
        return task

    @staticmethod
    def delete(task):
        """Removes the source data that was before copied to target from its originating disk.
        If delete was successfull TaskStatus is set to deleted.
        If any error/exception occured it is added to task and TaskStatus is set to error/exception.
        
        :param task: the task to be used for delete.
        :return task: the updated task.
        
        :raises CopyProcessSequenceException: if it is not allowed to delete in current TaskStatus
        """
        if os.path.isfile(task.absolute_source_path):
            try:
                # a simple file removing utility
                os.remove(task.absolute_source_path)
            except FileNotFoundError as file_err:
                task.add_exception(CopyProcessFailedException(Copytool.NO_SRC_FILE_ERR
                                                              % (task.get_id(), file_err.output)))
                task.status = TaskStatus.EXCEPTION
                return task
            except PermissionError:
                task.add_exception(CopyProcessFailedException(Copytool.NO_PERM % task.get_id()))
                task.status = TaskStatus.EXCEPTION
                return task
        elif os.path.isdir(task.absolute_source_path):
            try:
                # a recursive file removing utility
                shutil.rmtree(task.absolute_source_path)
            except FileNotFoundError as file_err:
                task.add_exception(CopyProcessFailedException(Copytool.NO_SRC_FILE_ERR
                                                              % (task.get_id(), file_err.output)))
                task.status = TaskStatus.EXCEPTION
                return task
            except PermissionError:
                task.add_exception(CopyProcessFailedException(Copytool.NO_PERM % task.get_id()))
                task.status = TaskStatus.EXCEPTION
                return task
        else:
            if not os.path.exists(task.absolute_source_path):
                task.add_exception(CopyProcessFailedException(Copytool.NO_SRC_FILE_CK % task.get_id()))
            else:
                task.add_exception(CopyProcessFailedException(Copytool.INVALID_SOURCE
                                                              % (task.get_id(), task.get_absolute_source_path())))
            task.status = TaskStatus.EXCEPTION
            return task
        # if we get here no exception was triggered
        task.status = TaskStatus.DELETED
        return task

    def kill_process(self, task):
        """
        Interrupts the currently ongoing copy-process and deletes the already
        copied parts from the target disk. If everithing went well TaskStatus
        is set to terminated. If any error/exception occured it is added to
        task and TaskStatus is set to error/exception.
        
        :param task: the currently executed task.
        :return task: the updated task.
        """
        if not self.is_copying():
            raise (OperationNotAllowedException(Copytool.TOOL_NOT_RUNNING % task.worker_name))
        try:
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
        except Exception as e:
            task.add_error(e)
            task.status = TaskStatus.ERROR
        # to use delete method we create a dummy task
        dummy = Task(42, task.source_path, task.msg_out)
        dummy.status = TaskStatus.CHECKED
        if os.path.exists(task.absolute_target_path):
            dummy = self.delete(dummy)
        # now, error handling...
        if dummy.status == TaskStatus.ERROR:
            task.add_error(dummy.get_errors()[0])
            task.status = TaskStatus.ERROR
        elif dummy.status == TaskStatus.EXCEPTION:
            task.add_exception(dummy.get_exceptions()[0])
            task.status = TaskStatus.EXCEPTION
        else:
            # if there was an error during process kill we do not want to
            # overwrite it
            if task.status == TaskStatus.ERROR:
                return task
            task.status = TaskStatus.TERMINATED
            #self._process = None # this is done in execute_cmd method
        return task

    def is_copying(self, ):
        """returns true if the tool is currently executed."""
        self._process_lock.acquire()
        is_copying = self._process is not None
        self._process_lock.release()
        return is_copying
