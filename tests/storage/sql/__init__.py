import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.event import listens_for
from sqlalchemy.pool import Pool

from vakt.storage.sql.model import Base


# Need for switching on case sensitive LIKE statements on Sqlite
@listens_for(Pool, 'connect')
def run_on_connect(dbapi_con, connection_record):
    try:
        dbapi_con.execute('pragma case_sensitive_like=ON')
    except:
        pass


def create_test_sql_engine():
    dsn = os.getenv('DATABASE_DSN')
    if not dsn:
        pytest.exit('Please set DATABASE_DSN env variable with the target database DSN, ex: sqlite:///:memory:')
    engine = create_engine(dsn, encoding='utf-8')
    try:
        with engine.begin() as connection:
            connection.execute(text('select 1'))
    except OperationalError as e:
        pytest.exit('DATABASE_DSN is not correct. Error: %s' % e)
    return engine
