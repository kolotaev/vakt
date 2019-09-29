import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.event import listens_for
from sqlalchemy.pool import Pool

from vakt.storage.sql.model import Base


# Need for switching on case sensitive LIKE statements on SqlLite
@listens_for(Pool, "connect")
def my_on_connect(dbapi_con, connection_record):
    if hasattr(dbapi_con, 'execute'):
        dbapi_con.execute('pragma case_sensitive_like=ON')


def create_test_sql_engine():
    dsn = os.getenv('DATABASE_DSN')
    if not dsn:
        pytest.exit('Please set DATABASE_DSN env variable with the target database DSN, ex: sqlite:///:memory:')
    engine = create_engine(dsn, echo=False)
    try:
        engine.execute(text('select 1'))
    except Exception as e:
        pytest.exit('DATABASE_DSN is not correct. Error: %s' % e)
    return engine
