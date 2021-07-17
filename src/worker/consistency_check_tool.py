#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class ConsistencyCheckTool:
    __metaclass__ = ABCMeta

    WRONG_SETUP = ("At worker %s:\nCould not execute '%s', the program was not found."
                   + " Please make sure to have it installed. The Error message was:\n%s")

    @abstractmethod
    def get_name(self):
        """Returns the name of underlying Unix-tool."""
        raise NotImplementedError

    @abstractmethod
    def consistency_check(self, task):
        """
        Compares the content of task sourcefile and copied file. If the content is found to be the same by measure of
        the underlying tool (eg. having the same sha256-sums) task_status is set to checked. If any error occurs
        durign checking a corresponding exception/error is added to task and its status is set to exception/error.
        
        :param task: the task containing source and copyfile names.
        :return task: the updated task.
        """
        raise NotImplementedError
