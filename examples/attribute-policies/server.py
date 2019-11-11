import logging
import uuid
import os

import vakt
from vakt.rules import Eq, Any, NotEq, StartsWith, In, RegexMatch, CIDR, And, Greater, Less

import Pyro4

import pymongo
from vakt.storage.mongo import MongoStorage

from vakt.storage.sql import SQLStorage
from vakt.storage.sql.model import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


# Policies that guard our tiny Github clone.
policies = [
    vakt.Policy(
        str(uuid.uuid4()),
        actions=[Eq('get'), Eq('list'), Eq('read')],
        resources=[StartsWith('repos/google/tensor')],
        subjects=[Any()],
        effect=vakt.ALLOW_ACCESS,
        description='Grant read-access for all Google repositories starting with "tensor" to any User'
    ),
    vakt.Policy(
        str(uuid.uuid4()),
        actions=[In('delete', 'prune', 'exterminate')],
        resources=[RegexMatch(r'repos\/.*?\/.*?')],
        subjects=[{'name': Any(), 'role': Eq('admin')}, {'name': Eq('defunkt')}, Eq('defunkt')],
        effect=vakt.ALLOW_ACCESS,
        description='Grant delete-access for any repository to any User with "admin" role, or to a User named defunkt'
    ),
    vakt.Policy(
        str(uuid.uuid4()),
        actions=[Any()],
        resources=[{'category': Eq('administration'), 'sub': In('panel', 'switch')}],
        subjects=[{'name': Any(), 'role': NotEq('developer')}],
        effect=vakt.ALLOW_ACCESS,
        context={'ip': CIDR('127.0.0.1/32')},
        description="""
        Allow access to administration interface subcategories: 'panel', 'switch' if user is not
        a developer and came from local IP address.
        """
    ),
    vakt.Policy(
        str(uuid.uuid4()),
        actions=[Eq('fork')],
        resources=[StartsWith('repos/DataDog', ci=True)],
        subjects=[{'name': Any(), 'stars': And(Greater(50), Less(999))}],
        effect=vakt.ALLOW_ACCESS,
        description='Allow forking any DataDog repository for users that have > 50 and < 999 stars'
    ),
]


@Pyro4.behavior(instance_mode='single')
class GitHubGuardian:
    def __init__(self):
        self.storage = self._create_storage()
        self.guard = vakt.Guard(self.storage, vakt.RulesChecker())
        for p in policies:
            self.storage.add(p)

    @Pyro4.expose
    def check(self, inquiry):
        print('got inquiry', inquiry)
        return self.guard.is_allowed(inquiry)

    @Pyro4.expose
    def add_policy(self, policy):
        self.storage.add(policy)

    @staticmethod
    def _create_storage():
        # Here we instantiate the Policy Storage.
        # In this case it's Memory or MongoDB Storage,
        # but we can opt to SQL Storage, any other third-party storage, etc.
        def create_sql_storage(dsn):
            engine = create_engine(dsn, echo=True)
            Base.metadata.create_all(engine)
            session = scoped_session(sessionmaker(bind=engine))
            return SQLStorage(scoped_session=session)
        print('storage is ', os.environ.get('STORAGE'))
        use_storage = os.environ.get('STORAGE')
        if use_storage == 'mongo':
            user, password, host = 'root', 'root', 'localhost:27017'
            uri = 'mongodb://%s:%s@%s' % (user, password, host)
            return MongoStorage(pymongo.MongoClient(host=host), 'vakt_db', collection='vakt_github_guard')
        elif use_storage == 'mysql':
            return create_sql_storage('mysql+pymysql://root:root@localhost/vakt_db')
        elif use_storage == 'pg':
            return create_sql_storage('postgresql+psycopg2://postgres:root@localhost/vakt_db')
        else:
            return vakt.MemoryStorage()


def main():
    # configure logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(logging.StreamHandler())
    # start server
    Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
    Pyro4.Daemon.serveSimple({GitHubGuardian: "github.guardian"}, port=9999, ns=False)


if __name__ == '__main__':
    main()
