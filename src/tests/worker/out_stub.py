#!/usr/bin/python
#-*- coding: utf-8 -*-

from worker.msg_out import Out

class OutStub(Out):
    
    def __init__(self):
        pass
    
    def update_status(self, new_status):
        pass
    
    def update_task(self, task):
        pass
    
    def register(self, master_adress, master_token, worker_name, worker_address, aliases, status):
        pass
    
    def raise_exception(self, task):
        exception = task.get_exceptions()[0]
        raise(exception)
    
    def raise_error(self, task):
        error = task.get_errors()[0]
        raise(error)
    
    def final_informations(self, task):
        pass
