"""
Redis storage for Policies.
"""

import logging
import pickle

from ..storage.abc import Storage
from ..policy import Policy
from ..exceptions import PolicyExistsError


log = logging.getLogger(__name__)


# todo - move to a separate module
class JSONSerializer:
    """
    Serializes/de-serializes policies to JSON for Redis storage
    """
    @staticmethod
    def serialize(policy):
        return policy.to_json()

    @staticmethod
    def deserialize(data):
        return Policy.from_json(data)


# todo - add levels
class PickleSerializer:
    """
    Serializes/de-serializes policies Python pickle representation for Redis storage
    """
    @staticmethod
    def serialize(policy):
        return pickle.dumps(policy)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)


class RedisStorage(Storage):
    """Stores all policies in Redis"""

    def __init__(self, client, collection='vakt', serializer=None):
        self.client = client
        self.sr = serializer
        self.collection = collection
        if serializer is None:
            self.serializer = JSONSerializer

    def prefix(self, uid):
        return '%s:%s' % (self.collection, uid)

    def add(self, policy):
        try:
            key = self.prefix(policy.uid)
            self.client.set(key, self.sr.serialize(policy), nx=True)
        except Exception:
            log.error('Error trying to create already existing policy with UID=%s.', policy.uid)
            raise PolicyExistsError(policy.uid)
        log.info('Added Policy: %s', policy)

    def get(self, uid):
        key = self.prefix(uid)
        ret = self.client.get(key)
        if not ret:
            return None
        return self.sr.deserialize(ret)

    def get_all(self, limit, offset):
        self._check_limit_and_offset(limit, offset)
        # Special check for: https://docs.mongodb.com/manual/reference/method/cursor.limit/#zero-value
        if limit == 0:
            return []
        match_pattern = self.prefix('*')
        cur = self.client.scan(cursor=offset, match=match_pattern, count=limit)
        return self.__feed_policies(cur)

    def find_for_inquiry(self, inquiry, checker=None):
        self.retrieve_all(batch=100)

    def update(self, policy):
        uid = policy.uid
        try:
            key = self.prefix(uid)
            self.client.set(key, self.sr.serialize(policy), xx=True)
            log.info('Updated Policy with UID=%s. New value is: %s', uid, policy)
        except Exception as e:
            # todo - fix
            raise e

    def delete(self, uid):
        self.client.el(uid)
        log.info('Deleted Policy with UID=%s.', uid)

    def __feed_policies(self, cursor):
        """
        Yields Policies from the given cursor.
        """
        for data in cursor:
            yield self.sr.deserialize(data)
