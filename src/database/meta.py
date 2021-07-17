#!/usr/bin/python
#s-* coding: utf-8 -*-'
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

path = os.path.dirname(__file__)
engine = create_engine('sqlite:///' + path + '/../../database/dmd_data.sqlite3',
                    connect_args={'check_same_thread':False},
                    poolclass=StaticPool)
Session = sessionmaker(bind=engine)
Base = declarative_base()

def get_session(obj):
    if Session.object_session(obj):
        return Session.object_session(obj)
    else:
        session = Session()
        session.add(obj)
        return session

def has_active_session(obj):
    return Session.object_session(obj) is not None

def close_object_session(obj):
    Session.object_session(obj).close()

def clear_data():
    session = Session()
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()
