# This example shows how to run Vakt MongoStorage migrations.

import logging
import atexit

from pymongo import MongoClient
from vakt import Policy, ALLOW_ACCESS
from vakt.storage.mongo import MongoStorage, MongoMigrationSet
from vakt.storage.migration import Migrator

# setup logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(logging.StreamHandler())

# create storage object
client = MongoClient('localhost', 27017)
storage = MongoStorage(client, 'vakt_policies_migration_test', collection='policies')

# save some policies
storage.add(
    Policy('a', actions=['<get.*>'], resources=['test:<.*>', 'prod:<.*>'], subjects=['Max'], effect=ALLOW_ACCESS)
)
storage.add(
    Policy('b', actions=['post'], resources=['<.*>'], subjects=['<.*>'])
)

# create a migrator
migrator = Migrator(MongoMigrationSet(storage))

# run all known migrations
# this is expected to error for saved policies when running migration #2, see logs
migrator.up()
migrator.down()

# run a single migration by number
migrator.up(number=1)
migrator.down(number=1)


# cleanup database
def prune():
    storage.delete('a')
    storage.delete('b')


atexit.register(prune)

