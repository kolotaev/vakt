"""
MongoDB Storage and Migrations for Policies.
"""

import logging

import bson.json_util as b_json
from pymongo.errors import DuplicateKeyError

from ..storage.abc import Storage, Migration
from ..exceptions import PolicyExistsError, UnknownCheckerType
from ..policy import Policy
from ..checker import StringExactChecker, StringFuzzyChecker, RegexChecker


DEFAULT_COLLECTION = 'vakt_policies'

log = logging.getLogger(__name__)


class MongoStorage(Storage):
    """Stores all policies in MongoDB"""

    def __init__(self, client, db_name, collection=DEFAULT_COLLECTION):
        self.client = client
        self.database = self.client[db_name]
        self.collection = self.database[collection]
        self.condition_fields = [
            'actions',
            'subjects',
            'resources',
        ]

    def add(self, policy):
        try:
            self.collection.insert_one(self.__prepare_doc(policy))
        except DuplicateKeyError:
            log.error('Error trying to create already existing policy with UID=%s.', policy.uid)
            raise PolicyExistsError(policy.uid)
        log.info('Added Policy: %s.', policy)

    def get(self, uid):
        ret = self.collection.find_one(uid)
        if not ret:
            return None
        return self.__prepare_from_doc(ret)

    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        cur = self.collection.find(limit=limit, skip=offset)
        return self.__feed_policies(cur)

    def find_for_inquiry(self, inquiry, checker=None):
        q_filter = self._create_filter(inquiry, checker)
        cur = self.collection.find(q_filter)
        return self.__feed_policies(cur)

    def update(self, policy):
        uid = policy.uid
        self.collection.update_one(
            {'_id': uid},
            {"$set": self.__prepare_doc(policy)},
            upsert=False)
        log.info('Updated Policy with UID=%s. New value is: %s.', uid, policy)

    def delete(self, uid):
        self.collection.delete_one({'_id': uid})
        log.info('Deleted Policy with UID=%s.', uid)

    def _create_filter(self, inquiry, checker):
        """
        Returns proper query-filter based on the checker type.
        """
        if isinstance(checker, StringFuzzyChecker):
            return self.__string_query_on_conditions('$regex', lambda field: getattr(inquiry, field))
        elif isinstance(checker, StringExactChecker):
            return self.__string_query_on_conditions('$eq', lambda field: getattr(inquiry, field))
            # We do not use Reverse-regexp match since it's not implemented yet in MongoDB.
            # Doing it via Javascript function gives no benefits over Vakt final Guard check.
            # See: https://jira.mongodb.org/browse/SERVER-11947
        elif isinstance(checker, RegexChecker) or not checker:  # opt to RegexChecker as default.
            return {}
        else:
            log.error('Provided Checker type is not supported.')
            raise UnknownCheckerType(checker)

    def __string_query_on_conditions(self, operator, get_value):
        """
        Construct MongoDB query.
        """
        conditions = []
        for field in self.condition_fields:
            conditions.append(
                {
                    field: {
                        '$elemMatch': {
                            operator: get_value(field.rstrip('s'))
                        }
                    }
                }
            )
        return {"$and": conditions}

    @staticmethod
    def __prepare_doc(policy):
        """
        Prepare Policy object as a document for insertion.
        """
        # todo - add dict inheritance
        doc = b_json.loads(policy.to_json())
        doc['_id'] = policy.uid
        return doc

    @staticmethod
    def __prepare_from_doc(doc):
        """
        Prepare Policy object as a return from MongoDB.
        """
        # todo - add dict inheritance
        del doc['_id']
        return Policy.from_json(b_json.dumps(doc))

    def __feed_policies(self, cursor):
        """
        Yields Policies from the given cursor.
        """
        for doc in cursor:
            yield self.__prepare_from_doc(doc)


class Migration0To1x0x3(Migration):
    """
    Migration between versions 0 and 1.0.3
    """

    def __init__(self, storage):
        self.storage = storage
        self.index_name = lambda i: i + '_idx'
        self.multi_key_indices = [
            'actions',
            'subjects',
            'resources',
        ]

    @property
    def order(self):
        return 1

    def up(self):
        # MongoDB automatically creates a multikey index if any indexed field is an array;
        # https://docs.mongodb.com/manual/core/index-multikey/#create-multikey-index
        for field in self.multi_key_indices:
            self.storage.collection.create_index(field, name=self.index_name(field))

    def down(self):
        for field in self.multi_key_indices:
            self.storage.collection.drop_index(self.index_name(field))
