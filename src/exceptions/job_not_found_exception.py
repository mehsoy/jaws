#!/usr/bin/python
#-*- coding: utf-8 -*-

from .not_existing_entity_exception import NotExistingEntityException

class JobNotFoundException(NotExistingEntityException):
    pass
