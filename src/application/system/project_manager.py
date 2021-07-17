#!/usr/bin/python
#-*- coding: utf-8 -*-

from user import User
from database import meta 
from sqlalchemy import Column, Integer, ForeignKey
from user_role import UserRole

#association Table for ProjectManager and Users
project_manager_has_users = Table(  'managers_has_members',
                                    meta.Base.metadata,
                                    Column('user_id', Integer, ForeignKey('users.id')),
                                    Column('manager_id',Integer, ForeignKey('project_managers.id')                              

class ProjectManager(User):
    """
    Represents a Group Owner
    """

    __tablename__ = 'project_managers'
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': UserRole.ProjectManager
    }
    def __init__(self):
        self.team_memebers = None

    def get_role(self, ):
        return UserRole.ProjectManager

    def get_team_members(self, ):
        pass

    def has_user_in_team(self, user):
        pass

    def add_user_to_team(self, user):
        pass

