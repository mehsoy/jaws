from datetime import timedelta, datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.ext.hybrid import hybrid_property

from application.handlers.config_handler import ConfigHandler
from database import meta
from application.system.storage import Storage
from .user import User


class Workspaces(meta.Base):

    __tablename__ = 'workspaces'
    id = Column('id', Integer, primary_key=True)
    username = Column(String, ForeignKey(User.name))
    label = Column(String, nullable=False)
    counter = Column(Integer, nullable=False)
    full_name = Column(String, nullable=False)
    storage = Column(String, ForeignKey(Storage.alias))
    time_created = Column(DateTime(timezone=True))
    max_extension_period = Column(Integer)
    max_extensions = Column(Integer)
    times_extended = Column(Integer)
    expiration_date = Column(DateTime(timezone=True))
    full_path = Column(String)
    status = Column(String)
    freetext = Column(String)
    freetext2 = Column(String)
    dummy = Column(Integer)

    def __init__(self, username, label, storage, max_extension_period, max_extensions, counter):
        self.username = username
        self.label = label
        self.counter = counter
        self.full_name = ConfigHandler().assemble_workspace_full_name(username, label, counter)
        self.storage = storage
        self.time_created = datetime.now()
        self.max_extension_period = max_extension_period
        self.max_extensions = max_extensions
        self.times_extended = 0
        self.expiration_date = datetime.now() + timedelta(days=max_extension_period)
        workspace_options = ConfigHandler().get_workspace_options()
        for option in workspace_options:
            for key in option:
                setattr(self, key, option[key])
        session = meta.get_session(self)
        session.add(self)
        session.commit()

    @hybrid_property
    def status(self):
        if self.expiration_date > datetime.now():
            return 'ACTIVE'
        else:
            return 'EXPIRED'

    @hybrid_property
    def time_remaining(self):
        return max([timedelta(seconds=0), self.expiration_date - datetime.now()])

    def set_storage(self, storage):
        session = meta.get_session(self)
        self.storage = storage
        session.commit()

    def set_full_path(self, path):
        session = meta.get_session(self)
        self.full_path = path
        session.commit()

    def set_value(self, key, value):
        session = meta.get_session(self)
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise AttributeError('The attribute ' + key + 'doesn\'t exist.')
        session.commit()

    def remove(self):
        session = meta.get_session(self)
        session.delete(self)
        session.commit()

    def extend(self):
        session = meta.get_session(self)
        if self.max_extensions <= self.times_extended:
            raise OverflowError('This workspace\' lifetime can\'t be extended anymore')
        else:
            self.times_extended = self.times_extended + 1
            self.expiration_date = self.expiration_date + timedelta(days=self.max_extension_period)
        session.commit()

    @classmethod
    def get_by_username(cls, username):
        session = meta.Session()
        workspaces = session.query(cls).filter(cls.username == username).all()
        return workspaces

    @classmethod
    def get_by_full_name(cls, full_name):
        session = meta.Session()
        workspaces = session.query(cls).filter(cls.full_name == full_name).one_or_none()
        return workspaces

    @classmethod
    def get_by_path(cls, path):
        session = meta.Session()
        workspaces = session.query(cls).filter(cls.full_path == path).one_or_none()
        return workspaces

    @classmethod
    def get_by_triple(cls, username, label, counter):
        session = meta.Session()
        w = session.query(cls).filter(Workspaces.username == username)\
            .filter(Workspaces.label == label)\
            .filter(Workspaces.counter==counter).first()
        return w

    @classmethod
    def get_all(cls):
        session = meta.Session()
        workspaces = session.query(cls)
        return workspaces.all()

    @classmethod
    def calc_counter(cls, label, username) -> int:
        session = meta.Session()
        workspaces = session.query(cls).filter(cls.label==label).filter(cls.username==username).all()
        numbers = [x.counter for x in workspaces]

        if not numbers: numbers = [-1]
        for i in range(0, max(numbers)+3):
            if i in numbers:
                continue
            else:
                return i


