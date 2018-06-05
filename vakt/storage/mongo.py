"""
MongoDB storage for Policies.
"""

import logging

from ..storage.abc import Storage
from ..exceptions import PolicyExistsError


DEFAULT_COLLECTION = 'vakt_policies'

log = logging.getLogger(__name__)


class MongoStorage(Storage):
    """Stores all policies in MongoDB"""

    def __init__(self, client, collection=DEFAULT_COLLECTION):
        self.client = client
        self.db = self.client[collection]

    def add(self, policy):
        uid = policy.uid
        try:
            self.db.insert_one(policy.to_json())
        except Exception:
            log.error('Error trying to create already existing policy with UID=%s', uid)
            raise PolicyExistsError

    def get(self, uid):
        pass

    def get_all(self, limit, offset):
        pass

    def find_for_inquiry(self, inquiry):
        pass

    def update(self, policy):
        pass

    def delete(self, uid):
        pass
