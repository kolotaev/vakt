"""
MongoDB storage for Policies.
"""

import logging
import json

from pymongo.errors import DuplicateKeyError

from ..storage.abc import Storage
from ..exceptions import PolicyExistsError, UnknownCheckerType
from ..policy import Policy
from ..checker import StringExactChecker, StringFuzzyChecker, RegexChecker


DEFAULT_COLLECTION = 'vakt_policies'

log = logging.getLogger(__name__)


class MongoStorage(Storage):
    """Stores all policies in MongoDB"""

    def __init__(self, client, db_name, collection=DEFAULT_COLLECTION):
        self.client = client
        self.db = self.client[db_name]
        self.collection = self.db[collection]
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

    def get(self, uid):
        ret = self.collection.find_one(uid)
        if not ret:
            return None
        return self.__prepare_from_doc(ret)

    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        cur = self.collection.find(limit=limit, skip=offset)
        for doc in cur:
            yield self.__prepare_from_doc(doc)

    def find_for_inquiry(self, inquiry, checker=None):
        if isinstance(checker, StringFuzzyChecker):
            # todo - use index. fts.
            q_filter = self.__string_query_on_conditions('$regex', lambda f: getattr(inquiry, f))
        elif isinstance(checker, StringExactChecker):
            q_filter = self.__string_query_on_conditions('$eq', lambda f: getattr(inquiry, f))
        # opt to RegexChecker if None or unknown.
        # We do not use Reverse-regexp match since it's not implemented yet in MongoDB.
        # Doing it via Javascript function gives no benefits over Vakt final Guard check.
        # See: https://jira.mongodb.org/browse/SERVER-11947
        elif isinstance(checker, RegexChecker) or not checker:
            q_filter = {}
        else:
            raise UnknownCheckerType(checker)
        cur = self.collection.find(q_filter)
        for doc in cur:
            yield self.__prepare_from_doc(doc)

    def update(self, policy):
        uid = policy.uid
        self.collection.update_one(
            {'_id': uid},
            {"$set": self.__prepare_doc(policy)},
            upsert=False)

    def delete(self, uid):
        self.collection.delete_one({'_id': uid})

    def __string_query_on_conditions(self, operator, fn):
        """
        Construct MongoDB query.
        """
        conditions = []
        for f in self.condition_fields:
            conditions.append(
                {
                    f: {
                        '$elemMatch': {
                            operator: fn(f.rstrip('s'))
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
        doc = json.loads(policy.to_json())
        doc['_id'] = policy.uid
        return doc

    @staticmethod
    def __prepare_from_doc(doc):
        """
        Prepare Policy object as a return from MongoDB.
        """
        # todo - add dict inheritance
        del doc['_id']
        return Policy.from_json(json.dumps(doc))
