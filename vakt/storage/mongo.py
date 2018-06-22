"""
MongoDB storage for Policies.
"""

import logging
import json

from pymongo.errors import DuplicateKeyError

from ..storage.abc import Storage
from ..exceptions import PolicyExistsError
from ..policy import Policy


DEFAULT_COLLECTION = 'vakt_policies'

log = logging.getLogger(__name__)


class MongoStorage(Storage):
    """Stores all policies in MongoDB"""

    def __init__(self, client, db_name, collection=DEFAULT_COLLECTION, use_regex=True):
        self.client = client
        self.db = self.client[db_name]
        self.collection = self.db[collection]
        # todo - add non-regex check
        self.use_regex = use_regex

    def add(self, policy):
        policy._id = policy.uid
        try:
            self.collection.insert_one(self._prepare_doc(policy))
        except DuplicateKeyError:
            log.error('Error trying to create already existing policy with UID=%s.', policy.uid)
            raise PolicyExistsError(policy.uid)

    def get(self, uid):
        ret = self.collection.find_one(uid)
        if not ret:
            return None
        del ret['_id']
        return Policy.from_json(json.dumps(ret))

    def get_all(self, limit, offset):
        pass

    def find_for_inquiry(self, inquiry):
        pass

    def update(self, policy):
        uid = policy.uid
        self.collection.update_one(
            {'_id': uid},
            {"$set": self._prepare_doc(policy)},
            upsert=False)

    def delete(self, uid):
        self.collection.delete_one({'_id': uid})

    @staticmethod
    def _prepare_doc(policy):
        # todo - add dict inheritance
        return json.loads(policy.to_json())