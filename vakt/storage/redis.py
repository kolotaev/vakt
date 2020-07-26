"""
Redis storage for Policies.
"""

import logging
import pickle

from ..storage.abc import Storage
from ..policy import Policy
from ..exceptions import PolicyExistsError


log = logging.getLogger(__name__)

DEFAULT_COLLECTION = 'vakt_policies'


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
        return Policy.from_json(data.decode('utf-8'))


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
    """
    Stores Policies in Redis.

    Stores all policies in a single hash whose name is a `collection` argument.
    Each filed in this hash is a Policy's UID and the value of this key is a serialized Policy representation.
    """

    def __init__(self, client, collection=DEFAULT_COLLECTION, serializer=None):
        # todo - use hiredis
        self.client = client
        self.collection = collection
        self.sr = serializer
        if serializer is None:
            self.sr = JSONSerializer()

    def add(self, policy):
        try:
            uid = policy.uid
            done = self.client.hsetnx(self.collection, uid, self.sr.serialize(policy))
            if done == 0:
                log.error('Error trying to create already existing policy with UID=%s.', uid)
                raise PolicyExistsError(uid)
        # todo - log stacktrace?
        except Exception as e:
            log.error('Error trying to create already existing policy with UID=%s.', uid)
            raise PolicyExistsError(uid)
        log.info('Added Policy: %s', policy)

    def get(self, uid):
        ret = self.client.hget(self.collection, uid)
        if not ret:
            return None
        return self.sr.deserialize(ret)

    def get_all(self, limit, offset):
        # todo - explain?
        self._check_limit_and_offset(limit, offset)
        # Special check for: https://docs.mongodb.com/manual/reference/method/cursor.limit/#zero-value
        if limit == 0:
            return []
        result = self.client.hscan(self.collection, cursor=offset, count=limit)
        if len(result) < 2:
            log.error('Error calling Redis SCAN. Supposed to return tuple with 2 elements. Got: %s', result)
            return []
        return self.__feed_policies(result[1])

    def find_for_inquiry(self, inquiry, checker=None):
        # todo - use lock?
        data = self.client.hgetall(self.collection)
        if not data:
            return []
        return self.__feed_policies(data)

    def update(self, policy):
        uid = policy.uid
        # todo - use scripting for transactional update
        exists = self.client.hexists(self.collection, uid)
        if exists:
            self.client.hset(self.collection, uid, self.sr.serialize(policy))
            log.info('Updated Policy with UID=%s. New value is: %s', uid, policy)

        # def transactional_update(pipe):
        #     # pipe.multi()
        #     rr = pipe.hexists(self.collection, uid)
        #     if rr:
        #         pipe.hset(self.collection, uid, self.sr.serialize(policy))
        #         # pipe.execute()
        # res = self.client.transaction(transactional_update, self.collection)
        # return res

        # pipe = self.client.pipeline()
        # try:
        #     pipe.hexists(self.collection, uid)
        #     pipe.hset(self.collection, uid, self.sr.serialize(policy))
        #     res = pipe.execute()
        #     if not res[0]:
        #         pipe.reset()
        #     log.info('Updated Policy with UID=%s. New value is: %s', uid, policy)
        # except Exception as e:
        #     # todo - fix
        #     pipe.reset()
        #     raise e

    def delete(self, uid):
        # todo - check exceptions?
        self.client.hdel(self.collection, uid)
        log.info('Deleted Policy with UID=%s.', uid)

    def __feed_policies(self, data):
        """
        Yields Policies from the given cursor.
        """
        # todo - why dict is returned???
        for uid in data:
            yield self.sr.deserialize(data[uid])
