from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime
import ast
from database import meta


class Storage(meta.Base):

    __tablename__ = 'storages'

    alias = Column('alias', String, primary_key=True)
    mountpoint = Column(String)
    accept_jobs = Column(Boolean)
    has_home_dir = Column(Boolean)
    is_archive = Column(Boolean)
    max_extensions = Column(Integer)
    max_extension_period = Column(Integer)
    description = Column(String)

    def __init__(self, alias, mountpoint, accept_jobs, has_home_dir, is_archive, max_extensions,
                 max_extension_period, description):
        self.alias = alias
        self.mountpoint = mountpoint
        self.accept_jobs = accept_jobs
        self.has_home_dir = has_home_dir
        self.is_archive = is_archive
        self.max_extensions = max_extensions
        self.max_extension_period = max_extension_period
        self.description = description

        session = meta.get_session(self)
        session.commit()

    def set_accept_jobs(self, v):
        session = meta.get_session(self)
        self.accept_jobs = v
        session.commit()

    @classmethod
    def get_storages(cls):
        session = meta.Session()
        return session.query(cls).all()

    @classmethod
    def get_home_storages(cls):
        session = meta.Session()
        return session.query(cls).filter(cls.has_home_dir == True).all()

    @classmethod
    def get_storage_by_mountpoint(cls, mnt):
        session = meta.Session()
        return session.query(cls).filter(cls.mountpoint == mnt).one_or_none()

    @classmethod
    def get_storage_by_name(cls, name):
        """
        Returns a Storage with the given Name or None
        :param name: the alias to search
        :type name: String
        :returns a Storage or None
        """
        session = meta.Session()
        return session.query(cls).filter(cls.alias == name).one_or_none()

    def set_value(self, key, value):
        session = meta.get_session(self)
        if hasattr(self, key):
            if key in ['has_home_dir', 'accept_jobs', 'is_archive']:
                if value in ['True', 'true']:
                    value = True
                elif value in ['False', 'false']:
                    value = False
                else:
                    raise ValueError('You cant set ' + key + ' to ' + value)
            setattr(self, key, value)
        else:
            raise AttributeError('The attribute ' + key + 'doesn\'t exist.')
        session.commit()
