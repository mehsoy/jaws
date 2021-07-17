#!/usr/bin/python
#-*- coding: utf-8 -*-

import sqlalchemy

from sqlalchemy import String, Column, Integer, Enum, ForeignKey
from database import meta
from .user_role import UserRole
#from .administrator import Administrator
from exceptions.user_not_found_exception import UserNotFoundException

class User(meta.Base):
    """
    Represents a unique user with a given security Token
    """
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, unique=True)
    token = Column('token', String)
    user_type = Column('user_type', Enum(UserRole))
    
    __mapper_args__ = {
        'polymorphic_identity': UserRole.User,
        'polymorphic_on': user_type,
        'with_polymorphic': '*'
    }
    
    def __init__(self, name, token=None):
        """
        Default Constructor
        :param name: name of the user
        :param token: secret
        :type name: String
        :type token: String
        """
        self.name = name
        self.token = token
        session = meta.Session()
        session.add(self)
        session.commit()
    
    @classmethod
    def get_users(cls, roles=None, names=None):
        """
        Returns users with the given parameters:
        :param roles: List of roles (User,Admin,...)
        :param names: List of Names
        """
        session = meta.Session()
        users =  session.query(cls)
        if role is not None:
            users = users.filter(cls.user_type.in_(roles))
        if name is not None:
            users = users.filter(cls.name.in_(names))

    @classmethod
    def get_user_by_username(cls, username):
        """
        Returns a user with the given Name or None
        :param username: name to look for
        :type username: String
        :returns: User or None
        """
        session = meta.Session()
        user = session.query(cls).filter(cls.name == username).one_or_none()
        if user is None:
            raise UserNotFoundException("User " + username + " does not exist")
        else:
            return user
    
    def get_token(self,):
        """"
        Returns the token
        :returns: token
        """
        return self.token

    def get_username(self):
        """
        Returns username
        :return: username
        """
        return self.name

    def get_user_type(self):
        """
        Returns user type
        :return:
        """
        return self.user_type

    def set_user_type(self, user_type):
        """
        Sets UserRole to type
        :param type: UserRole
        """
        session = meta.get_session(self)
        self.user_type = user_type
        session.commit()
        session.flush()
        return

    def set_token(self, token):
        session = meta.get_session(self)
        self.token = token
        session.commit()
        session.flush()
        return

class Administrator(User):
    """
    Represents a User which is also an Administrator
    """
    __mapper_args__ = {
        'polymorphic_identity': UserRole.Administrator
    }
    
    def __init__(self, name, token):
        try:
            User.get_user_by_username(name)
        except UserNotFoundException:
            super().__init__(name, token)

        User.get_user_by_username(name).set_user_type(UserRole.Administrator)
        session = meta.get_session(self)
        session.commit()

    @property
    def get_role(self, ):
        return UserRole.Administrator


